from typing import AnyStr, Any

from pydantic import BaseModel, Field


class RestModel(BaseModel):

    pass


class RequestModel(RestModel):

    pass


class ResponseHeader(BaseModel):

    code : int = 0
    message:str="ok"


    pass

class ResponseModel(RestModel):

    response : ResponseHeader = Field(default_factory=ResponseHeader)


    pass


class InferResponse(ResponseModel):
    filename:str
    elapsed_ms:Any
    count:int
    detections:Any
    pass

class InferTestResponse(ResponseModel):

    name:str=""
    age:int=0

    pass


class PingRequest(RequestModel):
    name:str = ""
    pass

class PingResponse(ResponseModel):
    name: str = ""
    age: int = 0

