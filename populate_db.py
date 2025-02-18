# populate_db.py
from database import SessionLocal, engine, Base
import models

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def populate_database():
    # Create tables first
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Create teachers
        teachers_data = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "age": 35,
                "sex": "M",
                "qualification": "C2"
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "age": 42,
                "sex": "F",
                "qualification": "C1"
            }
        ]

        for teacher_data in teachers_data:
            teacher = models.Teacher(**teacher_data)
            db.add(teacher)
        
        db.commit()
        print("Teachers added successfully!")

        # Create students
        students_data = [
            {
                "first_name": "Alice",
                "last_name": "Johnson",
                "age": 20,
                "sex": "F",
                "email": "alice@example.com",
                "password": models.pwd_context.hash("password123"),
                "level": "B2",
                "vocabulary": 2500,
                "teacher_id": 1
            },
            {
                "first_name": "Bob",
                "last_name": "Wilson",
                "age": 22,
                "sex": "M",
                "email": "bob@example.com",
                "password": models.pwd_context.hash("password456"),
                "level": "A2",
                "vocabulary": 1500,
                "teacher_id": 2
            }
        ]

        for student_data in students_data:
            student = models.Student(**student_data)
            db.add(student)
        
        db.commit()
        print("Students added successfully!")

        # Create manager
        manager = models.Manager(
            email="admin@example.com",
            password=models.pwd_context.hash("admin123")
        )
        db.add(manager)
        db.commit()
        print("Manager added successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()