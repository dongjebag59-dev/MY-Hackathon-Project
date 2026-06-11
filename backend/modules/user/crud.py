from sqlalchemy.orm import Session
from modules.user.models import User, UserPlan


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_nickname(db: Session, nickname: str):
    return db.query(User).filter(User.nickname == nickname).first()


def create_user(db: Session, email: str, hashed_password: str, nickname: str = None):
    user = User(
        email=email,
        hashed_password=hashed_password,
        nickname=nickname,
        credits=3,
        plan=UserPlan.free
    )
    db.add(user)
    db.flush()   # ID 할당만, commit은 signup router에서 bonus와 함께 한 번에
    db.refresh(user)
    return user