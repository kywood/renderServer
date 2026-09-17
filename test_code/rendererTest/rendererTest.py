from modules.render.cCanvas import cCanvas
from modules.render.cColor import Colors
from modules.render.cRenderer import cRenderer
from modules.render.cSize import cSize


def main():
    canvas = cCanvas(
        size = cSize(800,600)
    )

    try:
        canvas.begin(bg_color=Colors.WHITE)
        renderer = cRenderer(canvas)
        renderer.circle(400, 300, 100, fill=Colors.BLUE)


        image = canvas.finish()
    finally:
        canvas.release()
    image.save("test.png")
    pass


if __name__ == '__main__':
    main()