from modules.database.SyncDatabase import SyncDatabase

db = SyncDatabase("postgresql://testuser:testpass@localhost:5432/testdb")
db.initialize()

# select
result = db.select("SELECT * FROM users")
print(f"총 {result.row_count}건")
while result.next():
    row = result.get()
    print(row["name"], row["email"])

# select_one
row = db.select_one("SELECT * FROM users WHERE id = :id", {"id": 1})
print(row["name"])

# execute
affected = db.update("UPDATE users SET name = :name WHERE id = :id", {"name": "choi", "id": 1})
print(f"{affected}건 수정")

db.close()