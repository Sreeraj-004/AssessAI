import React from "react";
import { Link } from "react-router-dom";
import "./auth.css";
import logo from "./logo.jpg"; // Ensure the logo file exists

const LoginPage = () => {
  return (
    <div className="auth-container">
      <div className="auth-card">
        <img src={logo} alt="AssessAI Logo" className="auth-logo" />
        <h2>Login</h2>

        <form>
          <div>
            <input type="email" placeholder="Email" required />
          </div>
          <div>
            <input type="password" placeholder="Password" required />
          </div>
          <button type="submit">Login</button>
        </form>

        <p>
          New user? <Link to="/register">Register here</Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
