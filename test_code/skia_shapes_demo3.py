"""
skia-python GPU 도형 그리기 데모

핵심: Skia GPU를 쓰려면 먼저 OpenGL 컨텍스트를 만들어야 함.
  - 데스크탑 (모니터 있음): GLFW로 숨긴 윈도우 생성
  - 서버 (모니터 없음):    EGL + moderngl 로 headless 컨텍스트 생성

pip install skia-python glfw moderngl
"""

import math
import skia


# ══════════════════════════════════════════════════════════════════════════
#  1단계: OpenGL 컨텍스트 생성 (이게 있어야 Skia GPU가 동작함)
# ══════════════════════════════════════════════════════════════════════════

def _try_glfw():
    """방법 1: GLFW 숨긴 윈도우 — 데스크탑 환경"""
    try:
        import glfw
        if not glfw.init():
            return None, None

        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)   # 안 보이는 윈도우
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(1, 1, "", None, None)
        if not window:
            glfw.terminate()
            return None, None

        glfw.make_context_current(window)
        print("[GL] GLFW OpenGL context 생성 완료")

        # 이제 Skia가 이 GL context를 감지할 수 있음
        skia_context = skia.GrDirectContext.MakeGL()
        if skia_context:
            print("[GPU] Skia GPU context 생성 성공!")
            return skia_context, ("glfw", window)

        glfw.terminate()
    except ImportError:
        pass
    return None, None


def _try_egl():
    """방법 2: EGL headless — 서버 환경 (모니터 불필요)"""
    try:
        import moderngl
        # EGL backend로 headless GL context 생성
        _mgl_ctx = moderngl.create_standalone_context(backend="egl")
        print("[GL] EGL headless context 생성 완료 (moderngl)")

        # EGL용 Skia GL 인터페이스 명시적 생성
        interface = skia.GrGLInterface.MakeEGL()
        skia_context = skia.GrDirectContext.MakeGL(interface)
        if skia_context:
            print("[GPU] Skia GPU context 생성 성공! (EGL)")
            return skia_context, ("egl", _mgl_ctx)
    except Exception as e:
        print(f"[EGL] 실패: {e}")
    return None, None


def _try_glx():
    """방법 3: GLX — X11 환경"""
    try:
        import moderngl
        _mgl_ctx = moderngl.create_standalone_context()  # 기본: GLX
        print("[GL] GLX context 생성 완료 (moderngl)")

        skia_context = skia.GrDirectContext.MakeGL()
        if skia_context:
            print("[GPU] Skia GPU context 생성 성공! (GLX)")
            return skia_context, ("glx", _mgl_ctx)
    except Exception as e:
        print(f"[GLX] 실패: {e}")
    return None, None


def create_gpu_context():
    """
    GPU context 생성을 순서대로 시도:
      1) GLFW (데스크탑)
      2) EGL  (headless 서버)
      3) GLX  (X11)
      4) 전부 실패 → None (CPU 폴백)
    """
    for method in [_try_glfw, _try_egl, _try_glx]:
        ctx, backend_info = method()
        if ctx is not None:
            return ctx, backend_info

    print("[CPU] GPU context 생성 실패 — CPU 렌더링으로 폴백")
    return None, None


def create_surface(gpu_context, width: int, height: int):
    """Skia surface 생성 — GPU 있으면 GPU, 없으면 CPU"""
    if gpu_context is not None:
        info = skia.ImageInfo.MakeN32Premul(width, height)
        surface = skia.Surface.MakeRenderTarget(gpu_context, skia.Budgeted.kNo, info)
        if surface is not None:
            print(f"[GPU] Render target 생성 완료 ({width}x{height})")
            return surface
        print("[GPU] Surface 생성 실패 — CPU 폴백")

    print(f"[CPU] Raster surface ({width}x{height})")
    return skia.Surface(width, height)


def cleanup(gpu_context, backend_info):
    """리소스 정리"""
    if gpu_context:
        gpu_context.abandonContext()
    if backend_info:
        kind, handle = backend_info
        if kind == "glfw":
            import glfw
            glfw.terminate()


