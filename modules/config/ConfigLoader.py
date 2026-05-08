import os
import configparser
from typing import Optional
from modules.Utils.Singleton import SingletonBase


class ConfigLoader(SingletonBase):
    def __init__(self, path: str = "config.ini"):
        super().__init__()


        self.path = path
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
