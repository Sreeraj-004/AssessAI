import React from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from "./Login";
import ManageQuestionBank from './frontend/src/components/ManageQuestionBank';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/manage-question-bank" element={<ManageQuestionBank />} />
        <Route path="/" element={
          <div>
            <h1>Welcome to AssessAI</h1>
            <Login />
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;
