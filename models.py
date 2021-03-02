from sqlalchemy import Sequence
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base





BaseModel = declarative_base()
class DiscordUser(BaseModel):
    __tablename__ = 'discord-users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    member_name = Column(String(50))
    member_id = Column(Integer)
    member_nickname = Column(String(50))

    def __repr__(self):
        return f"{self.member_name} - {self.member_id} - {self.member_nickname} "