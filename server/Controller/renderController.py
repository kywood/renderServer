from fastapi import FastAPI

from modules.config.ConfigLoader import ConfigLoader
from server.Controller.IController import  abController


class RenderController(abController):

    def __init__(self,config: ConfigLoader,prefix: str = ""):
        super().__init__(config,prefix)

    def _register_routes(self) -> None:
        """이 컨트롤러가 가진 엔드포인트들을 app에 등록"""

        @self.router.get("/")
        def health():
            return {"status": "ok"}


        @self.router.get("/health")
        def health():
            return {"status": "health_ok"}

        @self.router.get("/wafer")
        def render_wafer():
            from modules.render.renderer import GPURenderer, Colors, Color
            renderer = GPURenderer(width=1024, height=1024, use_gpu=True)

            renderer.begin(1024, 1024)
            from modules.render.renderer import Colors
            renderer.clear(Colors.BLACK)
            renderer.wafer(
                cx=512, cy=512, radius=400,
                fill=Color(180, 180, 190),
                stroke=Color(120, 120, 130),
                stroke_width=2,
            )
            image_bytes = renderer.finish_bytes(format="png")
            renderer.release()

            from starlette.responses import StreamingResponse
            import io
            return StreamingResponse(
                io.BytesIO(image_bytes),
                media_type="image/png",
            )
        pass