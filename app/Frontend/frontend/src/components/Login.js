import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Login.css"; // Ensure the CSS file is imported

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }

      // Verify token exists and is complete
      if (!data.access_token || typeof data.access_token !== 'string') {
        throw new Error('Invalid token received from server');
      }

      // Store the full token
      localStorage.setItem("token", data.access_token);
      console.log('Token stored successfully:', data.access_token);

      localStorage.setItem("role", data.role); // Store the user role
      localStorage.setItem("username", email.split('@')[0]); // Store username from email
      
      // Redirect based on user role
      if (data.role === "student") {
        window.location.href = "/student-dashboard";
      } else if (data.role === "teacher") {
        window.location.href = "/teacher-dashboard";
      } else {
        // Fallback for any other role
        alert("Login successful!");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <img src="/logo.jpg" alt="Logo" className="logo" />
          <h2>Welcome to AssessAI</h2>
          <p className="login-subtitle">Sign in to continue</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          
          <button type="submit" className="login-button">
            Sign In
          </button>
          
          <div className="register-link">
            Don't have an account? <Link to="/register">Register</Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
