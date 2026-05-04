import sys

from common_lib.Utils.Singleton import SingletonBase


class BasePath(SingletonBase):


    def __init__(self , relative_path: str = None ):
        super().__init__()
        from pathlib import Path

        entry = sys.argv[0]
        base_path = Path(entry).resolve().parent

        if relative_path:
            base_path = (base_path / relative_path).resolve()

        self._basePath = base_path

        # self._basePath = path(__file__).resolve().parents[0]
        pass

    def GetBasePath(self):
        return self._basePath

    # def GetBasePath(self,up: int = 0):
    #     if up <= 0:
    #         return self._basePath
    #
    #     cur = self._basePath
    #     for _ in range(up):
    #         parent = cur.parent
    #         if parent == cur:
    #             break
    #         cur = parent
    #     return cur

    def SetUp(self, n: int = 1):
        """
        basePath = basePath.parents[n-1]
        """
        cur = self._basePath
        for _ in range(n):
            parent = cur.parent
            if parent == cur:
                break
            cur = parent

        self._basePath = cur
        return self._basePath

    def SetBasePath(self, path):
        from pathlib import Path
        self._basePath = Path(path).expanduser().resolve()
        return self._basePath

    def Path(self ,*paths: str, trailing_slash = False ):
        new_paths = (self._basePath.as_posix(), *paths)
        from common_lib.Utils.PathUtil import PathUtil
        return PathUtil.Path(*new_paths,
                             trailing_slash=trailing_slash)

    def Dir(self ,*paths: str ):
        new_paths = (self._basePath.as_posix(), *paths)
        from common_lib.Utils.PathUtil import PathUtil
        return PathUtil.Dir(*new_paths)

    def File(self ,*paths: str ):
        new_paths = (self._basePath.as_posix(), *paths)
        from common_lib.Utils.PathUtil import PathUtil
        return PathUtil.File(*new_paths)
#

# #
# #
# if __name__ == '__main__':
#     pa=BasePath.instance("../../").GetBasePath()
#
#     print(pa)
#
#     d= BasePath.instance().Dir("a","bb","aa")
#
#     print(d)
#
#     d = BasePath.instance().File("a", "bb", "aa","a.mov")
#     print(d)
#


