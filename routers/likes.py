from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from auth.auth import get_current_user
import models 

router = APIRouter(prefix="/questions", tags=["Likes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 질문 좋아요
@router.post("/{question_id}/like")
def like_question(
    question_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 중복 좋아요 방지
    existing = db.query(models.Like).filter_by(
        user_id=current_user.id, question_id=question_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already liked")
    
    like = models.Like(user_id=current_user.id, question_id=question_id)
    db.add(like)
    db.commit()
    return {"message": "Liked"}

# 좋아요 취소
@router.post("/{question_id}/unlike")
def unlike_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.Like).filter_by(
        user_id=current_user.id, question_id=question_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(existing)
    db.commit()
    return {"message": "Unliked"}
