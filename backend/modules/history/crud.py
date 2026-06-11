import json
from sqlalchemy.orm import Session
from modules.generate.models import GenerationHistory


def get_history_list(db: Session, user_id: int = None, limit: int = 50):
    query = db.query(GenerationHistory)
    if user_id:
        query = query.filter(GenerationHistory.user_id == user_id)
    return query.order_by(GenerationHistory.created_at.desc()).limit(limit).all()


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