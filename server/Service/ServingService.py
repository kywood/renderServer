from Config.ConfigLoader import ConfigLoader
from Service.Service import IService
from fastapi import UploadFile, File, Request, HTTPException

class ServingService(IService):

    def __init__(self , config : ConfigLoader):
        super().__init__()
        self._config = config
        pass

    async def infer(self,file: UploadFile = File(...)):
        import tempfile
        import os
        import time

        from Inference.InferenceManager import InferenceManager

        # 1) 업로드 파일을 임시 파일로 저장
        suffix = os.path.splitext(file.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            # 2) 추론 실행
            mgr = InferenceManager.instance()

            t0 = time.time()
            results = mgr.infer(tmp_path)
            elapsed_ms = (time.time() - t0) * 1000.0

            # 3) 결과 파싱 (YOLO 결과 → JSON)
            r = results[0]
            detections = []
            boxes = r.boxes

            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i])
                detections.append({
                    "class_id": cls_id,
                    "class_name": r.names.get(cls_id, str(cls_id)),
                    "confidence": float(boxes.conf[i]),
                    "bbox": list(map(float, boxes.xyxy[i])),  # [x1,y1,x2,y2]
                })

            from Models.RestModel import InferResponse
            return InferResponse(
                filename=file.filename,
                elapsed_ms=elapsed_ms,
                count=len(detections),
                detections=detections
            )


        finally:
            # 임시파일 삭제
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    pass

    async def infer_vis(self,file: UploadFile = File(...)):
        import tempfile
        import os
        import time
        import cv2
        from fastapi.responses import Response

        from Inference.InferenceManager import InferenceManager

        suffix = os.path.splitext(file.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            mgr = InferenceManager.instance()

            t0 = time.time()
            results = mgr.infer(tmp_path)
            elapsed_ms = (time.time() - t0) * 1000.0

            r = results[0]

            # ✅ 박스가 그려진 이미지(Numpy array, 보통 BGR) 얻기
            annotated = r.plot()  # shape: (H,W,3)

            # ✅ JPEG로 인코딩
            ok, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            if not ok:
                return Response(content=b"failed to encode image", status_code=500)

            # (선택) 성능/시간 헤더로 전달
            headers = {"X-Elapsed-Ms": f"{elapsed_ms:.2f}"}

            return Response(content=buf.tobytes(), media_type="image/jpeg", headers=headers)

        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        pass