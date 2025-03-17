-- Add feedback column to student_answers table
ALTER TABLE student_answers
ADD COLUMN IF NOT EXISTS feedback JSON;
