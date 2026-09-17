import io
import math
import skia

from modules.render.cCanvas import cCanvas
from modules.render.cColor import cColor, Colors


class cRenderer:

    def __init__(self, canvas: cCanvas):
        self._owner_canvas = canvas

    @property
    def _canvas(self):
        return self._owner_canvas.canvas

    def clip_path(self, path):
        self._canvas.clipPath(path, doAntiAlias=True)

    def draw_path(
            self, path,
            fill=None,
            stroke=None,
            stroke_width=1.0,
    ):
        if fill is not None:
            self._canvas.drawPath(
                path,
                skia.Paint(
                    AntiAlias=True,
                    Color=fill.to_skia(),
                    Style=skia.Paint.kFill_Style,
                ),
            )

        if stroke is not None:
            self._canvas.drawPath(
                path,
                skia.Paint(
                    AntiAlias=True,
                    Color=stroke.to_skia(),
                    Style=skia.Paint.kStroke_Style,
                    StrokeWidth=stroke_width,
                ),
            )
    # ── 도형: 원 ─────────────────────────────────────────────────────

    def circle(
        self,
        cx: float, cy: float, radius: float,
        fill: cColor = None,
        stroke: cColor = None,
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
        color: cColor = Colors.WHITE,
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
        color: cColor = Colors.WHITE,
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
        fill: cColor = None,
        stroke: cColor = None,
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
        color: cColor = Colors.WHITE, width: float = 2,
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
        fill: cColor = None,
        stroke: cColor = None,
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



    def path(
        self,
        points: list[tuple[float, float]],
        closed: bool = False,
        fill: cColor = None,
        stroke: cColor = None,
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
        color: cColor = Colors.WHITE,
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
        fill: cColor = Colors.BLUE,
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
        colors: list[cColor],
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
        self._canvas.scale(sx, sx if sy is None else sy)

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
