import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AttendExam.css';

const AttendExam = () => {
  const navigate = useNavigate();
  const [examId, setExamId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    
    if (!token || role !== 'student') {
      navigate('/login');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!examId.trim()) {
      setError('Please enter an exam ID');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      
      // First, check if the exam exists and is accessible
      const response = await fetch(`http://127.0.0.1:8000/exam/${examId.trim()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to access exam');
      }

      // If the exam exists, check if it's started
      if (data.message && data.message.includes('not started yet')) {
        // Extract exam name if available
        const examName = data.message.match(/exam '([^']+)'/)?.[1] || 'Upcoming Exam';
        
        // Navigate to waiting lobby
        navigate('/waiting-lobby', { 
          state: { 
            examInfo: {
              examId: examId.trim(),
              examName: examName
            }
          }
        });
        return;
      }

      // If exam has started, confirm entry
      const confirmResponse = await fetch('http://127.0.0.1:8000/exam/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ exam_id: examId.trim() })
      });

      const confirmData = await confirmResponse.json();

      if (!confirmResponse.ok) {
        throw new Error(confirmData.detail || 'Failed to confirm exam entry');
      }

      if (confirmData.status === 'success') {
        // Redirect to exam session
        navigate('/exam-session', { 
          state: { 
            examId: examId.trim(),
            examName: data.message.match(/exam '([^']+)'/)?.[1] || 'Current Exam'
          } 
        });
      } else {
        setError('Could not start the exam. Please try again.');
      }
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/student-exams');
  };

  return (
    <div className="attend-exam-container">
      <div className="attend-exam-card">
        <h2>Attend Exam</h2>
        <p className="attend-exam-instruction">
          Enter the Exam ID provided by your teacher to attend the exam.
        </p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="examId">Exam ID:</label>
            <input
              type="text"
              id="examId"
              value={examId}
              onChange={(e) => setExamId(e.target.value)}
              placeholder="Enter exam ID"
              disabled={loading}
              required
            />
          </div>

          <div className="form-buttons">
            <button 
              type="button" 
              className="cancel-button" 
              onClick={handleCancel}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Attend Exam'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AttendExam;
