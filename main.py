from fastapi import FastAPI, Request, APIRouter, Depends, Form
from routers import questions, answers, users, likes
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Question
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

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

@app.get("/questions/create")
def question_create_form(request: Request):
    return templates.TemplateResponse("question_create.html", {"request": request})

@app.post("/questions/create")
def question_create(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    # 로그인 구현 전이므로 user_id 하드코딩 
    question = Question(title=title, content=content, user_id=1)
    db.add(question)
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)