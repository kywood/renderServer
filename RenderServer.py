from fastapi import FastAPI
from server.Controller.IController import IController
from server.Controller.renderController import RenderController


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


    from server.Server.ApiServer import ApiServer
    server = ApiServer(title=configLoader.Get('APP','NAME'))
    # server.add_controller(RenderController(configLoader, prefix="/render") )
    from server.Controller.RenderControllerAsync import RenderControllerAsync
    server.add_controller(RenderControllerAsync(configLoader, prefix="/render") )
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

