import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './StudentExams.css'; // Reusing the same CSS for now

const StudentResults = () => {
  const navigate = useNavigate();
  const [examResults, setExamResults] = useState([]);
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
    
    // Fetch exam results
    fetchExamResults(token);
  }, [navigate]);

  const fetchExamResults = async (token) => {
    try {
      setLoading(true);
      // This is a placeholder - you'll need to implement the actual API call
      const response = await fetch('http://127.0.0.1:8000/student/results/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch results');
      }

      const data = await response.json();
      setExamResults(data.results || []);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/student-dashboard');
  };

  return (
    <div className="exams-container">
      <div className="exams-header">
        <button className="back-button" onClick={handleBackToDashboard}>
          Back to Dashboard
        </button>
        <h1>Exam Results</h1>
        <div></div> {/* Empty div for flex spacing */}
      </div>

      <div className="exams-table-container">
        <h2>Your Exam Results</h2>
        
        {loading ? (
          <p className="loading-message">Loading your results...</p>
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : examResults.length === 0 ? (
          <p className="no-exams-message">You don't have any exam results yet.</p>
        ) : (
          <table className="exams-table">
            <thead>
              <tr>
                <th>Exam Name</th>
                <th>Date</th>
                <th>Score</th>
                <th>Status</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {examResults.map((result) => (
                <tr key={result.id}>
                  <td>{result.exam_name}</td>
                  <td>{new Date(result.date).toLocaleDateString()}</td>
                  <td>{result.score}</td>
                  <td>
                    <span className={`result ${result.passed ? 'passed' : 'failed'}`}>
                      {result.passed ? 'Passed' : 'Failed'}
                    </span>
                  </td>
                  <td>
                    <button 
                      className="view-details-button"
                      onClick={() => navigate(`/result-details/${result.id}`)}
                    >
                      View Details
                    </button>
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

export default StudentResults;
