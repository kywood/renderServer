class Row:

    def __init__(self, data: dict, columns: list[str]):
        self._data = data
        self._columns = columns

    def get(self, key) -> any:
        if isinstance(key, int):
            col = self._columns[key]
            return self._data[col]
        return self._data[key]

    def __getitem__(self, key):
        return self.get(key)

    def __repr__(self):
        return str(self._data)


class ResultSet:

    def __init__(self, rows: list[dict], affected_count: int = None):
        self._rows = rows
        self._columns = list(rows[0].keys()) if rows else []
        self._cursor = -1
        self._affected_count = affected_count if affected_count is not None else len(rows)

    def next(self) -> bool:
        self._cursor += 1
        return self._cursor < len(self._rows)

    def get(self) -> Row:
        return Row(self._rows[self._cursor], self._columns)

    def first(self) -> Row | None:
        return Row(self._rows[0], self._columns) if self._rows else None

    @property
    def row_count(self) -> int:
        return len(self._rows)



    @property
    def affected_count(self) -> int:
        """SELECT: len(rows), DML: actual rowcount from DB"""
        return self._affected_count

    def is_empty(self) -> bool:
        return len(self._rows) == 0

    def reset(self) -> None:
        self._cursor = -1

    def __iter__(self):
        self.reset()
        while self.next():
            yield self.get()

    def __len__(self):
        return len(self._rows)