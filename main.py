from fastapi import FastAPI, Request, Depends, Form, Path
from routers import questions, answers, users, likes
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from models import User
from auth.auth import create_access_token
from auth.hashing import Hasher
from auth.auth import get_current_user

from database import SessionLocal
from models import Question, Answer, Like

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

@app.get("/questions/{question_id}")
def question_detail(
    request: Request,
    question_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    return templates.TemplateResponse("question_detail.html", {
        "request": request,
        "question": question
    })

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

@app.get("/form-login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/form-login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == username).first()
    if not user or not Hasher.verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "이메일 또는 비밀번호가 잘못되었습니다."
        })

    token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@app.get("/form-signup")
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/form-signup")
def signup_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 이메일 중복 확인
    user = db.query(User).filter(User.email == email).first()
    if user:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "이미 존재하는 이메일입니다."
        })

    new_user = User(
        username=username,
        email=email,
        password_hash=Hasher.hash_password(password)
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/", status_code=302)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response

@app.get("/users/me")
def read_my_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("my_page.html", {
        "request": request,
        "user": current_user
    })

from auth.auth import get_current_user

@app.get("/my-page")
def my_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("my_page.html", {
        "request": request,
        "user": current_user
    })

# 내가 쓴 질문 보기
@app.get("/my/questions")
def my_questions(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    questions = db.query(Question).filter(Question.user_id == current_user.id).all()
    return templates.TemplateResponse("my_questions.html", {"request": request, "questions": questions})

# 내가 쓴 답변 보기
@app.get("/my/answers")
def my_answers(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    answers = db.query(Answer).filter(Answer.user_id == current_user.id).all()
    return templates.TemplateResponse("my_answers.html", {"request": request, "answers": answers})

# 질문 수정 폼
@app.get("/questions/{question_id}/edit")
def edit_question_form(question_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == current_user.id).first()
    if not question:
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("edit_question.html", {"request": request, "question": question})

# 질문 수정 처리
@app.post("/questions/{question_id}/edit")
def update_question(question_id: int, request: Request, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == current_user.id).first()
    if question:
        question.title = title
        question.content = content
        db.commit()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

# 질문 삭제
@app.get("/questions/{question_id}/delete")
def delete_question(question_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == current_user.id).first()
    if question:
        db.delete(question)
        db.commit()
    return RedirectResponse(url="/", status_code=HTTP_302_FOUND)

# 답변 작성 처리
@app.post("/questions/{question_id}/answer")
def create_answer(question_id: int, content: str = Form(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_answer = Answer(content=content, question_id=question_id, user_id=current_user.id)
    db.add(new_answer)
    db.commit()
    return RedirectResponse(url=f"/questions/{question_id}", status_code=HTTP_302_FOUND)

# 좋아요 처리
@app.get("/questions/{question_id}/like")
def like_question(question_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing_like = db.query(Like).filter(Like.user_id == current_user.id, Like.question_id == question_id).first()
    if not existing_like:
        new_like = Like(user_id=current_user.id, question_id=question_id)
        db.add(new_like)
        db.commit()
    return RedirectResponse(url=f"/questions/{question_id}", status_code=HTTP_302_FOUND)

