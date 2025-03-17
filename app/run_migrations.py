from migrations.add_evaluation_columns import upgrade

if __name__ == "__main__":
    print("Running database migrations...")
    try:
        upgrade()
        print("Successfully added evaluation columns to student_answers table")
    except Exception as e:
        print(f"Error during migration: {str(e)}")
