from enum import Enum, auto 

class AddChannelResult(Enum):
    SUCCESS = auto()             
    RELATION_EXISTS = auto()     
    USER_NOT_FOUND = auto()      
    CHANNEL_NOT_FOUND = auto()  
    OTHER_ERROR = auto()   