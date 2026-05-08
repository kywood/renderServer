from fastapi import FastAPI
from Controller.IController import IController
from Config.ConfigLoader import ConfigLoader
from fastapi import UploadFile, File, Request, HTTPException

class ServingController(IController):

    def __init__(self,config: ConfigLoader):
        super().__init__()

        from Service.ServingService import ServingService
        self._service = ServingService(config)

        self._config = config

        from Dtos.S3Dto import S3ConnectDto
        self._s3ConnetctionDTO = S3ConnectDto().SetDTOFromConfig(config)

        # self.s3_endpoint = config.get("MINIO", "S3_ENDPOINT")
        # self.s3_bucket = config.get("MINIO", "S3_BUCKET")
        # self.s3_access_key = config.get("MINIO", "S3_ACCESS_KEY")
        # self.s3_secret_key = config.get("MINIO", "S3_SECRET_KEY")

        self.run_id = config.get("YOLO_MODEL", "RUN_ID")
        self.default_device = config.get("SERVING_RUNTIME", "YOLO_DEVICE", "auto")

        pass


    def register(self, app: FastAPI) -> None:
        """이 컨트롤러가 가진 엔드포인트들을 app에 등록"""

        @app.get("/health")
        def health():
            return {"status": "ok"}


        @app.get("/dir")
        def health_dir():
            from Config.ConfigHelper import ConfigHelper
            path = ConfigHelper.GetCachePath()

            print(f"path:{path}")
            return {"status": "ok"}


        from Models.RestModel import PingResponse
        # from Models.RestModel import PingRequest
        @app.get("/ping/{name}", response_model=PingResponse)
        def health_dir(name:str):
            from Models.RestModel import ResponseHeader
            return PingResponse(response=ResponseHeader(code=1,message="dd"),  name="a" , age=10)


        from Models.RestModel import InferResponse
        @app.post("/infer" , response_model=InferResponse)
        async def infer(request: Request,file: UploadFile = File(...)):
            return await self._service.infer(file)


        from Models.RestModel import InferResponse
        @app.post("/infer_vis" )
        async def infer_vis(request: Request,file: UploadFile = File(...)):
            return await self._service.infer_vis(file)

    pass
