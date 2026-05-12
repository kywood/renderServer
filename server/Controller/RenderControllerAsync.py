from fastapi.responses import StreamingResponse
from modules.config.ConfigLoader import ConfigLoader
from modules.render.renderer import GPURenderer, Colors , Color
from server.Controller.IController import abController
import asyncio
import io


class RenderControllerAsync(abController):

    def __init__(self, config: ConfigLoader, prefix: str = ""):
        super().__init__(config, prefix)

    def _render_wafer(self) -> bytes:
        renderer = GPURenderer(width=1024, height=1024, use_gpu=True)
        renderer.begin(1024, 1024)
        renderer.clear(Colors.BLACK)
        renderer.wafer(
            cx=512, cy=512, radius=400,
            fill=Color(180, 180, 190),
            stroke=Color(120, 120, 130),
            stroke_width=2,
        )
        image_bytes = renderer.finish_bytes(format="png")
        renderer.release()
        return image_bytes

    def _register_routes(self) -> None:

        @self.router.get("/")
        async def health():
            return {"status": "ok"}

        @self.router.get("/health")
        async def health_check():
            return {"status": "health_ok"}

        @self.router.get("/wafer")
        async def render_wafer():
            loop = asyncio.get_event_loop()
            image_bytes = await loop.run_in_executor(None, self._render_wafer)

            return StreamingResponse(
                io.BytesIO(image_bytes),
                media_type="image/png",
            )