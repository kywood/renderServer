from modules.render import cPoint
from modules.render.cRect import cRect


class cCell:


    def __init__(self , * ,
                 wafer ,
                 id:cPoint ,
                 rect : cRect ,
                 is_in_wafer : bool ):
        self._wafer = wafer
        self._id = id
        self._rect = rect ,
        self._is_in_wafer = is_in_wafer

    def size(self):
        return self._wafer.size

    @property
    def parent_wafer(self):
        return self._wafer.parent_wafer

    @property
    def id(self):
        return self._id










