from abc import ABC

from pydantic import BaseModel

from modules.models.model.IModel import IModel


class ModelBase(IModel, BaseModel, ABC):
    def to_dict(self) -> dict:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    def release(self):
        pass

