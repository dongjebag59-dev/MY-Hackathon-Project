import json
from sqlalchemy.orm import Session
from modules.generate.models import GenerationHistory


def get_history_list(db: Session, user_id: int = None, skip: int = 0, limit: int = 20, search: str = ""):
    query = db.query(GenerationHistory)
    if user_id:
        query = query.filter(GenerationHistory.user_id == user_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            GenerationHistory.shop_name.ilike(like) | GenerationHistory.keyword.ilike(like)
        )
    return query.order_by(GenerationHistory.created_at.desc()).offset(skip).limit(limit).all()


def count_history(db: Session, user_id: int, search: str = "") -> int:
    query = db.query(GenerationHistory).filter(GenerationHistory.user_id == user_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            GenerationHistory.shop_name.ilike(like) | GenerationHistory.keyword.ilike(like)
        )
    return query.count()


def get_history_by_id(db: Session, history_id: int):
    return db.query(GenerationHistory).filter(GenerationHistory.id == history_id).first()


def delete_history(db: Session, history_id: int):
    history = get_history_by_id(db, history_id)
    if history:
        try:
            db.delete(history)
            db.commit()
        except Exception:
            db.rollback()
            raise
    return history