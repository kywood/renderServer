from abc import abstractmethod, ABC
from typing import Any


class IDelegate(ABC):

    def __init__(self , func):
        if func is None:
            raise ValueError("func must not be None")

        self._func=func
        pass


    @abstractmethod
    def Invoke(self, *args, **kwargs)->Any:
        raise NotImplementedError


class Action(IDelegate):

    def __init__(self, func):
        super().__init__(func)

    def __call__(self, *args, **kwargs) -> None:
        self.Invoke(*args, **kwargs)

    def Invoke(self , *args , **kwargs) -> None:
        self._func(*args, **kwargs)


class Func(IDelegate):

    def __init__(self, func):
        super().__init__(func)

    def __call__(self, *args, **kwargs) -> Any:
        return self.Invoke(*args, **kwargs)

    def Invoke(self, *args, **kwargs) -> Any:
        return self._func(*args, **kwargs)

#
# def sun(a,b):
#     return a+b
#
# def main():
#     a=Func( lambda a,b:a+b)
#     s= a.Invoke(a=1,b=2)
#
#
#     print(s)
#
#     lis=[]
#
#     lis.append( lambda a,b:a+b )
#
#     a=lis[0](10,20)
#
#     print(a)
#
#
#
#     pass
#
#
# if __name__ == '__main__':
#     main()
#
#
