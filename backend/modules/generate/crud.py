import json
from sqlalchemy.orm import Session
from modules.generate.models import GenerationHistory


def save_history(db: Session, data: dict, output: dict, user_id: int = None):
    history = GenerationHistory(
        user_id=user_id,
        shop_name=data["shop_name"],
        business_type=data["business_type"],
        region=data["region"],
        keyword=data["keyword"],
        feature=data.get("feature"),
        tone=data.get("tone", "friendly"),
        input_payload=json.dumps(data, ensure_ascii=False),
        output_payload=json.dumps(output, ensure_ascii=False),
        credits_used=1
    )
     # ✅ 피드백 1: commit 실패 시 rollback 처리
    try:
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    except Exception:
        db.rollback()
        raise