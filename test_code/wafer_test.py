import skia
import math
import random



def draw_arrow(canvas, x1, y1, x2, y2, color, head_size=5, line_width=1):
    """
    (x1, y1)에서 (x2, y2)로 향하는 화살표를 그리는 함수
    """
    angle = math.atan2(y2 - y1, x2 - x1)

    # 1. 화살표 몸통 (선)
    paint_line = skia.Paint(
        AntiAlias=True, Color=color,
        Style=skia.Paint.kStroke_Style, StrokeWidth=line_width
    )
    canvas.drawLine(x1, y1, x2, y2, paint_line)

    # 2. 화살촉 (삼각형 path)
    path = skia.Path()
    path.moveTo(x2, y2)
    path.lineTo(
        x2 - head_size * math.cos(angle - math.pi / 6),
        y2 - head_size * math.sin(angle - math.pi / 6),
    )
    path.lineTo(
        x2 - head_size * math.cos(angle + math.pi / 6),
        y2 - head_size * math.sin(angle + math.pi / 6),
    )
    path.close()

    paint_head = skia.Paint(
        AntiAlias=True, Color=color, Style=skia.Paint.kFill_Style
    )
    canvas.drawPath(path, paint_head)


def draw_single_wafer(canvas, radius, num_arrows=1000):
    """
    (0, 0) 좌표를 중심으로 웨이퍼 1개와 1000개의 화살표를 그리는 함수
    """
    # 1. 웨이퍼 바탕
    wafer_paint = skia.Paint(
        AntiAlias=True, Color=skia.ColorSetRGB(220, 225, 230),  # 화살표가 잘 보이게 바탕을 살짝 밝게
        Style=skia.Paint.kFill_Style
    )
    canvas.drawCircle(0, 0, radius, wafer_paint)

    # --- 클리핑 영역 시작 (이 안에서 그리는 것은 웨이퍼 밖으로 삐져나가지 않음) ---
    clip_path = skia.Path()
    clip_path.addCircle(0, 0, radius)
    canvas.save()
    canvas.clipPath(clip_path, doAntiAlias=True)

    # 2. 다이(Die) 그리드
    grid_paint = skia.Paint(
        AntiAlias=True, Color=skia.ColorSetRGB(180, 185, 190),
        Style=skia.Paint.kStroke_Style, StrokeWidth=1
    )
    die_size = 40
    for i in range(-radius, radius, die_size):
        canvas.drawLine(i, -radius, i, radius, grid_paint)  # 세로선
        canvas.drawLine(-radius, i, radius, i, grid_paint)  # 가로선

    # 3. 1000개의 화살표 무작위 생성 및 그리기 (오버레이/벡터 데이터 시뮬레이션)
    arrow_color = skia.ColorSetRGB(234, 67, 53)  # 빨간색 화살표

    for _ in range(num_arrows):
        # 웨이퍼 내부(원형)에 골고루 분포하도록 극좌표계(r, theta)를 사용하여 랜덤 좌표 생성
        theta = random.uniform(0, 2 * math.pi)
        # 영역 내 균등 분포를 위해 sqrt 사용
        r = radius * math.sqrt(random.random())

        # 화살표 시작점 (x1, y1)
        x1 = r * math.cos(theta)
        y1 = r * math.sin(theta)

        # 화살표의 방향과 길이 (무작위 벡터)
        vector_angle = random.uniform(0, 2 * math.pi)
        vector_length = random.uniform(5, 15)  # 화살표 길이 5~15 픽셀

        # 화살표 끝점 (x2, y2)
        x2 = x1 + vector_length * math.cos(vector_angle)
        y2 = y1 + vector_length * math.sin(vector_angle)

        # 화살표 그리기
        draw_arrow(canvas, x1, y1, x2, y2, arrow_color, head_size=4, line_width=1.5)

    canvas.restore()
    # --- 클리핑 영역 종료 ---

    # 4. 웨이퍼 테두리
    edge_paint = skia.Paint(
        AntiAlias=True, Color=skia.ColorSetRGB(80, 85, 90),
        Style=skia.Paint.kStroke_Style, StrokeWidth=3
    )
    canvas.drawCircle(0, 0, radius, edge_paint)


def create_multi_wafer_image():
    wafer_radius = 150
    margin = 50
    cols = 5
    rows = 2

    cell_size = (wafer_radius * 2) + margin
    total_width = (cell_size * cols) + margin
    total_height = (cell_size * rows) + margin

    # 큰 캔버스 생성
    surface = skia.Surface(total_width, total_height)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)

    # 10개의 웨이퍼 그리기
    for row in range(rows):
        for col in range(cols):
            cx = margin + wafer_radius + (col * cell_size)
            cy = margin + wafer_radius + (row * cell_size)

            canvas.save()
            canvas.translate(cx, cy)

            # 여기서 웨이퍼 하나당 1000개의 화살표가 함께 그려집니다.
            draw_single_wafer(canvas, wafer_radius, num_arrows=1000)

            # 라벨 텍스트
            font = skia.Font(skia.Typeface(), 24)
            text_paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
            canvas.drawString(f"Wafer {row * cols + col + 1}", -45, wafer_radius + 30, font, text_paint)

            canvas.restore()

    # 이미지 저장
    image = surface.makeImageSnapshot()
    image.save("10_wafers_with_vectors.png", skia.kPNG)
    print(f"이미지 저장 완료: 10_wafers_with_vectors.png")
    print(f"총 {cols * rows * 1000:,}개의 화살표가 렌더링되었습니다.")


if __name__ == "__main__":
    create_multi_wafer_image()