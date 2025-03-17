from .database import SQLALCHEMY_DATABASE_URL
from .mdl import Base, StudentAnswer
from sqlalchemy import create_engine, Column, Float, Boolean, DateTime

def upgrade():
    # Create engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Add new columns
    with engine.begin() as connection:
        connection.execute("""
            ALTER TABLE student_answers 
            ADD COLUMN score_earned FLOAT;
        """)
        connection.execute("""
            ALTER TABLE student_answers 
            ADD COLUMN is_evaluated BOOLEAN DEFAULT FALSE;
        """)
        connection.execute("""
            ALTER TABLE student_answers 
            ADD COLUMN evaluation_timestamp DATETIME;
        """)

def downgrade():
    # Create engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # Remove columns
    with engine.begin() as connection:
        connection.execute("ALTER TABLE student_answers DROP COLUMN score_earned;")
        connection.execute("ALTER TABLE student_answers DROP COLUMN is_evaluated;")
        connection.execute("ALTER TABLE student_answers DROP COLUMN evaluation_timestamp;")
