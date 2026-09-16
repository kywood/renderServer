




class cWaferRenderer:


    def __init__(self, renderer):
        self._renderer = renderer

    def draw(self, wafer):
        # 외곽 경로 생성 — 배경, 클리핑, 테두리에 공통 사용
        path = self._create_wafer_path(wafer)

        self._draw_background(wafer, path)

        self._renderer.save()
        try:
            # 클리핑을 먼저 설정해야 이후 그림이 밖으로 안 나감
            self._apply_clip(path)

            self._draw_grid(wafer)
            self._draw_arrows(wafer)
        finally:
            self._renderer.restore()

        # 테두리는 마지막에 그려 선명하게 표시
        self._draw_outline(wafer, path)

    def _create_wafer_path(self, wafer):
        # 원 또는 노치가 포함된 skia.Path 생성
        pass

    def _draw_background(self, wafer, path):
        # 웨이퍼 내부 색 채우기
        pass

    def _apply_clip(self, path):
        self._renderer._canvas.clipPath(
            path,
            doAntiAlias=True,
        )

    def _draw_grid(self, wafer):
        # wafer의 셀 좌표를 이용해 그리드 그리기
        pass

    def _draw_arrows(self, wafer):
        # 셀의 top / left / right / bottom 화살표 그리기
        pass

    def _draw_outline(self, wafer, path):
        # 웨이퍼 외곽 테두리 그리기
        pass

    pass


