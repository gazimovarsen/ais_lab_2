import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import models
import uuid
from datetime import timedelta
from auth import create_access_token


@pytest.fixture(scope="module")
def engine():
    return create_engine("postgresql://postgres:123456@localhost:5432/english_gang")


@pytest.fixture(scope="function")
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    Base.metadata.create_all(bind=connection)

    yield session

    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def create_test_manager(db):
    manager_email = f"admin_{uuid.uuid4().hex}@example.com"
    manager = models.Manager(
        email=manager_email,
        password=models.Manager.hash_password("admin123"),
        is_superuser=True,
        is_active=True,
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)

    access_token = create_access_token(
        data={"sub": manager.email, "role": "manager", "user_id": manager.id},
        expires_delta=timedelta(minutes=30),
    )

    return {"manager": manager, "access_token": access_token}


def test_protected_endpoint(client, db):
    # Создаем тестового менеджера
    manager_data = create_test_manager(db)

    # Пробуем получить доступ без токена
    response = client.get("/api/me")  # Обновленный URL
    assert response.status_code == 401

    # Пробуем получить доступ с токеном
    headers = {"Authorization": f"Bearer {manager_data['access_token']}"}
    response = client.get("/api/me", headers=headers)  # Обновленный URL
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "manager"


def test_role_based_access(client, db):
    # Создаем менеджера
    manager_data = create_test_manager(db)
    manager_headers = {"Authorization": f"Bearer {manager_data['access_token']}"}

    # Создаем учителя
    teacher_data = {
        "first_name": "Test",
        "last_name": "Teacher",
        "age": 30,
        "sex": "M",
        "qualification": "B2",
        "email": f"teacher_{uuid.uuid4().hex}@example.com",
        "password": "teacher123",
    }
    teacher_response = client.post(
        "/api/teachers/", json=teacher_data, headers=manager_headers  # Обновленный URL
    )
    assert teacher_response.status_code == 200
    teacher_id = teacher_response.json()["id"]

    # Создаем студента
    student_data = {
        "first_name": "Test",
        "last_name": "Student",
        "age": 20,
        "sex": "M",
        "email": f"student_{uuid.uuid4().hex}@example.com",
        "level": "B1",
        "vocabulary": 2000,
        "teacher_id": teacher_id,
        "password": "student123",
    }

    # Создаем студента через API менеджера
    student_response = client.post(
        "/api/students/", json=student_data, headers=manager_headers  # Обновленный URL
    )
    assert student_response.status_code == 200

    # Получаем токен для студента
    student_token_response = client.post(
        "/api/token",
        data={
            "username": student_data["email"],
            "password": "student123",
        },  # Обновленный URL
    )
    assert student_token_response.status_code == 200
    student_token = student_token_response.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Проверяем что студент не может удалить учителя
    delete_response = client.delete(
        f"/api/teachers/{teacher_id}", headers=student_headers
    )  # Обновленный URL
    assert delete_response.status_code == 403
