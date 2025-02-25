# test_crud.py
import pytest
import time
import uuid
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
import models


@pytest.fixture(scope="module")
def engine():
    return create_engine("postgresql://postgres:qwerty@localhost:5432/english_gang")


@pytest.fixture(scope="function")
def db(engine):
    # Start transaction
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    # Create tables
    Base.metadata.create_all(bind=connection)

    yield session

    # Rollback transaction
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


@pytest.fixture(scope="function")
def manager_token(client, db):
    # Создаем уникальный email для каждого теста
    manager_email = f"admin_{uuid.uuid4().hex}@example.com"

    # Создаем менеджера
    manager = models.Manager(
        email=manager_email,
        password=models.Manager.hash_password("admin123"),
        is_superuser=True,
        is_active=True,
    )
    db.add(manager)
    db.commit()

    # Получаем токен - обратите внимание на обновленный URL с /api/ префиксом
    response = client.post(
        "/api/token", data={"username": manager_email, "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(manager_token):
    return {"Authorization": f"Bearer {manager_token}"}


def create_sample_teacher(client, auth_headers):
    return client.post(
        "/api/teachers/",  # Обновленный URL с /api/ префиксом
        json={
            "first_name": "John",
            "last_name": "Doe",
            "age": 35,
            "sex": "M",
            "qualification": "C2",
            "email": f"teacher_{uuid.uuid4().hex}@example.com",  # Уникальный email для учителя
        },
        headers=auth_headers,
    )


def test_create_teacher(client, auth_headers):
    response = create_sample_teacher(client, auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"


def test_read_teachers(client, auth_headers):
    response = client.get("/api/teachers/", headers=auth_headers)  # Обновленный URL
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_teacher(client, auth_headers):
    teacher = create_sample_teacher(client, auth_headers).json()
    response = client.put(
        f"/api/teachers/{teacher['id']}",  # Обновленный URL
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "age": 40,
            "sex": "F",
            "qualification": "C1",
            "email": f"teacher_updated_{uuid.uuid4().hex}@example.com",  # Уникальный email для обновления
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"


def test_delete_teacher(client, auth_headers):
    teacher = create_sample_teacher(client, auth_headers).json()
    response = client.delete(
        f"/api/teachers/{teacher['id']}", headers=auth_headers
    )  # Обновленный URL
    assert response.status_code == 200


def create_sample_student(client, auth_headers):
    # Generate unique email
    email = f"student_{uuid.uuid4().hex}@mail.com"

    # First create a teacher
    teacher = client.post(
        "/api/teachers/",  # Обновленный URL
        json={
            "first_name": "John",
            "last_name": "Doe",
            "age": 35,
            "sex": "M",
            "qualification": "C2",
            "email": f"teacher_{uuid.uuid4().hex}@example.com",  # Уникальный email для учителя
        },
        headers=auth_headers,
    ).json()

    return client.post(
        "/api/students/",  # Обновленный URL
        json={
            "first_name": "Alex",
            "last_name": "Petrov",
            "age": 17,
            "sex": "M",
            "email": email,
            "level": "B2",
            "vocabulary": 3000,
            "teacher_id": teacher["id"],
            "password": "alexbest2025",
        },
        headers=auth_headers,
    )


def test_create_student(client, auth_headers):
    response = create_sample_student(client, auth_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Alex"


def test_read_students(client, auth_headers):
    response = client.get("/api/students/", headers=auth_headers)  # Обновленный URL
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_student(client, auth_headers):
    student = create_sample_student(client, auth_headers).json()
    response = client.put(
        f"/api/students/{student['id']}",  # Обновленный URL
        json={
            "first_name": "Alex",
            "last_name": "Petrov",
            "age": 17,
            "sex": "M",
            "email": f"student_updated_{uuid.uuid4().hex}@mail.com",  # Уникальный email для обновления
            "level": "A2",
            "vocabulary": 3000,
            "teacher_id": student["teacher_id"],
            "password": "alexbest2025",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["level"] == "A2"


def test_delete_student(client, auth_headers):
    create_response = create_sample_student(client, auth_headers)
    assert create_response.status_code == 200
    student = create_response.json()

    delete_response = client.delete(
        f"/api/students/{student['id']}", headers=auth_headers
    )  # Обновленный URL
    assert delete_response.status_code == 200

    verify_response = client.get(
        f"/api/students/{student['id']}", headers=auth_headers
    )  # Обновленный URL
    assert verify_response.status_code == 404
