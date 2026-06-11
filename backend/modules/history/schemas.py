from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HistoryOut(BaseModel):
    id: int
    shop_name: str
    business_type: str
    region: str
    keyword: str
    feature: Optional[str]
    tone: str
    output_payload: str
    credits_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class CreditTransactionOut(BaseModel):
    id: int
    amount: int
    type: str
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class RegenerateOut(BaseModel):
    message: str
    output: dict
    history_id: int
    credits_remaining: int

    class Config:
        from_attributes = True