from sqlalchemy import create_engine, text
from pathlib import Path

# Database configuration
instance_dir = Path(__file__).parent.parent / "instance"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{instance_dir}/app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def migrate():
    with engine.connect() as connection:
        # Create new table with the additional column
        connection.execute(text("""
            CREATE TABLE student_answers_new (
                id VARCHAR PRIMARY KEY,
                student_id VARCHAR NOT NULL,
                exam_id VARCHAR NOT NULL,
                question_id VARCHAR NOT NULL,
                selected_option VARCHAR,
                typed_answer TEXT,
                section_type VARCHAR NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                score_earned FLOAT,
                is_evaluated BOOLEAN DEFAULT 0,
                has_passed BOOLEAN,
                evaluation_timestamp DATETIME,
                feedback TEXT,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(exam_id) REFERENCES exams(exam_id),
                FOREIGN KEY(question_id) REFERENCES questions(id)
            )
        """))
        
        # Copy data from old table to new table
        connection.execute(text("""
            INSERT INTO student_answers_new (
                id, student_id, exam_id, question_id, selected_option,
                typed_answer, section_type, timestamp, score_earned,
                is_evaluated, evaluation_timestamp, feedback
            )
            SELECT id, student_id, exam_id, question_id, selected_option,
                   typed_answer, section_type, timestamp, score_earned,
                   is_evaluated, evaluation_timestamp, feedback
            FROM student_answers
        """))
        
        # Drop old table
        connection.execute(text("DROP TABLE student_answers"))
        
        # Rename new table to original name
        connection.execute(text("ALTER TABLE student_answers_new RENAME TO student_answers"))
        
        connection.commit()

if __name__ == "__main__":
    migrate()
