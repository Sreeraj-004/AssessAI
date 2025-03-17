import { Routes, Route, Navigate } from 'react-router-dom';  

import Login from './components/Login';
import Register from './components/Register';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import StudentExams from './components/StudentExams';
import StudentResults from './components/StudentResults';
import AttendExam from './components/AttendExam';
import WaitingLobby from './components/WaitingLobby';
import ExamSession from './components/ExamSession';
import ManageQuestionBank from './components/ManageQuestionBank';
import CreateQuestionBank from './components/CreateQuestionBank';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/student-dashboard" element={<StudentDashboard />} />
        <Route path="/teacher-dashboard" element={<TeacherDashboard />} />
        <Route path="/student-exams" element={<StudentExams />} />
        <Route path="/student-results" element={<StudentResults />} />
        <Route path="/attend-exam" element={<AttendExam />} />
        <Route path="/waiting-lobby" element={<WaitingLobby />} />
        <Route path="/exam-session" element={<ExamSession />} />
        <Route path="/create-question-bank" element={<CreateQuestionBank />} />
        <Route path="/manage-question-bank" element={<ManageQuestionBank />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </div>
  );
}

export default App;
