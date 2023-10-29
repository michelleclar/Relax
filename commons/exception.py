class MATCH_EXCEPTION(Exception):
    """没有找到元素"""

    def __init__(self, message):
        super().__init__(message)


class CLICK_EXCEPTION(Exception):
    """点击失败"""

    def __init__(self, message):
        super().__init__(message)


class FIND_WIN_TITLE_EXCEPTION(Exception):
    """没有找到标题的window"""

    def __init__(self, message):
        super().__init__(message)


class STACK_EXCEPTION(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QUEUE_EXCEPTION(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
