import skia
from modules.render.cColor import cColor, Colors
from modules.render.cRenderer import cRenderer
from modules.wafer.cWafer import cWafer
import math


class cWaferRenderer:

    def __init__(self, renderer: cRenderer):
        self._renderer = renderer


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
        # wafer의 셀 좌표를 이용해 그리드 그리기
        grid_size = wafer.grid_size
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

    def _draw_arrows(self, wafer: cWafer):
        # 셀의 top / left / right / bottom 화살표 그리기
        pass

    def _draw_outline(self, wafer: cWafer, path):
        self._renderer.draw_path(
            path,
            stroke=cColor(64, 64, 64),
            stroke_width=wafer.stroke,
        )
        pass

    pass


