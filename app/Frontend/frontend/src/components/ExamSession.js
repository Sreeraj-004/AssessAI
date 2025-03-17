import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './ExamSession.css';

const ExamPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [examId, setExamId] = useState('');
  const [examName, setExamName] = useState('');
  const [questions, setQuestions] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentSection, setCurrentSection] = useState('MCQ');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [username, setUsername] = useState('');
  const timerRef = useRef(null);

  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState({});
  const [feedback, setFeedback] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [wordCounts, setWordCounts] = useState({});
  const [progress, setProgress] = useState(0);
  
  // Refs for text areas to handle auto-resizing
  const textAreaRefs = useRef({});

  // Format time remaining into HH:MM:SS
  const formatTimeRemaining = useCallback((seconds) => {
    if (seconds === null) return '--:--:--';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    navigate('/login');
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUsername = localStorage.getItem('username');
    if (!token) {
      navigate('/login');
      return;
    }
    setUsername(storedUsername || 'Student');

    const idFromState = location.state?.examId;
    const nameFromState = location.state?.examName;
    const timeFromState = location.state?.timeRemaining;

    if (!idFromState) {
      setError('No exam ID provided');
      setLoading(false);
      return;
    }

    setExamId(idFromState);
    if (nameFromState) setExamName(nameFromState);
    if (timeFromState) setTimeRemaining(timeFromState);
    
    // Fetch exam details and questions
    const fetchExamDetails = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/exam/${idFromState}/section/${currentSection}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch exam details');
        }

        const data = await response.json();
        
        if (!data.questions || !Array.isArray(data.questions)) {
          throw new Error('Invalid exam data received');
        }

        setQuestions(data.questions);
        
        // Initialize answers and submitted state for each question
        const initialAnswers = {};
        const initialSubmitted = {};
        data.questions.forEach(q => {
          initialAnswers[q.id] = '';
          initialSubmitted[q.id] = false;
        });
        setAnswers(prev => ({ ...prev, ...initialAnswers }));
        setSubmitted(prev => ({ ...prev, ...initialSubmitted }));
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching exam:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchExamDetails();

    // Set up countdown timer
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          submitAllAnswers();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    timerRef.current = timer;

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [navigate, location, currentSection]);

  // Update progress whenever answers change
  useEffect(() => {
    const answeredCount = Object.values(answers).filter(answer => answer.trim()).length;
    const totalQuestions = questions.length;
    const newProgress = totalQuestions ? Math.round((answeredCount / totalQuestions) * 100) : 0;
    setProgress(newProgress);
  }, [answers, questions]);

  // Handle answer changes
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));

    // Update word count for the answer
    const words = value.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCounts(prev => ({
      ...prev,
      [questionId]: words.length
    }));

    // Auto-resize textarea
    const textArea = textAreaRefs.current[questionId];
    if (textArea) {
      textArea.style.height = 'auto';
      textArea.style.height = textArea.scrollHeight + 'px';
    }
  };

  // Navigate between questions
  const navigateQuestion = (direction) => {
    const newIndex = currentQuestionIndex + direction;
    if (newIndex >= 0 && newIndex < questions.length) {
      setCurrentQuestionIndex(newIndex);
    }
  };

  // Submit an individual answer
  const submitAnswer = async (questionId) => {
    if (submitted[questionId] || !answers[questionId]) return;

    setSubmitting(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/exam/submit-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          exam_id: examId,
          question_id: questionId,
          answer: answers[questionId]
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit answer');
      }

      const data = await response.json();
      
      setSubmitted(prev => ({
        ...prev,
        [questionId]: true
      }));
      
      setFeedback(prev => ({
        ...prev,
        [questionId]: {
          type: 'success',
          message: data.feedback || 'Answer submitted successfully'
        }
      }));

      // Move to next question if available
      if (currentQuestionIndex < questions.length - 1) {
        navigateQuestion(1);
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
      setFeedback(prev => ({
        ...prev,
        [questionId]: {
          type: 'error',
          message: 'Failed to submit answer: ' + err.message
        }
      }));
    } finally {
      setSubmitting(false);
    }
  };

  // Submit all remaining answers
  const submitAllAnswers = async () => {
    const unsubmittedQuestions = questions
      .map(q => q.id)
      .filter(id => !submitted[id] && answers[id]);

    if (unsubmittedQuestions.length === 0) {
      navigate('/exam-results', { state: { examId } });
      return;
    }

    setSubmitting(true);
    try {
      for (const questionId of unsubmittedQuestions) {
        await submitAnswer(questionId);
      }
      navigate('/exam-results', { state: { examId } });
    } catch (err) {
      setError('Failed to submit all answers. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="exam-page">
        <div className="loading">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading exam...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="exam-page">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/student-exams')} className="back-button">
          Back to Exams
        </button>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="exam-page">
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

      <div className="exam-header">
        <h1>{examName || 'Exam Session'}</h1>
        <div className="exam-info">
          <div className="progress-indicator">
            Progress: {progress}%
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
          <div className="timer">
            Time Remaining: {formatTimeRemaining(timeRemaining)}
          </div>
        </div>
      </div>

      <div className="exam-content">
        <div className="question-navigation">
          <button 
            onClick={() => navigateQuestion(-1)} 
            disabled={currentQuestionIndex === 0}
            className="nav-button prev"
          >
            Previous
          </button>
          <span className="question-counter">
            Question {currentQuestionIndex + 1} of {questions.length}
          </span>
          <button 
            onClick={() => navigateQuestion(1)} 
            disabled={currentQuestionIndex === questions.length - 1}
            className="nav-button next"
          >
            Next
          </button>
        </div>

        {currentQuestion && (
          <div className="question-card">
            <div className="question-header">
              <h3>Question {currentQuestionIndex + 1}</h3>
              {currentQuestion.max_words && (
                <div className="word-count">
                  Words: {wordCounts[currentQuestion.id] || 0} / {currentQuestion.max_words}
                </div>
              )}
            </div>

            <div className="question-content">
              <p>{currentQuestion.text}</p>
              {currentQuestion.image_url && (
                <img 
                  src={currentQuestion.image_url} 
                  alt="Question illustration" 
                  className="question-image"
                />
              )}
            </div>

            <div className="answer-section">
              <textarea
                ref={el => textAreaRefs.current[currentQuestion.id] = el}
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                placeholder="Type your answer here..."
                disabled={submitted[currentQuestion.id]}
                maxLength={currentQuestion.max_words ? currentQuestion.max_words * 7 : undefined}
              />

              {feedback[currentQuestion.id] && (
                <div className={`feedback ${feedback[currentQuestion.id].type}`}>
                  {feedback[currentQuestion.id].message}
                </div>
              )}

              <button
                className={`submit-button ${submitted[currentQuestion.id] ? 'submitted' : ''}`}
                onClick={() => submitAnswer(currentQuestion.id)}
                disabled={!answers[currentQuestion.id] || submitted[currentQuestion.id] || submitting}
              >
                {submitted[currentQuestion.id] ? 'Submitted' : submitting ? 'Submitting...' : 'Submit Answer'}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="exam-footer">
        <button
          className="submit-all-button"
          onClick={submitAllAnswers}
          disabled={submitting || Object.keys(answers).length === 0}
        >
          {submitting ? 'Submitting...' : 'Submit All & Finish'}
        </button>
      </div>
    </div>
  );
};

export default ExamPage;
