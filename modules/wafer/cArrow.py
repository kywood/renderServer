from glfw import set_window_aspect_ratio
from modules.render import cPoint
from modules.render.cColor import cColor
from numpy.compat import os_PathLike


class cArrow:

    def __init__(self ,
                 start_point : cPoint ,
                 end_point : cPoint ,
                 color :cColor):

        self._start_point = start_point
        self._end_point = end_point
        self._color     = color

    @property
    def start_point(self):
        return self._start_point

    @property
    def end_point(self):
        return self._end_point

    @property
    def color(self):
        return self._color



