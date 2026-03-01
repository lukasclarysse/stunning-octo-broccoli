from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import models, crud, auth, database, schemas
from pydantic import BaseModel

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stunning Octo Broccoli API", "status": "online"}

@app.post("/register", response_model=schemas.UserResponse)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = crud.create_user(
        db,
        username=user.username,
        password=user.password,
        email=user.email
    )

    return new_user

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login", response_model=schemas.UserResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, credentials.username)

    if not user or not auth.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user

@app.get("/getuserbyid", response_model=schemas.UserResponse)
def read_user(
    user_id: int = Query(..., description="ID of the user"),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[schemas.UserResponse])
def read_all_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users