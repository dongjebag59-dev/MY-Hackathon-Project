import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UserPlan(str, enum.Enum):
    free     = "free"
    monthly  = "monthly"
    per_use  = "per_use"


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nickname        = Column(String(100), unique=True, nullable=True, index=True)   # 중복 불허
    credits         = Column(Integer, nullable=False, default=3)
    plan            = Column(Enum(UserPlan), nullable=False, default=UserPlan.free)
    is_active       = Column(Boolean, nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # ✅ 피드백 2: GenerationHistory는 user 삭제 시 SET NULL로 이력 보존하므로
    #    cascade에서 delete-orphan 제거 → "save-update, merge"로 변경
    histories     = relationship("GenerationHistory", back_populates="user",
                                 cascade="save-update, merge")
    transactions  = relationship("CreditTransaction", back_populates="user",
                                 cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user",
                                 cascade="all, delete-orphan")
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    email      = Column(String(255), nullable=False, index=True)
    token      = Column(String(100), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used       = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())    