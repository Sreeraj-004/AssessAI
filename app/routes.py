from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, constr, validator
from .database import SessionLocal, get_db, Base
from .mdl import User, QuestionBank, Question, Exam, StudentAnswer
from .crud import (
    get_user_by_username,
    get_user_by_email,
    create_user,
)
from .services.QB import (
    get_question_bank_by_id,
    get_question_banks_by_owner,
    create_question_bank,
    delete_question_bank,
)
from .services.question import (
    create_question,
    get_questions_by_bank,
)
from .services.Exam_creation import (
    create_exam,
    get_exam_details,
)
from .services.evaluation import (
    evaluate_student_answers,
    evaluate_mcq_answer,
    evaluate_text_answer,
)
from .services.answering import store_student_answer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
import random, json
import time
from collections import defaultdict
import bcrypt
import re
from .security.jwt_utils import create_access_token, get_current_user
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

#user register model
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Add OPTIONS handlers for CORS preflight requests
@router.options("/register/")
async def register_options():
    return {}

@router.post("/register/")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    # Check if the user already exists by username or email
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create the new user
    new_user = create_user(
        db, username=user.username, email=user.email, role=user.role, password=user.password
    )
    return {"message": "User created successfully", "id": new_user.id}

# Define a model for login credentials
class LoginCredentials(BaseModel):
    email: str
    password: str

# Add OPTIONS handlers for CORS preflight requests
@router.options("/login/")
async def login_options():
    return {}

# Login route
@router.post("/login/")
def login(credentials: LoginCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if the provided password matches the stored hashed password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create the JWT token with user ID and role
    access_token = create_access_token(data={
        "sub": user.id,
        "role": user.role
    })
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role  # Include role in response
    }

class QuestionBankCreate(BaseModel):
    name: str
    description: str = None

