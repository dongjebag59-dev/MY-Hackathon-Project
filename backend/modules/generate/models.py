from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class GuestUsage(Base):
    """비로그인 사용자 IP별 무료 체험 횟수 추적"""
    __tablename__ = "guest_usage"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv6 포함 최대 45자
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"),
                            nullable=True, index=True)
    shop_name      = Column(String(100), nullable=False)
    business_type  = Column(String(50),  nullable=False)
    region         = Column(String(100), nullable=False)
    keyword        = Column(String(100), nullable=False)
    feature        = Column(String(200), nullable=True)
    tone           = Column(String(20),  nullable=False, default="friendly")
    input_payload  = Column(Text, nullable=False)
    output_payload = Column(Text, nullable=False)
    credits_used   = Column(Integer, nullable=False, default=1)
    created_at     = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="histories")