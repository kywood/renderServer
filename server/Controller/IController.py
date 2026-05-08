from abc import ABC, abstractmethod
from fastapi import FastAPI, APIRouter

from modules.config.ConfigLoader import ConfigLoader


class IController(ABC):

    @abstractmethod
    def register(self, app: FastAPI) -> None:
        ...



class abController(IController , ABC):

    def __init__(self , config: ConfigLoader,prefix: str = ""):

        self.config = config
        self.prefix = prefix
        self.router: APIRouter = None

    def register(self, app: FastAPI) -> None:
        self.router = APIRouter(prefix=self.prefix)
        self._register_routes()
        app.include_router(self.router)

    @abstractmethod
    def _register_routes(self) -> None:
        ...
