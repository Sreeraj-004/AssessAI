import React from "react";
import "./QuestionBank.css";
import { FaPlus } from "react-icons/fa";
import logo from "./assets/logo.jpg"; // Ensure logo is in src/assets/

const QuestionBank = () => {
  return (
    <div className="question-bank-container">
      {/* AssessAI Logo */}
      <img src={logo} alt="AssessAI Logo" className="logo" />

      {/* Title */}
      <h1 className="title">
        📚 Question Bank
      </h1>

      {/* Button */}
      <div className="question-box">
        <button className="create-btn">
          <FaPlus className="icon" /> Create New Question Bank
        </button>
      </div>
    </div>
  );
};

export default QuestionBank;
