"""
skia-python 도형 그리기 데모

GPU가 있으면 GPU, 없으면 CPU — 드로잉 코드는 동일.
"""

import math
import skia


def create_surface(width: int, height: int):
    """
    GPU surface 생성 시도 → 실패 시 CPU surface 폴백.
    어느 쪽이든 반환되는 surface의 canvas API는 동일.
    """
    # 1) GPU 시도
    context = skia.GrDirectContext.MakeGL()
    if context is not None:
        info = skia.ImageInfo.MakeN32Premul(width, height)
        surface = skia.Surface.MakeRenderTarget(context, skia.Budgeted.kNo, info)
        if surface is not None:
            print(f"[GPU] OpenGL surface 생성 완료 ({width}x{height})")
            return surface, context
        context.abandonContext()

    # 2) CPU 폴백
    print(f"[CPU] 래스터 surface 폴백 ({width}x{height})")
    surface = skia.Surface(width, height)
    return surface, None


# ── 도형 유틸 함수들 ─────────────────────────────────────────────────────

def draw_arrow(canvas, x1, y1, x2, y2, color=skia.ColorWHITE, head_size=15, line_width=2):
    """화살표"""
    angle = math.atan2(y2 - y1, x2 - x1)

    paint = skia.Paint(
        AntiAlias=True, Color=color,
        Style=skia.Paint.kStroke_Style,
        StrokeWidth=line_width, StrokeCap=skia.Paint.kRound_Cap,
    )
    canvas.drawLine(x1, y1, x2, y2, paint)

    path = skia.Path()
    path.moveTo(x2, y2)
    path.lineTo(x2 - head_size * math.cos(angle - math.pi/6),
                y2 - head_size * math.sin(angle - math.pi/6))
    path.lineTo(x2 - head_size * math.cos(angle + math.pi/6),
                y2 - head_size * math.sin(angle + math.pi/6))
    path.close()
    canvas.drawPath(path, skia.Paint(AntiAlias=True, Color=color, Style=skia.Paint.kFill_Style))


def draw_dashed_line(canvas, x1, y1, x2, y2, color=skia.ColorWHITE, line_width=2, dash_on=10, dash_off=5):
    """점선"""
    paint = skia.Paint(
        AntiAlias=True, Color=color,
        Style=skia.Paint.kStroke_Style, StrokeWidth=line_width,
        PathEffect=skia.DashPathEffect.Make([dash_on, dash_off], 0),
    )
    canvas.drawLine(x1, y1, x2, y2, paint)


def draw_circle_with_shadow(canvas, cx, cy, radius, color=skia.Color(66, 133, 244), shadow_blur=10):
    """그림자 원"""
    shadow_paint = skia.Paint(
        AntiAlias=True, Color=skia.Color(0, 0, 0, 80),
        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, shadow_blur),
    )
    canvas.drawCircle(cx + 4, cy + 4, radius, shadow_paint)
    canvas.drawCircle(cx, cy, radius, skia.Paint(AntiAlias=True, Color=color))


# ── 메인 ─────────────────────────────────────────────────────────────────

def main():
    width, height = 800, 600
    surface, gpu_context = create_surface(width, height)

    # ── 여기서부터 GPU든 CPU든 코드 동일 ────────────────────────────
    with surface as canvas:
        canvas.clear(skia.Color(30, 30, 40))

        # 1. 원 (채우기)
        canvas.drawCircle(150, 150, 80, skia.Paint(
            AntiAlias=True, Color=skia.Color(66, 133, 244)))

        # 2. 원 (테두리만)
        canvas.drawCircle(350, 150, 60, skia.Paint(
            AntiAlias=True, Color=skia.Color(234, 67, 53),
            Style=skia.Paint.kStroke_Style, StrokeWidth=3))

        # 3. 그림자 원
        draw_circle_with_shadow(canvas, 550, 150, 60,
                                color=skia.Color(168, 80, 222))

        # 4. 직선
        canvas.drawLine(50, 280, 750, 280, skia.Paint(
            AntiAlias=True, Color=skia.ColorWHITE, StrokeWidth=2))

        # 5. 점선
        draw_dashed_line(canvas, 50, 320, 750, 320,
                         color=skia.Color(255, 255, 255, 100), line_width=1)

        # 6. 화살표들
        draw_arrow(canvas, 50, 400, 300, 400,
                   color=skia.Color(52, 168, 83), head_size=20, line_width=3)
        draw_arrow(canvas, 350, 420, 350, 360,
                   color=skia.Color(251, 188, 4), head_size=16, line_width=2)

        # 7. 사각형
        canvas.drawRect(skia.Rect(450, 340, 650, 440), skia.Paint(
            AntiAlias=True, Color=skia.Color(251, 188, 4), Style=skia.Paint.kFill_Style))

        # 8. 둥근 사각형
        rrect = skia.RRect.MakeRectXY(skia.Rect(450, 460, 650, 540), 16, 16)
        canvas.drawRRect(rrect, skia.Paint(
            AntiAlias=True, Color=skia.Color(0, 188, 212), Style=skia.Paint.kFill_Style))

        # 9. 삼각형 (Path)
        path = skia.Path()
        path.moveTo(100, 550)
        path.lineTo(200, 460)
        path.lineTo(300, 550)
        path.close()
        canvas.drawPath(path, skia.Paint(
            AntiAlias=True, Color=skia.Color(255, 109, 0, 200), Style=skia.Paint.kFill_Style))

        # 10. 텍스트
        font = skia.Font(skia.Typeface(), 24)
        canvas.drawString("GPU Shapes Demo", 280, 580, font,
                          skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))

        # GPU면 flush 필요
        if gpu_context:
            surface.flushAndSubmit()

    # ── 저장 ────────────────────────────────────────────────────────
    image = surface.makeImageSnapshot()
    image.save("shapes_demo.png", skia.kPNG)
    print("저장됨: shapes_demo.png")

    # 정리
    if gpu_context:
        gpu_context.abandonContext()


if __name__ == "__main__":
    main()
