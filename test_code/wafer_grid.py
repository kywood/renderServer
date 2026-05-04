import skia


def draw_wafer_with_grid(cx, cy, radius, notch_angle, notch_depth, stroke_width=5.0, grid_size=20.0,
                         output_filename="wafer_grid.png"):
    """
    내부는 흰색, 테두리는 짙은 회색, 내부에 격자(Grid)가 그려진 노치 웨이퍼를 생성합니다.
    """
    # 1. 캔버스 생성
    surface = skia.Surface(int(cx * 2), int(cy * 2))
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)

    # 2. 패스(path) 생성 (웨이퍼 외곽선)
    path = skia.Path()
    bounds = skia.Rect.MakeLTRB(cx - radius, cy - radius, cx + radius, cy + radius)
    half_notch = notch_angle / 2.0
    start_angle = 90.0 + half_notch
    sweep_angle = 360.0 - notch_angle

    path.arcTo(bounds, start_angle, sweep_angle, False)
    notch_tip_x = cx
    notch_tip_y = cy + radius - notch_depth
    path.lineTo(notch_tip_x, notch_tip_y)
    path.close()

    # 3. 페인트(Paint) 속성 설정
    # 내부 채우기 (흰색)
    fill_paint = skia.Paint(AntiAlias=True, Color=skia.ColorWHITE, Style=skia.Paint.kFill_Style)

    # 테두리 그리기 (짙은 회색)
    stroke_color = skia.ColorSetARGB(255, 64, 64, 64)
    stroke_paint = skia.Paint(AntiAlias=True, Color=stroke_color, Style=skia.Paint.kStroke_Style,
                              StrokeWidth=stroke_width)

    # 격자 선 그리기 (연한 회색, 얇은 선)
    grid_color = skia.ColorSetARGB(255, 220, 220, 220)
    grid_paint = skia.Paint(AntiAlias=True, Color=grid_color, Style=skia.Paint.kStroke_Style, StrokeWidth=1.0)

    # ==========================================
    # 4. 캔버스에 그리기 단계 (순서 및 클리핑 중요)
    # ==========================================

    # 4-1. 가장 먼저 내부를 흰색으로 채웁니다.
    canvas.drawPath(path, fill_paint)

    # 4-2. 격자 그리기 (클리핑 적용)
    canvas.save()  # 현재 캔버스 상태(클리핑 없는 상태)를 임시 저장

    # 웨이퍼 모양(path) 안쪽에만 그려지도록 마스킹 처리를 합니다.
    canvas.clipPath(path, doAntiAlias=True)

    # 수직선(세로선) 그리기
    x = cx - radius
    while x <= cx + radius:
        canvas.drawLine(x, cy - radius, x, cy + radius, grid_paint)
        x += grid_size

    # 수평선(가로선) 그리기
    y = cy - radius
    while y <= cy + radius:
        canvas.drawLine(cx - radius, y, cx + radius, y, grid_paint)
        y += grid_size

    canvas.restore()  # 클리핑 해제 (원래 캔버스 상태로 복구)

    # 4-3. 클리핑이 해제된 상태에서 마지막으로 테두리를 덮어 그립니다.
    canvas.drawPath(path, stroke_paint)

    # 5. 결과물 저장
    image = surface.makeImageSnapshot()
    image.save(output_filename, skia.kPNG)
    print(f"격자가 추가된 웨이퍼 렌더링 완료! '{output_filename}' 저장 완료.")


# ==========================================
# 실행 부분
# grid_size를 변경하여 다이(칩)의 크기를 조절할 수 있습니다.
# ==========================================
if __name__ == "__main__":
    # 격자 크기를 20 픽셀로 설정하여 그리기
    draw_wafer_with_grid(cx=250, cy=250, radius=200, notch_angle=20, notch_depth=30, stroke_width=4.0, grid_size=20.0,
                         output_filename="wafer_with_grid.png")