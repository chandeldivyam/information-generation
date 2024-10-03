# app/api/routes/question_answer.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.question_answer import QuestionAnswerService
from app.schemas.question_answer import QuestionAnswerCreate, QuestionAnswerSearch, QuestionAnswerResponse
from typing import List
from app.core.logging_config import logging
from langchain.schema import Document
from app.core.exceptions import AppException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/questions", response_model=QuestionAnswerResponse)
async def add_question_answer(
    qa_data: QuestionAnswerCreate,
    qa_service: QuestionAnswerService = Depends()
):
    try:
        result = await qa_service.add_question_answer(qa_data)
        return result
    except Exception as e:
        logger.error(f"Error adding question and answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions/relevant", response_model=List[Document])
async def get_relevant_questions(
    search_params: QuestionAnswerSearch,
    qa_service: QuestionAnswerService = Depends()
):
    try:
        results = await qa_service.get_relevant_questions(search_params)
        return results
    except AppException as ae:
        raise HTTPException(status_code=ae.status_code, detail=ae.detail)
    except Exception as e:
        logger.error(f"Error retrieving relevant questions: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: str,
    qa_service: QuestionAnswerService = Depends()
):
    try:
        result = await qa_service.delete_question(question_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))