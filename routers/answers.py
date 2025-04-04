from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas, crud
from database import SessionLocal
from typing import List
from auth.auth import get_current_user

router = APIRouter(prefix="/questions/{question_id}/answers", tags=["Answers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Answer)
def create_answer(
    question_id: int, 
    answer: schemas.AnswerCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    # 임시 user_id
    return crud.create_answer(
        db=db, 
        answer=answer, 
        question_id=question_id, 
        user_id=current_user.id
        )

@router.get("/", response_model=List[schemas.Answer])
def read_answers(question_id: int, db: Session = Depends(get_db)):
    return crud.get_answers_by_question(db, question_id=question_id)

