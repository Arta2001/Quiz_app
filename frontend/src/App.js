import React, { useState, useEffect } from 'react';
import './App.css'; 

const QuizApp = () => {
    const [questions, setQuestions] = useState([]); 
    const [feedback, setFeedback] = useState({});
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0); 


    useEffect(() => {
        fetchQuestions();
    }, []);

   
    const fetchQuestions = async () => {
        try {
            const response = await fetch('http://localhost:8000/questions'); 
            const data = await response.json(); 

            const initialFeedback = {};
            data.forEach(question => {
                initialFeedback[question._id] = '';
            });

            setFeedback(initialFeedback); 
            setQuestions(data); 
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    };

   
    const checkAnswer = async (questionId, optionId) => {
        try {
            const response = await fetch('http://localhost:8000/check_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question_id: questionId, option_selected: optionId }), 
            });

            const data = await response.json();

            setFeedback(prevFeedback => ({
                ...prevFeedback,
                [questionId]: data.correct ? 'Correct answer!' : 'Incorrect answer.',
            }));
        } catch (error) {
            console.error('Error checking answer:', error);
        }
    };


    const handleNextQuestion = () => {
        setCurrentQuestionIndex(prevIndex => prevIndex + 1);
    };

    return (
        <div className="quiz-container">
            <h1>Quiz App</h1>
            {questions.length === 0 ? (
                <p>Loading questions...</p>
            ) : (
                <div className="question-card">
                    <h3>{questions[currentQuestionIndex].question}</h3>
                    <ul className="options-list">
                        {questions[currentQuestionIndex].options.map(option => (
                            <li key={option.option_id} className="option-item">
                                <input
                                    type="radio"
                                    id={option.option_id}
                                    name={`question_${questions[currentQuestionIndex]._id}`}
                                    onChange={() => checkAnswer(questions[currentQuestionIndex]._id, option.option_id)}
                                />
                                <label htmlFor={option.option_id}>{option.text}</label>
                            </li>
                        ))}
                    </ul>
                    <p className="feedback">{feedback[questions[currentQuestionIndex]._id]}</p>
                    <button
                        className="next-button"
                        onClick={handleNextQuestion}
                        disabled={currentQuestionIndex === questions.length - 1}
                    >
                        Next Question
                    </button>
                </div>
            )}
        </div>
    );
};

export default QuizApp;
