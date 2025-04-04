from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
import models
import schemas, crud
from database import SessionLocal
from auth.auth import get_current_user

router = APIRouter(prefix="/questions", tags=["Questions"])

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 질문 생성
@router.post("/", response_model=schemas.Question)
def create_question(
    question: schemas.QuestionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    return crud.create_question(db=db, question=question, user_id=current_user.id)

# 질문 전체 조회 (리스트)
@router.get("/", response_model=List[schemas.Question])
def read_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_questions(db, skip=skip, limit=limit)

# 질문 하나 조회
@router.get("/{question_id}", response_model=schemas.Question)
def read_question(question_id: int, db: Session = Depends(get_db)):
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question

@router.put("/{question_id}", response_model=schemas.Question)
def update_question(
    question_id: int = Path(...), 
    updated: schemas.QuestionCreate = ..., # 수정할 데이터
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    question = crud.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own questions")
    
    # 수정 내용 반영
    question.title = updated.title
    question.content = updated.content
    db.commit()
    db.refresh(question)
    return question

@router.delete("/{question_id}")
def delete_question(
    question_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    question = crud.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own questions")
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted"}