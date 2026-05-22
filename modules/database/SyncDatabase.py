from sqlalchemy import create_engine, text

from modules.database.AbDatabase import AbSyncDatabase
from modules.database.ResultSet import ResultSet, Row


class SyncDatabase(AbSyncDatabase):

    def __init__(self, url: str, **engine_kwargs):
        super().__init__(url)
        self._engine = None
        self._engine_kwargs = engine_kwargs

    def initialize(self) -> None:
        defaults = {
            "echo": False,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_recycle": 3600,
        }
        defaults.update(self._engine_kwargs)
        self._engine = create_engine(self._url, **defaults)

    def select(self, query: str, params: dict = None) -> ResultSet:
        with self._engine.connect() as conn:
            # from sqlalchemy import text
            result = conn.execute(text(query), params or {})
            rows = [dict(row._mapping) for row in result]
            return ResultSet(rows)

    def select_one(self, query: str, params: dict = None) -> ResultSet:
        # result = self.select(query, params)
        # return result.first()
        with self._engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            row = result.fetchone()
            rows = [dict(row._mapping)] if row else []
            return ResultSet(rows)

    def update(self, query: str, params: dict = None) -> ResultSet:
        with self._engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text(query), params or {})
            conn.commit()
            return ResultSet(rows=[], affected_count=result.rowcount)

    def close(self) -> None:
        if self._engine:
            self._engine.dispose()