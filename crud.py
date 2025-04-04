from sqlalchemy.orm import Session
from models import Question, User, Answer
import schemas

# 질문 생성
def create_question(db: Session, question: schemas.QuestionCreate, user_id: int):
    db_question = Question(
        title=question.title,
        content=question.content,
        user_id=user_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# 질문 전체 조회
def get_questions(db: Session, skip: int = 0, limit: int = 10):
    questions = db.query(Question).offset(skip).limit(limit).all()

    for q in questions:
        q.likes_count = len(q.likes)

    return questions

# 질문 단건 조회
def get_question(db: Session, question_id: int):
    q = db.query(Question).filter(Question.id == question_id).first()
    if q:
        q.likes_count = len(q.likes)

    return q

# 답변 생성
def create_answer(db: Session, answer: schemas.AnswerCreate, question_id: int, user_id: int):
    db_answer = Answer(
        content=answer.content,
        question_id=question_id,
        user_id=user_id
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

# 특정 질문의 답변 조회 
def get_answers_by_question(db: Session, question_id: int):
    return db.query(Answer).filter(Answer.question_id == question_id).all()


