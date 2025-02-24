# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas
import json

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from auth import (
    Token,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_student,
    get_current_teacher,  
    get_current_manager,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from typing import List
from datetime import timedelta


app = FastAPI()

# Добавляем CORS middleware перед всеми маршрутами
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ЭТО ====================================
@app.get("/tests/a1")
def show_test_a1():
    with open("tests/a1.json", "r", encoding="utf-8") as f:
        data = json.load(f)
            
    return data

@app.get("/")
def home_page():
    return {
        "message": "Hello world!"
    }
# =============================================================

# Аутентификация
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),  # Добавляем зависимость для базы данных
):
    # Теперь передаем db в функцию authenticate_user
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


# User profile endpoint
@app.get("/users/me", response_model=schemas.UserInfo)
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

    return user_info


# Teacher CRUD operations
@app.post("/teachers/", response_model=schemas.Teacher)
def create_teacher(
    teacher: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    current_user: models.Manager = Depends(get_current_manager),
):
    db_teacher = models.Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@app.get("/teachers/", response_model=List[schemas.Teacher])
def read_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Только менеджеры могут видеть список всех учителей
    if current_user["role"] == "manager":
        return db.query(models.Teacher).offset(skip).limit(limit).all()
    # Студенты и учителя не могут видеть список учителей
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def read_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Менеджер может видеть любого учителя
    if current_user["role"] == "manager":
        return teacher
    # Учитель может видеть только свой профиль
    elif current_user["role"] == "teacher" and current_user["user"].id == teacher_id:
        return teacher
    # Все остальные запросы запрещены
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@app.put("/teachers/{teacher_id}", response_model=schemas.Teacher)
def update_teacher(
    teacher_id: int,
    teacher: schemas.TeacherCreate,
    db: Session = Depends(get_db),
    current_user: models.Manager = Depends(get_current_manager),
):
    db_teacher = (
        db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    )
    if db_teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")

    for key, value in teacher.model_dump().items():
        setattr(db_teacher, key, value)

    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@app.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: models.Manager = Depends(get_current_manager),
):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")

    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}


# Student CRUD operations
@app.post("/students/", response_model=schemas.Student)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.Manager = Depends(get_current_manager),
):
    # Check if email already exists
    existing = (
        db.query(models.Student).filter(models.Student.email == student.email).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = models.Student.hash_password(student.password)
    db_student = models.Student(
        **student.model_dump(exclude={"password"}), password=hashed_password
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


# Для студентов
@app.get("/students/", response_model=List[schemas.Student])
def read_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Если пользователь - учитель, показываем только его студентов
    if current_user["role"] == "teacher":
        return (
            db.query(models.Student)
            .filter(models.Student.teacher_id == current_user["user"].id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    # Если менеджер - показываем всех
    elif current_user["role"] == "manager":
        return db.query(models.Student).offset(skip).limit(limit).all()
    # Если студент - показываем только его
    else:
        return [current_user["user"]]


@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Проверяем права доступа
    if current_user["role"] == "student" and current_user["user"].id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if (
        current_user["role"] == "teacher"
        and student.teacher_id != current_user["user"].id
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return student


@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(
    student_id: int,
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Verify access permissions
    if current_user["role"] == "student" and current_user["user"].id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")

    db_student = (
        db.query(models.Student).filter(models.Student.id == student_id).first()
    )
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check if email is being changed to an existing one
    if student.email != db_student.email:
        existing = (
            db.query(models.Student)
            .filter(models.Student.email == student.email)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    update_data = student.model_dump(exclude={"password"}, exclude_unset=True)

    if student.password:
        update_data["password"] = models.Student.hash_password(student.password)

    for key, value in update_data.items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.Manager = Depends(get_current_manager),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
