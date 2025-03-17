# app/services/question.py

import json
from app.mdl import Question  # Make sure to import the correct Question model
from app.database import SessionLocal
from sqlalchemy.orm import Session

def create_question(
    question_bank_id: str,
    question_text: str,
    question_type: str,
    score: int = None,
    answer_key: str = None,
    min_words: int = None,
    max_words: int = None,
    options: dict = None,
    correct_option: str = None
):
    db = SessionLocal()
    try:
        # Default score values based on question type if not provided
        if not score:
            if question_type == "MCQ":
                score = 1
            elif question_type == "Paragraph":
                score = 5
            elif question_type == "Essay":
                score = 10
        # Set min_words and max_words based on question type
        if question_type == "MCQ":
            min_words, max_words = None, None  # MCQs don't have word limits
        elif question_type == "Paragraph":
            min_words, max_words = 10, 200  # Paragraph questions have word limits
        elif question_type == "Essay":
            min_words, max_words = 100, 500  # Essay questions have word limits

        # If the question is MCQ, options should be serialized as a JSON string
        if question_type == "MCQ" and options:
            options = json.dumps(options)  # Store options as JSON

        question = Question(
            question_bank_id=question_bank_id,
            question_text=question_text,
            question_type=question_type,
            score=score,
            answer_key=answer_key,
            min_words=min_words,  # Use the updated min_words
            max_words=max_words,  # Default max words
            options=options,
            correct_option=correct_option
        )

        db.add(question)
        db.commit()
        db.refresh(question)
        return question
    finally:
        db.close()


def get_questions_by_bank(db: Session,question_bank_id: str):
    db = SessionLocal()
    try:
        questions = db.query(Question).filter(Question.question_bank_id == question_bank_id).all()
        return questions
    finally:
        db.close()