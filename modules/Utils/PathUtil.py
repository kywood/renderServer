




class PathUtil:

    @staticmethod
    def Path(*paths: str, trailing_slash: bool = True) -> str:
        """
        S3/MinIO object key prefix 생성용

        - OS 독립
        - 중복 '/' 제거
        - 항상 POSIX 경로
        - trailing '/' 선택 가능 (폴더 prefix용)
        """
        from pathlib import PurePosixPath

        # 각 path 조각을 '/' 기준으로 분해 후 정규화
        parts = []
        for p in paths:
            if not p:
                continue
            # 윈도우/혼합 슬래시 대응
            p = p.replace("\\", "/")
            # print(p)
            parts.extend(x for x in p.split("/") if x)
            # print(parts)

        path = PurePosixPath(*parts)
        result = str(path)

        if trailing_slash and result and not result.endswith("/"):
            result += "/"

        return result

    @staticmethod
    def Dir(*paths: str) -> str:
        return PathUtil.Path(*paths, trailing_slash=True)

    @staticmethod
    def File(*paths: str) -> str:
        return PathUtil.Path(*paths, trailing_slash=False)


#
#
# def main():
#     pa = PathUtil.Path("tr/cc" , "ab","cd")
#
#     print(pa)
#
#     pass
#
#
# if __name__ == '__main__':
#     main()