from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey, Float, Boolean, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
import random
from sqlalchemy.sql import func

Base = declarative_base()

# Function to generate a unique user ID
def generate_user_id(username: str) -> str:
    random_number = random.randint(1000, 9999)
    return f"{username}{random_number}"

# Function to generate a 3-digit ID with prefix
def generate_qb_id():
    return f"QB{random.randint(100, 999)}"

def generate_exam_id():
    return f"EX{random.randint(100, 999)}"

# Custom UUID type for SQLite compatibility
class SqliteUUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert UUID to string for storage"""
        if value is None:
            return None
        elif isinstance(value, UUID):
            return str(value)
        elif isinstance(value, str):
            try:
                return str(UUID(value))
            except ValueError:
                return value
        return str(value)

    def process_result_value(self, value, dialect):
        """Convert string from storage to UUID"""
        if value is None:
            return None
        try:
            return UUID(value) if value else None
        except (ValueError, AttributeError):
            # If the value is not a valid UUID, generate a new one
            return uuid4()



# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Now using String for username+number format
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String)

    student_answers = relationship("StudentAnswer", back_populates="student")
    exams = relationship("Exam", back_populates="teacher")

    @classmethod
    def get(cls, db, user_id: str):
        return db.query(cls).filter(cls.id == user_id).first()

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "role": self.role
        }

# QuestionBank Model
class QuestionBank(Base):
    __tablename__ = "question_banks"

    id = Column(String, primary_key=True, default=generate_qb_id)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="question_bank", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="question_bank")

    def to_dict(self):
        """Convert question bank to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": str(self.owner_id),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Question Model
class Question(Base):
    __tablename__ = "questions"

    id = Column(SqliteUUID, primary_key=True, default=uuid4)
    question_bank_id = Column(String, ForeignKey("question_banks.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    answer_key = Column(Text, nullable=True)
    min_words = Column(Integer, nullable=True)
    max_words = Column(Integer, nullable=True)
    options = Column(JSON, nullable=True)
    correct_option = Column(String, nullable=True)

    question_bank = relationship("QuestionBank", back_populates="questions")
    student_answers = relationship("StudentAnswer", back_populates="question")
    student_answers_questions = relationship("StudentAnswerQuestion", back_populates="question")

    def to_dict(self):
        """Convert question to dictionary"""
        return {
            "id": str(self.id),
            "question_bank_id": self.question_bank_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "score": self.score,
            "answer_key": self.answer_key,
            "min_words": self.min_words,
            "max_words": self.max_words,
            "options": self.options,
            "correct_option": self.correct_option
        }

# Exam Model
class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(String, primary_key=True, default=generate_exam_id)
    teacher_id = Column(String, ForeignKey("users.id"), nullable=False)
    question_bank_id = Column(String, ForeignKey("question_banks.id"), nullable=False)
    exam_name = Column(String, nullable=False)
    exam_date = Column(DateTime, nullable=False)
    sections = Column(JSON, nullable=False)
    pass_marks = Column(Float, nullable=False)  # New field for pass marks
    total_marks = Column(Float, nullable=False)  # New field for total marks
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="exams")
    question_bank = relationship("QuestionBank", back_populates="exams")

    def to_dict(self):
        """Convert exam to dictionary"""
        return {
            "id": self.exam_id,
            "teacher_id": str(self.teacher_id),
            "question_bank_id": self.question_bank_id,
            "exam_name": self.exam_name,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "sections": self.sections,
            "pass_marks": self.pass_marks,
            "total_marks": self.total_marks,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# StudentAnswer Model
class StudentAnswer(Base):
    __tablename__ = "student_answers"

    id = Column(SqliteUUID, primary_key=True, default=uuid4)
    student_id = Column(String, ForeignKey('users.id'))
    exam_id = Column(String, ForeignKey('exams.exam_id'))
    question_id = Column(SqliteUUID, ForeignKey('questions.id'))
    selected_option = Column(String, nullable=True)  # For MCQs
    typed_answer = Column(Text, nullable=True)  # For Essay/Paragraph
    section_type = Column(String, nullable=False)  # Section type: "MCQ", "Essay", etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    score_earned = Column(Float, nullable=True)
    is_evaluated = Column(Boolean, default=False)
    has_passed = Column(Boolean, nullable=True)  # New field to track if student passed
    evaluation_timestamp = Column(DateTime, nullable=True)
    feedback = Column(Text, nullable=True)  # Changed from JSON to Text for SQLite compatibility
    
    student = relationship("User", back_populates="student_answers")
    exam = relationship("Exam")
    question = relationship("Question", back_populates="student_answers")
    student_answers_questions = relationship("StudentAnswerQuestion", back_populates="student_answer")

    def to_dict(self):
        """Convert student answer to dictionary"""
        return {
            "id": str(self.id),
            "student_id": str(self.student_id),
            "exam_id": str(self.exam_id),
            "question_id": str(self.question_id),
            "selected_option": self.selected_option,
            "typed_answer": self.typed_answer,
            "section_type": self.section_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "score_earned": self.score_earned,
            "is_evaluated": self.is_evaluated,
            "has_passed": self.has_passed,
            "evaluation_timestamp": self.evaluation_timestamp.isoformat() if self.evaluation_timestamp else None,
            "feedback": self.feedback
        }

# Association Table for Many-to-Many Relationship
class StudentAnswerQuestion(Base):
    __tablename__ = "student_answer_questions"

    id = Column(SqliteUUID, primary_key=True, default=uuid4)
    student_answer_id = Column(SqliteUUID, ForeignKey("student_answers.id"), nullable=False)
    question_id = Column(SqliteUUID, ForeignKey("questions.id"), nullable=False)

    student_answer = relationship("StudentAnswer", back_populates="student_answers_questions")
    question = relationship("Question", back_populates="student_answers_questions")

    def to_dict(self):
        """Convert student answer question to dictionary"""
        return {
            "id": str(self.id),
            "student_answer_id": str(self.student_answer_id),
            "question_id": str(self.question_id)
        }
