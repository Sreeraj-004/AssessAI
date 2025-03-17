from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mdl import Exam, QuestionBank, Base

# Create the database connection
DATABASE_URL = "sqlite:///./assessment.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_specific_exam():
    """Fix the specific exam that's causing the error"""
    db = SessionLocal()
    try:
        # Find the problematic exam
        problematic_exam_id = "4e6c522e-187d-4320-a752-f6ace256dcf2"
        exam = db.query(Exam).filter(Exam.exam_id == problematic_exam_id).first()
        
        if not exam:
            print(f"Exam with ID {problematic_exam_id} not found!")
            return
        
        print(f"Found exam: {exam.exam_id}, question_bank_id: {exam.question_bank_id}")
        
        # If the question_bank_id is None, find a valid question bank to use
        if exam.question_bank_id is None:
            # Find a valid question bank
            default_question_bank = db.query(QuestionBank).first()
            
            if not default_question_bank:
                print("No question banks found in the database. Please create one first.")
                return
            
            # Update the exam with a valid question_bank_id
            print(f"Setting question_bank_id to {default_question_bank.id}")
            exam.question_bank_id = default_question_bank.id
            db.commit()
            print(f"Fixed exam with ID {exam.exam_id}!")
        else:
            print(f"Exam already has a valid question_bank_id: {exam.question_bank_id}")
    
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
    finally:
        db.close()

def fix_all_exams():
    """Fix all exams with NULL question_bank_id"""
    db = SessionLocal()
    try:
        # Find a valid question bank to use
        default_question_bank = db.query(QuestionBank).first()
        if not default_question_bank:
            print("No question banks found in the database. Please create one first.")
            return
        
        # Find all exams with NULL question_bank_id 
        exams_to_fix = db.query(Exam).filter(Exam.question_bank_id == None).all()
        fixed_count = 0
        
        for exam in exams_to_fix:
            print(f"Fixing exam {exam.exam_id}")
            exam.question_bank_id = default_question_bank.id
            fixed_count += 1
        
        db.commit()
        
        if fixed_count > 0:
            print(f"Fixed {fixed_count} exams with NULL question_bank_id")
        else:
            print("No exams needed fixing")
    
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting exam fix script...")
    fix_specific_exam()
    fix_all_exams()
    print("Done!")
