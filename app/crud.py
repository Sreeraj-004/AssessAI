# crud.py

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from datetime import datetime
from .mdl import User, Exam
from .database import SessionLocal
import bcrypt
import random

def generate_user_id(username: str) -> str:
    """Generate a user ID in the format username+random_number"""
    # Remove any whitespace and special characters from username
    clean_username = ''.join(e for e in username if e.isalnum()).lower()
    # Generate a random 5-digit number
    random_number = str(random.randint(10000, 99999))
    # Combine username and random number
    return f"{clean_username}{random_number}"

def create_user(db: Session, username: str, email: str, role: str, password: str):  
   
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Generate unique user_id based on the username
    user_id = f"{username.lower()}{str(hash(username))[:5]}"
    db_user = User(id=user_id, username=username, email=email, role=role, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def update_user(db: Session, user_id: str, username: str = None, email: str = None, role: str = None, password: str = None):
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_user:
        if username:
            db_user.username = username
        if email:
            db_user.email = email
        if role:
            db_user.role = role
        if password:
            db_user.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db.commit()
        db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if db_user:
        db.delete(db_user)
        db.commit()
    
    return db_user


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_username_or_email(db: Session, username: str, email: str):
    return db.query(User).filter((User.username == username) | (User.email == email)).first()


def create_exam(db: Session, title: str, user_id: str, questions: list):
    db_exam = Exam(title=title, user_id=user_id, questions=questions)
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam


def get_exams_by_user(db: Session, user_id: str):
    return db.query(Exam).filter(Exam.user_id == user_id).all()
