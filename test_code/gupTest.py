from modules.render.renderer import GPURenderer


def main():



    renderer = GPURenderer(
        width=1024,
        height=1024,
        use_gpu=True,
    )

    renderer.begin()
    print(renderer.gpu_info)

    pass

if __name__ == '__main__':
    main()