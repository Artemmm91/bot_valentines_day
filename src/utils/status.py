EMPTY = ""


class Declaration:
    @staticmethod
    def get_base_name():
        return "DCL"

    WAIT_FOR_NAME = "WFN"
    WAIT_FOR_TEXT = "WFT"
    WAIT_FOR_CONFIRM = "WFC"

    @staticmethod
    def get_info_status(status):
        return Declaration.get_base_name() + status

