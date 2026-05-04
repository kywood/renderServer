import ctypes
from enum import Enum

from pydantic import PrivateAttr

from modules.models.model.ModelBase import ModelBase
from test_code.renderInfoModelTest.renderInfoModelTest import GLQuery


class E_RENDER_TYPE(str , Enum):
    GPU = "GPU"
    CPU = "CPU"



class RenderingHwInfo(ModelBase):
    render_type : E_RENDER_TYPE = E_RENDER_TYPE.CPU
    vendor: str = ""
    device_name: str = ""
    gl_version: str = ""
    max_texture_size: int = 0


    _gl: object = PrivateAttr(default=None)

    @property
    def is_gpu(self) -> bool:
        return self.render_type == E_RENDER_TYPE.GPU

    @property
    def summary(self) -> str:
        if self.is_gpu:
            return f"[GPU] {self.device_name} ({self.vendor}, GL {self.gl_version})"
        return "[CPU] Software Rendering"

    @classmethod
    def create(cls, gl_query: GLQuery = None) -> "RenderingHwInfo":
        """GLQuery만 넘기면 끝. None이면 CPU."""
        if gl_query is None:
            return cls(render_type=E_RENDER_TYPE.CPU)

        return cls(
            render_type=E_RENDER_TYPE.GPU,
            vendor=gl_query.vendor,
            device_name=gl_query.device_name,
            gl_version=gl_query.gl_version,
            max_texture_size=gl_query.max_texture_size,
        )

    #
    # @classmethod
    # def create(cls, gl) -> "RenderingHwInfo":
    #     """gl만 넘기면 끝. None이면 CPU."""
    #     if gl is None:
    #         return cls(backend=E_RENDER_TYPE.CPU)
    #
    #     gl.glGetString.restype = ctypes.c_char_p
    #
    #     def _get(enum):
    #         result = gl.glGetString(enum)
    #         return result.decode("utf-8", errors="replace") if result else "Unknown"
    #
    #     val = ctypes.c_int()
    #     gl.glGetIntegerv(0x0D33, ctypes.byref(val))
    #
    #     info = cls(
    #         backend=E_RENDER_TYPE.GPU,
    #         vendor=_get(0x1F00),
    #         device_name=_get(0x1F01),
    #         gl_version=_get(0x1F02),
    #         max_texture_size=val.value,
    #     )
    #     info._gl = gl
    #     return info

    def release(self):
        self._gl = None