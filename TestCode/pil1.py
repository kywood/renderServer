from Render.renderer import GPURenderer, Colors

# 1) 렌더러 생성 (GPU 자동 감지)
renderer = GPURenderer(width=800, height=600)

# 2) 캔버스 열고 그리기
renderer.begin()
renderer.clear(Colors.BLACK)

renderer.circle(400, 300, 100, fill=Colors.BLUE)

# 3) 결과 꺼내기
image = renderer.finish()        # PIL Image
image.save("output.png")
renderer.release()