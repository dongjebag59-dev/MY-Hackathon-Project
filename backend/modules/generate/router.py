import json as _json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from modules.generate.schemas import GenerateRequest
from modules.generate import service
from modules.generate.crud import save_history
from modules.generate.models import GuestUsage
from modules.history.models import CreditTransaction, CreditTransactionType
from modules.user.models import User
from modules.user import service as user_service

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",   # nginx 버퍼링 비활성화
}

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """토큰이 있으면 User 반환, 없으면 None 반환 (비로그인 허용)"""
    if not token:
        return None
    payload = user_service.decode_token(token)
    if not payload:
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.post("/stream", response_model=None)
async def generate_stream(
    request: Request,
    body: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    """4종 콘텐츠 병렬 생성 — SSE로 완료된 순서대로 스트리밍."""
    client_ip = request.client.host if request.client else "unknown"

    # 크레딧 차감 선행 (flush, 아직 commit 안 함 — 생성 실패 시 rollback)
    service.check_and_deduct_credit(db, current_user, client_ip)

    input_data = body.model_dump()
    user_id = current_user.id if current_user else None

    async def event_generator():
        results: dict = {}
        try:
            async for content_type, result in service.stream_generate_content(input_data):
                results[content_type] = result
                yield f"data: {_json.dumps({'type': content_type, 'data': result}, ensure_ascii=False)}\n\n"
        except Exception as exc:
            db.rollback()
            yield f"data: {_json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n"
            return

        if not any(k in results for k in ("blog", "review", "shorts", "thumbnail")):
            db.rollback()
            yield f"data: {_json.dumps({'type': 'error', 'message': '콘텐츠 생성에 실패했습니다.'}, ensure_ascii=False)}\n\n"
            return

        try:
            history = save_history(db, input_data, results, user_id=user_id)
            if current_user:
                db.add(CreditTransaction(
                    user_id=current_user.id,
                    amount=-1,
                    type=CreditTransactionType.use,
                    note="콘텐츠 생성",
                ))
            else:
                db.add(GuestUsage(ip_address=client_ip))
            db.commit()
            if current_user:
                db.refresh(current_user)
            yield f"data: {_json.dumps({'type': 'done', 'history_id': history.id, 'credits_remaining': current_user.credits if current_user else None}, ensure_ascii=False)}\n\n"
        except Exception:
            db.rollback()
            yield f"data: {_json.dumps({'type': 'error', 'message': '저장 중 오류가 발생했습니다.'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=SSE_HEADERS)


@router.post("", response_model=None)
async def generate(
    request: Request,
    body: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    client_ip = request.client.host if request.client else "unknown"

    # 크레딧 차감 또는 비로그인 IP 체크
    service.check_and_deduct_credit(db, current_user, client_ip)

    # 콘텐츠 생성
    input_data = body.model_dump()
    output = await service.generate_content(input_data)

    if "error" in output or not any(k in output for k in ["blog", "review", "shorts", "thumbnail"]):
        db.rollback()
        raise HTTPException(status_code=500, detail="콘텐츠 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")

    # 히스토리 저장 — crud.save_history() 로 일원화
    try:
        history = save_history(db, input_data, output, user_id=current_user.id if current_user else None)
        if current_user:
            db.add(CreditTransaction(
                user_id=current_user.id,
                amount=-1,
                type=CreditTransactionType.use,
                note="콘텐츠 생성",
            ))
        else:
            db.add(GuestUsage(ip_address=client_ip))
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="저장 중 오류가 발생했습니다.")

    return {
        "message": "콘텐츠 생성 성공",
        "input": input_data,
        "output": output,
        "history_id": history.id,
        "credits_remaining": current_user.credits if current_user else None,
    }