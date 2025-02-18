# test_db.py
from database import engine, Base
import models
import sys

def test_connection():
    try:
        # Try to create all tables
        Base.metadata.create_all(bind=engine)
        print("Successfully connected to database and created tables!")
        
        # Try to make a simple query
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("Successfully executed a test query!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()