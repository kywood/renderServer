from modules.render.cPoint import cPoint


class cRect:

    def __init__(self , point : cPoint , size : cPoint):
        self._point = point
        self._size = size

    @property
    def point(self):
        return self._point

    @property
    def size(self):
        return self._size

    @property
    def x(self):
        return self._point.x

    @property
    def y(self):
        return self._point.y

    @property
    def width(self):
        return self._size.x

    @property
    def height(self):
        return self._size.y

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def center(self):
        return cPoint(
            self.x + self.width / 2,
            self.y + self.height / 2,
        )

    @property
    def top_left(self):
        return cPoint(self.left, self.top)

    @property
    def top_right(self):
        return cPoint(self.right, self.top)

    @property
    def bottom_left(self):
        return cPoint(self.left, self.bottom)

    @property
    def bottom_right(self):
        return cPoint(self.right, self.bottom)

    def __eq__(self, other):
        if not isinstance(other, cRect):
            return NotImplemented
        return (
            self._point == other._point
            and self._size == other._size
        )

    def __hash__(self):
        return hash((self._point, self._size))

    def __repr__(self):
        return (
            f"cRect(x={self.x}, y={self.y}, "
            f"width={self.width}, height={self.height})"
        )
#
#
# def main():
#     rect = cRect(cPoint(10, 20), cPoint(30, 40))
#
#     print(rect.left, rect.top)  # 10 20
#     print(rect.right, rect.bottom)  # 40 60
#     print(rect.center.x)  # 25.0
#
#     pass
#
# if __name__ == '__main__':
#     main()

