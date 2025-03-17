from sqlalchemy.orm import Session
from ..mdl import StudentAnswer, Question, Exam
import re
from typing import Dict, List

def check_sentence_validity(sentence: str) -> bool:
    """Check if a sentence has too many repeated words"""
    words = sentence.lower().split()
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
        if word_count[word] >= 5:  # If any word appears 5 or more times
            return False
    return True

def analyze_essay_content(text: str, answer_key: str) -> Dict:
    """Analyze essay content for meaningful keywords and answer key reflection"""
    # Split into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    # Filter valid sentences (no excessive word repetition)
    valid_sentences = [s for s in sentences if check_sentence_validity(s)]
    
    # Get keywords from answer key
    key_words = set(re.sub(r'[^\w\s]', '', answer_key.lower()).split())
    
    # Count meaningful sentences (>10 words with keywords)
    meaningful_sentences = []
    for sentence in valid_sentences:
        words = sentence.split()
        if len(words) > 10:  # Check word count
            # Check if sentence contains any keyword
            sentence_words = set(re.sub(r'[^\w\s]', '', sentence.lower()).split())
            if sentence_words & key_words:  # If there's any intersection with keywords
                meaningful_sentences.append(sentence)
    
    # Check if content reflects answer key
    total_words = set(re.sub(r'[^\w\s]', '', text.lower()).split())
    key_coverage = len(total_words & key_words) / len(key_words) if key_words else 0
    
    return {
        "valid_sentences": len(valid_sentences),
        "meaningful_sentences": len(meaningful_sentences),
        "key_coverage": key_coverage,
        "total_words": len(total_words)
    }

def analyze_essay_structure(text: str) -> Dict:
    """Analyze the structure of an essay"""
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    # Check for introduction and conclusion
    has_intro = len(paragraphs) >= 1
    has_conclusion = len(paragraphs) > 1
    
    # Check for transition words that indicate good structure
    transition_words = ['however', 'therefore', 'furthermore', 'moreover', 'in addition', 'consequently', 'thus', 'hence']
    uses_transitions = any(word in text.lower() for word in transition_words)
    
    return {
        "well_structured": len(paragraphs) >= 3 and uses_transitions,
        "has_introduction": has_intro,
        "has_conclusion": has_conclusion,
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "uses_transition_words": uses_transitions
    }

def generate_descriptive_feedback(
    score_fraction: float,
    structure_analysis: Dict,
    points_covered: int,
    total_points: int,
    word_count: int,
    min_words: int,
    max_words: int = None
) -> List[str]:
    """Generate detailed feedback points based on the analysis"""
    feedback = []
    
    # Structure feedback
    if structure_analysis["well_structured"]:
        feedback.append(" Clear and well-organized presentation of ideas")
    else:
        if not structure_analysis["has_introduction"]:
            feedback.append("Consider starting with a stronger opening to engage the reader")
        if not structure_analysis["has_conclusion"]:
            feedback.append("Try wrapping up your main points for a stronger finish")
        if not structure_analysis["uses_transition_words"]:
            feedback.append("Adding connecting phrases between ideas could enhance readability")
    
    # Content coverage feedback
    coverage_percentage = (points_covered / total_points) * 100
    if coverage_percentage >= 80:
        feedback.append(" Comprehensive coverage of the topic")
    elif coverage_percentage >= 60:
        feedback.append(" Good grasp of key concepts")
    else:
        feedback.append("Consider exploring additional aspects of the topic")
        feedback.append("Expanding your analysis would strengthen the response")
    
    # Word count feedback
    if word_count < min_words:
        feedback.append("Your ideas deserve more elaboration")
    elif max_words and word_count > max_words:
        feedback.append("Try to be more concise while maintaining key points")
    else:
        feedback.append(" Good balance in explanation length")
    
    # Quality indicators
    if score_fraction >= 0.8:
        feedback.append(" Excellent depth of understanding shown")
    elif score_fraction >= 0.6:
        feedback.append(" Good understanding with room for deeper analysis")
    else:
        feedback.append("Further development of ideas would enhance your answer")
    
    return feedback

def evaluate_mcq_answer(student_answer: str, correct_option: str) -> tuple:
    """Evaluate an MCQ answer and return score and feedback"""
    is_correct = student_answer.lower().strip() == correct_option.lower().strip()
    feedback = {
        "correct": is_correct,
        "correct_answer": correct_option,
        "feedback": " Excellent choice!" if is_correct else "Review this concept for better understanding"
    }
    return (1.0 if is_correct else 0.0), feedback

