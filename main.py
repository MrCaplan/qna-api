from fastapi import FastAPI, Request, Depends, Form
from routers import questions, answers, users, likes
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from database import SessionLocal
from models import Question

app = FastAPI()

# 정적 파일
app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 폴더
templates = Jinja2Templates(directory="templates")

# DB 세션 의존성
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

# 메인 페이지 
@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    questions = db.query(Question).order_by(Question.created_at.desc()).all()
    return templates.TemplateResponse("index.html", {"request": request, "questions": questions})


@app.get("/form-create-question")
def show_form(request: Request):
    return templates.TemplateResponse("create_question_test.html", {"request": request})

@app.post("/form-create-question")
def save_form(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    question = Question(title=title, content=content, user_id=1)  # 임시 user_id
    db.add(question)
    db.commit()
    return RedirectResponse(url="/", status_code=302)

