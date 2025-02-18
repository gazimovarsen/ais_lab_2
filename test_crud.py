# test_crud.py
import pytest
import time
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db

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

def create_sample_teacher(client):
    return client.post("/teachers/", json={
        "first_name": "John",
        "last_name": "Doe",
        "age": 35,
        "sex": "M",
        "qualification": "C2"
    })

def test_create_teacher(client):
    response = create_sample_teacher(client)
    assert response.status_code == 200
    assert response.json()["first_name"] == "John"

def test_read_teachers(client):
    response = client.get("/teachers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_teacher(client):
    teacher = create_sample_teacher(client).json()
    response = client.put(f"/teachers/{teacher['id']}", json={
        "first_name": "Jane",
        "last_name": "Smith",
        "age": 40,
        "sex": "F",
        "qualification": "C1"
    })
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"

def test_delete_teacher(client):
    teacher = create_sample_teacher(client).json()
    response = client.delete(f"/teachers/{teacher['id']}")
    assert response.status_code == 200

# test_crud.py
import uuid

def create_sample_student(client):
    # Generate unique email
    email = f"student_{uuid.uuid4().hex}@mail.com"
    
    # First create a teacher
    teacher = client.post("/teachers/", json={
        "first_name": "John",
        "last_name": "Doe",
        "age": 35,
        "sex": "M",
        "qualification": "C2"
    }).json()
    
    return client.post("/students/", json={
        "first_name": "Alex",
        "last_name": "Petrov",
        "age": 17,
        "sex": "M",
        "email": email,
        "level": "B2",
        "vocabulary": 3000,
        "teacher_id": teacher["id"],
        "password": "alexbest2025"
    })

def test_create_student(client):
    response = create_sample_student(client)  # Убираем unique_id
    assert response.status_code == 200
    assert response.json()["first_name"] == "Alex"

def test_read_students(client):
    response = client.get("/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_student(client):
    student = create_sample_student(client).json()  # Убираем unique_id
    new_unique_id = int(time.time())  # Генерируем уникальный email
    response = client.put(f"/students/{student['id']}", json={
        "first_name": "Alex",
        "last_name": "Petrov",
        "age": 17,
        "sex": "M",
        "email": f"alexpetrov{new_unique_id}@mail.com",
        "level": "A2",
        "vocabulary": 3000,
        "teacher_id": student["teacher_id"],
        "password": "alexbest2025"
    })
    assert response.status_code == 200
    assert response.json()["level"] == "A2"

# test_crud.py
def test_delete_student(client):
    # Create student with unique email
    create_response = create_sample_student(client)
    assert create_response.status_code == 200
    student = create_response.json()
    
    # Delete the student
    delete_response = client.delete(f"/students/{student['id']}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    verify_response = client.get(f"/students/{student['id']}")
    assert verify_response.status_code == 404
