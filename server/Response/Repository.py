from abc import ABC, abstractmethod

from modules.database.IDatabase import IDatabase, ISyncDatabase, IAsyncDatabase
from modules.database.ResultSet import Row, ResultSet


class IRepository(ABC):
    pass


class ISyncRepository(IRepository):

    @abstractmethod
    def find_by_id(self, id: int) -> Row | None:
        ...

    @abstractmethod
    def find_all(self) -> ResultSet:
        ...

    @abstractmethod
    def insert(self, data: dict) -> int:
        ...

    @abstractmethod
    def update(self, data: dict) -> int:
        ...

    @abstractmethod
    def delete(self, id: int) -> int:
        ...


class IAsyncRepository(IRepository):

    @abstractmethod
    async def find_by_id_async(self, id: int) -> Row | None:
        ...

    @abstractmethod
    async def find_all_async(self) -> ResultSet:
        ...

    @abstractmethod
    async def insert_async(self, data: dict) -> int:
        ...

    @abstractmethod
    async def update_async(self, data: dict) -> int:
        ...

    @abstractmethod
    async def delete_async(self, id: int) -> int:
        ...


class AbRepository(ABC):

    def __init__(self, db: IDatabase):
        self._db = db


class AbSyncRepository(AbRepository, ISyncRepository, ABC):

    def __init__(self, db: ISyncDatabase):
        super().__init__(db)


class AbAsyncRepository(AbRepository, IAsyncRepository, ABC):

    def __init__(self, db: IAsyncDatabase):
        super().__init__(db)
