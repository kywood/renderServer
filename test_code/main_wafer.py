import random
import math
import skia

# renderer.py에서 필요한 클래스들을 불러옵니다.
from modules.render import GPURenderer, Color, Colors


def draw_wafer_demo():
    # 1. 렌더러 초기화 (해상도 800x800)
    width, height = 800, 800
    renderer = GPURenderer(width=width, height=height)

    # 캔버스 렌더링 시작 및 배경색 지정
    renderer.begin(bg_color=Colors.WHITE)

    # 웨이퍼 중심 좌표와 반지름 설정
    cx, cy = width / 2, height / 2
    radius = 330

    # 커스텀 색상 정의 (RGBA 지원)
    WAFER_BG = Color(225, 230, 235)  # 밝은 실리콘 배경색
    GRID_COLOR = Color(180, 185, 190)  # 그리드 선 색상
    EDGE_COLOR = Color(80, 85, 90)  # 테두리 색상
    DEFECT_COLOR = Color(234, 67, 53, 200)  # 불량 다이 표시용 (반투명 빨강)

    print(f"렌더링 엔진: {renderer.gpu_info} 사용 중...")

    # 2. 바탕 및 그림자 효과 (단 한 줄로 그림자+원 그리기 완료)
    renderer.circle_with_shadow(cx, cy, radius, fill=WAFER_BG, shadow_blur=15, shadow_offset=(5, 5))

    # --- 클리핑 시작 (웨이퍼 밖으로 삐져나가지 않도록) ---
    renderer.save()
    clip_path = skia.Path()
    clip_path.addCircle(cx, cy, radius - 2)  # 테두리 두께를 고려해 살짝 작게 클리핑
    renderer._canvas.clipPath(clip_path, doAntiAlias=True)

    # 3. 다이(Die) 그리드 그리기 (renderer.line의 dashed 옵션 활용)
    die_size = 40
    for x in range(int(cx - radius), int(cx + radius), die_size):
        renderer.line(x, cy - radius, x, cy + radius, color=GRID_COLOR, width=1.5, dashed=True)
    for y in range(int(cy - radius), int(cy + radius), die_size):
        renderer.line(cx - radius, y, cx + radius, y, color=GRID_COLOR, width=1.5, dashed=True)

    # 4. 특정 다이에 불량(Defect) 표시 (둥근 사각형 활용)
    defect_positions = [
        (cx - 80, cy - 40), (cx + 40, cy + 80),
        (cx - 120, cy + 120), (cx + 120, cy - 160),
        (cx, cy - 120)
    ]
    for dx, dy in defect_positions:
        # 단 한 줄로 모서리가 둥근 사각형 채우기
        renderer.rect(dx, dy, die_size, die_size, fill=DEFECT_COLOR, corner_radius=8)

    # 5. 오버레이/벡터 데이터 렌더링 (화살표 200개 무작위 배치)
    for _ in range(200):
        theta = random.uniform(0, 2 * math.pi)
        r = radius * math.sqrt(random.random())

        x1 = cx + r * math.cos(theta)
        y1 = cy + r * math.sin(theta)

        vec_angle = random.uniform(0, 2 * math.pi)
        vec_len = random.uniform(10, 25)

        x2 = x1 + vec_len * math.cos(vec_angle)
        y2 = y1 + vec_len * math.sin(vec_angle)

        # 단 한 줄로 화살표 그리기
        renderer.arrow(x1, y1, x2, y2, color=Colors.BLUE, line_width=2, head_size=6)

    # --- 클리핑 해제 ---
    renderer.restore()

    # 6. 웨이퍼 테두리 및 노치(Notch)
    renderer.circle(cx, cy, radius, stroke=EDGE_COLOR, stroke_width=4)
    renderer.circle(cx, cy + radius, 6, fill=Colors.WHITE)  # 하단에 파인 노치 표현

    # 7. 타이틀 텍스트 추가 (정렬 기능 지원)
    renderer.text("Wafer Bin Map & Vectors", cx, 50, size=32, color=Colors.BLACK, bold=True, align="center")
    renderer.text("Powered by skia-python GPU", cx, 760, size=20, color=EDGE_COLOR, align="center")

    # 8. 결과물 디스크에 저장
    result_image = renderer.finish()
    result_image.save("wafer_rendered_by_class.png")
    print("저장 완료: wafer_rendered_by_class.png")

    # 메모리 정리
    renderer.release()


if __name__ == "__main__":
    draw_wafer_demo()