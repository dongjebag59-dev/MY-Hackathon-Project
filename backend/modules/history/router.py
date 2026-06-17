import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from modules.history import crud
from modules.history.schemas import HistoryOut, RegenerateOut
from modules.history.models import CreditTransaction, CreditTransactionType
from modules.user.models import User
from modules.user.router import get_current_user
from modules.generate.models import GenerationHistory
from modules.generate import service as generate_service
from typing import List, Dict, Any

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
def list_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if limit > 100:
        limit = 100
    items = crud.get_history_list(db, current_user.id, skip=skip, limit=limit)
    total = crud.count_history(db, current_user.id)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{history_id}", response_model=HistoryOut)
def get_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    h = crud.get_history_by_id(db, history_id)
    if not h or h.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="이력을 찾을 수 없습니다.")
    return h


@router.delete("/{history_id}", status_code=204)
def delete_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    h = crud.get_history_by_id(db, history_id)
    if not h or h.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="이력을 찾을 수 없습니다.")
    crud.delete_history(db, history_id)


@router.post("/{history_id}/regenerate", response_model=RegenerateOut)
async def regenerate(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    h = crud.get_history_by_id(db, history_id)
    if not h or h.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="이력을 찾을 수 없습니다.")

    user = db.query(User).filter(User.id == current_user.id).with_for_update().first()
    if not user or user.credits <= 0:
        raise HTTPException(status_code=402, detail="크레딧이 부족합니다. 충전 후 이용해 주세요.")
    user.credits -= 1
    db.flush()
    current_user.credits = user.credits

    input_data = json.loads(h.input_payload)
    output = await generate_service.generate_content(input_data)

    if "error" in output or not any(k in output for k in ["blog", "review", "shorts", "thumbnail"]):
        db.rollback()
        raise HTTPException(status_code=500, detail="콘텐츠 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")

    new_history = GenerationHistory(
        user_id=current_user.id,
        shop_name=h.shop_name,
        business_type=h.business_type,
        region=h.region,
        keyword=h.keyword,
        feature=h.feature,
        tone=h.tone,
        input_payload=h.input_payload,
        output_payload=json.dumps(output, ensure_ascii=False),
        credits_used=1,
    )

    try:
        db.add(new_history)
        db.add(CreditTransaction(
            user_id=current_user.id,
            amount=-1,
            type=CreditTransactionType.use,
            note="콘텐츠 재생성",
        ))
        db.commit()
        db.refresh(new_history)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="재생성 저장 중 오류가 발생했습니다.")

    return RegenerateOut(
        message="재생성 성공",
        output=output,
        history_id=new_history.id,
        credits_remaining=current_user.credits,
    )