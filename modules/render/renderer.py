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

    # @staticmethod
    # def _create_gpu_context():
    #     """
    #     Skia GPU에 필요한 OpenGL 컨텍스트를 생성.
    #     순서: GLFW(데스크탑) → EGL(headless) → GLX(X11) → 실패
    #     """
    #     # 1) GLFW — 데스크탑 환경 (숨긴 윈도우)
    #     try:
    #         import glfw
    #         if glfw.init():
    #             glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    #             glfw.window_hint(glfw.STENCIL_BITS, 8)
    #             window = glfw.create_window(1, 1, "", None, None)
    #             if window:
    #                 glfw.make_context_current(window)
    #                 ctx = skia.GrDirectContext.MakeGL()
    #                 if ctx:
    #                     logger.info("GPU context 생성 성공 (GLFW)")
    #                     return ctx, ("glfw", window)
    #             glfw.terminate()
    #     except ImportError:
    #         pass
    #     except Exception as e:
    #         logger.debug("GLFW 실패: %s", e)
    #
    #     # 2) EGL — headless 서버 (모니터 불필요)
    #     try:
    #         import moderngl
    #         mgl = moderngl.create_standalone_context(backend="egl")
    #         interface = skia.GrGLInterface.MakeEGL()
    #         ctx = skia.GrDirectContext.MakeGL(interface)
    #         if ctx:
    #             logger.info("GPU context 생성 성공 (EGL)")
    #             return ctx, ("egl", mgl)
    #     except Exception as e:
    #         logger.debug("EGL 실패: %s", e)
    #
    #     # 3) GLX — X11 환경
    #     try:
    #         import moderngl
    #         mgl = moderngl.create_standalone_context()
    #         ctx = skia.GrDirectContext.MakeGL()
    #         if ctx:
    #             logger.info("GPU context 생성 성공 (GLX)")
    #             return ctx, ("glx", mgl)
    #     except Exception as e:
    #         logger.debug("GLX 실패: %s", e)
    #
    #     logger.warning("GPU context 생성 실패 — CPU 폴백")
    #     return None, None
    #
    #

    @staticmethod
    def _create_gpu_context():
        """
        Skia GPU에 필요한 OpenGL 컨텍스트를 생성.
        도커(Headless) 전용 고정: 불필요한 GLFW/GLX 단계를 제거하고 EGL로 직행합니다.
        """
        import moderngl
        import skia

        # 1) EGL — headless 서버 (모니터 불필요, 도커 환경 직행)
        try:
            # ⚠️ 중요: 4개의 워커가 동시에 렌더링을 때릴 때 가끔 충돌하는 것을 방지하기 위해
            # moderngl과 skia를 EGL 백엔드로 확실하게 묶어줍니다.
            mgl = moderngl.create_standalone_context(backend="egl")

            # Skia에게 명시적으로 EGL 인터페이스를 제공하여 드라이버 레벨에서 꼬이지 않게 합니다.
            interface = skia.GrGLInterface.MakeEGL()
            if not interface:
                # 환경에 따라 MakeEGL()이 None을 뱉는 경우가 있어서 안전장치 추가
                interface = skia.GrGLInterface.MakeNativeInterface()

            ctx = skia.GrDirectContext.MakeGL(interface)

            if ctx:
                logger.info("GPU context 생성 성공 (EGL Headless)")
                return ctx, ("egl", mgl)

        except Exception as e:
            logger.error("EGL 컨텍스트 생성 실패: %s", e)

        # 2) 모든 GPU 컨텍스트 생성 실패 시 CPU 소프트웨어 렌더링으로 폴백
        logger.warning("GPU context 생성 실패 — CPU 폴백 모드로 전환합니다.")
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

    # ── 도형: 삼각호 (바닥 호 이등변삼각형) ──────────────────────────

    def arc_triangle(
        self,
        cx: float, cy: float,
        base_width: float,
        height: float,
        curvature: float = 0.3,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
    ):
        """
        이등변삼각형 + 바닥만 호(곡선).

        Args:
            cx, cy: 꼭짓점 (상단) 좌표
            base_width: 바닥 변의 너비
            height: 꼭짓점에서 바닥까지 높이
            curvature: 바닥 호의 휘어짐 정도
                       양수 → 아래로 볼록 (↓)
                       음수 → 위로 오목 (↑)
                       0   → 직선 (일반 삼각형)
            fill: 채우기 색상
            stroke: 테두리 색상
            stroke_width: 테두리 두께

        사용법:
            renderer.arc_triangle(400, 100, base_width=200, height=150, curvature=0.3)
        """
        half_w = base_width / 2
        # 바닥 양 끝점
        left_x = cx - half_w
        left_y = cy + height
        right_x = cx + half_w
        right_y = cy + height

        # 바닥 호의 제어점 (quadratic bezier)
        ctrl_x = cx
        ctrl_y = cy + height + base_width * curvature

        p = skia.Path()
        p.moveTo(cx, cy)              # 꼭짓점
        p.lineTo(right_x, right_y)    # 오른쪽 직선 변
        p.quadTo(ctrl_x, ctrl_y, left_x, left_y)  # 바닥 호
        p.close()                     # 왼쪽 직선 변 (자동)

        if fill:
            paint = skia.Paint(AntiAlias=True, Color=fill.to_skia(), Style=skia.Paint.kFill_Style)
            self._canvas.drawPath(p, paint)
        if stroke:
            paint = skia.Paint(AntiAlias=True, Color=stroke.to_skia(), Style=skia.Paint.kStroke_Style, StrokeWidth=stroke_width)
            self._canvas.drawPath(p, paint)

    # ── 도형: 부채꼴 (원의 곡률을 따르는 노치) ─────────────────────

    def fan_notch(
        self,
        circle_cx: float, circle_cy: float,
        circle_radius: float,
        base_width: float,
        depth: float = None,
        angle_offset: float = 90,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
        arc_segments: int = 64,
    ):
        """
        원의 곡률을 정확히 따르는 부채꼴 (이등변삼각형 + 호).

        원 위의 두 점(P1, P2)을 밑변(base_width)으로 잡고,
        호는 원의 반지름으로 그려서 곡률이 정확히 일치함.
        꼭짓점(apex)은 원 안쪽으로 depth만큼 들어감.

        Args:
            circle_cx, circle_cy: 원의 중심
            circle_radius: 원의 반지름
            base_width: 밑변 길이 (원 위의 두 점 사이 직선 거리)
            depth: 꼭짓점이 원 안쪽으로 들어가는 깊이
                   None이면 base_width * 0.4 자동 계산
            angle_offset: 부채꼴 방향 (도, 화면 좌표계)
                          90  = 아래쪽 (기본, 웨이퍼 노치)
                          270 = 위쪽
                          0   = 오른쪽
                          180 = 왼쪽
            fill: 채우기 색상
            stroke: 테두리 색상
            stroke_width: 테두리 두께
            arc_segments: 호를 구성하는 선분 수 (클수록 부드러움)
        """
        r = circle_radius
        w = min(base_width, 2 * r * 0.99)

        # 반각 계산: θ = arcsin(w / 2r)
        half_angle = math.asin(w / (2 * r))

        # 방향 (라디안)
        dir_rad = math.radians(angle_offset)

        # 원 위의 두 점 (P1, P2)
        p1_angle = dir_rad - half_angle
        p2_angle = dir_rad + half_angle

        # 꼭짓점 (apex) — 원 안쪽으로 depth만큼 들어감
        d = depth if depth is not None else w * 0.4
        apex_x = circle_cx + (r - d) * math.cos(dir_rad)
        apex_y = circle_cy + (r - d) * math.sin(dir_rad)

        # path 구성: apex → P1 → 호(P1→P2, 점 찍기) → close(→apex)
        p = skia.Path()
        p.moveTo(apex_x, apex_y)

        # P1 → P2 까지 원 위의 점들을 직접 계산해서 찍음
        for i in range(arc_segments + 1):
            t = i / arc_segments
            angle = p1_angle + t * (p2_angle - p1_angle)
            px = circle_cx + r * math.cos(angle)
            py = circle_cy + r * math.sin(angle)
            p.lineTo(px, py)

        p.close()  # P2 → apex

        if fill:
            paint = skia.Paint(AntiAlias=True, Color=fill.to_skia(), Style=skia.Paint.kFill_Style)
            self._canvas.drawPath(p, paint)
        if stroke:
            paint = skia.Paint(AntiAlias=True, Color=stroke.to_skia(), Style=skia.Paint.kStroke_Style, StrokeWidth=stroke_width)
            self._canvas.drawPath(p, paint)

    # ── 도형: 웨이퍼 ─────────────────────────────────────────────

    def wafer(
        self,
        cx: float, cy: float,
        radius: float,
        notch_width: float = None,
        notch_depth: float = None,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
        notch_fill: Color = None,
        notch_stroke: Color = None,
    ):
        """
        반도체 웨이퍼 (원 + 하단 부채꼴 노치).

        Args:
            cx, cy: 웨이퍼 중심
            radius: 웨이퍼 반지름
            notch_width: 노치 밑변 길이 (None이면 radius * 0.12)
            notch_depth: 노치 깊이 (None이면 notch_width * 0.4)
            fill: 웨이퍼 채우기 색상
            stroke: 웨이퍼 테두리 색상
            notch_fill: 노치 채우기 (None이면 어두운 색 자동)
            notch_stroke: 노치 테두리

        사용법:
            renderer.wafer(400, 300, 200, fill=Color(180, 180, 190))
        """
        # 웨이퍼 본체 (원)
        self.circle(cx, cy, radius, fill=fill, stroke=stroke, stroke_width=stroke_width)

        # 노치 크기 자동 계산
        nw = notch_width if notch_width is not None else radius * 0.12
        nd = notch_depth if notch_depth is not None else nw * 0.4

        # 노치 색상 자동 설정 (웨이퍼보다 어두운 색)
        nf = notch_fill or Color(60, 60, 70)
        ns = notch_stroke

        # 하단 부채꼴 노치
        self.fan_notch(
            cx, cy, radius,
            base_width=nw, depth=nd,
            angle_offset=90,  # 아래쪽 (화면 좌표계: Y가 아래로 증가)
            fill=nf, stroke=ns, stroke_width=stroke_width,
        )

    def wafer_type2(
        self,
        cx: float, cy: float,
        radius: float,
        notch_width: float = None,
        notch_depth: float = None,
        fill: Color = None,
        stroke: Color = None,
        stroke_width: float = 2,
        bg_color: Color = None,
    ):
        """
        반도체 웨이퍼 (원 + 삼각형 겹치기 방식 노치).

        원을 그린 뒤 삼각형을 겹쳐서 노치를 자연스럽게 표현.
          1) 원 (fill + stroke)
          2) 삼각형 (stroke=원 테두리색, fill=배경색) → 노치 모양
          3) 삼각형 1px 아래 (stroke=배경색, fill=배경색) → 원 테두리 덮기

        Args:
            cx, cy: 웨이퍼 중심
            radius: 웨이퍼 반지름
            notch_width: 노치 밑변 길이 (None이면 radius * 0.12)
            notch_depth: 노치 깊이 (None이면 notch_width * 0.5)
            fill: 웨이퍼 채우기 색상
            stroke: 웨이퍼 테두리 색상
            stroke_width: 테두리 두께
            bg_color: 배경색 (노치 안쪽 + 원 테두리 덮기용, None이면 흰색)

        사용법:
            renderer.wafer_type2(400, 300, 200,
                                fill=Color(180, 180, 190),
                                stroke=Color(120, 120, 130))
        """
        wafer_fill = fill or Color(180, 180, 190)
        wafer_stroke = stroke or Color(120, 120, 130)
        bg = bg_color or Colors.WHITE

        nw = notch_width if notch_width is not None else radius * 0.12
        nd = notch_depth if notch_depth is not None else nw * 0.5

        # 1) 원 (웨이퍼 본체)
        self.circle(cx, cy, radius, fill=wafer_fill, stroke=wafer_stroke, stroke_width=stroke_width)

        # 노치 삼각형 꼭짓점 좌표
        half_w = nw / 2
        bottom = cy + radius  # 원의 맨 아래
        apex_y = bottom - nd  # 삼각형 꼭짓점 (위로 들어감)

        tri_points = [
            (cx - half_w, bottom),   # 왼쪽 아래
            (cx, apex_y),            # 꼭짓점 (위)
            (cx + half_w, bottom),   # 오른쪽 아래
        ]

        # 2) 삼각형 — 노치 모양 (테두리=원 테두리색, 내부=배경색)
        self.path(tri_points, closed=True, fill=bg, stroke=wafer_stroke, stroke_width=stroke_width)

        # 3) 삼각형 stroke_width만큼 아래 — 원 테두리 덮기 (테두리=배경색, 내부=배경색)
        tri_cover = [
            (cx - half_w, bottom + stroke_width),
            (cx, apex_y + stroke_width),
            (cx + half_w, bottom + stroke_width),
        ]
        self.path(tri_cover, closed=True, fill=bg, stroke=bg, stroke_width=stroke_width + 1)

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

    def _read_surface_to_pil(self) -> Image.Image:
        """Surface에서 픽셀을 읽어 PIL Image로 변환 (GPU/CPU 모두 동작)"""
        if self._use_gpu:
            self._surface.flushAndSubmit()

        # 현재 surface 크기
        w = self._surface.width()
        h = self._surface.height()

        # Surface에서 직접 픽셀 읽기 (GPU→CPU 전송 포함)
        info = skia.ImageInfo.Make(
            w, h,
            skia.kRGBA_8888_ColorType,
            skia.kUnpremul_AlphaType,
        )
        row_bytes = w * 4
        pixel_data = bytearray(h * row_bytes)
        success = self._surface.readPixels(info, pixel_data, row_bytes, 0, 0)

        if success:
            return Image.frombytes("RGBA", (w, h), bytes(pixel_data))

        raise RuntimeError("Surface에서 픽셀 읽기 실패")

    def finish(self) -> Image.Image:
        """렌더링 완료 → PIL Image 반환"""
        return self._read_surface_to_pil()

    def finish_bytes(self, format: str = "png", quality: int = 90) -> bytes:
        """렌더링 완료 → bytes 반환 (서버 응답용)"""
        pil_image = self._read_surface_to_pil()
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