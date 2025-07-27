from enum import Enum, auto
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True)
    is_active = Column(Boolean, default=False, nullable=False)
    first_name = Column(String, nullable=False)
    count_channel = Column(Integer, default=0)
    role = Column(String, default="client")
    channels = relationship(
        "Channel",
        secondary="user_channels",
        back_populates="users"
    )

class Channel(Base):
    __tablename__ = "channel_list"  
    
    channel_id = Column(Integer, primary_key=True)
    channel_name = Column(String, nullable=False)  
    users = relationship(
        "User",
        secondary="user_channels",
        back_populates="channels"
    )

class UserChannel(Base):
    __tablename__ = "user_channels"
    
    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    channel_id = Column(Integer, ForeignKey("channel_list.channel_id"), primary_key=True)

class AddChannelResult(Enum):
    SUCCESS = auto()             
    RELATION_EXISTS = auto()     
    USER_NOT_FOUND = auto()      
    CHANNEL_NOT_FOUND = auto()  
    OTHER_ERROR = auto()   