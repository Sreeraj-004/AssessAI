import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Create instance directory if it doesn't exist
INSTANCE_PATH = Path(__file__).parent / "instance"
INSTANCE_PATH.mkdir(exist_ok=True)

# Database URL (SQLite for now)
DB_PATH = INSTANCE_PATH / "app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.absolute()}"

# Create the engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # Add timeout for busy database
    }
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
