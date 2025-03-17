import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './WaitingLobby.css';

const WaitingLobby = ({ examId }) => {
    const [timeRemaining, setTimeRemaining] = useState(null);
    const [examName, setExamName] = useState('');
    const [error, setError] = useState(null);
    const [username, setUsername] = useState('');
    const navigate = useNavigate();

    // Function to format time remaining into HH:MM:SS
    const formatTimeRemaining = (seconds) => {
        if (seconds === null) return '--:--:--';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        navigate('/login');
    };

    // Function to check exam status
    const checkExamStatus = useCallback(async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`http://localhost:8000/exam/${examId}`, {
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch exam status');
            }

            const data = await response.json();
            const { status, time_remaining, exam_name } = data;
            
            if (status === 'running') {
                // Exam has started, redirect to exam page
                navigate(`/exam/${examId}`);
                return;
            }

            setTimeRemaining(time_remaining);
            setExamName(exam_name);

        } catch (err) {
            setError(err.message || 'An error occurred while checking exam status');
        }
    }, [examId, navigate]);

    // Effect to initialize and update countdown
    useEffect(() => {
        const token = localStorage.getItem('token');
        const storedUsername = localStorage.getItem('username');
        if (!token) {
            navigate('/login');
            return;
        }
        setUsername(storedUsername || 'Student');

        // Initial check
        checkExamStatus();

        // Set up interval for countdown
        const timer = setInterval(() => {
            setTimeRemaining(prev => {
                if (prev === null || prev <= 1) {
                    // When timer reaches 0, check exam status
                    checkExamStatus();
                    return prev;
                }
                return prev - 1;
            });
        }, 1000);

        // Set up interval to check exam status
        const statusCheck = setInterval(checkExamStatus, 30000);

        return () => {
            clearInterval(timer);
            clearInterval(statusCheck);
        };
    }, [checkExamStatus]);

    if (error) {
        return (
            <div className="waiting-lobby error">
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
                <div className="error-message">{error}</div>
                <button className="back-button" onClick={() => navigate('/dashboard')}>
                    Back to Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="waiting-lobby">
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

            <div className="content">
                <h1>{examName || 'Loading exam...'}</h1>
                <div className="timer">
                    <div className="time-display">{formatTimeRemaining(timeRemaining)}</div>
                    <div className="time-label">Until Exam Starts</div>
                </div>
                <div className="instructions">
                    <h2>Instructions</h2>
                    <ul>
                        <li>Please remain on this page until the exam starts</li>
                        <li>You will be automatically redirected when the exam begins</li>
                        <li>Ensure you have a stable internet connection</li>
                        <li>Have your materials ready before the exam starts</li>
                    </ul>
                </div>
            </div>
            <div className="animation-container">
                <div className="circle circle1"></div>
                <div className="circle circle2"></div>
                <div className="circle circle3"></div>
            </div>
        </div>
    );
};

export default WaitingLobby;
