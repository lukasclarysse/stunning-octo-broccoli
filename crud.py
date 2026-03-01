from sqlalchemy.orm import Session
import models
from auth import hash_password
from typing import Optional, List

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str, email: Optional[str] = None):
    hashed_pw = hash_password(password)
    new_user = models.User(username=username, password=hashed_pw, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()