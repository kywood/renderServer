from typing import Any, Iterable, Iterator


class ArrowContainer:


    def __init__(self):

        self._container = []

        pass

    def append(self , object : Any):
        self._container.append(object)

    def extend(self, arrows: Iterable[Any]) -> None:
        """화살표 여러 개 추가"""
        self._container.extend(arrows)

    def remove(self, arrow: Any) -> None:
        """일치하는 첫 번째 화살표 삭제. 없으면 ValueError"""
        self._container.remove(arrow)

    def pop(self, index: int = -1) -> Any:
        """해당 위치의 화살표를 꺼내서 반환"""
        return self._container.pop(index)

    def clear(self) -> None:
        """전체 삭제"""
        self._container.clear()

    def __len__(self) -> int:
        return len(self._container)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._container)

    def __getitem__(self, index: int | slice) -> Any:
        return self._container[index]

    def __setitem__(self, index: int, arrow: Any) -> None:
        self._container[index] = arrow

    def __delitem__(self, index: int) -> None:
        del self._container[index]

    def __contains__(self, arrow: Any) -> bool:
        return arrow in self._container

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._container!r})"