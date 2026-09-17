
import io
import math
import logging

import skia
from PIL import Image
from modules.render import cPoint
from modules.render.cColor import cColor, Colors
from modules.render.cSize import cSize

logger = logging.getLogger(__name__)

class cCanvas:

    def __init__(self,  size : cSize ,  use_gpu: bool = True):
        self._gpu_context = None
        self._surface = None
        self._canvas = None
        self._use_gpu = use_gpu
        self._gl_backend = None  # GL context 핸들 (정리용)
        self._size = size

        if use_gpu:
            self._gpu_context, self._gl_backend = self._create_gpu_context()
            if self._gpu_context is None:
                self._use_gpu = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        return False  # 오류는 호출한 쪽으로 전달


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

    @property
    def canvas(self):
        return self._canvas

    # ── 캔버스 수명주기 ──────────────────────────────────────────────

    def begin(self,  bg_color: cColor = None):
        """렌더링 시작 — 새 캔버스 생성"""


        w = self._size.width
        h = self._size.height

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

    def clear(self, color: cColor = Colors.BLACK):
        self._canvas.clear(color.to_skia())


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