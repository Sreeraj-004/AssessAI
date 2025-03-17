import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import RegisterPage from '../RegisterPage';
import Login from '../components/Login';
import './Home.css';

const Home = () => {
  return (
    <div className="app">
      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/register">Register</Link>
          </li>
          <li>
            <Link to="/login">Login</Link>
          </li>
        </ul>
      </nav>

      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <div className="welcome-container">
            <img src="/images/logo.svg" alt="AssessAI Logo" className="welcome-logo" />
            <h1>Welcome to AssessAI</h1>
            <p>Please register or login to continue</p>
            <div className="auth-buttons">
              <Link to="/register" className="button">Register</Link>
              <Link to="/login" className="button">Login</Link>
            </div>
          </div>
        } />
      </Routes>
    </div>
  );
};

export default Home;
