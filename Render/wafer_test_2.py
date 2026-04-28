import skia


def draw_wafer(cx, cy, radius, notch_angle, notch_depth, stroke_width=5.0, output_filename="wafer.png"):
    """
    내부는 흰색, 테두리는 짙은 회색이며 하단에 노치가 있는 웨이퍼를 그립니다.
    stroke_width 매개변수로 테두리의 두께를 조절할 수 있습니다.
    """
    # 1. 캔버스 생성
    surface = skia.Surface(int(cx * 2), int(cy * 2))
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)

    # 2. 패스(Path) 생성
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

    canvas.save()
    canvas.clipPath(path)


    # 3. 페인트(Paint) 속성 설정
    # 내부 채우기 (흰색)

    fill_color = skia.ColorSetARGB(255, 255, 255, 255)

    fill_paint = skia.Paint(
        AntiAlias=True,
        Color=fill_color,
        Style=skia.Paint.kFill_Style
    )

    # 테두리 그리기 (짙은 회색)
    stroke_color = skia.ColorSetARGB(255, 64, 64, 64)
    stroke_paint = skia.Paint(
        AntiAlias=True,
        Color=stroke_color,
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=stroke_width  # 👈 입력받은 두께 변수를 적용
    )

    canvas.restore()


    # 4. 캔버스에 그리기
    canvas.drawPath(path, fill_paint)  # 내부 채우기
    canvas.drawPath(path, stroke_paint)  # 테두리 그리기

    # 5. 결과물 저장
    image = surface.makeImageSnapshot()
    image.save(output_filename, skia.kPNG)
    print(f"웨이퍼 렌더링 완료! 두께 {stroke_width}px 적용됨. '{output_filename}' 저장 완료.")


# ==========================================
# 실행 부분
# stroke_width 값을 변경하여 테두리 두께를 마음대로 조절해 보세요!
# ==========================================
if __name__ == "__main__":
    # 예시: 테두리 두께를 10.0으로 굵게 설정하여 그리기
    draw_wafer(cx=250, cy=250, radius=200, notch_angle=6, notch_depth=5, stroke_width=10.0,
               output_filename="../TestCode/wafer_thick.png")

    # 예시: 테두리 두께를 2.0으로 얇게 설정하여 그리기
    draw_wafer(cx=250, cy=250, radius=200, notch_angle=2, notch_depth=5, stroke_width=1,
               output_filename="../TestCode/wafer_thin.png")