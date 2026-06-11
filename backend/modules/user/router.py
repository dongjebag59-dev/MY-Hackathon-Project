import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import ExpiredSignatureError, JWTError
from jose import jwt as jose_jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from modules.user.models import PasswordResetToken, User
from modules.user.schemas import UserRegister, Token, UserOut, PasswordChange
from modules.history.models import CreditTransaction, CreditTransactionType
from modules.user import crud, service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# JWT 현재 유저 추출 (의존성)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    
    try:
        payload = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다. 다시 로그인해 주세요.")
    except JWTError:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")
    user = db.query(User).filter(User.id == int(sub)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user


# 회원가입
@router.post("/signup", response_model=UserOut, status_code=201)
def signup(body: UserRegister, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
    if body.nickname and crud.get_user_by_nickname(db, body.nickname):
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")

    hashed = service.hash_password(body.password)
    try:
        user = crud.create_user(db, body.email, hashed, body.nickname)
        service.create_user_with_bonus(db, user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="회원가입 처리 중 오류가 발생했습니다.")
    return user

# 로그인
# Swagger Authorize 창과 맞추기 위해 form-data(username, password) 방식 사용
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀립니다.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")

    token = service.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# 내 정보 조회
@router.get("/me", response_model=UserOut)
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# 비밀번호 변경
@router.put("/password", status_code=200)
def change_password(
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not service.verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="새 비밀번호가 현재 비밀번호와 동일합니다.")

    try:
        current_user.hashed_password = service.hash_password(body.new_password)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="비밀번호 변경 중 오류가 발생했습니다.")
    return {"message": "비밀번호가 변경되었습니다."}

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


# 비밀번호 재설정 이메일 발송
@router.post("/password-reset/request")
async def request_password_reset(
    email: str,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email)
    if not user:
        # 보안상 존재 여부 노출 안 함
        return {"message": "이메일이 존재하면 재설정 링크를 발송했습니다."}

    # 기존 미사용 토큰 만료 처리 (중복 토큰 누적 방지)
    db.query(PasswordResetToken).filter(
        PasswordResetToken.email == email,
        PasswordResetToken.used == False,
    ).update({"used": True})

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_token = PasswordResetToken(
        email=email,
        token=token,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    reset_link = f"http://13.125.46.112:8000/reset-password.html?token={token}"

    message = MessageSchema(
        subject="[사장봇] 비밀번호 재설정 링크",
        recipients=[email],
        body=f"""
        <h2>비밀번호 재설정</h2>
        <p>아래 링크를 클릭하여 비밀번호를 재설정해주세요.</p>
        <p>링크는 1시간 동안 유효합니다.</p>
        <a href="{reset_link}" style="
            display: inline-block;
            padding: 12px 24px;
            background-color: #0F1E3F;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        ">비밀번호 재설정하기</a>
        <p>본인이 요청하지 않았다면 이 이메일을 무시해주세요.</p>
        """,
        subtype="html",
    )

    try:
        fm = FastMail(mail_config)
        await fm.send_message(message)
    except Exception:
        pass

    return {"message": "이메일이 존재하면 재설정 링크를 발송했습니다."}


# 비밀번호 재설정 실행
@router.post("/password-reset/confirm")
def confirm_password_reset(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.now(timezone.utc)
    ).first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="유효하지 않거나 만료된 링크입니다.")

    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="비밀번호는 6자 이상이어야 합니다.")

    user = crud.get_user_by_email(db, reset_token.email)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user.hashed_password = service.hash_password(new_password)
    reset_token.used = True
    db.commit()

    return {"message": "비밀번호가 성공적으로 재설정되었습니다."}