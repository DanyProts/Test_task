from enum import Enum, auto


class ChannelAccessStatus(Enum):
    SUCCESS = auto()
    NOT_FOUND = auto()
    NOT_A_CHANNEL = auto()
    JOIN_ERROR = auto()
    PARSE_ERROR = auto()
    UNKNOWN_ERROR = auto()