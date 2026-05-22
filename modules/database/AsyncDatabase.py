from sqlalchemy import text
from sqlalchemy.ext.asyncio.engine import create_async_engine

from modules.database.AbDatabase import AbAsyncDatabase
from modules.database.ResultSet import ResultSet, Row


class AsyncDatabase(AbAsyncDatabase):

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
        self._engine = create_async_engine(self._url, **defaults)

    async def select_async(self, query: str, params: dict = None) -> ResultSet:
        async with self._engine.connect() as conn:
            result = await conn.execute(text(query), params or {})
            rows = [dict(row._mapping) for row in result]
            return ResultSet(rows)

    async def select_one_async(self, query: str, params: dict = None) -> ResultSet:
        async with self._engine.connect() as conn:
            result = await conn.execute(text(query), params or {})
            row = result.fetchone()
            rows = [dict(row._mapping)] if row else []
            return ResultSet(rows)

    async def update_async(self, query: str, params: dict = None) -> ResultSet:
        async with self._engine.connect() as conn:
            result = await conn.execute(text(query), params or {})
            await conn.commit()
            return ResultSet(rows=[], affected_count=result.rowcount)

    async def close_async(self) -> None:
        if self._engine:
            await self._engine.dispose()