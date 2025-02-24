# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Database credentials
DB_USER = "postgres"
DB_PASSWORD = "qwerty"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "english_gang"

# Construct database URL using psycopg2 format
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engine with additional parameters
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
