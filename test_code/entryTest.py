from modules.config.ConfigLoader import ConfigLoader
# from modules.path.BasePath import testDepth


def main():


    from modules.path.BasePath import BasePath
    projectEntryPath = BasePath.instance().GetBasePath()
    configFolderPath = BasePath.instance().Dir("conf")
    configFilePath = BasePath.instance().File("conf" , "config.ini")

    print(f"projectEntryPath : {projectEntryPath}")
    print(f"configFolderPath : {configFolderPath}")
    print(f"configFilePath : {configFilePath}")

    # testDepth(configFilePath)

    #
    # configLoader = ConfigLoader.instance(configFilePath)
    # #
    # #
    # print(configLoader)
    #
    # vv = configLoader.Get("YOLO_MODEL" , "S3_PREFIX")
    #
    # print(f"vv:{vv}")


if __name__ == "__main__":
    main()

