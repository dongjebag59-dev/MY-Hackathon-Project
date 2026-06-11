"""서버 임포트 및 핵심 모듈 기본 동작 테스트."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_app_imports():
    """FastAPI 앱 전체 임포트 — 모듈 레벨 오류 검출."""
    from main import app
    assert app is not None


def test_prompt_builder_imports():
    """prompt_builder 4개 함수 모두 임포트 가능한지 확인."""
    from modules.generate.prompt_builder import (
        build_blog_prompt,
        build_review_prompt,
        build_shorts_prompt,
        build_thumbnail_prompt,
        BUSINESS_SEO,
    )
    assert len(BUSINESS_SEO) == 12


def test_prompt_builders_return_strings():
    """4개 프롬프트 빌더가 비어있지 않은 문자열을 반환하는지 확인.
    _get_context()의 BUSINESS_SEO 참조 오류를 런타임에서 잡아냄.
    """
    from modules.generate.prompt_builder import (
        build_blog_prompt,
        build_review_prompt,
        build_shorts_prompt,
        build_thumbnail_prompt,
    )
    kwargs = dict(
        shop_name="테스트카페",
        business_type="카페/베이커리",
        region="홍대",
        keyword="홍대카페",
        feature="직접 구운 베이커리",
        tone="friendly",
    )
    assert len(build_blog_prompt(**kwargs)) > 100
    assert len(build_review_prompt(**kwargs)) > 100
    assert len(build_shorts_prompt(**kwargs)) > 100
    assert len(build_thumbnail_prompt(**kwargs)) > 100


def test_prompt_builders_unknown_business_type():
    """등록되지 않은 업종도 폴백으로 정상 동작하는지 확인."""
    from modules.generate.prompt_builder import build_blog_prompt
    result = build_blog_prompt(
        shop_name="미지의가게",
        business_type="알수없는업종",
        region="서울",
        keyword="테스트",
    )
    assert isinstance(result, str)
    assert len(result) > 50


def test_sanitize():
    """_sanitize가 위험 문자를 제거하는지 확인."""
    from modules.generate.prompt_builder import _sanitize
    assert '"' not in _sanitize('악의적인 "입력" <script>')
    assert '<' not in _sanitize('<script>alert(1)</script>')
    assert len(_sanitize("a" * 300, max_len=200)) == 200
