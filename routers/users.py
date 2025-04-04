from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import schemas, models
from database import SessionLocal
from auth.hashing import Hasher
from auth.auth import create_access_token, get_current_user
import models, schemas
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        username=user.username, 
        email=user.email,
        password_hash=Hasher.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not Hasher.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# 내가 쓴 질문 목록 조회
@router.get("/me/questions", response_model=List[schemas.Question])
def get_my_questions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Question).filter(models.Question.user_id == current_user.id).all()

# 내가 쓴 답변 목록 조회
@router.get("/me/answers", response_model=List[schemas.Answer])
def get_my_answers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Answer).filter(models.Answer.user_id == current_user.id).all()
 
# 로그인한 사용자 정보 조회 API
@router.get("/me", response_model=schemas.User)
def get_current_user_profile(
    current_user: models.User = Depends(get_current_user)
):
    return current_user
