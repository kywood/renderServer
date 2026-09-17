




class cPoint:

    def __init__(self , x:int , y:int):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y



    def __eq__(self, other):
        if not isinstance(other, cPoint):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __hash__(self):
        return hash((self._x, self._y))

#
#
# def main():
#
#     di = {}
#
#     di[cPoint(0,0)] = '0-0'
#     di[cPoint(0,1)] = '0-1'
#     di[cPoint(0,2)] = '0-2'
#
#
#     for k , v in di.items():
#         print(k)
#         print(v)
#
#     di[cPoint(0,2)] = '0-2-0-2'
#
#     print("========================================")
#
#     for k , v in di.items():
#         print(k)
#         print(v)
#
#     pass
#
# if __name__ == '__main__':
#     main()