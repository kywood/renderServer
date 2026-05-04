from abc import ABC, abstractmethod


class IDTO(ABC):

    @abstractmethod
    def to_dict(self) -> dict: ...


    @abstractmethod
    def to_json(self) -> str: ...
