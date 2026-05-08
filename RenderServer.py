from fastapi import FastAPI
from server.Controller.IController import IController
from server.Controller.renderController import RenderController


#
# class ApiServer:
#     def __init__(self, title: str = "Haerujil24 Serving"):
#         self.app = FastAPI(title=title)
#         self._controllers: list[IController] = []
#
#     def add_controller(self, controller: IController) -> "ApiServer":
#         self._controllers.append(controller)
#         return self
#
#     def build(self) -> FastAPI:
#         for c in self._controllers:
#             c.register(self.app)
#         return self.app


def create_app() -> FastAPI:

    from modules.path.BasePath import BasePath
    projectEntryPath = BasePath.instance().GetBasePath()
    configFolderPath = BasePath.instance().Dir("conf")
    configFilePath = BasePath.instance().File("conf" , "config.ini")

    print(f"projectEntryPath : {projectEntryPath}")
    print(f"configFolderPath : {configFolderPath}")
    print(f"configFilePath : {configFilePath}")

    from modules.config.ConfigLoader import ConfigLoader
    configLoader = ConfigLoader.instance(configFilePath)


    # config = ConfigLoader.instance()
    # InferenceManager.instance(config).Initialize()

    from server.Server.ApiServer import ApiServer
    server = ApiServer(title=configLoader.Get('APP','NAME'))
    server.add_controller(RenderController(configLoader, prefix="/render") )
    app = server.build()
    return app


app = create_app()



def main():
    import os
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))  # GPU 서빙이면 1 권장

    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info",
    )



if __name__ == '__main__':
    main()

