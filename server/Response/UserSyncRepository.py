from modules.database.IDatabase import ISyncDatabase
from modules.database.ResultSet import Row, ResultSet
from server.Response.Repository import AbSyncRepository


class UserSyncRepository(AbSyncRepository):

    def __init__(self, db: ISyncDatabase):
        super().__init__(db)

    def find_by_id(self, id: int) -> Row | None:
        return self._db.select_one(
            "SELECT * FROM users WHERE id = :id", {"id": id}
        )

    def find_all(self) -> ResultSet:
        return self._db.select("SELECT * FROM users")

    def insert(self, data: dict) -> int:
        return self._db.update(
            "INSERT INTO users (name, email) VALUES (:name, :email)", data
        )

    def update(self, data: dict) -> int:
        return self._db.update(
            "UPDATE users SET name = :name, email = :email WHERE id = :id", data
        )

    def delete(self, id: int) -> int:
        return self._db.update(
            "DELETE FROM users WHERE id = :id", {"id": id}
        )
