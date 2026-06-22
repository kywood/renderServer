
# GPU Render Server

```commandline
 docker-compose -f deploy/gpu/docker-compose.yml up --build          
 docker-compose -f deploy/gpu/docker-compose.yml down                

```


## 성능 평가
```렌더러: Skia GPU (OpenGL/EGL)
웨이퍼: 6개 × 화살표 10,000개 = 총 60,000개

INFO:Render.renderer:GPU context 생성 성공 (GLFW)
  Wafer #1: 10,000 arrows — 102ms
  Wafer #2: 10,000 arrows — 102ms
  Wafer #3: 10,000 arrows — 101ms
  Wafer #4: 10,000 arrows — 94ms
  Wafer #5: 10,000 arrows — 92ms
  Wafer #6: 10,000 arrows — 93ms

드로잉 총: 584ms
finish() (GPU→CPU 전송 + 인코딩): 190ms
PNG 저장: 104ms

===== 총 소요: 877ms =====
렌더러: Skia GPU (OpenGL/EGL)
저장됨: wafer_map.png
INFO:Render.renderer:Renderer 리소스 해제 완료

종료 코드 0(으)로 완료된 프로세스
```