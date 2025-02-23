# auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas
from database import get_db

# Configuration from environment variables
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key-for-development-only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password handling
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Token schema
class Token(schemas.BaseModel):
    access_token: str
    token_type: str


class TokenData(schemas.BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None  # 'student', 'teacher', or 'manager'
    user_id: Optional[int] = None


# Password verification
def verify_password(plain_password, hashed_password):
    # Convert hashed_password to bytes if it's a string
    if isinstance(hashed_password, str):
        encoded_hash = hashed_password.encode("utf-8")
    else:
        encoded_hash = hashed_password

    # Verify the password
    plain_bytes = plain_password.encode("utf-8")
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        # Fallback to bcrypt direct comparison if passlib fails
        import bcrypt

        return bcrypt.checkpw(plain_bytes, encoded_hash)


# Authentication functions
# auth.py


def authenticate_user(email: str, password: str, db: Session):
    # Пробуем аутентифицировать как студента
    user = db.query(models.Student).filter(models.Student.email == email).first()
    if user and verify_password(password, user.password):
        return {"user": user, "role": "student"}

    # Пробуем аутентифицировать как менеджера
    user = db.query(models.Manager).filter(models.Manager.email == email).first()
    if user and verify_password(password, user.password):
        return {"user": user, "role": "manager"}

    # Добавляем аутентификацию учителя
    user = db.query(models.Teacher).filter(models.Teacher.email == email).first()
    if user and verify_password(password, user.password):
        return {"user": user, "role": "teacher"}

    # Аутентификация не удалась
    return None


# Token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: int = payload.get("user_id")
        if email is None or role is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role, user_id=user_id)
    except JWTError:
        raise credentials_exception

    if token_data.role == "student":
        user = (
            db.query(models.Student)
            .filter(models.Student.id == token_data.user_id)
            .first()
        )
    elif token_data.role == "manager":
        user = (
            db.query(models.Manager)
            .filter(models.Manager.id == token_data.user_id)
            .first()
        )
    elif token_data.role == "teacher":
        user = (
            db.query(models.Teacher)
            .filter(models.Teacher.id == token_data.user_id)
            .first()
        )
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    return {"user": user, "role": token_data.role}


# Role-based access control
def get_current_student(current_user=Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    return current_user["user"]


def get_current_manager(current_user=Depends(get_current_user)):
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    return current_user["user"]
    # main.py


def get_current_teacher(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Teacher access required"
        )
    return current_user["user"]