# ══════════════════════════════════════════════════════════════════════════
#  2단계: 도형 그리기 (GPU든 CPU든 코드 동일)
# ══════════════════════════════════════════════════════════════════════════

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
    canvas.drawPath(path, skia.Paint(AntiAlias=True, Color=color))


def draw_dashed_line(canvas, x1, y1, x2, y2, color=skia.ColorWHITE, line_width=2):
    """점선"""
    paint = skia.Paint(
        AntiAlias=True, Color=color,
        Style=skia.Paint.kStroke_Style, StrokeWidth=line_width,
        PathEffect=skia.DashPathEffect.Make([10, 5], 0),
    )
    canvas.drawLine(x1, y1, x2, y2, paint)


def draw_circle_shadow(canvas, cx, cy, radius, color=skia.Color(66, 133, 244), blur=10):
    """그림자 원"""
    shadow = skia.Paint(
        AntiAlias=True, Color=skia.Color(0, 0, 0, 80),
        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur),
    )
    canvas.drawCircle(cx + 4, cy + 4, radius, shadow)
    canvas.drawCircle(cx, cy, radius, skia.Paint(AntiAlias=True, Color=color))


# ══════════════════════════════════════════════════════════════════════════
#  메인
# ══════════════════════════════════════════════════════════════════════════

def main():
    # ── GL context + Skia GPU context 생성 ──────────────────────────
    gpu_context, backend_info = create_gpu_context()

    # ── Surface 생성 ────────────────────────────────────────────────
    width, height = 800, 600
    surface = create_surface(gpu_context, width, height)

    # ── 그리기 (GPU든 CPU든 이 아래 코드는 동일) ────────────────────
    with surface as canvas:
        canvas.clear(skia.Color(30, 30, 40))

        # 원 (채우기)
        canvas.drawCircle(150, 150, 80,
            skia.Paint(AntiAlias=True, Color=skia.Color(66, 133, 244)))

        # 원 (테두리)
        canvas.drawCircle(350, 150, 60,
            skia.Paint(AntiAlias=True, Color=skia.Color(234, 67, 53),
                       Style=skia.Paint.kStroke_Style, StrokeWidth=3))

        # 그림자 원
        draw_circle_shadow(canvas, 550, 150, 60, skia.Color(168, 80, 222))

        # 실선 / 점선
        canvas.drawLine(50, 280, 750, 280,
            skia.Paint(AntiAlias=True, Color=skia.ColorWHITE, StrokeWidth=2))
        draw_dashed_line(canvas, 50, 310, 750, 310,
            color=skia.Color(255, 255, 255, 100))

        # 화살표
        draw_arrow(canvas, 50, 400, 350, 400,
                   color=skia.Color(52, 168, 83), head_size=20, line_width=3)
        draw_arrow(canvas, 400, 420, 400, 360,
                   color=skia.Color(251, 188, 4), head_size=16, line_width=2)

        # 사각형
        canvas.drawRect(skia.Rect(450, 340, 650, 440),
            skia.Paint(AntiAlias=True, Color=skia.Color(251, 188, 4)))

        # 둥근 사각형
        rrect = skia.RRect.MakeRectXY(skia.Rect(450, 460, 650, 550), 16, 16)
        canvas.drawRRect(rrect,
            skia.Paint(AntiAlias=True, Color=skia.Color(0, 188, 212)))

        # 삼각형 (path)
        tri = skia.Path()
        tri.moveTo(100, 550)
        tri.lineTo(200, 460)
        tri.lineTo(300, 550)
        tri.close()
        canvas.drawPath(tri,
            skia.Paint(AntiAlias=True, Color=skia.Color(255, 109, 0, 200)))

        # 텍스트
        font = skia.Font(skia.Typeface(), 24)
        canvas.drawString("GPU Shapes Demo", 280, 580, font,
            skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))

        # GPU면 flush
        if gpu_context:
            surface.flushAndSubmit()

    # ── 저장 ────────────────────────────────────────────────────────
    image = surface.makeImageSnapshot()
    image.save("shapes_demo.png", skia.kPNG)
    print("저장됨: shapes_demo.png")

    # 정리
    cleanup(gpu_context, backend_info)


if __name__ == "__main__":
    main()
