from sqlalchemy import Column, Integer, String

from db import Base

# model/table
class  Friend(Base):
    __tablename__ = "friend"

    # fields
    id = Column(Integer,primary_key=True, index=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    age = Column(Integer)