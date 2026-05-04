from abc import ABC, abstractmethod


class IModel(ABC):

    @abstractmethod
    def to_dict(self) -> dict: ...

    @abstractmethod
    def to_json(self) -> str: ...

    @abstractmethod
    def release(self): ...





