from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    first_name = Column(String)
    count_channel = Column(Integer, default=0)
    role = Column(String, default="client")

    channels = relationship("Channel", back_populates="user", cascade="all, delete-orphan")


class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    channel_username = Column(String, nullable=False)

    user = relationship("User", back_populates="channels")
