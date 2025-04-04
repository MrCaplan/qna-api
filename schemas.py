from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QuestionCreate(BaseModel):
    title: str
    content: str

class Question(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    user: User

    likes_count: int

    class Config:
        orm_mode = True

class AnswerCreate(BaseModel):
    content: str

class Answer(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    user: User

    class Config:
        orm_mode = True
        