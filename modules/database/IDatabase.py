from abc import ABC, abstractmethod

from modules.database.ResultSet import ResultSet, Row


class IDatabase(ABC):

    @abstractmethod
    def initialize(self) -> None:
        ...


class ISyncDatabase(IDatabase):

    @abstractmethod
    def select(self, query: str, params: dict = None) -> ResultSet:
        ...

    @abstractmethod
    def select_one(self, query: str, params: dict = None) -> Row | None:
        ...

    @abstractmethod
    def update(self, query: str, params: dict = None) -> int:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


class IAsyncDatabase(IDatabase):

    @abstractmethod
    async def select_async(self, query: str, params: dict = None) -> ResultSet:
        ...

    @abstractmethod
    async def select_one_async(self, query: str, params: dict = None) -> Row | None:
        ...

    @abstractmethod
    async def update_async(self, query: str, params: dict = None) -> int:
        ...

    @abstractmethod
    async def close_async(self) -> None:
        ...