from abc import ABC
from modules.database.IDatabase import ISyncDatabase, IAsyncDatabase

class AbDatabase(ABC):

    def __init__(self, url: str, **engine_kwargs):
        self._url = url
        self._engine = None
        self._engine_kwargs = engine_kwargs

    @property
    def url(self) -> str:
        return self._url


class AbSyncDatabase(AbDatabase, ISyncDatabase, ABC):

    pass


class AbAsyncDatabase(AbDatabase , IAsyncDatabase, ABC):
    pass