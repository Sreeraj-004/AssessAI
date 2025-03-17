from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session, joinedload
from datetime import datetime
from uuid import uuid4
from app.database import Base
from app.mdl import User, Exam
from app.mdl import QuestionBank
from app.mdl import Question
import random
from typing import Dict
import json

# Exam function

def create_exam(db: Session, teacher_id: str, exam_name: str, exam_date: datetime, question_bank_id: str, sections: dict, pass_marks: float):
    try:
        print("Validating teacher...")
        teacher = db.query(User).filter(User.id == teacher_id).first()
        if not teacher:
            raise ValueError("Invalid teacher ID")

        print(f"Teacher found: {teacher}")

        exam_id = str(uuid4())
        all_sections = {}
        total_time = 0
        total_marks = 0  # Initialize total marks

        print("Validating sections...")
        for q_type, details in sections.items():
            if not isinstance(details, dict) or "count" not in details or "duration" not in details:
                raise ValueError(f"Invalid format for section '{q_type}'. Expected keys: 'count' and 'duration'.")

            count = details["count"]
            duration = details["duration"]
            total_time += duration

            if not isinstance(count, int) or not isinstance(duration, int):
                raise ValueError(f"Invalid data type for section '{q_type}'. 'count' and 'duration' must be integers.")

            # Get questions for this section to calculate total marks
            questions = db.query(Question).filter(
                Question.question_bank_id == question_bank_id,
                Question.question_type == q_type
            ).all()

            if len(questions) < count:
                raise ValueError(f"Not enough questions of type '{q_type}' in the question bank")

            # Calculate total marks for this section
            section_marks = sum(q.score for q in questions[:count])
            total_marks += section_marks

            section_data = {"count": count, "duration": duration}
            all_sections[q_type] = section_data

        print("Creating the exam...")
        new_exam = Exam(
            exam_id=exam_id,
            teacher_id=teacher_id,
            question_bank_id=question_bank_id,
            exam_name=exam_name,
            exam_date=exam_date,
            sections=all_sections,
            pass_marks=pass_marks,
            total_marks=total_marks
        )
        db.add(new_exam)
        db.commit()
        db.refresh(new_exam)

        # Generate a unique exam link (can be used for student access)
        exam_link = f"/exam/{new_exam.exam_id}"

        return {
            "success": True,
            "exam": {
                "exam_id": new_exam.exam_id,
                "exam_name": new_exam.exam_name,
                "total_time": total_time,
                "sections": all_sections,
                "exam_link": exam_link  # Include the exam link for access
            }
        }

    except ValueError as ve:
        print(f"Value Error: {str(ve)}")
        return {"success": False, "error": str(ve)}

    except Exception as e:
        db.rollback()
        print(f"Unexpected Error: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred."}




# Exam Creation Logic





def get_exam_details(db: Session, exam_id: str, teacher_id: str) -> Dict:
    # Retrieve the exam by ID and teacher ID
    exam = db.query(Exam).filter(Exam.exam_id == exam_id, Exam.teacher_id == teacher_id).first()

    if not exam:
        raise ValueError("Exam not found or you do not have permission to view it.")
    
    # Retrieve teacher name
    teacher = db.query(User).filter(User.id == teacher_id).first()
    if not teacher:
        raise ValueError("Teacher not found.")
   
   
    exam.question_bank_id == exam.question_bank_id
   
   
    # Initialize the total score
    total_score = 0

    # Prepare the response data
    exam_details = {
        "exam_name": exam.exam_name,
        "teacher_name": teacher.username,  # Assuming the `User` model has a `name` field
        "exam_date": exam.exam_date.strftime('%Y-%m-%dT%H:%M:%S'),
        "total_duration": sum(section.get("duration", 0) for section in exam.sections.values()),  # Sum of all section durations
        "total_score": 0,  # Will be updated after calculating all section scores
        "sections": []
    }

    # Retrieve sections from the JSON field in the exam model
    for section_name, section_data in exam.sections.items():
        section_details = {
            "section_name": section_name,
            "duration": section_data.get("duration", 0),  # Assuming each section has a duration
            "score": 0,  # Initialize section score
            "questions": []
        }

        # Retrieve questions for the section
        questions = db.query(Question).filter(Question.question_bank_id == exam.question_bank_id).all()

        for question in questions:
            if question.question_type in section_data.get("types", []):
                question_details = {
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "score": question.score,
                    "min_word_count": question.min_words,
                    "max_word_count": question.max_words,
                    "options": [],  # Default to empty list for non-MCQ questions
                    "answer_key": question.answer_key
                }

                # Handle MCQ options
                if question.question_type == "MCQ":
                    question_details["options"] = question.options
                    question_details["correct_option"] = question.correct_option
                
                # Handle Paragraph questions (add answer key)
                elif question.question_type == "Paragraph":
                    question_details["answer_key"] = question.answer_key
                
                # Handle Essay questions (add answer key and max word count)
                elif question.question_type == "Essay":
                    question_details["answer_key"] = question.answer_key
                    question_details["max_word_count"] = question.max_words

                # Add the question score to the section score
                section_details["score"] += question.score

                # Add the question to the section details
                section_details["questions"].append(question_details)

        # Add the section score to the total score
        total_score += section_details["score"]

        # Add section details to the exam details
        exam_details["sections"].append(section_details)
    
    # Update the total score in the exam details
    exam_details["total_score"] = total_score

    return exam_details






def handle_exam_link(db: Session, exam_id: str, student_id: str):
    # Validate exam existence
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        return {"success": False, "message": "Exam not found"}

    current_time = datetime.now()

    # Check if the student is accessing before start time
    if current_time < exam.exam_date:
        return {
            "success": True,
            "status": "waiting_lobby",
            "message": "The exam has not started yet. Please wait.",
            "exam_start_time": exam.exam_date,
        }

    # Check if the student is late
    late_join_cutoff = exam.exam_date.replace(hour=9, minute=50)
    if current_time > late_join_cutoff:
        return {
            "success": False,
            "message": "You cannot join the exam after the allowed time."
        }

    # Exam is starting
    return {
        "success": True,
        "status": "start_exam",
        "message": "The exam is starting now!",
        "first_section": list(exam.sections.keys())[0],  # Return the first section
    }