@router.post("/question_banks/")
def create_question_bank_endpoint(
    qb_data: QuestionBankCreate,
    current_user = Depends(get_current_user),  # Authenticate user
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Access the id using the appropriate method based on the type
    if hasattr(current_user, 'id'):
        owner_id = current_user.id
    elif isinstance(current_user, dict):
        owner_id = current_user["id"]
    else:
        raise HTTPException(status_code=500, detail="Invalid user object type")
    
    question_bank = create_question_bank(
        name=qb_data.name,
        description=qb_data.description,
        owner_id=owner_id,  # Use authenticated user's ID
    )
    return {
        "message": "Question Bank created successfully!",
        **question_bank  # Unpack the question bank details directly
    }

@router.get("/question_banks/")
def get_question_banks(current_user = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Access the id using the appropriate method based on the type
    if hasattr(current_user, 'id'):
        owner_id = current_user.id
    elif isinstance(current_user, dict):
        owner_id = current_user["id"]
    else:
        raise HTTPException(status_code=500, detail="Invalid user object type")
    
    question_banks = get_question_banks_by_owner(owner_id=owner_id)
    return {"success": True, "data": question_banks}

@router.delete("/question_banks/{qb_id}")
def delete_question_bank_endpoint(qb_id: str, current_user = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Access the id using the appropriate method based on the type
    if hasattr(current_user, 'id'):
        owner_id = current_user.id
    elif isinstance(current_user, dict):
        owner_id = current_user["id"]
    else:
        raise HTTPException(status_code=500, detail="Invalid user object type")
    
    success = delete_question_bank(qb_id=qb_id, owner_id=owner_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question bank not found or not authorized to delete")

    return {"success": True, "message": "Question bank deleted successfully"}

class QuestionCreate(BaseModel):
    question_bank_id: str
    question_text: str
    question_type: str
    score: int = None
    answer_key: str = None
    min_words: int = None
    max_words: int = None
    options: dict = None  # JSON format for MCQ options
    correct_option: str = None

@router.post("/questions/")
def create_question_endpoint(
    question_data: QuestionCreate,
    current_user = Depends(get_current_user),  # Authenticate user
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    question = create_question(
        question_bank_id=question_data.question_bank_id,
        question_text=question_data.question_text,
        question_type=question_data.question_type,
        score=question_data.score,
        answer_key=question_data.answer_key,
        min_words=question_data.min_words,
        max_words=question_data.max_words,
        options=question_data.options,
        correct_option=question_data.correct_option
    )
    return {"success": True, "data": question}


@router.get("/view_questions/{question_bank_id}")
def view_questions(
    question_bank_id: str,
    db: Session = Depends(get_db),  # Database session injected here
    current_user = Depends(get_current_user),  # Authenticate user
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Retrieve the question bank details
    question_bank = get_question_bank_by_id(db, question_bank_id)
    if not question_bank:
        raise HTTPException(status_code=404, detail="Question Bank not found")

    # Retrieve the questions for the question bank
    questions = get_questions_by_bank(db, question_bank_id)
    
    # Format the output for each question
    question_details = []
    for question in questions:
        question_info = {
            "question_bank_name": question_bank.name,
            "question_type": question.question_type,
            "question_text": question.question_text,
            "score": question.score,
        }

        if question.question_type == "MCQ":
            question_info.update({
                "options": question.options,
                "correct_option": question.correct_option,
            })
        elif question.question_type in ["Paragraph", "Essay"]:
            question_info.update({
                "answer_key": question.answer_key,
                "min_words": question.min_words,
                "max_words": question.max_words,
            })

        question_details.append(question_info)

    return {"success": True, "data": question_details}




class ExamCreateRequest(BaseModel):
    exam_name: str
    exam_date: datetime
    question_bank_id: str
    sections: Dict[str, Dict[str, int]]  # Expecting sections in the specified format
    pass_marks: float

@router.post("/create_exam/")
def create_exam_route(
    request: ExamCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # Get authenticated user
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Call the create_exam function using the authenticated user's ID
        if hasattr(current_user, 'id'):
            teacher_id = current_user.id
        elif isinstance(current_user, dict):
            teacher_id = current_user["id"]
        else:
            raise HTTPException(status_code=500, detail="Invalid user object type")
        
        exam = create_exam(
            db=db,
            teacher_id=teacher_id,  # Use authenticated user's ID
            question_bank_id=request.question_bank_id,
            exam_name=request.exam_name,
            exam_date=request.exam_date,
            sections=request.sections,
            pass_marks=request.pass_marks
        )
        return {"success": True, "exam": exam}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")  # Debugging log
        return {"success": False, "error": "An unexpected error occurred."}
 

# Define response model for the exam details response
class GetExamDetailsResponse(BaseModel):
    exam_name: str
    teacher_name: str
    exam_date: str
    total_duration: int
    total_score: int
    sections: List[Dict]

# Define request body model
class GetExamDetailsRequest(BaseModel):
    exam_id: str
    teacher_id: str

# Define the route for getting exam details
@router.post("/get_exam_details", response_model=GetExamDetailsResponse)
def get_exam_details_route(
    request: GetExamDetailsRequest,  # Parse request body as JSON
    db: Session = Depends(get_db)
):
    """
    Route to get exam details.
    """
    try:
        # Call the service function to fetch exam details
        response = get_exam_details(db=db, exam_id=request.exam_id, teacher_id=request.teacher_id)
        return response
    except ValueError as e:  # Catch specific errors for better responses
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  # Catch any other general errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
 #exam link

@router.get("/exam/{exam_id}")
def access_exam(exam_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Check if the exam exists
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    # Check if the user is logged in
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to access this exam.")

    # Check the current timing
    current_time = datetime.now()
    exam_start_time = exam.exam_date
    exam_end_time = exam_start_time + timedelta(hours=1)  # 1 hour duration

    # Calculate time remaining in seconds
    time_until_start = (exam_start_time - current_time).total_seconds()
    time_until_end = (exam_end_time - current_time).total_seconds()

    if current_time < exam_start_time:
        return {
            "status": "waiting",
            "message": f"The exam '{exam.exam_name}' has not started yet. You will be directed to the waiting lobby.",
            "start_time": exam_start_time.isoformat(),
            "time_remaining": int(time_until_start),
            "exam_name": exam.exam_name
        }
    elif current_time > exam_end_time:
        raise HTTPException(status_code=403, detail="The exam has ended.")

    # If we're here, the exam is currently running
    return {
        "status": "running",
        "message": f"You may now enter the exam '{exam.exam_name}'.",
        "time_remaining": int(time_until_end),
        "exam_name": exam.exam_name
    }

class ExamConfirmRequest(BaseModel):
    exam_id: str

@router.post("/exam/confirm")
def confirm_exam_entry(
    request: ExamConfirmRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check if the exam exists
    exam = db.query(Exam).filter(Exam.exam_id == request.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    # Check if the user is logged in
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to confirm.")

    # Check the current timing
    current_time = datetime.now()
    exam_start_time = exam.exam_date
    exam_end_time = exam_start_time + timedelta(hours=1)  # 1 hour duration

    # Calculate time remaining in seconds
    time_until_start = (exam_start_time - current_time).total_seconds()
    time_until_end = (exam_end_time - current_time).total_seconds()

    if current_time < exam_start_time:
        return {
            "status": "waiting_lobby",
            "message": f"Please wait. The exam will start at {exam_start_time.strftime('%Y-%m-%d %H:%M')}.",
            "time_remaining": int(time_until_start),
            "exam_name": exam.exam_name
        }
    elif current_time > exam_end_time:
        raise HTTPException(status_code=403, detail="The entry period for this exam has closed.")

    # Allow entry and provide the link to the first section
    return {
        "status": "success",
        "message": f"You have successfully entered the exam '{exam.exam_name}'.",
        "redirect_to": f"/exam/{request.exam_id}/section/MCQ",
        "time_remaining": int(time_until_end),
        "exam_name": exam.exam_name
    }

@router.post("/exam/{exam_id}/submit")
def final_submit_exam(
    exam_id: str,
    answers: dict,  # Expecting a dictionary of question_id: answer
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Validate if the exam exists
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    # Validate if the student is logged in
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to submit answers.")

    # Iterate over answers and store them
    for question_id, answer in answers.items():
        new_answer = StudentAnswer(
            exam_id=exam_id,
            student_id=current_user.id if hasattr(current_user, 'id') else current_user["id"],
            question_id=question_id,
            answer=answer
        )
        db.add(new_answer)

    # Commit all answers to the database
    db.commit()
    return {"status": "success", "message": "All answers submitted successfully!"}


@router.get("/exam/{exam_id}/section/{section_type}/summary")
def fetch_exam_section_summary(
    exam_id: str, 
    section_type: str, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    # Check if the exam exists
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    # Check if the user is logged in
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to view this exam.")

    # Ensure the section exists in the exam
    if section_type not in exam.sections:
        raise HTTPException(status_code=404, detail="Section not found in the exam.")

    # Get the question bank associated with the exam
    question_bank = db.query(QuestionBank).filter(QuestionBank.id == exam.question_bank_id).first()
    if not question_bank:
        raise HTTPException(status_code=404, detail="Question bank not found.")

    # Fetch questions for the specified section
    questions = db.query(Question).filter(
        Question.question_bank_id == question_bank.id,
        Question.question_type == section_type
    ).all()

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this section.")

    # Initialize summary data
    summary_data = {
        "exam_name": exam.exam_name,
        "section_type": section_type,
        "total_score": sum(q.score for q in questions),  # Calculate total score
        "total_time": exam.sections[section_type]["duration"],  # Total duration of the section
        "questions": []
    }

    # Prepare questions with details
    for q in questions:
        question_data = {
            "question_text": q.question_text,
            "score": q.score
        }

        if section_type == "MCQ":
            question_data.update({
                "options": q.options,
                "correct_option": q.correct_option,
            })
        elif section_type in ["Paragraph", "Essay"]:
            question_data.update({
                "answer_key": q.answer_key,
                "min_words": q.min_words,
                "max_words": q.max_words,
            })

        summary_data["questions"].append(question_data)

    return {"status": "success", "summary": summary_data}


@router.get("/exam/{exam_id}/section/{section_type}")
def fetch_exam_section(
    exam_id: str,
    section_type: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check if the exam exists
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    # Check if the user is logged in
    if not current_user:
        raise HTTPException(status_code=401, detail="You must be logged in to attend the exam.")

    # Ensure the section exists in the exam
    sections = json.loads(exam.sections) if isinstance(exam.sections, str) else exam.sections
    if section_type not in sections:
        raise HTTPException(status_code=404, detail="Section not found in the exam.")

    # Retrieve section details
    section_details = sections[section_type]
    question_count = section_details["count"]
    section_duration = section_details["duration"]

    # Get the question bank associated with the exam
    question_bank = db.query(QuestionBank).filter(QuestionBank.id == exam.question_bank_id).first()
    if not question_bank:
        raise HTTPException(status_code=404, detail="Question bank not found.")

    # Fetch and limit questions
    questions = db.query(Question).filter(
        Question.question_bank_id == question_bank.id,
        Question.question_type == section_type
    ).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this section.")

    # Shuffle and limit questions
    selected_questions = random.sample(questions, min(len(questions), question_count))

    # Initialize the section data
    section_data = {
        "section_type": section_type,
        "duration": section_duration,
        "questions": []
    }

    for q in selected_questions:
        # Ensure question ID is treated as UUID if needed
        question_id = str(q.id)  # Convert UUID to string if it's UUID

        if section_type == "MCQ":
            try:
                options_dict = json.loads(q.options) if q.options else {}
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid options format for a question.")

            # Shuffle options
            options_list = list(options_dict.items())
            random.shuffle(options_list)
            shuffled_options = {k: v for k, v in options_list}

            section_data["questions"].append({
                "question_id": question_id,
                "question_text": q.question_text,
                "options": shuffled_options,

                "score": q.score
            })

        elif section_type in ["Paragraph", "Essay"]:
            section_data["questions"].append({
                "question_id": question_id,
                "question_text": q.question_text,
                "word_count_limit": q.max_words,
                "score": q.score
            })

    return {"status": "success", "section_data": section_data}




@router.post("/exam/{exam_id}/submit_answer")
async def submit_answer(
    exam_id: str,
    answer_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Ensure the student is logged in
    if not current_user or (hasattr(current_user, 'role') and current_user.role != "student") or (isinstance(current_user, dict) and current_user["role"] != "student"):
        raise HTTPException(status_code=401, detail="You must be logged in as a student to submit answers.")
    
    # Check if the exam exists
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")
    
    try:
        # Validate and extract the question ID
        question_id = UUID(answer_data.get("question_id"))
        
        # Get the question to determine its type
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found.")
        
        # Create new answer record
        new_answer = StudentAnswer(
            exam_id=exam_id,
            student_id=current_user.id if hasattr(current_user, 'id') else current_user["id"],
            question_id=question_id,
            selected_option=answer_data.get("selected_option"),
            typed_answer=answer_data.get("typed_answer"),
            section_type=question.question_type
        )
        
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
        
        # Evaluate the answer immediately
        if question.question_type.lower() == 'mcq':
            score_fraction, feedback = evaluate_mcq_answer(new_answer.selected_option, question.correct_option)
            new_answer.feedback = str(feedback)  # Convert feedback dict to string
        else:
            score_fraction, feedback = evaluate_text_answer(
                new_answer.typed_answer,
                question.answer_key,
                question.min_words or 0,
                question.max_words
            )
            new_answer.feedback = str(feedback)  # Convert feedback dict to string
        
        # Update answer with evaluation results
        earned_score = round(score_fraction * question.score, 2)  # Round to 2 decimal places
        new_answer.score_earned = earned_score
        new_answer.is_evaluated = True
        new_answer.evaluation_timestamp = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Answer submitted and evaluated successfully.",
            "score": earned_score,
            "max_score": question.score,
            "feedback": feedback  # Original feedback object in response
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Invalid question ID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving answer: {str(e)}")

@router.get("/exam/{exam_id}/evaluate/{student_id}")
def evaluate_exam(
    exam_id: str,
    student_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Evaluate all answers for a student in an exam
    Returns evaluation results including scores and feedback
    """
    # Ensure the user has permission (teacher or the student themselves)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if (hasattr(current_user, 'role') and current_user.role != "teacher") and (hasattr(current_user, 'id') and current_user.id != student_id) and (isinstance(current_user, dict) and current_user["role"] != "teacher" and current_user["id"] != student_id):
        raise HTTPException(status_code=403, detail="Not authorized to view these results")
    
    try:
        # Call the service function to fetch exam details
        results = evaluate_student_answers(db, student_id, exam_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exam/{exam_id}/results")
def view_exam_results(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """View results for an entire exam (teacher only)"""
    if not current_user or (hasattr(current_user, 'role') and current_user.role != "teacher") or (isinstance(current_user, dict) and current_user["role"] != "teacher"):
        raise HTTPException(status_code=403, detail="Only teachers can view all exam results")
        
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    # Get all answers for this exam grouped by student
    results = db.query(
        StudentAnswer.student_id,
        User.username,
        func.sum(StudentAnswer.score_earned).label('total_score'),
        func.count(StudentAnswer.id).label('questions_answered')
    ).join(User, StudentAnswer.student_id == User.id)\
     .filter(StudentAnswer.exam_id == exam_id)\
     .group_by(StudentAnswer.student_id, User.username)\
     .all()
     
    return {
        "exam_id": exam_id,
        "exam_name": exam.exam_name,
        "results": [
            {
                "student_id": result.student_id,
                "student_name": result.username,
                "total_score": float(result.total_score) if result.total_score else 0.0,
                "questions_answered": result.questions_answered
            }
            for result in results
        ]
    }

@router.get("/exam/{exam_id}/student/{student_id}/results")
def view_student_exam_results(
    exam_id: str,
    student_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """View detailed results for a specific student's exam"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    # Check authorization
    if (hasattr(current_user, 'role') and current_user.role != "teacher") and (hasattr(current_user, 'id') and current_user.id != student_id) and (isinstance(current_user, dict) and current_user["role"] != "teacher" and current_user["id"] != student_id):
        raise HTTPException(status_code=403, detail="Not authorized to view these results")
        
    # Get student answers with questions
    answers = db.query(StudentAnswer, Question)\
        .join(Question, StudentAnswer.question_id == Question.id)\
        .filter(
            StudentAnswer.exam_id == exam_id,
            StudentAnswer.student_id == student_id
        ).all()
        
    if not answers:
        raise HTTPException(status_code=404, detail="No answers found for this student in the exam")
        
    # Get student and exam details
    student = db.query(User).filter(User.id == student_id).first()
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    
    results = []
    total_score = 0
    max_possible_score = 0
    
    for answer, question in answers:
        result = {
            "question_id": str(question.id),
            "question_text": question.question_text,
            "question_type": question.question_type,
            "score_earned": answer.score_earned,
            "max_score": question.score,
        }

        if question.question_type.lower() == 'mcq':
            result.update({
                "selected_option": answer.selected_option,
                "correct_option": question.correct_option,
                "options": question.options
            })
        else:
            result.update({
                "typed_answer": answer.typed_answer,
                "answer_key": question.answer_key,
                "min_words": question.min_words,
                "max_words": question.max_words
            })
            
        total_score += answer.score_earned if answer.score_earned else 0
        max_possible_score += question.score
        results.append(result)
    
    return {
        "exam_id": exam_id,
        "exam_name": exam.exam_name,
        "student_id": student_id,
        "student_name": student.username,
        "total_score": total_score,
        "max_possible_score": max_possible_score,
        "score_percentage": (total_score / max_possible_score * 100) if max_possible_score > 0 else 0,
        "answers": results
    }

@router.get("/teacher/student/{student_id}/results")
def view_student_all_results(
    student_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """View all exam results for a specific student (teacher only)"""
    if not current_user or (hasattr(current_user, 'role') and current_user.role != "teacher") or (isinstance(current_user, dict) and current_user["role"] != "teacher"):
        raise HTTPException(status_code=403, detail="Only teachers can view all student results")
        
    # Get all exams and answers for the student
    results = db.query(
        Exam,
        func.sum(StudentAnswer.score_earned).label('total_score'),
        func.count(StudentAnswer.id).label('questions_answered')
    ).join(StudentAnswer, Exam.exam_id == StudentAnswer.exam_id)\
     .filter(StudentAnswer.student_id == student_id)\
     .group_by(Exam.exam_id)\
     .all()
     
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    return {
        "student_id": student_id,
        "student_name": student.username,
        "exams": [
            {
                "exam_id": exam.exam_id,
                "exam_name": exam.exam_name,
                "exam_date": exam.exam_date.isoformat(),
                "total_score": float(total_score) if total_score else 0.0,
                "questions_answered": questions_answered
            }
            for exam, total_score, questions_answered in results
        ]
    }

# Result viewing routes
@router.get("/api/exams/list")
def list_exams(db: Session = Depends(get_db)):
    """List all exams with basic information"""
    try:
        exams = db.query(Exam).all()
        return [{
            "exam_id": exam.exam_id,
            "exam_name": exam.exam_name,
            "created_at": exam.created_at,
        } for exam in exams]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Student exams endpoint
@router.get("/student/exams/")
def get_student_exams(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get all exams attended by the current student
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if (hasattr(current_user, 'role') and current_user.role != "student") or (isinstance(current_user, dict) and current_user["role"] != "student"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get student ID from the current user
    if hasattr(current_user, 'id'):
        student_id = current_user.id
    elif isinstance(current_user, dict):
        student_id = current_user["id"]
    else:
        raise HTTPException(status_code=500, detail="Invalid user object type")
    
    # Query the database for exams that the student has attended
    # This assumes there's a StudentAnswer table that links students to exams
    student_exams_query = (
        db.query(
            Exam.id,
            Exam.exam_name.label("name"),
            User.username.label("teacher_name"),
            Exam.exam_date.label("date"),
        )
        .join(StudentAnswer, StudentAnswer.exam_id == Exam.id)
        .join(User, User.id == Exam.teacher_id)
        .filter(StudentAnswer.student_id == student_id)
        .distinct()
        .all()
    )
    
    # Format the results
    exams = []
    for exam in student_exams_query:
        # Check if the exam has been evaluated
        result = db.query(StudentAnswer).filter(
            StudentAnswer.exam_id == exam.id,
            StudentAnswer.student_id == student_id,
            StudentAnswer.score.isnot(None)  # Check if score is not null
        ).first()
        
        # Calculate the total score and determine if passed
        total_score = None
        passed = None
        if result:
            # Get all answers for this exam by this student
            answers = db.query(StudentAnswer).filter(
                StudentAnswer.exam_id == exam.id,
                StudentAnswer.student_id == student_id
            ).all()
            
            # Sum up the scores
            if answers:
                scores = [a.score for a in answers if a.score is not None]
                if scores:
                    total_score = sum(scores)
                    
                    # Get pass marks for this exam
                    exam_details = db.query(Exam).filter(Exam.id == exam.id).first()
                    if exam_details and exam_details.pass_marks is not None:
                        passed = total_score >= exam_details.pass_marks
        
        exams.append({
            "id": str(exam.id),
            "name": exam.name,
            "teacher_name": exam.teacher_name,
            "date": exam.date.isoformat() if exam.date else None,
            "result": f"{total_score}" if total_score is not None else None,
            "passed": passed
        })
    
    return {"exams": exams}

@router.get("/api/exams/{exam_id}/results/summary")
def get_exam_results_summary(exam_id: str, db: Session = Depends(get_db)):
    """Get summary of all students' results for an exam, including pass/fail and grades"""
    try:
        # Get exam details
        exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        # Get all student answers for this exam
        results = []
        student_answers = db.query(StudentAnswer).filter(
            StudentAnswer.exam_id == exam_id
        ).all()

        # Group answers by student
        student_scores = {}
        for answer in student_answers:
            if answer.student_id not in student_scores:
                student_scores[answer.student_id] = {
                    "total_score": 0,
                    "student": answer.student
                }
            student_scores[answer.student_id]["total_score"] += answer.score_earned or 0

        # Function to determine grade based on percentage
        def calculate_grade(percentage):
            if percentage >= 90:
                return "A+"
            elif percentage >= 80:
                return "A"
            elif percentage >= 70:
                return "B+"
            elif percentage >= 60:
                return "B"
            elif percentage >= 50:
                return "C"
            return "Fail"

        # Format results
        for student_id, data in student_scores.items():
            total_score = round(data["total_score"], 2)
            percentage = (total_score / exam.total_marks) * 100
            grade = calculate_grade(percentage)
            passed = total_score >= exam.pass_marks

            results.append({
                "student_id": student_id,
                "student_name": data["student"].username,
                "total_score": total_score,
                "max_score": exam.total_marks,
                "percentage": round(percentage, 2),
                "grade": grade,
                "status": "Passed" if passed else "Failed"
            })

        return {
            "exam_id": exam_id,
            "exam_title": exam.exam_name,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/api/exams/{exam_id}/results/students/{student_id}")
def get_student_exam_detail(exam_id: str, student_id: str, db: Session = Depends(get_db)):
    """Get detailed results for a specific student in an exam"""
    try:
        # Verify exam exists
        exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        # Get student details
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get all answers grouped by section
        answers = db.query(StudentAnswer).filter(
            StudentAnswer.exam_id == exam_id,
            StudentAnswer.student_id == student_id
        ).all()

        # Group answers by section
        sections = {}
        total_score = 0
        for answer in answers:
            if answer.section_type not in sections:
                sections[answer.section_type] = []
            
            question = answer.question
            score_earned = answer.score_earned or 0  # Avoid None values
            total_score += score_earned

            answer_detail = {
                "question_id": str(question.id),
                "question_text": question.question_text,
                "score_earned": score_earned,
                "max_score": question.score
            }

            if question.question_type.lower() == 'mcq':
                answer_detail.update({
                    "selected_option": answer.selected_option,
                    "correct_option": question.correct_option
                })
            else:
                answer_detail.update({
                    "typed_answer": answer.typed_answer,
                    "answer_key": question.answer_key if hasattr(question, "answer_key") else None,
                    "feedback": answer.feedback if hasattr(answer, "feedback") else None
                })
            
            sections[answer.section_type].append(answer_detail)

        # Calculate percentage and determine pass/fail status
        percentage = (total_score / exam.total_marks) * 100
        passed = total_score >= exam.pass_marks

        # Function to determine grade based on percentage
        def calculate_grade(percentage):
            if percentage >= 90:
                return "A+"
            elif percentage >= 80:
                return "A"
            elif percentage >= 70:
                return "B+"
            elif percentage >= 60:
                return "B"
            elif percentage >= 50:
                return "C"
            return "Fail"

        grade = calculate_grade(percentage)

        return {
            "exam_id": exam_id,
            "exam_title": exam.exam_name,
            "student_id": student_id,
            "student_name": f"{student.username}",  # Corrected student name formatting
            "total_score": round(total_score, 2),
            "max_score": exam.total_marks,
            "percentage": round(percentage, 2),
            "grade": grade,
            "status": "Passed" if passed else "Failed",
            "sections": sections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/students/{student_id}/results")
def get_student_all_results(student_id: str, db: Session = Depends(get_db)):
    """Get all exam results for a specific student"""
    try:
        # Verify student exists
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get all answers grouped by exam
        answers = db.query(StudentAnswer).filter(
            StudentAnswer.student_id == student_id
        ).all()

        # Group by exam
        exam_results = {}
        for answer in answers:
            if answer.exam_id not in exam_results:
                exam_results[answer.exam_id] = {
                    "exam_id": answer.exam_id,
                    "exam_name": answer.exam.exam_name,
                    "total_score": 0,
                    "max_score": answer.exam.total_marks,
                    "date": answer.exam.created_at
                }
            exam_results[answer.exam_id]["total_score"] += answer.score_earned or 0

        return {
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "results": list(exam_results.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migrate_exam_ids")
def migrate_exam_ids(db: Session = Depends(get_db)):
    """Temporary endpoint to migrate old exam IDs to new format"""
    exams = db.query(Exam).all()
    updated = []
    for exam in exams:
        if not exam.exam_id.startswith('EX'):
            new_id = f"EX{random.randint(100, 999)}"
            # Update all related records
            student_answers = db.query(StudentAnswer).filter(StudentAnswer.exam_id == exam.exam_id).all()
            for answer in student_answers:
                answer.exam_id = new_id
            
            # Store the original question_bank_id before making changes
            original_question_bank_id = exam.question_bank_id
            
            # Update the exam ID
            exam.exam_id = new_id
            
            # Ensure question_bank_id is preserved
            if exam.question_bank_id is None and original_question_bank_id is not None:
                exam.question_bank_id = original_question_bank_id
            elif exam.question_bank_id is None:
                # If it was null before, we need to provide a valid value
                # Use a default question bank or create one if needed
                default_question_bank = db.query(QuestionBank).first()
                if default_question_bank:
                    exam.question_bank_id = default_question_bank.id
                else:
                    # Log error if no question bank exists - this needs admin intervention
                    print(f"ERROR: Cannot update exam {new_id} - no question bank available")
                    continue
            
            updated.append({"old_id": exam.exam_id, "new_id": new_id})
    db.commit()
    return {"message": "Exam IDs migrated", "updated": updated}

@router.get("/fix_exam/{exam_id}")
def fix_exam(exam_id: str, db: Session = Depends(get_db)):
    """Fix a specific exam by providing a valid question_bank_id if it's NULL"""
    try:
        # Find the exam
        exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
        if not exam:
            return {"success": False, "message": f"Exam with ID {exam_id} not found"}
        
        # Check if the question_bank_id is NULL
        if exam.question_bank_id is None:
            # Find a valid question bank to use
            default_question_bank = db.query(QuestionBank).first()
            if not default_question_bank:
                return {"success": False, "message": "No question banks found in the database. Please create one first."}
            
            # Update the exam with a valid question_bank_id
            exam.question_bank_id = default_question_bank.id
            db.commit()
            
            return {
                "success": True, 
                "message": f"Fixed exam with ID {exam_id}. Set question_bank_id to {default_question_bank.id}"
            }
        else:
            return {"success": True, "message": f"Exam already has a valid question_bank_id: {exam.question_bank_id}"}
    
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error fixing exam: {str(e)}"}

@router.get("/fix_all_exams")
def fix_all_exams(db: Session = Depends(get_db)):
    """Fix all exams with NULL question_bank_id"""
    try:
        # Find a valid question bank to use
        default_question_bank = db.query(QuestionBank).first()
        if not default_question_bank:
            return {"success": False, "message": "No question banks found in the database. Please create one first."}
        
        # Find all exams with NULL question_bank_id
        exams_to_fix = db.query(Exam).filter(Exam.question_bank_id == None).all()
        fixed_count = 0
        
        for exam in exams_to_fix:
            exam.question_bank_id = default_question_bank.id
            fixed_count += 1
        
        db.commit()
        
        if fixed_count > 0:
            return {"success": True, "message": f"Fixed {fixed_count} exams with NULL question_bank_id"}
        else:
            return {"success": True, "message": "No exams needed fixing"}
    
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error fixing exams: {str(e)}"}

app.include_router(router)