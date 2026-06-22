import os
import configparser
from pathlib import Path
from typing import Optional
from modules.Utils.Singleton import SingletonBase


class ConfigLoader(SingletonBase):
    def __init__(self, path: str = "config.ini"):
        super().__init__()

        p = Path(path)

        # 2. 만약 리눅스 환경인데 맨 앞 슬래시가 빠진 'app/conf/...' 형태로 들어왔다면
        if os.name != 'nt' and p.as_posix().startswith("app/"):
            # 강제로 앞에 슬래시를 붙여 진짜 절대 경로(/app/...)로 복원합니다.
            self.path = os.path.abspath("/" + p.as_posix())
        else:
            # 그 외 윈도우 환경이거나 정상적인 절대 경로라면 자체 resolve() 및 absolute 처리
            self.path = os.path.abspath(p.resolve())

        self._config = configparser.ConfigParser()

        self._load()

        # self._lock = threading.Lock()

    def _load(self) :
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Config file not found: {self.path}")

        self._config.read(self.path, encoding="utf-8")
        return self

    # ----------------------------
    # Getter APIs
    # ----------------------------
    def Get(self, section: str, key: str, default: Optional[str] = None) -> str:
        if self._config.has_option(section, key):
            return self._config.get(section, key)
        if default is not None:
            return default
        raise KeyError(f"Config not found: [{section}] {key}")

    def GetInt(self, section: str, key: str, default: Optional[int] = None) -> int:
        if self._config.has_option(section, key):
            return self._config.getint(section, key)
        if default is not None:
            return default
        raise KeyError(f"Config not found: [{section}] {key}")

    def GetBool(self, section: str, key: str, default: Optional[bool] = None) -> bool:
        if self._config.has_option(section, key):
            return self._config.getboolean(section, key)
        if default is not None:
            return default
        raise KeyError(f"Config not found: [{section}] {key}")

    def Has(self, section: str, key: str) -> bool:
        return self._config.has_option(section, key)
