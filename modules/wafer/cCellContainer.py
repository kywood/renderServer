from modules.wafer import cCell


class CellContainer:


    def __init__(self):

        self._container = {}

        pass

    def append(self , cell : cCell):
        self._container[cell.id] = cell

    def get(self,cell : cCell):
        return self._container[cell.id]

    def remove(self, cell_id: str | int) -> 'cCell | None':
        """컨테이너에서 지정한 ID의 cell을 제거하고 반환합니다."""
        if hasattr(cell_id, 'id'):
            cell_id = cell_id.id
        return self._container.pop(cell_id, None)

    def clear(self) -> None:
        """컨테이너를 비웁니다."""
        self._container.clear()

    # --- 파이썬 특수 메서드 (파이썬다운 객체 조작) ---
    # --- items() 메서드 추가 ---
    def items(self):
        """(cell_id, cell) 튜플 쌍을 반환합니다."""
        return self._container.items()

    def keys(self):
        """cell_id 목록을 반환합니다."""
        return self._container.keys()

    def values(self):
        """cell 객체 목록을 반환합니다."""
        return self._container.values()


    def __getitem__(self, cell_id: str | int) -> 'cCell':
        """container[cell_id] 형태로 접근할 수 있게 합니다."""
        cell = self.get(cell_id)
        if cell is None:
            raise KeyError(f"ID가 '{cell_id}'인 Cell을 찾을 수 없습니다.")
        return cell

    def __contains__(self, cell_id: str | int) -> bool:
        """'cell_id in container' 또는 'cell in container' 형태로 존재 여부를 확인합니다."""
        if hasattr(cell_id, 'id'):
            cell_id = cell_id.id
        return cell_id in self._container

    def __len__(self) -> int:
        """len(container) 형태로 컨테이너 안의 cell 개수를 구합니다."""
        return len(self._container)

    def __iter__(self):
        """for cell in container: 구문으로 바로 순회할 수 있게 합니다."""
        return iter(self._container.values())

    def __repr__(self) -> str:
        return f"<CellContainer count={len(self._container)}>"