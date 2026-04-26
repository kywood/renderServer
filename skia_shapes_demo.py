"""
skia-python 기반 도형 그리기 예제

pip install skia-python

skia-python이 제공하는 드로잉 API:
  canvas.drawCircle(cx, cy, radius, paint)    # 원
  canvas.drawLine(x1, y1, x2, y2, paint)      # 선
  canvas.drawRect(rect, paint)                 # 사각형
  canvas.drawRRect(rrect, paint)               # 둥근 사각형
  canvas.drawArc(oval, start, sweep, ...)      # 호
  canvas.drawPath(path, paint)                 # 자유 경로 (화살표 등)
  canvas.drawString(text, x, y, font, paint)   # 텍스트
  canvas.drawImage(image, x, y)                # 이미지 합성
  + 블러, 그림자, 그라디언트, 클리핑, 변환(회전/스케일) 전부 지원
"""

import skia
import numpy as np


def example_cpu_rendering():
    """CPU 렌더링 — 가장 간단한 방식"""

    width, height = 800, 600
    surface = skia.Surface(width, height)

    with surface as canvas:
        # 배경
        canvas.clear(skia.Color(30, 30, 40))

        # ── 1. 원 그리기 ────────────────────────────────────────────
        paint_fill = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(66, 133, 244),  # 파랑
            Style=skia.Paint.kFill_Style,
        )
        canvas.drawCircle(200, 200, 80, paint_fill)

        # 원 테두리만
        paint_stroke = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(234, 67, 53),  # 빨강
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=3,
        )
        canvas.drawCircle(400, 200, 60, paint_stroke)

        # ── 2. 선 그리기 ────────────────────────────────────────────
        paint_line = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(255, 255, 255),
            StrokeWidth=2,
        )
        canvas.drawLine(100, 350, 700, 350, paint_line)

        # ── 3. 화살표 (Path로 구현) ─────────────────────────────────
        draw_arrow(canvas, 100, 450, 400, 450,
                   color=skia.Color(52, 168, 83),  # 초록
                   head_size=20, line_width=3)

        # ── 4. 사각형 ───────────────────────────────────────────────
        rect = skia.Rect(500, 100, 700, 250)
        paint_rect = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(251, 188, 4),  # 노랑
            Style=skia.Paint.kFill_Style,
        )
        canvas.drawRect(rect, paint_rect)

        # 둥근 사각형
        rrect = skia.RRect.MakeRectXY(skia.Rect(500, 300, 700, 420), 16, 16)
        paint_rrect = skia.Paint(
            AntiAlias=True,
            Color=skia.Color(168, 80, 222),  # 보라
            Style=skia.Paint.kFill_Style,
        )
        canvas.drawRRect(rrect, paint_rrect)

        # ── 5. 텍스트 ───────────────────────────────────────────────
        font = skia.Font(skia.Typeface(), 28)
        paint_text = skia.Paint(
            AntiAlias=True,
            Color=skia.ColorWHITE,
        )
        canvas.drawString("Hello GPU Server!", 250, 550, font, paint_text)

    # 이미지 저장
    image = surface.makeImageSnapshot()
    image.save("shapes_cpu.png", skia.kPNG)
    print("저장됨: shapes_cpu.png")

    # numpy 배열로도 변환 가능 (서버 응답용)
    array = np.array(image)
    print(f"numpy shape: {array.shape}")  # (600, 800, 4)


