import math

from modules.render.cPoint import cPoint
from modules.render.cRect import cRect
from modules.wafer.cCellContainer import CellContainer


class cWafer(object):


    def __init__(self , point , radius , grid_size , stroke ):
        self._point = point
        self._radius = radius
        self._grid_size = grid_size
        self._stroke = stroke

        from modules.wafer.cCellContainer import CellContainer
        self._cellContainer = CellContainer()

        pass

    def _size(self):
        return self._radius * 2

    def is_in_rect(self , rect : cRect):
        radius_squared = self._radius ** 2

        corners = (
            (rect.left, rect.top),
            (rect.right, rect.top),
            (rect.left, rect.bottom),
            (rect.right, rect.bottom),
        )

        for x, y in corners:
            distance_squared = (
                    (x - self._point.x) ** 2
                    + (y - self._point.y) ** 2
            )

            if distance_squared > radius_squared:
                return False  # 하나라도 원 밖이면 탈락

        return True  # 모두 원 안에 있음


    ## 여기서 Cell 을 계산 하고 가지고 있자...
    def _init(self):

        from modules.wafer.cCell import cCell
        from modules.render.cRect import cRect

        wide_count = math.ceil(self._size() / self._grid_size)
        # 전체 그리드의 실제 너비
        grid_width = wide_count * self._grid_size

        # 원 중심을 기준으로 그리드의 왼쪽 위 계산
        left = self._point.x - grid_width / 2
        top = self._point.y - grid_width / 2

        for row in range(wide_count):
            for col in range(wide_count):
                cell_id = cPoint(col, row)

                x = left + col * self._grid_size
                y = top + row * self._grid_size

                rt = cRect(
                    point=cPoint(x, y),
                    size=cPoint(grid_width, grid_width)
                )

                self._cellContainer.append(
                    cCell(
                        wafer=self,
                        id=cell_id,
                        rect=rt,
                        is_in_wafer=self.is_in_rect(rt)
                    )
                )

        pass


    @classmethod
    def create(cls , point , radius , grid_size , stroke = 1.0 ):
        return cWafer (
            point ,
            radius ,
            grid_size ,
            stroke
        )

    # def __repr__(self):
    #     return (
    #         f"cRect(x={self.x}, y={self.y}, "
    #         f"width={self.width}, height={self.height})"
    #     )