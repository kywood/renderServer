"""
renderer.py — skia-python 기반 GPU 렌더러

기존 ModernGL 직접 구현 대신 Skia의 Canvas API를 사용.
GPU 가속은 Skia가 내부적으로 OpenGL/EGL을 통해 처리.

지원 도형:
  - circle       원 (채우기/테두리)
  - line         직선
  - arrow        화살표
  - rect         사각형
  - rounded_rect 둥근 사각형
  - arc          호
  - path         자유 경로
  - text         텍스트
  - image        이미지 합성
  + 블러, 그림자, 그라디언트, 클리핑, 변환
"""

import io
import math
import logging
from dataclasses import dataclass

import skia
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class Color:
    """RGBA 색상 (0~255)"""
    r: int = 255
    g: int = 255
    b: int = 255
    a: int = 255

    def to_skia(self) -> int:
        return skia.Color(self.r, self.g, self.b, self.a)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        h = hex_str.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) if len(h) == 8 else 255
        return cls(r, g, b, a)


class Colors:
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)
    RED = Color(234, 67, 53)
    GREEN = Color(52, 168, 83)
    BLUE = Color(66, 133, 244)
    YELLOW = Color(251, 188, 4)
    PURPLE = Color(168, 80, 222)
    CYAN = Color(0, 188, 212)
    ORANGE = Color(255, 109, 0)
    TRANSPARENT = Color(0, 0, 0, 0)


