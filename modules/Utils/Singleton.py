import threading
from typing import Any, Dict


class SingletonBase:
    _instances: Dict[type, Any] = {}
    _lock = threading.Lock()
    _creating = set()   # 🔥 현재 instance()를 통해 생성 중인 클래스

    def __init__(self):
        # 🔥 공통 안전장치: 직접 생성 차단
        cls = self.__class__
        if cls not in SingletonBase._creating:
            raise RuntimeError(
                f"{cls.__name__} must be created via "
                f"{cls.__name__}.instance(...)"
            )

    @classmethod
    def instance(cls, *args, **kwargs):
        inst = cls._instances.get(cls)
        if inst is not None:
            if args or kwargs:
                raise ValueError(
                    f"{cls.__name__} singleton already created; "
                    f"don't pass args/kwargs again."
                )
            return inst

        with cls._lock:
            inst = cls._instances.get(cls)
            if inst is None:
                cls._creating.add(cls)     # ✅ “정식 경로” 표시
                try:
                    inst = cls(*args, **kwargs)
                    cls._instances[cls] = inst
                finally:
                    cls._creating.remove(cls)
        return inst

    def Initialize(self): pass