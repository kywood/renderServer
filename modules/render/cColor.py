import skia


class cColor:

    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


    def to_skia(self) -> int:
        return skia.Color(self.r, self.g, self.b, self.a)

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        h = hex_str.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) if len(h) == 8 else 255
        return cls(r, g, b, a)

    pass



class Colors:
    WHITE = cColor(255, 255, 255)
    BLACK = cColor(0, 0, 0)
    RED = cColor(234, 67, 53)
    GREEN = cColor(52, 168, 83)
    BLUE = cColor(66, 133, 244)
    YELLOW = cColor(251, 188, 4)
    PURPLE = cColor(168, 80, 222)
    CYAN = cColor(0, 188, 212)
    ORANGE = cColor(255, 109, 0)
    TRANSPARENT = cColor(0, 0, 0, 0)