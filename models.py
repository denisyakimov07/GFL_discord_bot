from sqlalchemy import Sequence, ForeignKey
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime

from sqlalchemy.orm import relationship

timezone_offset = -8.0  # Pacific Standard Time (UTC−08:00)
tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))

BaseModel = declarative_base()


class DiscordUser(BaseModel):
    __tablename__ = 'discord-users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    member_name = Column(String(50))
    member_id = Column(BigInteger)
    member_nickname = Column(String(50))
    create_time = Column(DateTime, default=datetime.datetime.now(tzinfo))
    avatar_url = Column(Text)

    def __repr__(self):
        return f"{self.member_name} - {self.member_id} - {self.member_nickname}"


class OnlineTimeLog(BaseModel):
    __tablename__ = 'online-time-log'
    id = Column(Integer, Sequence('time-log_id_seq'), primary_key=True)
    member_id = Column(BigInteger)
    create_time = Column(DateTime, default=datetime.datetime.now(tzinfo))
    status = Column(Boolean)

    def __repr__(self):
        return f"{self.member_id} - {self.status}"


class OnlineStreamTimeLog(BaseModel):
    __tablename__ = 'stream-time-log'
    id = Column(Integer, Sequence('Stream-log_id_seq'), primary_key=True)
    member_id = Column(BigInteger)
    create_time = Column(DateTime, default=datetime.datetime.now(tzinfo))
    status = Column(Boolean)

    def __repr__(self):
        return f"{self.member_id} - {self.status}"


class UserVerifiedLog(BaseModel):
    __tablename__ = 'verified_users'
    id = Column(Integer, Sequence('media_post_id_seq'), primary_key=True)
    member_id = Column(BigInteger)  # User get role
    admin_id = Column(BigInteger)  # User added role
    create_time = Column(DateTime, default=datetime.datetime.now(tzinfo))

    def __repr__(self):
        return f"{self.member_id} - {self.admin_id}"