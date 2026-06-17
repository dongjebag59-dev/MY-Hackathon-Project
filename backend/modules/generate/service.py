import asyncio
import json
import re
from fastapi import HTTPException
from openai import AsyncOpenAI, RateLimitError, AuthenticationError, OpenAIError
from sqlalchemy.orm import Session
from config import settings
from modules.generate.prompt_builder import (
    build_prompt,
    build_blog_prompt,
    build_review_prompt,
    build_shorts_prompt,
    build_thumbnail_prompt,
)
from modules.generate.models import GuestUsage
from modules.user.models import User

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

GUEST_FREE_LIMIT = 1


def extract_json(raw: str) -> dict | None:
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


async def generate_content(data: dict) -> dict:
    """기존 /generate 엔드포인트용 — 내부적으로 병렬 생성 사용."""
    return await generate_content_parallel(data)


async def _generate_single_type(content_type: str, prompt: str) -> dict:
    """단일 콘텐츠 타입을 OpenAI에 요청하고 파싱된 dict 반환."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2000,
            timeout=45,
            response_format={"type": "json_object"},
        )
    except RateLimitError:
        return {"error": "OpenAI 크레딧 부족 또는 요청 한도 초과"}
    except AuthenticationError:
        return {"error": "OpenAI API 키가 유효하지 않습니다"}
    except OpenAIError as e:
        return {"error": f"OpenAI 오류: {str(e)}"}

    raw = response.choices[0].message.content
    result = extract_json(raw)
    return result if result else {"error": f"{content_type} 파싱 실패"}


async def generate_content_parallel(data: dict) -> dict:
    """4종 콘텐츠를 병렬로 생성 — asyncio.gather로 동시 요청."""
    kwargs = dict(
        shop_name=data.get("shop_name", ""),
        business_type=data.get("business_type", ""),
        region=data.get("region", ""),
        keyword=data.get("keyword", ""),
        feature=data.get("feature", "") or "",
        tone=data.get("tone", "friendly"),
    )
    blog, review, shorts, thumbnail = await asyncio.gather(
        _generate_single_type("blog",      build_blog_prompt(**kwargs)),
        _generate_single_type("review",    build_review_prompt(**kwargs)),
        _generate_single_type("shorts",    build_shorts_prompt(**kwargs)),
        _generate_single_type("thumbnail", build_thumbnail_prompt(**kwargs)),
    )
    return {"blog": blog, "review": review, "shorts": shorts, "thumbnail": thumbnail}


async def stream_generate_content(data: dict):
    """4종 콘텐츠 병렬 생성 — 완료되는 순서대로 (content_type, result) 튜플을 yield.
    제너레이터가 닫히면(클라이언트 중단 포함) 미완료 태스크를 즉시 취소한다.
    """
    kwargs = dict(
        shop_name=data.get("shop_name", ""),
        business_type=data.get("business_type", ""),
        region=data.get("region", ""),
        keyword=data.get("keyword", ""),
        feature=data.get("feature", "") or "",
        tone=data.get("tone", "friendly"),
    )
    tasks = {
        name: asyncio.create_task(_generate_single_type(name, prompt))
        for name, prompt in {
            "blog":      build_blog_prompt(**kwargs),
            "review":    build_review_prompt(**kwargs),
            "shorts":    build_shorts_prompt(**kwargs),
            "thumbnail": build_thumbnail_prompt(**kwargs),
        }.items()
    }
    pending = set(tasks.values())
    task_to_name = {v: k for k, v in tasks.items()}

    try:
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                yield task_to_name[task], task.result()
    finally:
        # 클라이언트 중단 또는 예외 발생 시 미완료 OpenAI 요청 취소
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)


def check_and_deduct_credit(db: Session, current_user: User, client_ip: str):
    """크레딧 차감 또는 비로그인 IP 체크.
    with_for_update()로 행 잠금을 획득한 후 차감 — 동시 요청 이중 차감 방지.
    """
    if current_user:
        user = (
            db.query(User)
            .filter(User.id == current_user.id)
            .with_for_update()
            .first()
        )
        if not user or user.credits <= 0:
            raise HTTPException(status_code=402, detail="크레딧이 부족합니다. 충전 후 이용해 주세요.")
        user.credits -= 1
        db.flush()
        current_user.credits = user.credits
    else:
        guest_count = db.query(GuestUsage).filter(GuestUsage.ip_address == client_ip).count()
        if guest_count >= GUEST_FREE_LIMIT:
            raise HTTPException(status_code=403, detail="무료 체험은 1회만 가능합니다. 회원가입 후 이용해 주세요.")

