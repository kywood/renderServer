
class cSize:

    def __init__(self , w , h):
        self._w = w
        self._h = h

    @property
    def w(self):
        return self._w


    @property
    def width(self):
        return self._w


    @property
    def h(self):
        return self._h

    @property
    def height(self):
        return self._h


    def __eq__(self, other):
        if not isinstance(other, cSize):
            return NotImplemented
        return self._w == other._w and self._h == other._h

    def __hash__(self):
        return hash((self._w, self._h))
