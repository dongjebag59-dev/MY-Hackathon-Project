from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings
from modules.history.models import CreditTransaction, CreditTransactionType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def create_user_with_bonus(db, user):
    """
    가입 보너스 CreditTransaction 기록.
    User.credits 초기값(3)과 동기화되어야 함.
    crud.create_user()에서 credits=3으로 설정하므로 합산 일치.
    """
    db.add(CreditTransaction(
        user_id=user.id,
        amount=3,
        type=CreditTransactionType.earn,
        note="가입 보너스",
    ))