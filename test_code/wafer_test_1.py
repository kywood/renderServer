import skia


def draw_wafer(cx, cy, radius, notch_angle, notch_depth, output_filename="wafer.png"):
    # 1. 그림을 그릴 표면(Surface)과 캔버스 생성
    # 웨이퍼가 넉넉히 들어갈 크기로 캔버스 설정 (예: 중심 x 2)
    surface = skia.Surface(int(cx * 2), int(cy * 2))
    canvas = surface.getCanvas()

    # 배경을 흰색으로 칠하기 (투명 배경을 원하면 생략 가능)
    canvas.clear(skia.ColorWHITE)

    # 2. 페인트(Paint) 속성 설정
    paint = skia.Paint(
        AntiAlias=True,  # 계단 현상 방지 (선을 부드럽게)
        Color=skia.ColorGRAY,  # 웨이퍼 색상 (회색)
        Style=skia.Paint.kFill_Style  # 내부 채우기
    )

    # 3. 패스(path) 그리기 시작
    path = skia.Path()

    # 원이 그려질 경계 사각형 (Bounding Box) 지정
    bounds = skia.Rect.MakeLTRB(cx - radius, cy - radius, cx + radius, cy + radius)

    # 노치 각도 계산 (절반)
    half_notch = notch_angle / 2.0

    # 메인 웨이퍼 원호(Arc) 그리기
    # 파이썬 Skia에서도 0도는 3시 방향, 90도는 6시 방향(하단)입니다.
    start_angle = 90.0 + half_notch
    sweep_angle = 360.0 - notch_angle

    # arcTo(사각형 영역, 시작 각도, 그릴 각도, forceMoveTo=False)
    # False의 의미: 이전 점과 시작점을 선으로 자연스럽게 연결함
    path.arcTo(bounds, start_angle, sweep_angle, False)

    # 4. 노치(Notch) 꼭짓점으로 선 긋기 (안으로 파고드는 부분)
    notch_tip_x = cx
    notch_tip_y = cy + radius - notch_depth
    path.lineTo(notch_tip_x, notch_tip_y)

    # 5. 패스 닫기
    # 꼭짓점에서 원호의 시작점으로 선을 자동으로 연결하여 도형을 완성합니다.
    path.close()

    # 6. 캔버스에 완성된 패스 그리기
    canvas.drawPath(path, paint)

    # 7. 결과물을 이미지(PNG)로 추출하여 저장
    image = surface.makeImageSnapshot()
    image.save(output_filename, skia.kPNG)
    print(f"웨이퍼 렌더링 완료! '{output_filename}' 파일이 저장되었습니다.")


# ==========================================
# 실행 부분
# 중심좌표(250, 250), 반지름 200, 파인 각도 20도, 파인 깊이 30
# ==========================================
if __name__ == "__main__":
    draw_wafer(cx=250, cy=250, radius=200, notch_angle=20, notch_depth=30)