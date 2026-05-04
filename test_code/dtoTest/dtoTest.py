from modules.models.ModelDTO import ModelDTO


class dtoTest(ModelDTO):

    r:str
    g:str
    b:str

    @classmethod
    def Create1(cls , r:str , g:str , b:str):
        return dtoTest(
            r=r,
            g=g,
            b=b
        )


    pass

def main():
    cc= dtoTest.Create1(

        r="r",
        g="g",
        b="b",
    )


    print(cc.r)
    print(cc.g)
    print(cc.b)

    pass

if __name__ == '__main__':
    main()