import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './StudentExams.css';

const StudentExams = () => {
  const navigate = useNavigate();
  const [attendedExams, setAttendedExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [username, setUsername] = useState('');

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const storedUsername = localStorage.getItem('username');
    
    if (!token || role !== 'student') {
      navigate('/login');
      return;
    }
    
    setUsername(storedUsername || 'Student');
    
    // Fetch attended exams
    fetchAttendedExams(token);
  }, [navigate]);

  const fetchAttendedExams = async (token) => {
    try {
      setLoading(true);
      // Get current user ID from token or localStorage if available
      // This is a placeholder - you'll need to implement the actual API call
      const response = await fetch('http://127.0.0.1:8000/student/exams/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch exams');
      }

      const data = await response.json();
      setAttendedExams(data.exams || []);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleAttendExam = () => {
    navigate('/attend-exam');
  };

  const handleBackToDashboard = () => {
    navigate('/student-dashboard');
  };

  return (
    <div className="exams-container">
      <div className="exams-header">
        <img src="/logo.jpg" alt="Assess AI Logo" className="logo" />
        <button className="back-button" onClick={handleBackToDashboard}>
          Back to Dashboard
        </button>
        <h1>Student Exams</h1>
        <div></div> {/* Empty div for flex spacing */}
      </div>

      <div className="attend-exam-section">
        <button className="attend-exam-button" onClick={handleAttendExam}>
          Attend Exam
        </button>
      </div>

      <div className="exams-table-container">
        <h2>Attended Exams</h2>
        
        {loading ? (
          <p className="loading-message">Loading your exams...</p>
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : attendedExams.length === 0 ? (
          <p className="no-exams-message">You haven't attended any exams yet.</p>
        ) : (
          <table className="exams-table">
            <thead>
              <tr>
                <th>Exam Name</th>
                <th>Teacher Name</th>
                <th>Date</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {attendedExams.map((exam) => (
                <tr key={exam.id}>
                  <td>{exam.name}</td>
                  <td>{exam.teacher_name}</td>
                  <td>{new Date(exam.date).toLocaleDateString()}</td>
                  <td>
                    {exam.result ? (
                      <span className={`result ${exam.passed ? 'passed' : 'failed'}`}>
                        {exam.result}
                      </span>
                    ) : (
                      <span className="pending">Pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default StudentExams;
