from fastapi import FastAPI, Request, APIRouter, Depends
from routers import questions, answers, users, likes
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Question

app = FastAPI()

# 정적 파일 
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 폴더 등록
templates = Jinja2Templates(directory="templates")
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API 라우터 등록
app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(users.router)
app.include_router(likes.router)

# HTML 렌더링 라우터 
@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    questions = db.query(Question).order_by(Question.created_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "questions": questions})