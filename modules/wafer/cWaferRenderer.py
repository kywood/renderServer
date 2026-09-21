import skia

import numpy as np
from modules.render import cPoint
from modules.render.cColor import cColor, Colors
from modules.render.cRenderer import cRenderer
from modules.wafer.cWafer import cWafer
import math


class cWaferRenderer:

    def __init__(self, renderer: cRenderer):
        self._renderer = renderer

    @property
    def _canvas(self):
        return self._renderer._canvas

    def draw(self, wafer:cWafer):
        # 외곽 경로 생성 — 배경, 클리핑, 테두리에 공통 사용
        path = self._create_wafer_path(wafer)

        self._draw_background(wafer, path)

        self._renderer.save()
        try:
            # 클리핑을 먼저 설정해야 이후 그림이 밖으로 안 나감
            self._apply_clip(path)

            self._draw_grid(wafer)
            self._draw_arrows(wafer)
        finally:
            self._renderer.restore()

        # 테두리는 마지막에 그려 선명하게 표시
        self._draw_outline(wafer, path)

    def _create_wafer_path(self, wafer: cWafer):
        # 원 또는 노치가 포함된 skia.Path 생성
        cx = wafer.point.x
        cy = wafer.point.y
        radius = wafer.radius

        path = skia.Path()

        if wafer.notch_angle == 0:
            path.addCircle(cx, cy, radius)
            return path

        bounds = skia.Rect.MakeLTRB(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
        )

        half_notch = wafer.notch_angle / 2.0

        path.arcTo(
            bounds,
            90.0 + half_notch,
            360.0 - wafer.notch_angle,
            False,
        )
        path.lineTo(cx, cy + radius - wafer.notch_depth)
        path.close()

        return path

    def _draw_background(self, wafer, path):
        self._renderer.draw_path(
            path,
            fill=Colors.WHITE,
        )
        pass

    def _apply_clip(self, path):
        self._renderer.clip_path(path)

    def _draw_grid(self, wafer: cWafer):
        """
        그리드의 모든 수직/수평선을 하나의 skia.Path로 묶어(Batching)
        Draw Call 1회로 그리기를 완료하는 최적화 버전
        """
        grid_size = wafer.grid_size.w
        count = math.ceil((wafer.radius * 2) / grid_size)
        grid_width = count * grid_size

        left = wafer.point.x - grid_width / 2
        top = wafer.point.y - grid_width / 2
        right = left + grid_width
        bottom = top + grid_width

        # 모든 격자선을 담을 단일 Path
        grid_path = skia.Path()

        # 1. 수직선 쌓기
        for i in range(count + 1):
            x = left + i * grid_size
            grid_path.moveTo(x, top)
            grid_path.lineTo(x, bottom)

        # 2. 수평선 쌓기
        for i in range(count + 1):
            y = top + i * grid_size
            grid_path.moveTo(left, y)
            grid_path.lineTo(right, y)

        # 3. 단 1번의 Draw Call로 GPU에 전송
        color = cColor(220, 220, 220)
        paint = skia.Paint(
            AntiAlias=True,
            Color=color.to_skia(),
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=1.0,
        )

        self._canvas.drawPath(grid_path, paint)

    def _draw_grid_op(self, wafer: cWafer):
        # wafer의 셀 좌표를 이용해 그리드 그리기
        grid_size = wafer.grid_size.w
        count = math.ceil((wafer.radius * 2) / grid_size)
        grid_width = count * grid_size

        left = wafer.point.x - grid_width / 2
        top = wafer.point.y - grid_width / 2
        right = left + grid_width
        bottom = top + grid_width

        color = cColor(220, 220, 220)

        # 수직선
        for i in range(count + 1):
            x = left + i * grid_size
            self._renderer.line(
                x, top, x, bottom,
                color=color,
                width=1.0,
            )

        # 수평선
        for i in range(count + 1):
            y = top + i * grid_size
            self._renderer.line(
                left, y, right, y,
                color=color,
                width=1.0,
            )

    def _draw_arrow(self ,
              start_point : cPoint,
              end_point: cPoint  ,
              color: cColor = Colors.BLUE,
              line_width:float = 1 ,
              head_size : float = 5 ,
              tail_radius: float = 2
              ):

        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y

        if dx == 0 and dy == 0:
            return

        self._renderer.line(
            x1=start_point.x,
            y1=start_point.y,
            x2=end_point.x,
            y2=end_point.y,
            color=color,
            width=line_width
        )
        # 시작점 → 끝점 방향각 (라디안)
        angle = np.atan2(dy, dx)

        if head_size > 0:
            spread = np.radians(30)

            left_x = end_point.x - head_size * np.cos(angle - spread)
            left_y = end_point.y - head_size * np.sin(angle - spread)

            right_x = end_point.x - head_size * np.cos(angle + spread)
            right_y = end_point.y - head_size * np.sin(angle + spread)

            self._renderer.path(
                points=[
                    (end_point.x, end_point.y),
                    (left_x, left_y),
                    (right_x, right_y),
                ],
                closed=True,
                fill=color,
            )


        if tail_radius > 0:
            self._renderer.circle(
                cx = start_point.x,
                cy = start_point.y,
                radius=tail_radius,
                fill=color,
            )

    def _draw_arrows_op(self, wafer: cWafer):
        # 셀의 top / left / right / bottom 화살표 그리기

        for cell_id , cell in wafer.cell_container.items():
            if cell.in_wafer():
                for arrow in cell.arrow_container:
                    self._draw_arrow(
                        start_point=arrow.start_point,
                        end_point=arrow.end_point,
                        color=arrow.color
                    )

    def _draw_arrows(self, wafer: cWafer):
        # 셀의 top / left / right / bottom 화살표 그리기
        """
            화살표 수천 개를 색상/스타일별 단일 skia.Path로 묶어(Batching)
            Draw Call을 극단적으로 줄이는 최적화 버전
            """
        # 색상별로 (선용 Path, 채우기용 Path) 나누어 저장
        stroke_paths_by_color = {}
        fill_paths_by_color = {}

        spread = 0.5235987755982988  # np.radians(30) 상수화로 매 루프 연산 방지

        # 기본 스타일 상수
        line_width = 1.0
        head_size = 5.0
        tail_radius = 2.0

        # import numpy as np

        for cell_id, cell in wafer.cell_container.items():
            if not cell.in_wafer():
                continue

            for arrow in cell.arrow_container:
                p1 = arrow.start_point
                p2 = arrow.end_point
                dx = p2.x - p1.x
                dy = p2.y - p1.y

                if dx == 0 and dy == 0:
                    continue

                color_skia = arrow.color.to_skia()

                # 색상별 Path 버퍼 준비
                if color_skia not in stroke_paths_by_color:
                    stroke_paths_by_color[color_skia] = skia.Path()
                    fill_paths_by_color[color_skia] = skia.Path()

                stroke_path = stroke_paths_by_color[color_skia]
                fill_path = fill_paths_by_color[color_skia]

                # 1. 몸통 선 (Stroke Path에 추가)
                stroke_path.moveTo(p1.x, p1.y)
                stroke_path.lineTo(p2.x, p2.y)

                angle = np.atan2(dy, dx)

                # 2. 화살표 머리 삼각형 (Fill Path에 추가)
                if head_size > 0:
                    left_x = p2.x - head_size * np.cos(angle - spread)
                    left_y = p2.y - head_size * np.sin(angle - spread)
                    right_x = p2.x - head_size * np.cos(angle + spread)
                    right_y = p2.y - head_size * np.sin(angle + spread)

                    fill_path.moveTo(p2.x, p2.y)
                    fill_path.lineTo(left_x, left_y)
                    fill_path.lineTo(right_x, right_y)
                    fill_path.close()

                # 3. 꼬리 원 (Fill Path에 추가)
                if tail_radius > 0:
                    fill_path.addCircle(p1.x, p1.y, tail_radius)

        # --- Draw Call 전송 (파이썬 루프 종료 후 색상당 1회만 실행) ---

        # 선 그리기용 Paint
        stroke_paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=line_width
        )
        # 면 채우기용 Paint
        fill_paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kFill_Style
        )

        for color_skia in stroke_paths_by_color.keys():
            # 1. 모든 몸통 선 한 번에 그리기
            stroke_paint.setColor(color_skia)
            self._canvas.drawPath(stroke_paths_by_color[color_skia], stroke_paint)

            # 2. 모든 머리/꼬리 도형 한 번에 그리기
            fill_paint.setColor(color_skia)
            self._canvas.drawPath(fill_paths_by_color[color_skia], fill_paint)



    def _draw_outline(self, wafer: cWafer, path):
        self._renderer.draw_path(
            path,
            stroke=cColor(64, 64, 64),
            stroke_width=wafer.stroke,
        )
        pass

    pass


