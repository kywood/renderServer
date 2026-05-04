# from render import renderer
from modules.render import GPURenderer, Colors

renderer = GPURenderer(width=800, height=600)

renderer.begin()
renderer.clear(Colors.BLACK)

# ── 원 ──────────────────────────────────────
renderer.circle(200, 200, 80, fill=Colors.BLUE)                    # 채우기
renderer.circle(400, 200, 60, stroke=Colors.RED, stroke_width=3)   # 테두리만
renderer.circle(600, 200, 50, fill=Colors.GREEN, stroke=Colors.WHITE)  # 둘 다

# ── 선 ──────────────────────────────────────
renderer.line(50, 350, 750, 350, color=Colors.WHITE, width=2)
renderer.line(50, 380, 750, 380, color=Colors.CYAN, dashed=True)   # 점선

# ── 화살표 ──────────────────────────────────
renderer.arrow(100, 450, 400, 450, color=Colors.GREEN, head_size=20, line_width=3)

# ── 사각형 ──────────────────────────────────
renderer.rect(500, 100, 200, 120, fill=Colors.YELLOW)                         # 일반
renderer.rect(500, 250, 200, 120, fill=Colors.PURPLE, corner_radius=16)       # 둥근

# ── 호 ──────────────────────────────────────
renderer.arc(300, 500, radius_x=80, start_angle=0, sweep_angle=270, color=Colors.CYAN)

# ── 다각형 (path) ──────────────────────────
renderer.path([(100,550), (200,480), (300,550)], closed=True, fill=Colors.ORANGE)

# ── 텍스트 ──────────────────────────────────
renderer.text("Hello GPU!", 300, 580, size=28, color=Colors.WHITE, bold=True, align="center")

image = renderer.finish()
renderer.release()
image.save("all_shapes.png")