def evaluate_text_answer(student_answer: str, answer_key: str, min_words: int = 0, max_words: int = None) -> tuple:
    """
    New evaluation algorithm:
    - Base score (0.2): More than 10 words with meaningful keywords (participation score)
    - Main score (0.8): Reflects answer key content
    - Full score requires meeting word count criteria
    """
    # Initial checks
    if not student_answer.strip():
        return 0.0, {"feedback": ["Please provide an answer to receive feedback"]}
    
    # Analyze content
    content_analysis = analyze_essay_content(student_answer, answer_key)
    word_count = content_analysis["total_words"]
    
    # Generate feedback and calculate score
    feedback = []
    score = 0.0
    max_possible_score = 1.0
    
    # Base participation score (20%)
    if content_analysis["meaningful_sentences"] > 0:
        score += 0.2  # Small score for meaningful attempt
        feedback.append(" Shows effort in addressing the question")
    
    # Main score based on answer key coverage (80%)
    key_coverage = content_analysis["key_coverage"]
    if key_coverage >= 0.8:
        score += 0.8
        feedback.append(" Excellent coverage of key concepts")
    elif key_coverage >= 0.6:
        score += 0.6
        feedback.append(" Good coverage of key concepts")
    elif key_coverage >= 0.4:
        score += 0.4
        feedback.append("Consider including more key concepts")
    else:
        feedback.append("Try to incorporate more relevant concepts")
    
    # Word count requirements for full marks
    if word_count < min_words:
        # Penalize score for being too short
        final_score = score * (word_count / min_words)
        feedback.append(f"Response is brief - expand to improve score ({word_count}/{min_words} words)")
    elif max_words and word_count > max_words:
        # Penalize score for being too long
        final_score = score * 0.7  # 30% penalty for exceeding limit
        feedback.append(f"Response exceeds length limit - be more concise ({word_count}/{max_words} words)")
    else:
        final_score = score
        feedback.append(" Good response length")
    
    return final_score, {
        "score": final_score,
        "max_score": max_possible_score,
        "word_count": word_count,
        "meaningful_sentences": content_analysis["meaningful_sentences"],
        "key_coverage_percentage": key_coverage * 100,
        "feedback": feedback
    }

def evaluate_student_answers(db: Session, student_id: str, exam_id: str) -> Dict:
    """
    Evaluate all answers for a student in an exam
    Returns a dictionary with scores and feedback
    """
    try:
        # Get all student answers for the exam
        student_answers = db.query(StudentAnswer).filter(
            StudentAnswer.student_id == student_id,
            StudentAnswer.exam_id == exam_id
        ).all()
        
        if not student_answers:
            return {"error": "No answers found for this student in the exam"}
        
        total_score = 0
        max_possible_score = 0
        evaluation_results = []
        
        for answer in student_answers:
            question = db.query(Question).filter(Question.id == answer.question_id).first()
            if not question:
                continue
                
            score_fraction = 0.0  # Score between 0 and 1
            feedback = None
            
            if question.question_type.lower() == 'mcq':
                score_fraction, feedback = evaluate_mcq_answer(answer.selected_option, question.correct_option)
            else:  # Essay or paragraph
                score_fraction, feedback = evaluate_text_answer(
                    answer.typed_answer,
                    question.answer_key,
                    question.min_words or 0,
                    question.max_words
                )
            
            earned_score = score_fraction * question.score
            total_score += earned_score
            max_possible_score += question.score
            
            evaluation_results.append({
                "question_id": str(question.id),
                "question_type": question.question_type,
                "score_earned": earned_score,
                "max_score": question.score,
                "feedback": feedback
            })
        
        # Safe division to calculate percentage
        score_percentage = 0
        if max_possible_score > 0:
            score_percentage = (total_score / max_possible_score * 100)
        
        return {
            "total_score": total_score,
            "max_possible_score": max_possible_score,
            "score_percentage": score_percentage,
            "question_scores": evaluation_results
        }
    except Exception as e:
        return {
            "error": f"An error occurred during evaluation: {str(e)}",
            "total_score": 0,
            "max_possible_score": 0,
            "score_percentage": 0,
            "question_scores": []
        }
