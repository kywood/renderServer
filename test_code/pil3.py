from modules.render import GPURenderer, Colors

renderer = GPURenderer(width=800, height=600)
print(renderer.gpu_info)

renderer.begin()
renderer.clear(Colors.BLACK)


# 그림자 원
renderer.circle_with_shadow(400, 300, 80, fill=Colors.BLUE, shadow_blur=15)

# 그라디언트 사각형
renderer.gradient_rect(100, 100, 600, 200,
    colors=[Colors.BLUE, Colors.PURPLE],
    direction="horizontal",        # horizontal / vertical / diagonal
    corner_radius=12)
# 예시: 반원
renderer.arc(cx=400, cy=300, radius_x=100, start_angle=0, sweep_angle=180)

# 예시: 3/4 원
renderer.arc(cx=400, cy=300, radius_x=100, start_angle=0, sweep_angle=270)

# 예시: 타원형 호
renderer.arc(cx=400, cy=300, radius_x=150, radius_y=80, start_angle=45, sweep_angle=90)


# 3) 결과 꺼내기
image = renderer.finish()        # PIL Image
renderer.release()

image.save("pil3.png")
