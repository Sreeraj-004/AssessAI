import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ManageQuestionBank.css';

const ManageQuestionBank = () => {
  const [mcqs, setMcqs] = useState([{ question: "", score: "", correctOption: "", options: [""] }]);
  const [paragraphs, setParagraphs] = useState([{ question: "", score: "", minWords: "", maxWords: "", answerKey: "" }]);
  const [essays, setEssays] = useState([{ question: "", score: "", minWords: "", maxWords: "", answerKey: "" }]);
  const [questionBankId, setQuestionBankId] = useState("");
  const [token, setToken] = useState("");

  // Get question bank ID from URL or localStorage
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id') || localStorage.getItem('editQuestionBankId');
    if (id) {
      setQuestionBankId(id);
      localStorage.setItem('editQuestionBankId', id);
    }
  }, []);

  // For testing purposes, set a sample question bank ID if none exists
  useEffect(() => {
    if (!localStorage.getItem("editQuestionBankId")) {
      localStorage.setItem("editQuestionBankId", "sample-qb-123");
      setQuestionBankId("sample-qb-123");
      console.log("Set sample question bank ID for testing");
    }
  }, []);

  const addMcqRow = () => {
    setMcqs([...mcqs, { question: "", score: "", correctOption: "", options: [""] }]);
  };

  const addParagraphRow = () => {
    setParagraphs([...paragraphs, { question: "", score: "", minWords: "", maxWords: "", answerKey: "" }]);
  };

  const addEssayRow = () => {
    setEssays([...essays, { question: "", score: "", minWords: "", maxWords: "", answerKey: "" }]);
  };

  const addMcqOption = (mcqIndex) => {
    const newMcqs = [...mcqs];
    newMcqs[mcqIndex].options.push("");
    setMcqs(newMcqs);
  };

  const handleMcqChange = (mcqIndex, field, value) => {
    const newMcqs = [...mcqs];
    newMcqs[mcqIndex][field] = value;
    setMcqs(newMcqs);
  };

  const handleMcqOptionChange = (mcqIndex, optionIndex, value) => {
    const newMcqs = [...mcqs];
    newMcqs[mcqIndex].options[optionIndex] = value;
    setMcqs(newMcqs);
  };

  const handleParagraphChange = (index, field, value) => {
    const newParagraphs = [...paragraphs];
    newParagraphs[index][field] = value;
    setParagraphs(newParagraphs);
  };

  const handleEssayChange = (index, field, value) => {
    const newEssays = [...essays];
    newEssays[index][field] = value;
    setEssays(newEssays);
  };

  const validateToken = (token) => {
    try {
      // Verify token structure
      if (typeof token !== 'string' || token.split('.').length !== 3) {
        console.error('Invalid token structure');
        return false;
      }

      // Decode token payload
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiration = payload.exp * 1000;

      // Check if token is expired
      if (Date.now() > expiration) {
        console.log('Token has expired');
        return false;
      }

      // Check if token is about to expire (within 5 minutes)
      if (expiration - Date.now() < 300000) {
        console.log('Token is about to expire');
        return 'refresh';
      }

      return true;
    } catch (error) {
      console.error('Error validating token:', error);
      return false;
    }
  };

  const refreshToken = async () => {
    try {
      const response = await axios.post('http://localhost:8000/refresh-token/', {
        refresh_token: localStorage.getItem('refreshToken')
      });

      localStorage.setItem('authToken', response.data.access_token);
      return true;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return false;
    }
  };

  const handleSaveMcq = async (index) => {
    try {
      // Get and validate token
      let token = localStorage.getItem('authToken');
      const tokenStatus = validateToken(token);

      if (tokenStatus === false) {
        console.log('Invalid or expired token, redirecting to login');
        localStorage.removeItem('authToken');
        window.location.href = '/login';
        return;
      }

      if (tokenStatus === 'refresh') {
        console.log('Attempting to refresh token');
        const refreshSuccess = await refreshToken();
        if (!refreshSuccess) {
          console.log('Token refresh failed, redirecting to login');
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          return;
        }
        token = localStorage.getItem('authToken');
      }

      console.log("Starting save MCQ process...");
      
      // Get the JWT token from localStorage
      console.log("Retrieved token from localStorage:", token ? "[exists]" : "[missing]");

      if (!token) {
        console.log("No token found, redirecting to login...");
        alert("Please log in first");
        window.location.href = "/login";
        return;
      }

      const mcq = mcqs[index];
      
      // Validate required fields
      if (!mcq.question || !mcq.score || !mcq.correctOption) {
        alert("Please fill in all required fields (Question, Score, and Correct Option)");
        return;
      }

      if (!questionBankId) {
        alert("Question bank ID is missing. Please make sure you accessed this page correctly.");
        return;
      }

      // Create the options object
      const optionsObject = {};
      
      // First option (correctOption) becomes option A
      optionsObject["A"] = mcq.correctOption;
      
      // Remaining options become B, C, D, etc.
      mcq.options.forEach((option, idx) => {
        if (option.trim() !== '') {  // Only include non-empty options
          const letterKey = String.fromCharCode(66 + idx); // 66 is ASCII for 'B'
          optionsObject[letterKey] = option;
        }
      });

      // Prepare the data for API
      const questionData = {
        question_bank_id: questionBankId,
        question_text: mcq.question,
        question_type: "MCQ",
        score: parseInt(mcq.score) || 0,
        options: optionsObject, // Send as object, backend expects a dict
        correct_option: "A" // Always A since we're making the first option the correct one
      };

      console.log("Sending data to API:", JSON.stringify(questionData, null, 2));

      // Add authentication headers
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };

      console.log("Making API request with headers:", headers);

      // Use the full API endpoint URL with authentication
      const response = await axios.post("http://localhost:8000/questions/", questionData, { 
        headers,
        withCredentials: true // Include cookies for authentication
      });
      
      console.log("API response received:", response.data);
      alert("MCQ saved successfully!");
    } catch (error) {
      console.error("API Error:", error);
      
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response headers:", error.response.headers);
        console.error("Response data:", error.response.data);
        
        if (error.response.status === 401) {
          console.log("Authentication failed, clearing token...");
          localStorage.removeItem('authToken');
          window.location.href = "/login";
          return;
        }
      }
      
      alert("Failed to save MCQ. Please try again.");
    }
  };

  const handleSaveParagraph = async (index) => {
    try {
      const para = paragraphs[index];
      
      // Validate required fields
      if (!para.question || !para.score) {
        alert("Please fill in all required fields (Question and Score)");
        return;
      }

      if (!questionBankId) {
        alert("Question bank ID is missing. Please make sure you accessed this page correctly.");
        return;
      }

      const questionData = {
        question_bank_id: questionBankId,
        question_text: para.question,
        question_type: "Paragraph", // Uppercase as expected by the backend
        score: parseInt(para.score) || 0,
        min_words: parseInt(para.minWords) || 0,
        max_words: parseInt(para.maxWords) || 0,
        answer_key: para.answerKey
      };

      console.log("Sending paragraph data to API:", JSON.stringify(questionData, null, 2));

      // Get the JWT token from localStorage
      const token = localStorage.getItem('authToken');
      if (!token) {
        alert("Please log in first");
        window.location.href = "/login"; // Redirect to login page
        return;
      }

      // Add authentication headers
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };

      // Use the full API endpoint URL with authentication
      const response = await axios.post("http://localhost:8000/questions/", questionData, { 
        headers,
        withCredentials: true // Include cookies for authentication
      });
      
      alert("Paragraph question saved successfully!");
      console.log("Saved paragraph:", response.data);
    } catch (error) {
      console.error("API Error:", error);
      
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response headers:", error.response.headers);
        console.error("Response data:", error.response.data);
        
        if (error.response.status === 401) {
          console.log("Authentication failed, clearing token...");
          localStorage.removeItem('authToken');
          window.location.href = "/login";
          return;
        }
      }
      
      alert("Failed to save paragraph. Please try again.");
    }
  };

  const handleSaveEssay = async (index) => {
    try {
      const essay = essays[index];
      
      // Validate required fields
      if (!essay.question || !essay.score) {
        alert("Please fill in all required fields (Question and Score)");
        return;
      }

      if (!questionBankId) {
        alert("Question bank ID is missing. Please make sure you accessed this page correctly.");
        return;
      }

      const questionData = {
        question_bank_id: questionBankId,
        question_text: essay.question,
        question_type: "Essay", // Uppercase as expected by the backend
        score: parseInt(essay.score) || 0,
        min_words: parseInt(essay.minWords) || 0,
        max_words: parseInt(essay.maxWords) || 0,
        answer_key: essay.answerKey
      };

      console.log("Sending essay data to API:", JSON.stringify(questionData, null, 2));

      // Get the JWT token from localStorage
      const token = localStorage.getItem('authToken');
      if (!token) {
        alert("Please log in first");
        window.location.href = "/login"; // Redirect to login page
        return;
      }

      // Add authentication headers
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };

      // Use the full API endpoint URL with authentication
      const response = await axios.post("http://localhost:8000/questions/", questionData, { 
        headers,
        withCredentials: true // Include cookies for authentication
      });
      
      alert("Essay question saved successfully!");
      console.log("Saved essay:", response.data);
    } catch (error) {
      console.error("API Error:", error);
      
      if (error.response) {
        console.error("Response status:", error.response.status);
        console.error("Response headers:", error.response.headers);
        console.error("Response data:", error.response.data);
        
        if (error.response.status === 401) {
          console.log("Authentication failed, clearing token...");
          localStorage.removeItem('authToken');
          window.location.href = "/login";
          return;
        }
      }
      
      alert("Failed to save essay. Please try again.");
    }
  };

  return (
    <div className="manage-question-bank-container">
      <div className="manage-question-bank">
        <img src={process.env.PUBLIC_URL + "/logo.jpg"} alt="AssessAI Logo" className="logo" />
        <h1 className="title">Question Bank</h1>
        
        {/* MCQ Section */}
        <div className="question-section">
          <h2>MCQ</h2>
          <div className="question-box">
            {mcqs.map((mcq, index) => (
              <div key={index} className="question-row">
                <input 
                  type="text" 
                  placeholder="Question" 
                  value={mcq.question} 
                  onChange={(e) => handleMcqChange(index, "question", e.target.value)} 
                />
                <input 
                  type="number" 
                  placeholder="Score" 
                  value={mcq.score} 
                  onChange={(e) => handleMcqChange(index, "score", e.target.value)} 
                />
                <div className="options-container">
                  {/* First option (Correct Option) */}
                  <div className="option-row">
                    <label>Correct Option (A):</label>
                    <input 
                      type="text" 
                      placeholder="First option (correct)" 
                      value={mcq.correctOption} 
                      onChange={(e) => handleMcqChange(index, "correctOption", e.target.value)} 
                    />
                  </div>
                  
                  {/* Additional options starting from Option 2 */}
                  {mcq.options.map((option, optIndex) => (
                    <div key={optIndex} className="option-row">
                      <label>Option {optIndex + 2} ({String.fromCharCode(66 + optIndex)}):</label>
                      <input 
                        type="text" 
                        placeholder={`Option ${optIndex + 2}`} 
                        value={option} 
                        onChange={(e) => handleMcqOptionChange(index, optIndex, e.target.value)} 
                      />
                    </div>
                  ))}
                  <button className="add-option" onClick={() => addMcqOption(index)}>+ Add Option</button>
                </div>
                <button className="save-button" onClick={() => handleSaveMcq(index)}>Save</button>
              </div>
            ))}
            <button className="add-mcq-button" onClick={addMcqRow}>+ Add MCQ</button>
          </div>
        </div>
        
        {/* Paragraph Section */}
        <div className="question-section">
          <h2>Paragraph</h2>
          <div className="question-box">
            {paragraphs.map((para, index) => (
              <div key={index} className="question-row">
                <input type="text" placeholder="Question" value={para.question} onChange={(e) => handleParagraphChange(index, "question", e.target.value)} />
                <input type="number" placeholder="Min Words" value={para.minWords} onChange={(e) => handleParagraphChange(index, "minWords", e.target.value)} />
                <input type="number" placeholder="Max Words" value={para.maxWords} onChange={(e) => handleParagraphChange(index, "maxWords", e.target.value)} />
                <input type="number" placeholder="Score" value={para.score} onChange={(e) => handleParagraphChange(index, "score", e.target.value)} />
                <input type="text" placeholder="Answer Key" value={para.answerKey} onChange={(e) => handleParagraphChange(index, "answerKey", e.target.value)} />
                <button className="save-button" onClick={() => handleSaveParagraph(index)}>Save</button>
              </div>
            ))}
            <button className="add-paragraph-button" onClick={addParagraphRow}>+ Add Paragraph</button>
          </div>
        </div>
        
        {/* Essay Section */}
        <div className="question-section">
          <h2>Essay</h2>
          <div className="question-box">
            {essays.map((essay, index) => (
              <div key={index} className="question-row">
                <input type="text" placeholder="Question" value={essay.question} onChange={(e) => handleEssayChange(index, "question", e.target.value)} />
                <input type="number" placeholder="Min Words" value={essay.minWords} onChange={(e) => handleEssayChange(index, "minWords", e.target.value)} />
                <input type="number" placeholder="Max Words" value={essay.maxWords} onChange={(e) => handleEssayChange(index, "maxWords", e.target.value)} />
                <input type="number" placeholder="Score" value={essay.score} onChange={(e) => handleEssayChange(index, "score", e.target.value)} />
                <input type="text" placeholder="Answer Key" value={essay.answerKey} onChange={(e) => handleEssayChange(index, "answerKey", e.target.value)} />
                <button className="save-button" onClick={() => handleSaveEssay(index)}>Save</button>
              </div>
            ))}
            <button className="add-essay-button" onClick={addEssayRow}>+ Add Essay</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageQuestionBank;
