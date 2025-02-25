# routers/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from datetime import timedelta
from typing import Dict, Any

from auth import (
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["user"].email,
            "role": user["role"],
            "user_id": user["user"].id,
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.Student)
async def register_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
):
    # Check if email already exists
    existing = (
        db.query(models.Student).filter(models.Student.email == student.email).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = models.Student.hash_password(student.password)

    # Create new student with default values
    student_data = student.model_dump(exclude={"password"})
    student_data["vocabulary"] = 0
    student_data["teacher_id"] = 1  # Could change to teacher selection logic

    db_student = models.Student(**student_data, password=hashed_password)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student

@router.get("/me", response_model=schemas.UserInfo)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    user = current_user["user"]
    role = current_user["role"]

    user_info = {
        "id": user.id,
        "email": user.email,
        "role": role,
        "is_active": user.is_active,
        "additional_info": {},
    }

    if role == "student":
        user_info["additional_info"].update(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "level": user.level,
                "vocabulary": user.vocabulary,
                "teacher_id": user.teacher_id,
            }
        )
    elif role == "manager":
        user_info["additional_info"].update({"is_superuser": user.is_superuser})
    elif role == "teacher":
        user_info["additional_info"].update(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "qualification": user.qualification,
            }
        )

    return user_info