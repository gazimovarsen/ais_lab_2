# models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import bcrypt

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    sex = Column(String)
    qualification = Column(String)  # Matches schema
    
    students = relationship("Student", back_populates="teacher")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    sex = Column(String)
    email = Column(String, unique=True, index=True)
    level = Column(String)          # Matches schema
    vocabulary = Column(Integer)    # Matches schema
    password = Column(String)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    teacher = relationship("Teacher", back_populates="students")

    @staticmethod
    def hash_password(password: str) -> str:
        """Static method for password hashing"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    @staticmethod
    def hash_password(password: str) -> str:
        """Consistent hashing for managers"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')