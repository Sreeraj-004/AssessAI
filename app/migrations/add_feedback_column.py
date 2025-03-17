import sqlite3
import os
from pathlib import Path

# Get the database path
db_path = Path(__file__).parent.parent / "instance" / "app.db"

def add_feedback_column():
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if the column exists
        cursor.execute("PRAGMA table_info(student_answers)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        # Add the column if it doesn't exist
        if 'feedback' not in column_names:
            cursor.execute('ALTER TABLE student_answers ADD COLUMN feedback TEXT')
            print("Successfully added feedback column")
        else:
            print("Feedback column already exists")

        # Commit the changes
        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    add_feedback_column()