def example_gpu_rendering():
    """
    GPU 가속 렌더링 — RTX GPU에서 실행.
    headless 서버에서 EGL context를 사용.
    """

    width, height = 1920, 1080

    # EGL headless GPU context 생성
    context = skia.GrDirectContext.MakeGL()
    if context is None:
        print("GPU context 생성 실패 — CPU 폴백")
        return example_cpu_rendering()

    info = skia.ImageInfo.MakeN32Premul(width, height)
    surface = skia.Surface.MakeRenderTarget(
        context, skia.Budgeted.kNo, info,
    )

    if surface is None:
        print("GPU surface 생성 실패")
        context.abandonContext()
        return

    with surface as canvas:
        canvas.clear(skia.Color(20, 20, 30))

        # 동일한 드로잉 API — GPU에서 가속됨
        paint = skia.Paint(AntiAlias=True, Color=skia.Color(66, 133, 244))
        canvas.drawCircle(960, 540, 200, paint)

        draw_arrow(canvas, 200, 540, 760, 540,
                   color=skia.Color(52, 168, 83),
                   head_size=30, line_width=4)

        surface.flushAndSubmit()

    image = surface.makeImageSnapshot()
    image.save("shapes_gpu.png", skia.kPNG)
    print("GPU 렌더링 저장됨: shapes_gpu.png")

    context.abandonContext()


# ── 유틸: 화살표 그리기 ──────────────────────────────────────────────────

def draw_arrow(
    canvas,
    x1: float, y1: float,
    x2: float, y2: float,
    color=skia.ColorWHITE,
    head_size: float = 15,
    line_width: float = 2,
):
    """
    (x1,y1) → (x2,y2) 방향 화살표.
    Path를 사용해서 화살촉까지 한번에 그림.
    """
    import math

    angle = math.atan2(y2 - y1, x2 - x1)

    # 화살표 몸통 (선)
    paint = skia.Paint(
        AntiAlias=True,
        Color=color,
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=line_width,
        StrokeCap=skia.Paint.kRound_Cap,
    )
    canvas.drawLine(x1, y1, x2, y2, paint)

    # 화살촉 (삼각형 Path)
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
        AntiAlias=True,
        Color=color,
        Style=skia.Paint.kFill_Style,
    )
    canvas.drawPath(path, paint_head)


# ── 유틸: 다양한 도형 함수들 ─────────────────────────────────────────────

def draw_dashed_line(
    canvas,
    x1: float, y1: float,
    x2: float, y2: float,
    color=skia.ColorWHITE,
    dash_on: float = 10,
    dash_off: float = 5,
    line_width: float = 2,
):
    """점선"""
    paint = skia.Paint(
        AntiAlias=True,
        Color=color,
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=line_width,
        PathEffect=skia.DashPathEffect.Make([dash_on, dash_off], 0),
    )
    canvas.drawLine(x1, y1, x2, y2, paint)


def draw_rounded_rect(
    canvas,
    x: float, y: float, w: float, h: float,
    radius: float = 12,
    fill_color=None,
    stroke_color=None,
    stroke_width: float = 2,
):
    """둥근 사각형 (채우기 + 테두리)"""
    rrect = skia.RRect.MakeRectXY(skia.Rect(x, y, x + w, y + h), radius, radius)

    if fill_color:
        paint = skia.Paint(AntiAlias=True, Color=fill_color, Style=skia.Paint.kFill_Style)
        canvas.drawRRect(rrect, paint)

    if stroke_color:
        paint = skia.Paint(
            AntiAlias=True, Color=stroke_color,
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=stroke_width,
        )
        canvas.drawRRect(rrect, paint)


def draw_circle_with_shadow(
    canvas,
    cx: float, cy: float, radius: float,
    color=skia.Color(66, 133, 244),
    shadow_blur: float = 10,
):
    """그림자가 있는 원"""
    # 그림자 (SkMaskFilter 사용)
    shadow_paint = skia.Paint(
        AntiAlias=True,
        Color=skia.Color(0, 0, 0, 80),
        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, shadow_blur),
    )
    canvas.drawCircle(cx + 4, cy + 4, radius, shadow_paint)

    # 본체
    paint = skia.Paint(AntiAlias=True, Color=color)
    canvas.drawCircle(cx, cy, radius, paint)


if __name__ == "__main__":
    print("=== CPU 렌더링 ===")
    example_cpu_rendering()

    print("\n=== GPU 렌더링 ===")
    try:
        example_gpu_rendering()
    except Exception as e:
        print(f"GPU 렌더링 실패 (GPU 없는 환경): {e}")
        print("CPU 렌더링으로 대체됨")
