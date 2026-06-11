from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from modules.history.models import CreditTransaction, CreditTransactionType, Subscription, SubscriptionPlan, SubscriptionStatus
from modules.user.models import User, UserPlan
from modules.user.router import get_current_user

router = APIRouter()

# ── 충전 패키지 정의 ─────────────────────────────────────────
CREDIT_PACKAGES = {
    "light": {"credits": 3,  "price": 3900,  "plan": SubscriptionPlan.per_use},
    "basic": {"credits": 10, "price": 9900,  "plan": SubscriptionPlan.per_use},
    "pro":   {"credits": 25, "price": 19900, "plan": SubscriptionPlan.per_use},
}


class ChargeRequest(BaseModel):
    package: str               # "basic" | "standard" | "pro"
    pg_transaction_id: Optional[str] = None   # PG사 거래 ID (프론트에서 전달)



@router.get("/me")
def my_info(current_user: User = Depends(get_current_user)):
    """마이페이지 기본 정보 — 닉네임·이메일·크레딧·플랜"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "credits": current_user.credits,
        "plan": current_user.plan,
    }


@router.post("/charge")
def charge_credits(
    body: ChargeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    pkg = CREDIT_PACKAGES.get(body.package)
    if not pkg:
        raise HTTPException(
            status_code=400,
            detail=f"올바르지 않은 패키지입니다. 선택 가능: {list(CREDIT_PACKAGES.keys())}"
        )
    if body.pg_transaction_id:
        existing = db.query(Subscription).filter(
            Subscription.pg_transaction_id == body.pg_transaction_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="이미 처리된 결제입니다.")
# TODO: 실제 운영 시 PG사 API 호출하여 결제 검증 필요

    # 크레딧 충전
    try:
        current_user.credits += pkg["credits"]
        if current_user.plan == UserPlan.free:
            current_user.plan = UserPlan.per_use

        today = date.today()
        db.add(Subscription(
            user_id=current_user.id,
            plan=pkg["plan"],
            amount=pkg["price"],
            status=SubscriptionStatus.paid,
            period_start=today,
            period_end=None,
            pg_transaction_id=body.pg_transaction_id,
        ))
        db.add(CreditTransaction(
            user_id=current_user.id,
            amount=pkg["credits"],
            type=CreditTransactionType.earn,
            note=f"{body.package} 패키지 충전 ({pkg['credits']}회)",
        ))
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="충전 처리 중 오류가 발생했습니다.")

    return {
        "message": f"{pkg['credits']}크레딧이 충전되었습니다.",
        "credits": current_user.credits,
        "plan": current_user.plan,
        "charged": pkg["credits"],
        "price": pkg["price"],
    }


@router.get("/packages")
def list_packages():
    """구매 가능한 크레딧 패키지 목록"""
    return [
        {"id": key, "credits": val["credits"], "price": val["price"], "plan": val["plan"]}
        for key, val in CREDIT_PACKAGES.items()
    ]


@router.get("/credits")
def credits_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """크레딧 잔액 및 최근 거래 내역 20건"""
    transactions = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "credits": current_user.credits,
        "plan": current_user.plan,
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "note": t.note,
                "created_at": t.created_at,
            }
            for t in transactions
        ],
    }