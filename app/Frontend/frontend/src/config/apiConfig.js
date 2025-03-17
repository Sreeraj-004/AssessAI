const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  questionBanks: `${API_BASE_URL}/question_banks`,
  questions: `${API_BASE_URL}/questions`,
  createQuestionBank: `${API_BASE_URL}/question_banks`
};
