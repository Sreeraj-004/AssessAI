from uuid import uuid4
from app.mdl import QuestionBank
from app.database import SessionLocal
import random
from datetime import datetime  
from sqlalchemy.orm import Session

def generate_random_id(db):
    """Generate a unique random ID in the format 001-999."""
    while True:
        random_id = f"{random.randint(1, 999):03d}"  # Generates IDs like 001, 002, ...
        # Ensure the ID is unique by checking the database
        if not db.query(QuestionBank).filter(QuestionBank.id == random_id).first():
            return random_id
        
def format_date(timestamp):
    # Example: format date as "January 31, 2025, 01:41 AM"
    return timestamp.strftime("%B %d, %Y, %I:%M %p")


def create_question_bank(name: str, owner_id: str, description: str = None):
    db = SessionLocal()
    try:
        unique_id = generate_random_id(db)
        question_bank = QuestionBank(
            id=unique_id,  # Generate a unique ID
            name=name,
            description=description,
            owner_id=owner_id,
        )
        db.add(question_bank)
        db.commit()
        db.refresh(question_bank)
        created_at_formatted = question_bank.created_at.strftime("%d %b %Y, %I:%M %p")

        return {
            "message": "Question Bank created successfully!",
            "id": question_bank.id,
            "name": question_bank.name,
            "description": question_bank.description,
            "owner_id": question_bank.owner_id,
            "created_at": created_at_formatted
        }
    finally:
        db.close()

def get_question_banks_by_owner(owner_id: str):
    db = SessionLocal()
    try:
        return db.query(QuestionBank).filter(QuestionBank.owner_id == owner_id).all()
    finally:
        db.close()

def delete_question_bank(qb_id: str, owner_id: str):
    db = SessionLocal()
    try:
        question_bank = db.query(QuestionBank).filter(
            QuestionBank.id == qb_id,
            QuestionBank.owner_id == owner_id
        ).first()
        
        if not question_bank:
            return None

        db.delete(question_bank)
        db.commit()
        return True
    finally:
        db.close()

def get_question_bank_by_id(db: Session, question_bank_id: str):
    return db.query(QuestionBank).filter(QuestionBank.id == question_bank_id).first()
