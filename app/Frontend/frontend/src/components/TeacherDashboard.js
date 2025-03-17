import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../auth.css';
import './Dashboard.css';

const TeacherDashboard = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');

  // Check if user is authenticated and has the correct role
  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const storedUsername = localStorage.getItem('username');
    
    if (token && role === 'teacher') {
      setUsername(storedUsername || 'Teacher');
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    window.location.href = '/login';
  };

  const handleQuestionBankClick = () => {
    navigate('/create-question-bank');
  };

  const handleExamsClick = () => {
    // Navigate to exams page
    console.log('Navigate to exams');
  };

  const handleResultsClick = () => {
    // Navigate to results page
    console.log('Navigate to results');
  };

  return (
    <div className="dashboard-container">
      {/* Header with logo and teacher name */}
      <div className="dashboard-header">
        <div className="header-left">
          <img 
            src="/logo.jpg" 
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
        <h2 className="dashboard-title">Teacher Dashboard</h2>
        <p className="welcome-text">Welcome, {username}!</p>
        
        <div className="dashboard-cards">
          {/* Question Bank Box */}
          <div className="dashboard-card">
            <div className="card-content">
              <img src="/books.png" alt="Question Bank" className="card-image" />
              <h3 className="card-title">Question Bank</h3>
              <p className="card-subtitle">Create, view, and organize your question banks</p>
              <button className="card-button" onClick={handleQuestionBankClick}>
                Manage Question Bank
              </button>
            </div>
          </div>
          
          {/* Exams Box */}
          <div className="dashboard-card">
            <div className="card-content">
              <img src="/exam.png" alt="Exams" className="card-image" />
              <h3 className="card-title">Exams</h3>
              <p className="card-subtitle">Create, schedule, and manage exams</p>
              <button className="card-button" onClick={handleExamsClick}>
                Manage Exams
              </button>
            </div>
          </div>
          
          {/* Results Box */}
          <div className="dashboard-card">
            <div className="card-content">
              <img src="/result.png" alt="Results" className="card-image" />
              <h3 className="card-title">Results</h3>
              <p className="card-subtitle">Check student scores and evaluation reports</p>
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

export default TeacherDashboard;
