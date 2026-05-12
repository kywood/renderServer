from modules.database.IDatabase import IAsyncDatabase
from modules.database.ResultSet import Row, ResultSet
from server.Response.Repository import AbAsyncRepository


class UserAsyncRepository(AbAsyncRepository):

    def __init__(self, db: IAsyncDatabase):
        super().__init__(db)

    async def find_by_id_async(self, id: int) -> Row | None:
        return await self._db.select_one_async(
            "SELECT * FROM users WHERE id = :id", {"id": id}
        )

    async def find_all_async(self) -> ResultSet:
        return await self._db.select_async("SELECT * FROM users")

    async def insert_async(self, data: dict) -> int:
        return await self._db.update_async(
            "INSERT INTO users (name, email) VALUES (:name, :email)", data
        )

    async def update_async(self, data: dict) -> int:
        return await self._db.update_async(
            "UPDATE users SET name = :name, email = :email WHERE id = :id", data
        )

    async def delete_async(self, id: int) -> int:
        return await self._db.update_async(
            "DELETE FROM users WHERE id = :id", {"id": id}
        )

