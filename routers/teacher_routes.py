# routers/teacher_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from typing import List

from auth import (
    get_current_user,
    get_current_manager,
    get_current_teacher,
)

router = APIRouter(tags=["teachers"])

# Public API for getting teachers (no auth required)
@router.get("/teachers/public", response_model=List[schemas.Teacher])
def get_public_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get list of all teachers for public access"""
    return db.query(models.Teacher).offset(skip).limit(limit).all()

# Teacher CRUD operations
@router.post("/teachers/", response_model=schemas.Teacher)
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

@router.get("/teachers/", response_model=List[schemas.Teacher])
def read_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Any authenticated user can see the teacher list
    return db.query(models.Teacher).offset(skip).limit(limit).all()

@router.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def read_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.put("/teachers/{teacher_id}", response_model=schemas.Teacher)
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

@router.delete("/teachers/{teacher_id}")
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