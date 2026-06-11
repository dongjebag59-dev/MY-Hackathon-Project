import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class CreditTransactionType(str, enum.Enum):
    earn   = "earn"    # 크레딧 획득 (충전/보너스)
    use    = "use"     # 크레딧 차감 (콘텐츠 생성)
    refund = "refund"  # 환불


class SubscriptionPlan(str, enum.Enum):
    free      = "free"
    monthly   = "monthly"
    per_use   = "per_use"


class SubscriptionStatus(str, enum.Enum):
    paid     = "paid"
    failed   = "failed"
    refunded = "refunded"


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    amount     = Column(Integer, nullable=False)
    type       = Column(Enum(CreditTransactionType), nullable=False)
    note       = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="transactions")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                               nullable=False, index=True)
    plan              = Column(Enum(SubscriptionPlan), nullable=False)
    amount            = Column(Integer, nullable=False)
    status            = Column(Enum(SubscriptionStatus), nullable=False)
    period_start      = Column(Date, nullable=True)
    period_end        = Column(Date, nullable=True)
    pg_transaction_id = Column(String(100), nullable=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subscriptions")