class GPURenderer:
    """
    Skia 기반 GPU 가속 2D 렌더러.

    사용법:
        renderer = GPURenderer(width=1920, height=1080)

        renderer.begin()
        renderer.clear(Colors.BLACK)
        renderer.circle(400, 300, 100, fill=Colors.BLUE)
        renderer.arrow(100, 500, 600, 500, color=Colors.GREEN)
        renderer.text("Hello", 200, 100, size=32, color=Colors.WHITE)
        result = renderer.finish()  # PIL Image 반환

        result.save("output.png")
        # 또는 bytes로: renderer.finish_bytes(format="png")
    """

    def __init__(self, width: int = 1920, height: int = 1080, use_gpu: bool = True):
        self.width = width
        self.height = height
        self._gpu_context = None
        self._surface = None
        self._canvas = None
        self._use_gpu = use_gpu
        self._gl_backend = None  # GL context 핸들 (정리용)

        if use_gpu:
            self._gpu_context, self._gl_backend = self._create_gpu_context()
            if self._gpu_context is None:
                self._use_gpu = False

    @staticmethod
    def _create_gpu_context():
        """
        Skia GPU에 필요한 OpenGL 컨텍스트를 생성.
        순서: GLFW(데스크탑) → EGL(headless) → GLX(X11) → 실패
        """
        # 1) GLFW — 데스크탑 환경 (숨긴 윈도우)
        try:
            import glfw
            if glfw.init():
                glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
                glfw.window_hint(glfw.STENCIL_BITS, 8)
                window = glfw.create_window(1, 1, "", None, None)
                if window:
                    glfw.make_context_current(window)
                    ctx = skia.GrDirectContext.MakeGL()
                    if ctx:
                        logger.info("GPU context 생성 성공 (GLFW)")
                        return ctx, ("glfw", window)
                glfw.terminate()
        except ImportError:
            pass
        except Exception as e:
            logger.debug("GLFW 실패: %s", e)

        # 2) EGL — headless 서버 (모니터 불필요)
        try:
            import moderngl
            mgl = moderngl.create_standalone_context(backend="egl")
            interface = skia.GrGLInterface.MakeEGL()
            ctx = skia.GrDirectContext.MakeGL(interface)
            if ctx:
                logger.info("GPU context 생성 성공 (EGL)")
                return ctx, ("egl", mgl)
        except Exception as e:
            logger.debug("EGL 실패: %s", e)

        # 3) GLX — X11 환경
        try:
            import moderngl
            mgl = moderngl.create_standalone_context()
            ctx = skia.GrDirectContext.MakeGL()
            if ctx:
                logger.info("GPU context 생성 성공 (GLX)")
                return ctx, ("glx", mgl)
        except Exception as e:
            logger.debug("GLX 실패: %s", e)

        logger.warning("GPU context 생성 실패 — CPU 폴백")
        return None, None

    @property
    def gpu_info(self) -> str:
        return "Skia GPU (OpenGL/EGL)" if self._use_gpu and self._gpu_context else "Skia CPU"

    @property
    def max_texture_size(self) -> int:
        if self._gpu_context:
            return self._gpu_context.maxTextureSize()
        return 8192

    # ── 캔버스 수명주기 ──────────────────────────────────────────────

    def begin(self, width: int = None, height: int = None, bg_color: Color = None):
        """렌더링 시작 — 새 캔버스 생성"""
        w = width or self.width
        h = height or self.height

        if self._use_gpu and self._gpu_context:
            info = skia.ImageInfo.MakeN32Premul(w, h)
            self._surface = skia.Surface.MakeRenderTarget(
                self._gpu_context, skia.Budgeted.kNo, info,
            )
        else:
            self._surface = skia.Surface(w, h)

        if self._surface is None:
            raise RuntimeError("Surface 생성 실패")

        self._canvas = self._surface.getCanvas()
        if bg_color:
            self._canvas.clear(bg_color.to_skia())

    def clear(self, color: Color = Colors.BLACK):
        self._canvas.clear(color.to_skia())

    # ── 도형: 원 ─────────────────────────────────────────────────────

    def circle(
        self,
        cx: float, cy: float, radius: float,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
    ):
        """원 그리기"""
        if fill:
            paint = skia.Paint(AntiAlias=True, Color=fill.to_skia(), Style=skia.Paint.kFill_Style)
            self._canvas.drawCircle(cx, cy, radius, paint)
        if stroke:
            paint = skia.Paint(AntiAlias=True, Color=stroke.to_skia(), Style=skia.Paint.kStroke_Style, StrokeWidth=stroke_width)
            self._canvas.drawCircle(cx, cy, radius, paint)
        if not fill and not stroke:
            paint = skia.Paint(AntiAlias=True, Color=Colors.WHITE.to_skia())
            self._canvas.drawCircle(cx, cy, radius, paint)

    # ── 도형: 선 ─────────────────────────────────────────────────────

    def line(
        self,
        x1: float, y1: float, x2: float, y2: float,
        color: Color = Colors.WHITE,
        width: float = 2,
        dashed: bool = False,
        dash_pattern: list[float] = None,
    ):
        """직선 (실선/점선)"""
        paint = skia.Paint(
            AntiAlias=True, Color=color.to_skia(),
            Style=skia.Paint.kStroke_Style, StrokeWidth=width,
            StrokeCap=skia.Paint.kRound_Cap,
        )
        if dashed:
            pattern = dash_pattern or [10, 5]
            paint.setPathEffect(skia.DashPathEffect.Make(pattern, 0))
        self._canvas.drawLine(x1, y1, x2, y2, paint)

    # ── 도형: 화살표 ─────────────────────────────────────────────────

    def arrow(
        self,
        x1: float, y1: float, x2: float, y2: float,
        color: Color = Colors.WHITE,
        line_width: float = 2,
        head_size: float = 15,
        head_style: str = "filled",
    ):
        """화살표 (시작점 → 끝점)"""
        angle = math.atan2(y2 - y1, x2 - x1)
        self.line(x1, y1, x2, y2, color=color, width=line_width)

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

        style = skia.Paint.kFill_Style if head_style == "filled" else skia.Paint.kStroke_Style
        paint = skia.Paint(AntiAlias=True, Color=color.to_skia(), Style=style, StrokeWidth=line_width)
        self._canvas.drawPath(path, paint)

    # ── 도형: 사각형 ─────────────────────────────────────────────────

    def rect(
        self,
        x: float, y: float, w: float, h: float,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
        corner_radius: float = 0,
    ):
        """사각형 / 둥근 사각형"""
        r = skia.Rect(x, y, x + w, y + h)

        def _draw(paint):
            if corner_radius > 0:
                rrect = skia.RRect.MakeRectXY(r, corner_radius, corner_radius)
                self._canvas.drawRRect(rrect, paint)
            else:
                self._canvas.drawRect(r, paint)

        if fill:
            _draw(skia.Paint(AntiAlias=True, Color=fill.to_skia(), Style=skia.Paint.kFill_Style))
        if stroke:
            _draw(skia.Paint(AntiAlias=True, Color=stroke.to_skia(), Style=skia.Paint.kStroke_Style, StrokeWidth=stroke_width))

    # ── 도형: 호 ─────────────────────────────────────────────────────

    def arc(
        self,
        cx: float, cy: float,
        radius_x: float, radius_y: float = None,
        start_angle: float = 0, sweep_angle: float = 180,
        color: Color = Colors.WHITE, width: float = 2,
    ):
        """호 (타원형 호 지원)"""
        ry = radius_y or radius_x
        oval = skia.Rect(cx - radius_x, cy - ry, cx + radius_x, cy + ry)
        paint = skia.Paint(
            AntiAlias=True, Color=color.to_skia(),
            Style=skia.Paint.kStroke_Style, StrokeWidth=width,
            StrokeCap=skia.Paint.kRound_Cap,
        )
        self._canvas.drawArc(oval, start_angle, sweep_angle, False, paint)

    # ── 도형: 자유 경로 ──────────────────────────────────────────────

    def path(
        self,
        points: list[tuple[float, float]],
        closed: bool = False,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
    ):
        """다각형 / 자유 경로"""
        if not points:
            return
        p = skia.Path()
        p.moveTo(*points[0])
        for pt in points[1:]:
            p.lineTo(*pt)
        if closed:
            p.close()

        if fill:
            self._canvas.drawPath(p, skia.Paint(AntiAlias=True, Color=fill.to_skia(), Style=skia.Paint.kFill_Style))
        if stroke:
            self._canvas.drawPath(p, skia.Paint(AntiAlias=True, Color=stroke.to_skia(), Style=skia.Paint.kStroke_Style, StrokeWidth=stroke_width))

    # ── 도형: 텍스트 ─────────────────────────────────────────────────

    def text(
        self,
        text: str,
        x: float, y: float,
        size: float = 24,
        color: Color = Colors.WHITE,
        font_family: str = None,
        bold: bool = False,
        align: str = "left",
    ):
        """텍스트 렌더링"""
        style = skia.FontStyle.Bold() if bold else skia.FontStyle.Normal()
        typeface = skia.Typeface(font_family or "", style)
        font = skia.Font(typeface, size)
        font.setEdging(skia.Font.Edging.kAntiAlias)
        paint = skia.Paint(AntiAlias=True, Color=color.to_skia())

        if align in ("center", "right"):
            tw = font.measureText(text)
            if align == "center":
                x -= tw / 2
            else:
                x -= tw

        self._canvas.drawString(text, x, y, font, paint)

    # ── 이펙트 ───────────────────────────────────────────────────────

    def circle_with_shadow(
        self, cx: float, cy: float, radius: float,
        fill: Color = Colors.BLUE,
        shadow_blur: float = 10,
        shadow_offset: tuple[float, float] = (4, 4),
    ):
        """그림자가 있는 원"""
        shadow_paint = skia.Paint(
            AntiAlias=True, Color=skia.Color(0, 0, 0, 80),
            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, shadow_blur),
        )
        self._canvas.drawCircle(cx + shadow_offset[0], cy + shadow_offset[1], radius, shadow_paint)
        self.circle(cx, cy, radius, fill=fill)

    def gradient_rect(
        self, x: float, y: float, w: float, h: float,
        colors: list[Color],
        direction: str = "horizontal",
        corner_radius: float = 0,
    ):
        """그라디언트 사각형"""
        pts = {
            "horizontal": (skia.Point(x, y), skia.Point(x + w, y)),
            "vertical":   (skia.Point(x, y), skia.Point(x, y + h)),
            "diagonal":   (skia.Point(x, y), skia.Point(x + w, y + h)),
        }
        start, end = pts.get(direction, pts["horizontal"])
        shader = skia.GradientShader.MakeLinear(
            points=[start, end], colors=[c.to_skia() for c in colors],
        )
        paint = skia.Paint(AntiAlias=True, Shader=shader)
        r = skia.Rect(x, y, x + w, y + h)
        if corner_radius > 0:
            self._canvas.drawRRect(skia.RRect.MakeRectXY(r, corner_radius, corner_radius), paint)
        else:
            self._canvas.drawRect(r, paint)

    # ── 변환 ─────────────────────────────────────────────────────────

    def save(self):
        self._canvas.save()

    def restore(self):
        self._canvas.restore()

    def translate(self, dx: float, dy: float):
        self._canvas.translate(dx, dy)

    def rotate(self, degrees: float, cx: float = 0, cy: float = 0):
        self._canvas.rotate(degrees, cx, cy)

    def scale(self, sx: float, sy: float = None):
        self._canvas.scale(sx, sy or sx)

    # ── 이미지 합성 ──────────────────────────────────────────────────

    def draw_image(self, image_path: str, x: float, y: float, opacity: float = 1.0):
        img = skia.Image.open(image_path)
        paint = skia.Paint(Alphaf=opacity) if opacity < 1.0 else None
        self._canvas.drawImage(img, x, y, paint)

    def draw_image_from_bytes(
        self, data: bytes, width: int, height: int,
        x: float, y: float, opacity: float = 1.0,
    ):
        img = skia.Image.frombytes(data, (width, height), skia.kRGBA_8888_ColorType)
        paint = skia.Paint(Alphaf=opacity) if opacity < 1.0 else None
        self._canvas.drawImage(img, x, y, paint)

    # ── 결과 출력 ────────────────────────────────────────────────────

    def finish(self) -> Image.Image:
        """렌더링 완료 → PIL Image 반환"""
        if self._use_gpu:
            self._surface.flushAndSubmit()

        skia_image = self._surface.makeImageSnapshot()

        # GPU 이미지를 CPU(NumPy)로 안전하게 가져옵니다.
        # PIL 라이브러리와 색상 호환성을 맞추기 위해 RGBA 및 Unpremul 옵션을 줍니다.
        arr = skia_image.toarray(
            colorType=skia.kRGBA_8888_ColorType,
            alphaType=skia.kUnpremul_AlphaType
        )
        return Image.fromarray(arr)

    def finish_bytes(self, format: str = "png", quality: int = 90) -> bytes:
        """렌더링 완료 → bytes 반환 (서버 응답용)"""
        pil_image = self.finish()
        buf = io.BytesIO()
        if format == "jpeg":
            pil_image = pil_image.convert("RGB")
            pil_image.save(buf, format="JPEG", quality=quality)
        elif format == "webp":
            pil_image.save(buf, format="WEBP", quality=quality)
        else:
            pil_image.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        return buf.read()

    def release(self):
        self._surface = None
        self._canvas = None
        if self._gpu_context:
            self._gpu_context.abandonContext()
            self._gpu_context = None
        if self._gl_backend:
            kind, handle = self._gl_backend
            if kind == "glfw":
                try:
                    import glfw
                    glfw.terminate()
                except Exception:
                    pass
            self._gl_backend = None
        logger.info("Renderer 리소스 해제 완료")
