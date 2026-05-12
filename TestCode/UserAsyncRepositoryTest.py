import asyncio
from modules.database.AsyncDatabase import AsyncDatabase
from modules.database.DatabaseResource import DatabaseResource
from server.Response.UserAsyncRepository import UserAsyncRepository


async def main():
    # db = AsyncDatabase("postgresql+asyncpg://testuser:testpass@localhost:5432/testdb")
    # db.initialize()

    from modules.path.BasePath import BasePath
    projectEntryPath = BasePath.instance("../").GetBasePath()
    configFolderPath = BasePath.instance().Dir("conf")
    configFilePath = BasePath.instance().File("conf", "config.ini")

    print(f"projectEntryPath : {projectEntryPath}")
    print(f"configFolderPath : {configFolderPath}")
    print(f"configFilePath : {configFilePath}")

    from modules.config.ConfigLoader import ConfigLoader

    configLoader = ConfigLoader.instance(configFilePath)

    resource = DatabaseResource(configLoader)
    db = resource.create_async()


    repo = UserAsyncRepository(db)

    # 전체 조회
    result = await repo.find_all_async()
    print(f"총 {result.row_count}건")
    while result.next():
        row = result.get()
        print(row["id"], row["name"], row["email"])

    # 단건 조회
    row = await repo.find_by_id_async(1)
    if row:
        print(f"find_by_id: {row['name']}")

    # 추가
    affected = await repo.insert_async({"name": "jung", "email": "jung@test.com"})
    print(f"{affected}건 추가")

    # 수정
    affected = await repo.update_async({"id": 1, "name": "choi", "email": "choi@test.com"})
    print(f"{affected}건 수정")

    # 삭제
    affected = await repo.delete_async(2)
    print(f"{affected}건 삭제")

    await db.close_async()


if __name__ == "__main__":
    asyncio.run(main())