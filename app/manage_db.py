import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.mdl import User, Question, QuestionBank, Exam, StudentAnswer
from datetime import datetime
import uuid

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def view_all_users(db: Session):
    users = db.query(User).all()
    print("\n=== Users ===")
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print("-" * 30)

def view_all_question_banks(db: Session):
    qbs = db.query(QuestionBank).all()
    print("\n=== Question Banks ===")
    for qb in qbs:
        print(f"ID: {qb.id}")
        print(f"Name: {qb.name}")
        print(f"Description: {qb.description}")
        print(f"Owner ID: {qb.owner_id}")
        print(f"Created at: {qb.created_at}")
        print("-" * 30)

def view_all_questions(db: Session):
    questions = db.query(Question).all()
    print("\n=== Questions ===")
    for q in questions:
        print(f"ID: {q.id}")
        print(f"Bank ID: {q.question_bank_id}")
        print(f"Text: {q.question_text}")
        print(f"Type: {q.question_type}")
        print(f"Score: {q.score}")
        print("-" * 30)

def view_all_exams(db: Session):
    exams = db.query(Exam).all()
    print("\n=== Exams ===")
    for exam in exams:
        print(f"ID: {exam.exam_id}")
        print(f"Name: {exam.exam_name}")
        print(f"Teacher ID: {exam.teacher_id}")
        print(f"Date: {exam.exam_date}")
        print(f"Question Bank ID: {exam.question_bank_id}")
        print("-" * 30)

def add_test_user(db: Session):
    user = User(
        id=str(uuid.uuid4()),
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password_here",
        role="student"
    )
    db.add(user)
    db.commit()
    print(f"Added test user with ID: {user.id}")
    return user

def add_test_question_bank(db: Session, owner_id: str):
    qb = QuestionBank(
        id=str(uuid.uuid4()),
        name="Test Question Bank",
        description="A test question bank",
        owner_id=owner_id,
        created_at=datetime.utcnow()
    )
    db.add(qb)
    db.commit()
    print(f"Added test question bank with ID: {qb.id}")
    return qb

def add_test_question(db: Session, qb_id: str):
    question = Question(
        id=uuid.uuid4(),
        question_bank_id=qb_id,
        question_text="What is the capital of France?",
        question_type="mcq",
        score=5,
        options={"a": "London", "b": "Paris", "c": "Berlin", "d": "Madrid"},
        correct_option="b"
    )
    db.add(question)
    db.commit()
    print(f"Added test question with ID: {question.id}")
    return question

def add_test_exam(db: Session, teacher_id: str, qb_id: str):
    exam = Exam(
        exam_id=str(uuid.uuid4()),
        teacher_id=teacher_id,
        exam_name="Test Exam",
        exam_date=datetime.utcnow(),
        question_bank_id=qb_id,
        sections={"mcq": {"count": 5}, "descriptive": {"count": 2}}
    )
    db.add(exam)
    db.commit()
    print(f"Added test exam with ID: {exam.exam_id}")
    return exam

def main():
    db = get_db()
    while True:
        print("\nDatabase Management Menu:")
        print("1. View all users")
        print("2. View all question banks")
        print("3. View all questions")
        print("4. View all exams")
        print("5. Add test user")
        print("6. Add test question bank")
        print("7. Add test question")
        print("8. Add test exam")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ")
        
        if choice == "1":
            view_all_users(db)
        elif choice == "2":
            view_all_question_banks(db)
        elif choice == "3":
            view_all_questions(db)
        elif choice == "4":
            view_all_exams(db)
        elif choice == "5":
            add_test_user(db)
        elif choice == "6":
            user_id = input("Enter owner ID (user ID): ")
            add_test_question_bank(db, user_id)
        elif choice == "7":
            qb_id = input("Enter question bank ID: ")
            add_test_question(db, qb_id)
        elif choice == "8":
            teacher_id = input("Enter teacher ID: ")
            qb_id = input("Enter question bank ID: ")
            add_test_exam(db, teacher_id, qb_id)
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
