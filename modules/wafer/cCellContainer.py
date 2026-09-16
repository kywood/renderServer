from modules.wafer import cCell


class CellContainer:


    def __init__(self):

        self._container = {}

        pass

    def append(self , cell : cCell):
        self._container[cell.id] = cell

    def get(self,cell : cCell):
        return self._container[cell.id]



