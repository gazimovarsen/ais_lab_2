# schemas.py
from pydantic import BaseModel
from typing import Optional, List

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    sex: str
    email: str
    level: str
    vocabulary: int
    teacher_id: int

class StudentCreate(StudentBase):
    password: str

class Student(StudentBase):
    id: int

    class Config:
        from_attributes = True

class TeacherBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    sex: str
    qualification: str

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int
    students: List[Student] = []

    class Config:
        from_attributes = True

class ManagerBase(BaseModel):
    email: str

class ManagerCreate(ManagerBase):
    password: str

class Manager(ManagerBase):
    id: int

    class Config:
        from_attributes = True