"""
반도체 웨이퍼 6개 + 화살표 1만개씩 (총 6만개) 그리기

GPU 타는지 확인:
  - gpu_info 출력
  - 렌더링 시간 측정
"""

import math
import time
import random
import logging

from Render.renderer import Color, Colors, GPURenderer

logging.basicConfig(level=logging.INFO)


def draw_wafer(renderer, cx, cy, radius, label=""):
    """
    반도체 웨이퍼 1개 그리기
    - 원형 실리콘 + 노치(flat) + 테두리
    """
    # 웨이퍼 본체 (실리콘 회색)

    renderer.circle(cx, cy, radius,
                    fill=Color(180, 180, 190),
                    stroke=Color(120, 120, 130),
                    stroke_width=2)

    # 노치 (하단 flat 표시) — 작은 삼각형으로 표현
    notch_size = radius * 0.06
    renderer.path(
        [
            (cx - notch_size, cy + radius - 1),
            (cx, cy + radius - notch_size * 1.5),
            (cx + notch_size, cy + radius - 1),
        ],
        closed=True,
        fill=Color(60, 60, 70),
    )

    # 라벨
    if label:
        renderer.text(label, cx, cy + radius + 25,
                      size=16, color=Colors.WHITE, align="center")


def draw_arrows_on_wafer(renderer, cx, cy, radius, count=10000):
    """
    웨이퍼 위에 화살표 count개 그리기
    - 웨이퍼 원 안에만 배치
    - 랜덤 위치, 랜덤 방향, 랜덤 색상
    """
    inner_radius = radius * 0.9  # 가장자리 여유

    for _ in range(count):
        # 원 안의 랜덤 위치 (균등 분포)
        angle = random.uniform(0, 2 * math.pi)
        r = inner_radius * math.sqrt(random.random())
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)

        # 랜덤 방향 + 짧은 화살표
        arrow_angle = random.uniform(0, 2 * math.pi)
        length = random.uniform(3, 10)
        x2 = x + length * math.cos(arrow_angle)
        y2 = y + length * math.sin(arrow_angle)

        # 색상: 빨강~노랑~초록 (결함 심각도 표현)
        g = random.randint(50, 255)
        r_color = 255 - g
        color = Color(r_color, g, 30, 200)

        renderer.arrow(x, y, x2, y2,
                       color=color, line_width=0.5, head_size=2)


def main():
    # ── 설정 ────────────────────────────────────────────────────────
    canvas_w, canvas_h = 1920, 1280
    wafer_radius = 250
    arrows_per_wafer = 10000

    # 웨이퍼 6개 배치 (3x2 그리드)
    cols, rows = 3, 2
    spacing_x = canvas_w // cols
    spacing_y = (canvas_h - 80) // rows  # 하단 여유

    # ── 렌더러 생성 ─────────────────────────────────────────────────
    renderer = GPURenderer(width=canvas_w, height=canvas_h)

    # GPU 확인
    print(f"렌더러: {renderer.gpu_info}")
    print(f"웨이퍼: {cols * rows}개 × 화살표 {arrows_per_wafer:,}개 = 총 {cols * rows * arrows_per_wafer:,}개")
    print()

    # ── 렌더링 시작 ─────────────────────────────────────────────────
    renderer.begin()
    renderer.clear(Color(25, 25, 35))

    # 제목
    renderer.text(
        f"Wafer Defect Map — {cols * rows} wafers, {arrows_per_wafer:,} arrows each",
        canvas_w // 2, 35, size=24, color=Colors.WHITE, align="center", bold=True,
    )

    # ── 웨이퍼 + 화살표 그리기 ──────────────────────────────────────
    total_t0 = time.perf_counter()

    wafer_idx = 0
    for row in range(rows):
        for col in range(cols):
            wafer_idx += 1
            cx = spacing_x // 2 + col * spacing_x
            cy = 80 + spacing_y // 2 + row * spacing_y

            # 웨이퍼 그리기
            t0 = time.perf_counter()
            draw_wafer(renderer, cx, cy, wafer_radius, label=f"Wafer #{wafer_idx}")

            # 화살표 1만개
            draw_arrows_on_wafer(renderer, cx, cy, wafer_radius, count=arrows_per_wafer)
            elapsed = time.perf_counter() - t0
            print(f"  Wafer #{wafer_idx}: {arrows_per_wafer:,} arrows — {elapsed*1000:.0f}ms")

    total_draw = time.perf_counter() - total_t0
    print(f"\n드로잉 총: {total_draw*1000:.0f}ms")

    # ── 결과 출력 ───────────────────────────────────────────────────
    t0 = time.perf_counter()
    image = renderer.finish()
    finish_time = time.perf_counter() - t0
    print(f"finish() (GPU→CPU 전송 + 인코딩): {finish_time*1000:.0f}ms")

    t0 = time.perf_counter()
    image.save("wafer_map.png")
    save_time = time.perf_counter() - t0
    print(f"PNG 저장: {save_time*1000:.0f}ms")

    total = total_draw + finish_time + save_time
    print(f"\n===== 총 소요: {total*1000:.0f}ms =====")
    print(f"렌더러: {renderer.gpu_info}")
    print("저장됨: wafer_map.png")

    renderer.release()


if __name__ == "__main__":
    random.seed(42)
    main()