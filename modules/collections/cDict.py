from modules.collections.ICollection import ICollection


class cDict(ICollection):
    def __init__(self, datas: dict = None):
        super().__init__()

        self._items={}

        if datas:
            self.Register(datas)

    def IsContainKey(self, key):
        return key in self._items

    def Put(self, key, value):
        self._items[key] = value

    def Get(self, key):
        return self._items.get(key)

    def Register(self, datas: dict):
        self._items.update(datas)

    def __iter__(self):
        return iter(self._items)

    def __setitem__(self, key, value):
        self._items[key] = value

    def __getitem__(self, key):
        return self._items[key]