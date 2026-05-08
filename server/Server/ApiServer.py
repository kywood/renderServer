from server.Server.Server import IServer
from server.Controller.IController import IController
from fastapi import FastAPI


class ApiServer(IServer):

    def __init__(self, title: str = "Api Serving"):
        self.app = FastAPI(title=title)

        self._controllers: list[IController] = []

    def add_controller(self, controller: IController) -> "IServer":
        self._controllers.append(controller)
        return self

    def build(self) -> FastAPI:
        for c in self._controllers:
            c.register(self.app)
        return self.app
