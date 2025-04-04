from fastapi import FastAPI
from routers import questions, answers, users, likes
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(users.router)
app.include_router(likes.router)

