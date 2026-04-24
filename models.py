import uuid
from sqlalchemy import Column, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String)
    profile_picture = Column(String, nullable=True)
