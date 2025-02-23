# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import bcrypt
from passlib.context import CryptContext

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    sex = Column(String)
    qualification = Column(String)
    email = Column(String, unique=True, index=True, nullable=True)  # Add email for potential teacher login
    password = Column(String, nullable=True)  # Add password for potential teacher login
    is_active = Column(Boolean, default=True)
    
    students = relationship("Student", back_populates="teacher")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using passlib"""
        return pwd_context.hash(password)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    sex = Column(String)
    email = Column(String, unique=True, index=True)
    level = Column(String)
    vocabulary = Column(Integer)
    password = Column(String)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    is_active = Column(Boolean, default=True)

    teacher = relationship("Teacher", back_populates="students")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using passlib"""
        return pwd_context.hash(password)

class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using passlib"""
        return pwd_context.hash(password)