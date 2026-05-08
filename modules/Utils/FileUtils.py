from pathlib import Path

class FileUtils:

    @staticmethod
    def CheckDirAndMake( path ):
        targetPath = Path( path )
        targetPath.mkdir(parents=True, exist_ok=True)
        return targetPath
