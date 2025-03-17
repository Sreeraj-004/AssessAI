import os
import sys
from pathlib import Path

# Add the parent directory to Python path to make app package importable
app_dir = Path(__file__).parent.parent
sys.path.append(str(app_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create instance directory if it doesn't exist
instance_dir = Path(__file__).parent / "instance"
instance_dir.mkdir(exist_ok=True)

# Database configuration
SQLALCHEMY_DATABASE_URL = f"sqlite:///{instance_dir}/app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Import models
from app.mdl import Base, User, Question, QuestionBank, Exam, StudentAnswer, StudentAnswerQuestion

def init_db():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("All existing tables dropped.")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully!")

if __name__ == "__main__":
    init_db()
