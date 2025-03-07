from database import SessionLocal, engine, Base
from models import Teacher, Student, Manager

def create_tables():
    Base.metadata.drop_all(bind=engine)  # Удаляем старые таблицы (если нужно)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def populate_database():
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Создание учителей
        teachers_data = [
            {"first_name": "John", "last_name": "Doe", "age": 35, "sex": "M", "qualification": "C2"},
            {"first_name": "Jane", "last_name": "Smith", "age": 42, "sex": "F", "qualification": "C1"}
        ]

        teachers = [Teacher(**data) for data in teachers_data]
        db.add_all(teachers)
        db.flush()  # Гарантируем, что ID учителей уже назначены

        print("Teachers added successfully!")

        # Создание студентов
        students_data = [
            {"first_name": "Alice", "last_name": "Johnson", "age": 20, "sex": "F",
             "email": "alice@example.com", "password": Student.hash_password("password123"),
             "level": "B2", "vocabulary": 2500, "teacher_id": teachers[0].id},

            {"first_name": "Bob", "last_name": "Wilson", "age": 22, "sex": "M",
             "email": "bob@example.com", "password": Student.hash_password("password456"),
             "level": "A2", "vocabulary": 1500, "teacher_id": teachers[1].id}
        ]

        students = [Student(**data) for data in students_data]
        db.add_all(students)
        db.flush()

        print("Students added successfully!")

        # Создание менеджера
        manager = Manager(email="admin@example.com", password=Manager.hash_password("admin123"))
        db.add(manager)
        db.commit()

        print("Managers added successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()
