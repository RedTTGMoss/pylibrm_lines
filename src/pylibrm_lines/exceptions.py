from pylibrm_lines.lib import get_error_message


class LibMissing(Exception):
    def __init__(self):
        super().__init__("LIB rm_lines was not loaded properly")


class FailedToBuildTree(Exception):
    def __init__(self):
        super().__init__(
            "A major issue occurred reading the LINES file and building the scene tree"
        )


class FailedToMakeRenderer(Exception):
    def __init__(self):
        super().__init__(
            "Failed to make renderer from scene tree. PLEASE REPORT THE FAULTING LINES FILE!"
        )


class FailedToConvertToJson(Exception):
    def __init__(self):
        super().__init__("An issue occurred while converting scene tree to json")


class FailedToConvertToMd(Exception):
    def __init__(self):
        super().__init__("An issue occurred while rendering to md")


class FailedToConvertToTxt(Exception):
    def __init__(self):
        super().__init__("An issue occurred while rendering to txt")


class NoSceneInfo(Exception):
    def __init__(self):
        super().__init__("The scene tree has no scene info.")


class GenericError(Exception):  # Librm_lines hook
    def __init__(self):
        err_msg = get_error_message()
        super().__init__(f"{self.__class__.__name__}: {err_msg}")


class TreeInstability(GenericError): ...


EXCEPTIONS_LIBRM_LINES = {-1: FailedToMakeRenderer, -2: TreeInstability}
