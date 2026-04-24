from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import models, crud, auth, database, schemas
from pydantic import BaseModel
import os
import shutil

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(docs_url="/geheim-6782-docs")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    user_id: str = Query(..., description="ID of the user"),
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

@app.post("/users/{user_id}/upload-profile-picture")
def upload_profile_picture(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    upload_dir = "uploads/profile_pictures"
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = file.filename.split(".")[-1].lower()
    allowed_extensions = {"jpg", "jpeg", "png", "webp"}

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid image format")

    file_name = f"user_{user_id}.{file_extension}"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.profile_picture = f"/uploads/profile_pictures/{file_name}"
    db.commit()
    db.refresh(user)

    return {"message": "Profile picture uploaded successfully"}
