import math

from modules.render.cPoint import cPoint
from modules.render.cRect import cRect


class cWafer(object):


    def __init__(self ,
                 point : cPoint,
                 radius : int,
                 grid_count : cPoint ,
                 stroke : float ,
                 notch_angle=4.0,
                 notch_depth=5.0,):
        self._point = point
        self._radius = radius
        self._grid_conut = grid_count
        # self._grid_size = grid_size

        self._grid_size = self._calculate_grid_cell_size()
        self._stroke = stroke

        self._notch_angle = notch_angle
        self._notch_depth = notch_depth

        from modules.wafer.cCellContainer import CellContainer
        self._cellContainer = CellContainer()


        self._init()

        pass

    def _calculate_grid_cell_size(self):
        diameter = 2 * self._radius

        # 한 칸의 가로 및 세로 폭
        cell_width = diameter / self._grid_conut.x
        cell_height = diameter / self._grid_conut.y

        from modules.render.cSize import cSize
        return cSize(cell_width, cell_height)


    def _size(self):
        return self._radius * 2

    @property
    def cell_container(self):
        return self._cellContainer

    @property
    def point(self):
        return self._point

    @property
    def radius(self):
        return self._radius

    @property
    def stroke(self):
        return self._stroke

    @property
    def grid_size(self):
        return self._grid_size

    @property
    def notch_angle(self):
        return self._notch_angle

    @property
    def notch_depth(self):
        return self._notch_depth

    def is_in_rect(self , rect : cRect):
        radius_squared = self._radius ** 2

        px, py = self._point.x, self._point.y

        corners = (
            (rect.left, rect.top),
            (rect.right, rect.top),
            (rect.left, rect.bottom),
            (rect.right, rect.bottom),
        )

        # print(f"[DEBUG] Circle Center: ({px}, {py}), Radius^2: {radius_squared}")

        for i, (x, y) in enumerate(corners):
            distance_squared = (x - px) ** 2 + (y - py) ** 2
            # print(f"[DEBUG] Corner {i}: ({x}, {y}) -> dist^2: {distance_squared}")

            if distance_squared > radius_squared:
                # print(f"[DEBUG] Failed at Corner {i}")
                return False

        return True

    ## 여기서 Cell 을 계산 하고 가지고 있자...
    def _init(self):

        from modules.wafer.cCell import cCell
        from modules.render.cRect import cRect

        wide_count = math.ceil(self._size() / self._grid_size.w)
        height_count = math.ceil(self._size() / self._grid_size.h)
        # 전체 그리드의 실제 너비
        grid_width = wide_count * self._grid_size.w
        grid_height = wide_count * self._grid_size.h

        # 원 중심을 기준으로 그리드의 왼쪽 위 계산
        left = self._point.x - grid_width / 2
        top = self._point.y - grid_height / 2



        import random

        for row in range(height_count):
            for col in range(wide_count):
                cell_id = cPoint(col, row)

                x = left + col * self._grid_size.w
                y = top + row * self._grid_size.h

                rt = cRect(
                    point=cPoint(x, y),
                    size=self._grid_size
                )


                self._cellContainer.append(
                    cCell(
                        wafer=self,
                        id=cell_id,
                        rect=rt,
                        arrow_count=random.randint(5, 20),
                        is_in_wafer=self.is_in_rect(rt)
                    )
                )

        pass


    @classmethod
    def create(cls , point , radius , grid_size : int , stroke = 1.0 ,
               notch_angle=4.0, notch_depth=5.0
               ):
        return cWafer (
            point =point ,
            radius = radius ,
            grid_size =grid_size ,
            stroke = stroke ,
            notch_angle=notch_angle,
            notch_depth=notch_depth
        )

    # def __repr__(self):
    #     return (
    #         f"cRect(x={self.x}, y={self.y}, "
    #         f"width={self.width}, height={self.height})"
    #     )