from modules.config.ConfigLoader import ConfigLoader
from modules.database.SyncDatabase import SyncDatabase
from modules.database.AsyncDatabase import AsyncDatabase


class DatabaseResource:

    def __init__(self, config: ConfigLoader):
        self._config = config

    def _build_url(self, driver: str) -> str:
        c = self._config
        return (
            f"{driver}://{c.Get('DATABASE','USER')}:{c.Get('DATABASE','PASSWORD')}"
            f"@{c.Get('DATABASE','HOST')}:{c.Get('DATABASE','PORT')}"
            f"/{c.Get('DATABASE','NAME')}"
        )

    def create_sync(self) -> SyncDatabase:
        url = self._build_url(self._config.Get('DATABASE', 'DRIVER'))
        db = SyncDatabase(url)
        db.initialize()
        return db

    def create_async(self) -> AsyncDatabase:
        url = self._build_url(self._config.Get('DATABASE', 'ASYNC_DRIVER'))
        db = AsyncDatabase(url)
        db.initialize()
        return db