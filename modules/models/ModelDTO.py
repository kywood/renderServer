from abc import ABC

from pydantic import BaseModel

from modules.models.dtos.IDto import IDTO


class ModelDTO(IDTO, BaseModel, ABC):
    """순수 데이터 전달용"""
    def to_dict(self) -> dict:
        return self.model_dump()
    def to_json(self) -> str:
        return self.model_dump_json(indent=2)