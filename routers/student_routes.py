# routers/student_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import List

from auth import (
    get_current_user,
    get_current_manager,
    get_current_student,
    get_current_teacher,
)

router = APIRouter(tags=["students"])

# Student CRUD operations
@router.post("/students/", response_model=schemas.Student)
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

@router.get("/students/", response_model=List[schemas.Student])
def read_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # If user is a teacher, show only their students
    if current_user["role"] == "teacher":
        return (
            db.query(models.Student)
            .filter(models.Student.teacher_id == current_user["user"].id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    # If manager - show all
    elif current_user["role"] == "manager":
        return db.query(models.Student).offset(skip).limit(limit).all()
    # If student - show only them
    else:
        return [current_user["user"]]

@router.get("/students/{student_id}", response_model=schemas.Student)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check access permissions
    if current_user["role"] == "student" and current_user["user"].id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if (
        current_user["role"] == "teacher"
        and student.teacher_id != current_user["user"].id
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return student

@router.put("/students/{student_id}", response_model=schemas.Student)
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

@router.delete("/students/{student_id}")
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