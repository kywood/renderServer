# ──────────────────────────────────────────────────────────────────────
# GPU render Server — NVIDIA Container Toolkit 기반
# 실행: docker run --gpus all -p 8000:8000 gpu-render-server
# ──────────────────────────────────────────────────────────────────────
FROM nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES=graphics,compute,utility

# EGL + OpenGL 개발 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev \
    libegl1-mesa-dev libgl1-mesa-dev libgles2-mesa-dev \
    libegl-mesa0 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Uvicorn 워커 4개 (GPU context는 각 워커별 1개)
CMD ["uvicorn", "RenderServer:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
