from modules.collections.ICollection import ICollection


class cList(ICollection):

    def __init__(self):
        super().__init__()

        self._items=[]

    def Put(self, value):
        self._items.append(value)

    def __iter__(self):
        return iter(self._items)