from sqlalchemy import create_engine, text
from pathlib import Path

# Database configuration
instance_dir = Path(__file__).parent.parent / "instance"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{instance_dir}/app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def migrate():
    with engine.connect() as connection:
        # Create new table with the additional columns
        connection.execute(text("""
            CREATE TABLE exams_new (
                exam_id VARCHAR PRIMARY KEY,
                teacher_id VARCHAR NOT NULL,
                question_bank_id VARCHAR NOT NULL,
                exam_name VARCHAR NOT NULL,
                exam_date DATETIME NOT NULL,
                sections JSON NOT NULL,
                pass_marks FLOAT,
                total_marks FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(teacher_id) REFERENCES users(id),
                FOREIGN KEY(question_bank_id) REFERENCES question_banks(id)
            )
        """))
        
        # Copy data from old table to new table
        connection.execute(text("""
            INSERT INTO exams_new (
                exam_id, teacher_id, question_bank_id, exam_name, 
                exam_date, sections, created_at
            )
            SELECT exam_id, teacher_id, question_bank_id, exam_name, 
                   exam_date, sections, created_at
            FROM exams
        """))
        
        # Drop old table
        connection.execute(text("DROP TABLE exams"))
        
        # Rename new table to original name
        connection.execute(text("ALTER TABLE exams_new RENAME TO exams"))
        
        connection.commit()

if __name__ == "__main__":
    migrate()
