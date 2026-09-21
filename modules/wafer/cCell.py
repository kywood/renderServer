from typing import List

from modules.render.cColor import cColor
from modules.render.cPoint import cPoint
from modules.render.cRect import cRect
from modules.wafer.cArrow import cArrow


class cCell:


    def __init__(self , * ,
                 wafer ,
                 id:cPoint ,
                 rect : cRect ,
                 arrow_count : int ,
                 is_in_wafer : bool ):
        self._wafer = wafer
        self._id = id
        self._rect = rect
        self._is_in_wafer = is_in_wafer

        self._arrow_count = arrow_count

        from modules.wafer.arrowContainer import ArrowContainer
        self._arrow_container = ArrowContainer()


        self._set_arrow_lists()

    def size(self):
        return self._wafer.size

    def in_wafer(self):
        return self._is_in_wafer

    @property
    def arrow_container(self):
        return self._arrow_container

    def _get_top_rand_point(self):
         import random
         x = random.randint( int(self._rect.left), int(self._rect.left +  self._rect.width))
         y = self._rect.top

         return cPoint(x,y)

    def _get_arraw_rand_end_point(self ,
                                  start_point : cPoint ,
                                  angle_degrees: float,
                                  distance: float
                                  ):
        import math

        angle_radians = math.radians(angle_degrees)

        # 삼각함수를 이용한 끝점 계산
        end_x = start_point.x + distance * math.cos(angle_radians)
        end_y = start_point.y + distance * math.sin(angle_radians)

        return cPoint(end_x, end_y)


    def _get_arrow_rand_color(self):

        colors = [
            cColor(230, 57, 70),
            cColor(244, 162, 97),
            cColor(233, 196, 106),
            cColor(42, 157, 143),
            cColor(58, 90, 64),
            cColor(78, 168, 222),
            cColor(29, 53, 87),
            cColor(114, 9, 183),
            cColor(247, 37, 133)
        ]

        import random
        return colors[random.randint(0, len(colors) - 1)]


    def _set_arrow_lists(self ):
        import random

        if self._is_in_wafer :

            angle_degrees_st = random.randint(0, 360)
            angle_degrees_ed = random.randint(0, 360)

            angle_start = min(angle_degrees_st, angle_degrees_ed)
            angle_end = max(angle_degrees_st, angle_degrees_ed)

            for i in range(self._arrow_count):

                start_point = self._get_top_rand_point()
                angle_degrees = random.randint(angle_start, angle_end)

                distance = random.uniform(5.0, 40.0)
                self._arrow_container.append(
                    cArrow(
                        start_point = start_point ,
                        end_point=self._get_arraw_rand_end_point(start_point  ,angle_degrees ,distance),
                        color = self._get_arrow_rand_color()
                    )
                )


    @property
    def parent_wafer(self):
        return self._wafer.parent_wafer

    @property
    def id(self):
        return self._id










