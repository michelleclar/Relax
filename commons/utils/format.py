from enum import Enum
class DataFormat(Enum):
    ONLY_DATE = "%Y-%m-%d"
    NORMAL = "%Y.%m.%d-%H:%M:%S"
    ONLY_TIME = "%H.%M.%S"
