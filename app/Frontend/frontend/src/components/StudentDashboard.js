import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../auth.css';
import './Dashboard.css';

const StudentDashboard = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [showProfileTooltip, setShowProfileTooltip] = useState(false);

  // Check if user is authenticated and has the correct role
  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const storedUsername = localStorage.getItem('username');
    
    if (!token || role !== 'student') {
      navigate('/login');
    } else {
      setUsername(storedUsername || 'Student');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    navigate('/login');
  };

  const handleExamClick = () => {
    navigate('/student-exams');
  };

  const handleResultsClick = () => {
    navigate('/student-results');
  };

  return (
    <div className="dashboard-container">
      {/* Header with logo and student name */}
      <div className="dashboard-header">
        <div className="header-left">
          <img 
            src="/Logo 2.jpg" 
            alt="AssessAI Logo" 
            className="dashboard-logo" 
          />
        </div>
        <div className="header-right">
          <span className="student-name">{username}</span>
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </div>

      <div className="dashboard-content">
        <h2 className="dashboard-title">Student Dashboard</h2>
        <p className="welcome-text">Welcome, {username}!</p>
        
        <div className="dashboard-cards">
          {/* Exam Box */}
          <div className="dashboard-card">
            <div className="card-content">
              <img src="/exam.png" alt="Exam" className="card-image" />
              <h3 className="card-title">Exam</h3>
              <p className="card-subtitle">Attend and view exams here</p>
              <button className="card-button" onClick={handleExamClick}>
                Manage Exams
              </button>
            </div>
          </div>
          
          {/* Results Box */}
          <div className="dashboard-card">
            <div className="card-content">
              <img src="/result.png" alt="Results" className="card-image" />
              <h3 className="card-title">Results</h3>
              <p className="card-subtitle">View results of attended exams</p>
              <button className="card-button" onClick={handleResultsClick}>
                View Results
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
