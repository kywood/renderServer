"""
RenderingHwInfo 테스트

GPU가 있으면 GPU 정보 출력, 없으면 CPU 폴백 확인.
"""

import ctypes
import sys


# ── GLQuery (GL 정보 조회 래퍼) ──────────────────────────────────────

class GLQuery:
    GL_VENDOR = 0x1F00
    GL_RENDERER = 0x1F01
    GL_VERSION = 0x1F02
    GL_MAX_TEXTURE_SIZE = 0x0D33

    def __init__(self):
        if sys.platform == "win32":
            self._gl = ctypes.cdll.LoadLibrary("opengl32.dll")
        else:
            self._gl = ctypes.cdll.LoadLibrary("libGL.so.1")
        self._gl.glGetString.restype = ctypes.c_char_p

    def get_string(self, enum: int) -> str:
        result = self._gl.glGetString(enum)
        return result.decode("utf-8", errors="replace") if result else "Unknown"

    def get_int(self, enum: int) -> int:
        val = ctypes.c_int()
        self._gl.glGetIntegerv(enum, ctypes.byref(val))
        return val.value

    @property
    def vendor(self) -> str:
        return self.get_string(self.GL_VENDOR)

    @property
    def device_name(self) -> str:
        return self.get_string(self.GL_RENDERER)

    @property
    def gl_version(self) -> str:
        return self.get_string(self.GL_VERSION)

    @property
    def max_texture_size(self) -> int:
        return self.get_int(self.GL_MAX_TEXTURE_SIZE)


# ── GL Context 생성 (GLQuery 사용 전에 필요) ─────────────────────────

def create_gl_context():
    """GLFW로 GL context 생성. 없으면 None."""
    try:
        import glfw
        if not glfw.init():
            return None
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(1, 1, "", None, None)
        if not window:
            glfw.terminate()
            return None
        glfw.make_context_current(window)
        print("[OK] GLFW GL context 생성 완료")
        return window
    except ImportError:
        print("[SKIP] glfw 미설치")
        return None
    except Exception as e:
        print(f"[FAIL] GLFW 실패: {e}")
        return None


# ── 테스트 ───────────────────────────────────────────────────────────

def test_gpu_info():
    """GPU 정보 조회 테스트"""
    print("=" * 60)
    print("RenderingHwInfo 테스트")
    print("=" * 60)

    # 1) GL context 생성
    print("\n[1] GL Context 생성")
    window = create_gl_context()

    if window:
        # 2) GLQuery로 GPU 정보 조회
        print("\n[2] GPU 정보 조회")
        gl = GLQuery()
        print(f"  Vendor       : {gl.vendor}")
        print(f"  Device       : {gl.device_name}")
        print(f"  GL Version   : {gl.gl_version}")
        print(f"  Max Texture  : {gl.max_texture_size}px")

        # 3) RenderingHwInfo 생성 (GPU)
        print("\n[3] RenderingHwInfo.create(gl)")
        from modules.render.RenderingHwInfo import RenderingHwInfo
        hw = RenderingHwInfo.create(gl)
        print(f"  render_type  : {hw.render_type}")
        print(f"  is_gpu       : {hw.is_gpu}")
        print(f"  summary      : {hw.summary}")

        # 4) 직렬화 테스트
        print("\n[4] 직렬화")
        print(f"  to_dict()    : {hw.to_dict()}")
        print(f"  to_json()    :")
        print(hw.to_json())

        # 정리
        import glfw
        glfw.terminate()

    else:
        print("\n[2] GPU 없음 — CPU 폴백 테스트")
        from modules.render.RenderingHwInfo import RenderingHwInfo
        hw = RenderingHwInfo.create(None)
        print(f"  render_type  : {hw.render_type}")
        print(f"  is_gpu       : {hw.is_gpu}")
        print(f"  summary      : {hw.summary}")
        print(f"  to_dict()    : {hw.to_dict()}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


def test_cpu_fallback():
    """CPU 폴백 강제 테스트"""
    print("\n[강제 CPU 테스트]")
    from modules.render.RenderingHwInfo import RenderingHwInfo
    hw = RenderingHwInfo.create(None)
    print(f"  render_type  : {hw.render_type}")
    print(f"  is_gpu       : {hw.is_gpu}")
    print(f"  summary      : {hw.summary}")
    print(f"  vendor       : '{hw.vendor}'")
    print(f"  device_name  : '{hw.device_name}'")
    assert hw.is_gpu == False
    assert hw.render_type.value == "CPU"
    print("  [PASS] CPU 폴백 정상")


if __name__ == "__main__":
    test_gpu_info()
    test_cpu_fallback()