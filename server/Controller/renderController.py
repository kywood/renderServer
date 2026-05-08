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

        pass