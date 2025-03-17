import React, { useState, useEffect } from "react";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import "./CreateQuestionBank.css";
import { API_ENDPOINTS } from '../config/apiConfig';

const CreateQuestionBank = () => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [questionBanks, setQuestionBanks] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(true);
  const [deleteConfirmation, setDeleteConfirmation] = useState(null);
  const navigate = useNavigate();

  // Fetch question banks on component mount
  useEffect(() => {
    fetchQuestionBanks();
  }, []);

  const fetchQuestionBanks = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please login again.');
        setLoading(false);
        return;
      }

      console.log('Fetching question banks with token:', token);
      const response = await axios.get(API_ENDPOINTS.questionBanks, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('Question banks API response:', response.data);

      if (response.data.success) {
        setQuestionBanks(response.data.data);
        setError(null); // Clear any previous errors
      }
    } catch (err) {
      console.error('Error fetching question banks:', err);
      console.error('Error response:', err.response);
      setError('Failed to fetch question banks. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication required. Please login again.');
      setLoading(false);
      return;
    }

    try {
      console.log('Sending request with token:', token);
      const response = await axios.post(
        API_ENDPOINTS.createQuestionBank,
        { name, description },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      console.log('API Response:', response.data);

      if (response.data) {
        alert('Question bank created successfully!');
        setName('');
        setDescription('');
        fetchQuestionBanks();
      }
    } catch (err) {
      console.error('API Error:', err);
      console.error('Error Details:', err.response);
      setError(err.response?.data?.detail || 'Failed to create question bank');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (questionBankId) => {
    navigate(`/manage-question-bank?id=${questionBankId}`);
  };

  const handleDelete = async (questionBankId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please login again.');
        return;
      }

      await axios.delete(`${API_ENDPOINTS.questionBanks}/${questionBankId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Remove the deleted question bank from the state
      setQuestionBanks(questionBanks.filter(qb => qb.id !== questionBankId));
      setDeleteConfirmation(null);
      alert('Question bank deleted successfully!');
    } catch (err) {
      console.error('Error deleting question bank:', err);
      setError('Failed to delete question bank. Please try again later.');
    }
  };

  return (
    <div className="container">
      {/* Logo and Title */}
      <img src="/logo.jpg" alt="AssessAI Logo" className="logo" />
      <h1 className="title">Question Bank</h1>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
          <button 
            className="retry-button" 
            onClick={fetchQuestionBanks}
            style={{ marginLeft: '10px' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Create New Question Bank Button */}
      <div className="create-button-container">
        <button 
          className="toggle-form-button" 
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Hide Form' : 'Create New Question Bank'}
        </button>
      </div>

      {/* Create Form (conditionally rendered) */}
      {showCreateForm && (
        <form onSubmit={handleSubmit} className="form-box">
          <div className="form-group">
            <label htmlFor="name" className="label">Name:</label>
            <input
              type="text"
              id="name"
              className="input-field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description" className="label">Description:</label>
            <textarea
              id="description"
              className="textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              autoComplete="off"
            />
          </div>

          <button type="submit" disabled={loading} className="create-button">
            {loading ? 'Creating...' : 'Create Question Bank'}
          </button>
        </form>
      )}

      {/* Question Banks Table */}
      <div className="table-container">
        <h2>Your Question Banks</h2>
        {loading ? (
          <p>Loading question banks...</p>
        ) : questionBanks.length === 0 ? (
          <p>No question banks found. Create one to get started!</p>
        ) : (
          <table className="question-banks-table">
            <thead>
              <tr>
                <th>Sl No</th>
                <th>Question Bank ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {questionBanks.map((qb, index) => (
                <tr key={qb.id}>
                  <td>{index + 1}</td>
                  <td>{qb.id}</td>
                  <td>{qb.name}</td>
                  <td>{qb.description || 'No description'}</td>
                  <td>
                    <button 
                      className="edit-button" 
                      onClick={() => handleEdit(qb.id)}
                    >
                      Edit
                    </button>
                    <button 
                      className="delete-button" 
                      onClick={() => setDeleteConfirmation(qb.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmation && (
        <div className="modal">
          <div className="modal-content">
            <h3>Confirm Delete</h3>
            <p>Are you sure you want to delete this question bank? This action cannot be undone.</p>
            <div className="modal-buttons">
              <button 
                className="cancel-button" 
                onClick={() => setDeleteConfirmation(null)}
              >
                Cancel
              </button>
              <button 
                className="confirm-delete-button" 
                onClick={() => handleDelete(deleteConfirmation)}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateQuestionBank;
