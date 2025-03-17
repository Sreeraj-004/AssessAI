import sqlite3
from pathlib import Path

# Get the path to the database file
db_path = Path(__file__).parent / "instance" / "app.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='student_answers';")
result = cursor.fetchone()
print("Table Schema:")
print(result[0] if result else "Table not found!")

# Try to get column info
try:
    cursor.execute("PRAGMA table_info(student_answers);")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"Column {col[0]}: {col[1]} ({col[2]})")
except sqlite3.OperationalError as e:
    print(f"\nError: {e}")

conn.close()
