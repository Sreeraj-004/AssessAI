from sqlalchemy.orm import Session
from app.mdl import *




def store_student_answer(db: Session, exam_id: str, student_id: str, question_id: str, answer_text: str = None, selected_option: str = None):
    try:
        # Fetch the question to check if it's valid
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError("Invalid question ID")

        # Create a new answer record
        new_answer = StudentAnswer(
            exam_id=exam_id,
            student_id=student_id,
            question_id=question_id,
            answer_text=answer_text,
            selected_option=selected_option
        )

        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
        
        return {"success": True, "message": "Answer submitted successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
