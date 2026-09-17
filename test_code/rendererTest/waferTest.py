from skia import Point

from modules.render.cCanvas import cCanvas
from modules.render.cColor import Colors
from modules.render.cRenderer import cRenderer
from modules.render.cSize import cSize
from modules.wafer.cWaferRenderer import cWaferRenderer


def main():
    with cCanvas(size=cSize(1280, 1900)) as canvas:
        canvas.begin(bg_color=Colors.WHITE)

        renderer = cRenderer(canvas)
        # renderer.circle(400, 300, 100, fill=Colors.BLUE)

        # renderer = cRenderer(canvas)
        wafer_renderer = cWaferRenderer(renderer)

        from modules.wafer.cWafer import cWafer
        from modules.render.cPoint import cPoint

        for row in range(5):
            for col in range(3):

                # x=220 * (col + 1)
                # y=220 * (row + 1)

                x = 220 + 420 * col
                y = 220 + 420 * row

                wafer_renderer.draw(cWafer(
                    point=cPoint(x=x, y=y),
                    radius=200,
                    grid_size=10,
                    stroke=2.0
                ))

        #
        # wafer_renderer.draw(cWafer(
        #     point=cPoint(x=220, y=220),
        #     radius=200,
        #     grid_size=10,
        #     stroke=2.0
        # ))
        #
        # wafer_renderer.draw(cWafer(
        #     point=cPoint(x=640, y=220),
        #     radius=200,
        #     grid_size=10,
        #     stroke=2.0
        # ))
        #
        # wafer_renderer.draw(cWafer(
        #     point=cPoint(x=1060, y=220),
        #     radius=200,
        #     grid_size=10,
        #     stroke=2.0
        # ))
        #
        # wafer_renderer.draw(cWafer(
        #     point=cPoint(x=220, y=640),
        #     radius=200,
        #     grid_size=10,
        #     stroke=2.0
        # ))
        #
        # wafer_renderer.draw(cWafer(
        #     point=cPoint(x=640, y=640),
        #     radius=200,
        #     grid_size=10,
        #     stroke=2.0
        # ))
        #
        #
        # wafer_renderer.draw(cWafer(
        #     point=cPoint(x=1060, y=640),
        #     radius=200,
        #     grid_size=10,
        #     stroke=2.0
        # ))




        image = canvas.finish()

    # with를 벗어나면 release() 자동 호출
    image.save("wafer_sample.png")


if __name__ == '__main__':
    main()