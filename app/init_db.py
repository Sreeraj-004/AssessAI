import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to Python path
import sys
parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Get the absolute path to the instance directory
instance_dir = Path(__file__).parent / "instance"
instance_dir.mkdir(exist_ok=True)

# Database configuration
SQLALCHEMY_DATABASE_URL = f"sqlite:///{instance_dir}/app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Import models after engine creation
from mdl import Base, User, Question, QuestionBank, Exam, StudentAnswer, StudentAnswerQuestion

def init_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization completed!")

if __name__ == "__main__":
    init_database()
