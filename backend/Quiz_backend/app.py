

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = MongoClient('mongodb://localhost:27017/')
db = client['quiz_db']
questions_collection = db['questions']



class Answer(BaseModel):
    option_id: str
    text: str


class Question(BaseModel):
    question: str
    answer: str
    options: List[Answer]


class CheckResponse(BaseModel):
    question_id: str
    option_selected: int = Field(..., ge=1, le=4)



@app.post('/check_response', response_model=dict)
def check_response(response: CheckResponse):
    try:
        question = questions_collection.find_one({"_id": ObjectId(response.question_id)})

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        selected_option = next(
            (opt for opt in question['options'] if opt['option_id'] == response.option_selected),
            None)

        if selected_option and selected_option['text'].strip().lower() == question['answer'].strip().lower():
            return {"status": "Successful", "correct": True}
        else:
            return {"status": "Unsuccessful", "correct": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/questions')
def get_questions():
    try:
        questions = list(questions_collection.find())
        formatted_questions = [{
            "_id": str(question['_id']),
            "question": question['question'],
            "options": question['options'],
            "answer": question['answer']
        } for question in questions]
        return formatted_questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/questions/{question_id}')
def get_question_by_id(question_id: str):
    try:
        question = questions_collection.find_one({"_id": ObjectId(question_id)})
        if question:
            formatted_question = {
                "_id": str(question['_id']),
                "question": question['question'],
                "options": question['options'],
                "answer": question['answer']
            }
            return formatted_question
        else:
            raise HTTPException(status_code=404, detail="Question not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/check_response', response_model=dict)
def check_response(response: dict):
    try:
        question = questions_collection.find_one({"_id": ObjectId(response.question_id)})

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        selected_option = next((opt for opt in question['options'] if opt['option_id'] == response.option_selected),
                               None)

        if selected_option['text'].strip().lower() == question['answer'].strip().lower():
            return {"status": "Successful", "correct": True}
        else:
            return {"status": "Unsuccessful", "correct": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/questions/{question_id}")
async def update_question(
        question_id: str,
        question_data: Question
):
    question_dict = question_data.dict(exclude_unset=True)

    result = questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$set": question_dict}
    )

    if result.modified_count == 1:
        return {"message": "Question updated successfully", "question_id": question_id, **question_dict}

    raise HTTPException(status_code=404, detail=f"Question with id {question_id} not found")


@app.delete("/questions/{question_id}")
async def delete_question(question_id: str):
    result = questions_collection.delete_one({"_id": ObjectId(question_id)})

    if result.deleted_count == 1:
        return {"message": "Question deleted successfully"}

    raise HTTPException(status_code=404, detail=f"Question with id {question_id} not found")
