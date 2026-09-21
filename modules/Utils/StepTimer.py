import time
import logging

logger = logging.getLogger(__name__)


class StepTimer:
    """
    구간별 실행 시간(Step)을 측정하고 기록하는 타이머.

    사용 예시 1 (with 블록):
        timer = StepTimer("Wafer Render")
        with timer.step("Grid Render"):
            self._draw_grid(wafer)
        with timer.step("Arrows Batch Render"):
            self._draw_arrows(wafer)
        timer.summary()

    사용 예시 2 (함수 호출):
        timer = StepTimer("Wafer Render")
        self._draw_grid(wafer)
        timer.mark("Grid Render Done")
        self._draw_arrows(wafer)
        timer.mark("Arrows Render Done")
        timer.summary()
    """

    def __init__(self, name: str = "Total Pipeline"):
        self.name = name
        self.total_start = time.perf_counter()
        self.last_mark = self.total_start
        self.records: list[tuple[str, float]] = []

    class _StepContext:
        def __init__(self, parent, step_name: str):
            self.parent = parent
            self.step_name = step_name
            self.start_time = 0.0

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0
            self.parent.records.append((self.step_name, elapsed_ms))
            print(f"⏱️ [{self.parent.name}] {self.step_name}: {elapsed_ms:.2f} ms")
            return False

    def step(self, step_name: str):
        """with 구문과 함께 사용하는 구간 측정 메서드"""
        return self._StepContext(self, step_name)

    def mark(self, step_name: str) -> float:
        """이전 mark 시점(또는 생성 시점)부터 지금까지의 시간을 측정하여 기록"""
        now = time.perf_counter()
        elapsed_ms = (now - self.last_mark) * 1000.0
        self.last_mark = now
        self.records.append((step_name, elapsed_ms))
        print(f"⏱️ [{self.name}] {step_name}: {elapsed_ms:.2f} ms")
        return elapsed_ms

    def summary(self):
        """측정된 전체 구간 요약 출력"""
        total_ms = (time.perf_counter() - self.total_start) * 1000.0
        print(f"========================================")
        print(f"📊 [{self.name}] 전체 요약 (총 소요시간: {total_ms:.2f} ms)")
        for step_name, elapsed_ms in self.records:
            percentage = (elapsed_ms / total_ms * 100) if total_ms > 0 else 0
            print(f"  - {step_name:<25}: {elapsed_ms:>7.2f} ms ({percentage:>5.1f}%)")
        print(f"========================================")