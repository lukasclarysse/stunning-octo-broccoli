from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    profile_picture: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
