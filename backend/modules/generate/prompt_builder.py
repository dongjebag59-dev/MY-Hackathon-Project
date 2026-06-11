import re

def _sanitize(text: str, max_len: int = 200) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'[\"\'`<>]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text[:max_len]

# 업종별 Few-Shot 예시
FEW_SHOT_EXAMPLES = {
    "음식점/식당": {
        "blog_example": """
[블로그 예시]
제목: 김포 구래동 맛집 | 서촌김밥 국내산 재료로 만든 건강한 한 끼

본문:
안녕하세요! 오늘은 김포 구래동에서 정말 맛있는 김밥집을 발견해서 소개해드리려고 해요 😊

## 김포 구래동 숨은 맛집, 서촌김밥
구래동을 지나다 우연히 발견한 서촌김밥! 간판부터 예사롭지 않았어요.
[이미지: 서촌김밥 외관 전경]

## 국내산 재료만 고집하는 특별함
요즘 원산지 걱정 없이 먹을 수 있는 곳이 얼마나 될까요?
서촌김밥은 100% 국내산 재료만 사용한다고 해서 더욱 믿음이 갔어요.
[이미지: 신선한 재료 준비 과정]

## 실제로 먹어본 불고기김밥 후기
한 입 베어물었을 때 느껴지는 신선함이 달랐어요.
[이미지: 불고기김밥 클로즈업]

#김포맛집 #구래동맛집 #김밥맛집 #국내산김밥 #서촌김밥
""",
        "review_example": "구래동에서 정말 맛있는 김밥집 찾았어요! 국내산 재료를 사용해서 그런지 재료가 신선하고 맛이 진해요. 불고기김밥은 꼭 드셔보세요. 사장님도 친절하시고 가격도 합리적이에요. 단골 될 것 같아요 😊",
    },
    "카페/베이커리": {
        "blog_example": """
[블로그 예시]
제목: 홍대 카페 추천 | 브레드앤커피 직접 구운 베이커리가 특별한 곳

본문:
안녕하세요! 오늘은 홍대에서 발견한 보석 같은 카페를 소개해드릴게요 ☕

## 홍대 감성 카페, 브레드앤커피
골목길 안쪽에 숨어있는 이 카페, 지나치기엔 너무 아까운 곳이에요.
[이미지: 카페 외관 및 간판]

## 매일 아침 직접 굽는 베이커리
냄새부터 달라요. 매장 안에 들어서면 갓 구운 빵 냄새가 가득해요.
[이미지: 갓 구운 베이커리 진열]

## 시그니처 메뉴 추천
크루아상 라떼는 꼭 드셔보세요!
[이미지: 시그니처 음료 및 베이커리]

#홍대카페 #홍대베이커리 #홍대브런치 #감성카페 #브레드앤커피
""",
        "review_example": "홍대에서 정말 분위기 좋은 카페 발견했어요! 매일 직접 굽는 베이커리라 신선하고 맛있어요. 크루아상이 특히 바삭하고 버터향이 진해서 너무 맛있었어요. 좌석도 넉넉하고 콘센트도 있어서 작업하기도 좋아요 ☕",
    },
    "피부관리/에스테틱": {
        "blog_example": """
[블로그 예시]
제목: 강남 피부관리 추천 | 글로우스킨 트러블 개선 후기 솔직하게

본문:
안녕하세요! 오랜 트러블 고민 끝에 드디어 찾은 피부관리샵 후기 남겨요 🌿

## 강남 피부관리 글로우스킨을 선택한 이유
SNS에서 후기를 보고 반신반의하며 예약했어요.
[이미지: 글로우스킨 내부 인테리어]

## 1회 관리 후 달라진 피부
원장님이 꼼꼼하게 피부 상태를 체크해주시고 맞춤 관리를 해주셨어요.
[이미지: 관리 전후 비교]

## 가격 및 예약 방법
첫 방문 이벤트가 있으니 꼭 확인해보세요!
[이미지: 시술 종류 및 가격표]

#강남피부관리 #에스테틱 #트러블케어 #피부개선 #글로우스킨
""",
        "review_example": "트러블 때문에 고민이 많았는데 글로우스킨 다녀오고 나서 정말 달라졌어요! 원장님이 피부 상태 꼼꼼히 봐주시고 맞춤 관리해주셔서 만족스러웠어요. 시술 후 피부가 촉촉하고 진정된 느낌이에요. 위생도 철저하고 원장님이 친절하게 설명해주셔서 좋았어요 🌿",
    },
    "헤어샵/미용실": {
        "blog_example": """
[블로그 예시]
제목: 신촌 헤어샵 추천 | 헤어스튜디오M 염색 후기 발색 미쳤어요

본문:
안녕하세요! 오늘은 신촌에서 찾은 인생 헤어샵 후기예요 💇‍♀️

## 신촌 헤어샵 헤어스튜디오M
예약제로 운영해서 기다림 없이 편하게 받을 수 있어요.
[이미지: 헤어스튜디오M 내부]

## 꼼꼼한 상담이 달랐어요
원하는 스타일 사진 가져갔더니 꼼꼼하게 분석해주셨어요.
[이미지: 상담 및 시술 과정]

## 염색 결과물 공개
발색이 정말 예쁘게 나왔어요!
[이미지: 염색 전후 비교]

#신촌헤어샵 #미용실추천 #염색후기 #헤어스튜디오 #신촌미용실
""",
        "review_example": "신촌에서 헤어샵 찾다가 발견했는데 대만족이에요! 원하는 색상 말했더니 꼼꼼하게 상담해주시고 피부톤에 맞게 색상 추천해주셔서 좋았어요. 발색도 예쁘고 손상도 적어요. 실장님 실력이 정말 좋으세요. 다음에도 또 올게요 💇‍♀️",
    },
    "네일아트/속눈썹": {
        "blog_example": """
[블로그 예시]
제목: 홍대 네일샵 추천 | 핑크네일 젤네일 지속력 3주 후기

본문:
안녕하세요! 오늘은 홍대 네일샵 후기 들고 왔어요 💅

## 홍대 핑크네일 찾아간 이유
인스타에서 디자인 보고 바로 예약했어요.
[이미지: 핑크네일 내부 및 작업 공간]

## 꼼꼼한 케어가 달라요
기본 케어부터 꼼꼼하게 해주셔서 지속력이 확실히 달라요.
[이미지: 네일 시술 과정]

## 3주 지속 후기
들뜸 없이 깔끔하게 유지됐어요!
[이미지: 완성된 네일 디자인]

#홍대네일 #젤네일 #네일아트 #네일추천 #핑크네일
""",
        "review_example": "홍대 네일샵 중에 제일 만족스러웠어요! 디자인도 예쁘게 해주시고 기본 케어도 꼼꼼하게 해주셔서 지속력이 달라요. 보통 2주면 들뜨는데 여기는 3주 넘게 유지됐어요. 위생도 철저하고 원장님이 친절하게 소통해주셔서 좋았어요 💅",
    },
    "학원/교육": {
        "blog_example": """
[블로그 예시]
제목: 강남 영어학원 추천 | 토익스쿨 3개월 만에 900점 달성 후기

본문:
안녕하세요! 토익 점수 때문에 고민이 많았는데 드디어 목표 달성했어요 📚

## 강남 토익스쿨을 선택한 이유
커리큘럼이 체계적이고 선생님들 이력이 화려해서 선택했어요.
[이미지: 토익스쿨 강의실]

## 3개월 수강 후기
매일 체계적인 학습 관리 덕분에 꾸준히 공부할 수 있었어요.
[이미지: 교재 및 학습 자료]

## 점수 향상 결과
시작 점수 650에서 3개월 만에 920 달성!
[이미지: 성적표 인증]

#강남영어학원 #토익학원 #토익900 #영어공부 #토익스쿨
""",
        "review_example": "토익 때문에 고민하다가 토익스쿨 등록했는데 정말 잘한 것 같아요! 선생님들이 꼼꼼하게 봐주시고 매일 학습 관리해주셔서 꾸준히 할 수 있었어요. 3개월 만에 270점 올렸어요. 커리큘럼이 체계적이고 질문하면 바로바로 답변해주셔서 좋았어요 📚",
    },
    "헬스/필라테스": {
        "blog_example": """
[블로그 예시]
제목: 강남 필라테스 추천 | 바디라인 3개월 후기 진짜 달라졌어요

본문:
안녕하세요! 오늘은 3개월 필라테스 후기 솔직하게 남겨요 🧘‍♀️

## 강남 바디라인 필라테스 선택 이유
소수정예 수업이라 집중 케어 받을 수 있어서 선택했어요.
[이미지: 바디라인 필라테스 내부]

## 1:1 맞춤 수업의 차이
자세 교정부터 체형 개선까지 꼼꼼하게 봐주셨어요.
[이미지: 수업 진행 모습]

## 3개월 전후 비교
자세가 확실히 달라졌어요!
[이미지: 체형 변화 비교]

#강남필라테스 #필라테스추천 #체형교정 #바디라인 #강남운동
""",
        "review_example": "필라테스 처음 시작했는데 바디라인에서 잘 배우고 있어요! 트레이너 선생님이 자세 하나하나 꼼꼼하게 봐주시고 제 체형에 맞게 운동 방향 잡아주셔서 좋아요. 3개월 하고 나니까 자세도 좋아지고 몸이 가벼워진 느낌이에요. 시설도 깨끗하고 선생님이 친절해요 🧘‍♀️",
    },
    "인테리어/리모델링": {
        "blog_example": """
[블로그 예시]
제목: 강남 인테리어 추천 | 홈스타일링 셀프 리모델링 후기 완전 만족

본문:
안녕하세요! 오늘은 강남에서 정말 만족스러운 인테리어 업체를 소개해드릴게요 🏠

## 강남 인테리어, 홈스타일링을 선택한 이유
SNS에서 시공 사례를 보고 바로 상담 신청했어요.
[이미지: 시공 전후 비교 사진]

## 꼼꼼한 상담과 견적
원하는 스타일을 말씀드렸더니 예산에 맞게 최적의 방법을 제안해주셨어요.
[이미지: 시공 과정]

## 완성된 결과물
기대 이상의 결과에 정말 감동받았어요!
[이미지: 완성된 인테리어]

#강남인테리어 #리모델링 #인테리어추천 #홈스타일링 #셀프인테리어
""",
        "review_example": "강남에서 인테리어 업체 찾다가 홈스타일링 선택했는데 정말 잘한 것 같아요! 상담부터 시공까지 꼼꼼하게 진행해주셨고 견적도 합리적이었어요. 원하는 스타일 정확하게 구현해주셔서 대만족입니다. 주변에도 적극 추천하고 있어요 🏠",
    },
    "반려동물/펫샵": {
        "blog_example": """
[블로그 예시]
제목: 강남 강아지 미용 추천 | 펫살롱 소형견 전문 미용 후기

본문:
안녕하세요! 오늘은 강남에서 찾은 강아지 미용 잘하는 곳 소개해드릴게요 🐾

## 강남 펫살롱, 선택한 이유
소형견 전문이라는 말에 믿음이 갔어요.
[이미지: 미용 전 강아지]

## 세심한 케어가 달랐어요
아이 성격에 맞게 천천히 케어해주셔서 스트레스 없이 미용받았어요.
[이미지: 미용 과정]

## 미용 결과 공개
너무 예쁘게 나왔어요!
[이미지: 미용 후 강아지]

#강남강아지미용 #펫살롱 #소형견미용 #강아지미용 #반려동물
""",
        "review_example": "강남 펫살롱 다녀왔는데 정말 만족해요! 저희 강아지가 낯선 곳을 무서워하는데 원장님이 너무 잘 달래주시고 세심하게 케어해주셨어요. 미용 결과도 너무 예쁘게 나왔고 아이도 스트레스 없이 받은 것 같아서 좋았어요 🐾",
    },
    "공방/클래스": {
        "blog_example": """
[블로그 예시]
제목: 홍대 도자기 공방 추천 | 클레이아트 원데이클래스 후기

본문:
안녕하세요! 오늘은 홍대에서 찾은 도자기 공방 후기 가져왔어요 🏺

## 홍대 클레이아트 공방 선택 이유
원데이클래스로 부담없이 시작할 수 있어서 선택했어요.
[이미지: 공방 내부]

## 초보도 쉽게 배울 수 있어요
선생님이 처음부터 차근차근 알려주셔서 생각보다 어렵지 않았어요.
[이미지: 만들기 과정]

## 완성작 공개
세상에 하나뿐인 나만의 작품 완성!
[이미지: 완성된 도자기]

#홍대공방 #도자기공방 #원데이클래스 #클레이아트 #취미
""",
        "review_example": "홍대 공방 원데이클래스 다녀왔는데 너무 좋았어요! 도자기 처음 해봤는데 선생님이 친절하게 알려주셔서 생각보다 잘 만들었어요. 소수 인원으로 진행돼서 집중적으로 배울 수 있었고 완성품도 직접 가져갈 수 있어서 좋았어요 🏺",
    },
    "PC방/게임방": {
        "blog_example": """
[블로그 예시]
제목: 홍대 PC방 추천 | 넥스트레벨 최신사양 + 프리미엄존 후기
 
본문:
안녕하세요! 오늘은 홍대에서 발견한 진짜 쾌적한 PC방 소개해드릴게요 🎮
 
## 홍대 넥스트레벨 PC방, 선택한 이유
최신 RTX 4080 사양에 1인 독립부스까지 갖추고 있어서 선택했어요.
[이미지: 프리미엄존 전경]
 
## 좌석 & 사양이 남달랐어요
144Hz 모니터에 게이밍 체어라 장시간 게임도 피로하지 않았어요.
[이미지: 좌석 및 모니터 클로즈업]
 
## 음식 메뉴도 수준급
컵라면부터 치킨까지 다양하고 가격도 합리적이에요.
[이미지: 매점 메뉴판]
 
#홍대PC방 #홍대게임방 #넥스트레벨 #프리미엄PC방 #홍대맛집
""",
        "review_example": "홍대에서 PC방 찾다가 넥스트레벨 갔는데 대만족이에요! RTX 4080 사양에 1인 독립부스라 집중해서 게임하기 너무 좋았어요. 자리도 넓고 체어가 편해서 4시간 있었는데 전혀 불편하지 않았어요. 가격도 시간당 합리적이고 매점 메뉴도 다양해서 자주 올 것 같아요 🎮",
    },
    "쥬얼리/액세서리샵": {
        "blog_example": """
[블로그 예시]
제목: 성수 쥬얼리샵 추천 | 실버링크 14K 반지 맞춤제작 후기
 
본문:
안녕하세요! 오늘은 성수에서 찾은 감성 쥬얼리샵 소개해드릴게요 💍
 
## 성수 실버링크, 선택한 이유
맞춤 각인 서비스가 있어서 세상에 하나뿐인 반지를 만들 수 있어서 선택했어요.
[이미지: 매장 내부 및 진열장]
 
## 디자인 상담부터 달랐어요
원하는 디자인을 꼼꼼하게 상담해주시고 피부톤에 맞는 소재도 추천해주셨어요.
[이미지: 상담 및 디자인 과정]
 
## 완성된 반지 공개
각인까지 들어가서 정말 특별한 반지가 완성됐어요!
[이미지: 완성된 쥬얼리 착용샷]
 
#성수쥬얼리 #쥬얼리샵 #실버링크 #14K반지 #맞춤각인
""",
        "review_example": "성수 쥬얼리샵 다녀왔는데 완전 만족이에요! 디자인 고민할 때 원장님이 친절하게 도와주셔서 제 취향에 딱 맞는 반지 완성했어요. 각인 서비스도 있어서 커플링으로 맞췄는데 너무 예뻐요. 마감도 깔끔하고 가격 대비 퀄리티가 정말 좋아요. 선물용으로도 강추해요 💍",
    },
}


def build_prompt(
    shop_name: str,
    business_type: str,
    region: str,
    keyword: str,
    feature: str = "",
    tone: str = "friendly"
) -> str:

    tone_guide = {
        "friendly": "친근하고 편안한 말투로, 이모지 1~2개 사용 가능",
        "professional": "격식체, 전문 용어를 자연스럽게 포함한 신뢰감 있는 말투",
        "emotional": "감성적이고 시적인 묘사, 짧고 여운 있는 문장",
    }

     # 사용자 입력 전처리 (prompt injection 방어)
    shop_name     = _sanitize(shop_name, max_len=100)
    business_type = _sanitize(business_type, max_len=50)
    region        = _sanitize(region, max_len=100)
    keyword       = _sanitize(keyword, max_len=100)
    feature       = _sanitize(feature, max_len=200)

    tone_desc = tone_guide.get(tone, tone_guide["friendly"])
    feature_text = f"\n가게 특징: {feature}" if feature else ""
    
    # 업종별 SEO 키워드 가이드
    business_seo = {
        "음식점/식당": {
            "keywords": ["맛집", "혼밥", "가성비", "웨이팅", "포장"],
            "review_focus": "음식 맛, 양, 가격 대비 만족도, 분위기",
            "shorts_hook": "이 집 못 가면 후회해요",
        },
        "카페/베이커리": {
            "keywords": ["카페", "디저트", "브런치", "분위기", "인스타"],
            "review_focus": "음료 맛, 베이커리, 인테리어, 좌석",
            "shorts_hook": "요즘 핫한 카페 발견",
        },
        "피부관리/에스테틱": {
            "keywords": ["피부관리", "에스테틱", "관리", "피부개선", "트러블"],
            "review_focus": "시술 효과, 원장님 실력, 위생, 가격",
            "shorts_hook": "피부가 이렇게 달라질 줄 몰랐어요",
        },
        "헤어샵/미용실": {
            "keywords": ["헤어샵", "미용실", "염색", "펌", "커트"],
            "review_focus": "디자이너 실력, 상담, 지속력, 가격",
            "shorts_hook": "드디어 내 인생 헤어 찾았다",
        },
        "네일아트/속눈썹": {
            "keywords": ["네일", "젤네일", "속눈썹", "연장", "케어"],
            "review_focus": "디자인, 지속력, 원장님 실력, 위생",
            "shorts_hook": "이 디자인 너무 예쁘지 않나요",
        },
        "학원/교육": {
            "keywords": ["학원", "교육", "강의", "수업", "선생님"],
            "review_focus": "강사 실력, 커리큘럼, 성적 향상, 분위기",
            "shorts_hook": "성적이 이렇게 오를 수 있다고요?",
        },
        "헬스/필라테스": {
            "keywords": ["헬스", "필라테스", "운동", "트레이닝", "PT"],
            "review_focus": "트레이너 실력, 시설, 청결, 가격",
            "shorts_hook": "운동 시작하고 몸이 달라졌어요",
        },
        "인테리어/리모델링": {
            "keywords": ["인테리어", "리모델링", "시공", "인테리어업체", "홈스타일링"],
            "review_focus": "시공 품질, 견적 합리성, 일정 준수, 사후 관리",
            "shorts_hook": "집이 이렇게 바뀔 줄 몰랐어요",
        },
        "반려동물/펫샵": {
            "keywords": ["강아지미용", "펫샵", "반려동물", "고양이", "펫케어"],
            "review_focus": "동물 케어 방식, 미용 결과, 위생, 스트레스 여부",
            "shorts_hook": "우리 아이가 이렇게 예뻐졌어요",
        },
        "공방/클래스": {
            "keywords": ["공방", "원데이클래스", "클래스", "취미", "핸드메이드"],
            "review_focus": "선생님 친절도, 난이도, 완성도, 재료 품질",
            "shorts_hook": "처음인데 이렇게 잘 만들었어요",
        },
         "PC방/게임방": {
            "keywords": ["PC방", "게임방", "최신사양", "프리미엄PC방", "게이밍"],
            "review_focus": "PC 사양, 좌석 편의성, 매점 메뉴, 청결, 가격",
            "shorts_hook": "이 PC방 사양 실화예요?",
        },
        "쥬얼리/액세서리샵": {
            "keywords": ["쥬얼리", "액세서리", "반지", "목걸이", "각인"],
            "review_focus": "디자인 퀄리티, 소재, 상담 친절도, 각인 서비스, 가격",
            "shorts_hook": "세상에 하나뿐인 반지 만들어봤어요",
        },
    }

    biz_info = business_seo.get(business_type, {
        "keywords": [keyword],
        "review_focus": "서비스 품질, 가격, 분위기",
        "shorts_hook": "이곳 꼭 가보세요",
    })

    seo_keywords = ", ".join(biz_info["keywords"])
    review_focus = biz_info["review_focus"]
    shorts_hook = biz_info["shorts_hook"]

    # Few-Shot 예시 가져오기
    few_shot = FEW_SHOT_EXAMPLES.get(business_type, {})
    blog_example = few_shot.get("blog_example", "")
    review_example = few_shot.get("review_example", "")

    few_shot_text = ""
    if blog_example:
        few_shot_text = f"""
[참고 예시 - 이 품질과 스타일을 참고하세요]
{blog_example}
리뷰 예시: {review_example}
"""

    prompt = f"""
당신은 네이버 블로그 SEO 전문가이자 소상공인 마케팅 콘텐츠 작가입니다.
{few_shot_text}
아래 정보를 바탕으로 4가지 콘텐츠를 생성해주세요.

[입력 정보]
가게명: {shop_name}
업종: {business_type}
지역: {region}
메인 키워드: {keyword}{feature_text}
말투: {tone_desc}

[업종별 SEO 가이드]
- 추천 연관 키워드: {seo_keywords}
- 리뷰 집중 포인트: {review_focus}
- 쇼츠 후킹 문구 참고: "{shorts_hook}"
[쇼츠/릴스 대본 작성 규칙]
- 30~40초 분량, 7컷 타임라인으로 구성
- 0~3초: 후킹 — 공감되는 질문이나 상황으로 시작
- 3~7초: 제품/서비스 소개 — 정면 노출
- 7~12초: 핵심 특징 클로즈업 — 질감/결과물/공간 강조
- 12~18초: 차별화 포인트 — 성분/기술/특기사항
- 18~24초: 사용/체험 장면 — 실제 사용 모습
- 24~31초: Before/After 또는 결과 강조
- 31~36초: 마무리 + 가게명 노출
- 각 컷마다 scene(화면), caption(자막), thumbnail_text(썸네일 문구) 포함
- filming_tips에 촬영 방법, 필수 장면, 자막 스타일, BGM, 컷 전환 포함
- instagram_body는 바로 올릴 수 있게 해시태그 포함해서 완성형으로 작성
- 업종에 맞는 현실적인 장면 묘사 (뷰티: 피부결/광, 음식: 비주얼/맛, 헤어: 시술 전후)
[플레이스 리뷰 작성 규칙]
- customer_review: 고객이 직접 방문한 것처럼 자연스러운 경험 중심 작성
  * 메인 키워드 1~2회 자연스럽게 포함
  * 구체적 경험 (직원 친절도, 결과물, 가격, 재방문 의사) 포함
  * 과장 표현 금지, 실제 후기처럼 자연스럽게
- owner_reply_1 (감사형): 리뷰 감사 + 방문 경험 공감 + 재방문 유도
  * 가게명 또는 키워드 1회 포함
  * 따뜻하고 친근한 어투
- owner_reply_2 (정보형): 구체적 서비스 언급 + 다음 방문 혜택 또는 추천 서비스 안내
  * 키워드 1회 포함
  * 신뢰감 있는 전문적 어투
[썸네일 작성 규칙]
- copies: 업종별 CTR 높은 3가지 패턴으로 작성
  * number_type: 구체적 숫자/횟수/기간 포함 (신뢰감)
  * question_type: 타겟의 고민/궁금증을 자극하는 질문형 (공감)
  * emotion_type: 감성적 변화/발견을 표현 (감성)
  * 모두 15자 이내, 임팩트 있게
- main_image_guide: 업종 특성에 맞는 최적 썸네일 장면 안내
  * best_shot: 클릭률 높은 대표 장면 (Before/After, 결과물, 얼굴 노출 등)
  * alternatives: 대안 장면 2가지
  * avoid: 클릭률 낮은 장면 (어두운 사진, 제품만 단독 등)
- design_guide: 업종별 최적 디자인 방향
  * 뷰티/헤어: 깔끔한 흰배경, 핑크/민트 포인트
  * 음식: 따뜻한 톤, 주황/빨강 포인트
  * 학원/교육: 신뢰감 있는 파랑/남색 계열
- cta: 업종에 맞는 행동 유도 문구 3종
  * 예약형: "지금 예약하기", "DM으로 문의"
  * 방문형: "오늘 방문해보세요", "가까운 {{지역}} 매장"
  * 정보형: "프로필 링크 클릭", "더 알아보기"
[SEO 규칙 - C-Rank·D.I.A+ 기준]

[제목 규칙]
- 지역명 + 키워드 앞배치, 25자 이내
- 제목에 경험성 단어 1개 포함 (추천/후기/솔직/다녀온/직접 중 택1)
- 예시: "김포 피부관리 추천 | 트러블 개선 직접 다녀온 후기"

[본문 구조 규칙]
- 도입부 첫 문장에 메인 키워드 반드시 포함
- 소제목 4개 이상 포함, 소제목 중 2개는 메인 키워드 또는 연관 키워드 포함
- 메인 키워드 3~5회 자연스럽게 배치 (연속 2회 이상 금지)
- 연관 키워드 ({seo_keywords}) 3개 이상 본문에 자연스럽게 포함
- 구체적 수치 최소 2개 이상 포함 (가격, 소요시간, 횟수, 용량 등)
- 3,000자 이상 작성
- 이미지 삽입 위치 [이미지: 설명] 형식으로 4회 이상 표시

[본문 필수 구성]
1. 도입부: 공감 문장 + 이 가게를 선택한 이유 (메인 키워드 포함)
2. 상세 경험: 구체적 수치와 함께 핵심 특징 2~3가지
3. 추천 포인트: 업종 특화 정보 ({review_focus} 중심)
4. 가게 기본 정보: 위치, 영업시간, 가격대, 예약 방법 (알고 있는 경우만)
5. 마무리: 추천 대상 + 재방문 의사 + 지역명 + 메인 키워드 재언급

[해시태그 규칙]
- 해시태그 7개 생성
- 지역명+키워드 조합 2개, 업종 관련 2개, 가게명 1개, 감성 키워드 2개

[금지 표현]
이로써, 이처럼, 혁신적인, 최고의, 완치, 100% 효과, 보장

아래 JSON 형식으로만 출력하세요. 다른 텍스트는 절대 포함하지 마세요:
{{
  "blog": {{
    "title": "제목 (25자 이내, 지역명+키워드 앞배치)",
    "body": "본문 전체 (3,000자 이상, 소제목 4개, [이미지: 설명] 4회, 구체적 수치 2개, 가게 기본정보 포함)",
    "hashtags": "#태그1 #태그2 #태그3 #태그4 #태그5 #태그6 #태그7"
  }},
  "review": {{
    "customer_review": "고객 입장 리뷰 예시 (300~350자, 방문 경험 중심, 키워드 자연 배치, 고객이 직접 쓴 것처럼 자연스럽게)",
    "owner_reply_1": "사장님 답글 예시 1 — 감사 + 방문 경험 공감 + 재방문 유도 (150~200자, 따뜻하고 친근한 톤, 가게명과 키워드 1회 포함)",
    "owner_reply_2": "사장님 답글 예시 2 — 구체적 서비스 언급 + 특별 혜택 안내 + 재방문 유도 (150~200자, 전문적이고 신뢰감 있는 톤, 키워드 1회 포함)"
  }},
  "shorts": {{
    "concept": "영상 컨셉 한 줄 (30~40초, 단독 리뷰형)",
    "timeline": [
      {{"time": "0~3초", "scene": "화면 설명 (썸네일용 후킹 장면)", "caption": "자막/대사", "thumbnail_text": "썸네일 문구"}},
      {{"time": "3~7초", "scene": "화면 설명", "caption": "자막/대사", "thumbnail_text": ""}},
      {{"time": "7~12초", "scene": "화면 설명 (제형/서비스 클로즈업)", "caption": "자막/대사", "thumbnail_text": ""}},
      {{"time": "12~18초", "scene": "화면 설명 (핵심 특징 강조)", "caption": "자막/대사", "thumbnail_text": ""}},
      {{"time": "18~24초", "scene": "화면 설명 (사용/체험 장면)", "caption": "자막/대사", "thumbnail_text": ""}},
      {{"time": "24~31초", "scene": "Before/After 또는 결과 장면", "caption": "자막/대사", "thumbnail_text": ""}},
      {{"time": "31~36초", "scene": "마무리 컷 + {shop_name} 노출", "caption": "자막/대사", "thumbnail_text": ""}}
    ],
    "filming_tips": {{
      "overall": "전체 촬영 포인트 (컨셉 방향)",
      "must_shots": ["필수 촬영 장면1", "필수 촬영 장면2", "필수 촬영 장면3", "필수 촬영 장면4", "필수 촬영 장면5"],
      "caption_style": "자막 스타일 가이드",
      "bgm": "배경음악 추천",
      "cut_transition": "컷 전환 팁"
    }},
    "caption_list": ["자막1", "자막2", "자막3", "자막4", "자막5", "자막6", "자막7", "자막8"],
    "instagram_body": "인스타그램/쇼츠 본문 (해시태그 포함, 바로 올릴 수 있게)"
  }},
  "thumbnail": {{
    "copies": {{
      "number_type": "숫자형 문구 (15자 이내, 예: 3회 만에 피부가 달라졌어요)",
      "question_type": "질문형 문구 (15자 이내, 예: 아직도 혼자 하세요?)",
      "emotion_type": "감성형 문구 (15자 이내, 예: 드디어 찾은 내 피부 루틴)"
    }},
    "main_image_guide": {{
      "best_shot": "메인 썸네일로 가장 효과적인 장면/사진 설명",
      "alternatives": ["대안 장면 1", "대안 장면 2"],
      "avoid": "피해야 할 장면/사진 설명"
    }},
    "design_guide": {{
      "background": "배경색 추천 및 이유",
      "font_style": "폰트 스타일 가이드",
      "point_color": "포인트 색상 추천"
    }},
    "cta": ["CTA 문구1 (예약/문의 유도)", "CTA 문구2", "CTA 문구3"]
  }}
}}
"""
    return prompt.strip()


# ── 병렬 생성용 분리 프롬프트 ─────────────────────────────────────────────────

def _get_context(
    shop_name: str,
    business_type: str,
    region: str,
    keyword: str,
    feature: str = "",
    tone: str = "friendly",
) -> dict:
    tone_guide = {
        "friendly": "친근하고 편안한 말투로, 이모지 1~2개 사용 가능",
        "professional": "격식체, 전문 용어를 자연스럽게 포함한 신뢰감 있는 말투",
        "emotional": "감성적이고 시적인 묘사, 짧고 여운 있는 문장",
    }
    biz = business_seo.get(business_type, {
        "keywords": [keyword],
        "review_focus": "서비스 품질, 가격, 분위기",
        "shorts_hook": "이곳 꼭 가보세요",
    })
    few = FEW_SHOT_EXAMPLES.get(business_type, {})
    return {
        "tone_desc": tone_guide.get(tone, tone_guide["friendly"]),
        "feature_text": f"\n가게 특징: {_sanitize(feature)}" if feature else "",
        "seo_keywords": ", ".join(biz["keywords"]),
        "review_focus": biz["review_focus"],
        "shorts_hook": biz["shorts_hook"],
        "blog_example": few.get("blog_example", ""),
        "review_example": few.get("review_example", ""),
    }


def build_blog_prompt(
    shop_name: str,
    business_type: str,
    region: str,
    keyword: str,
    feature: str = "",
    tone: str = "friendly",
) -> str:
    shop_name     = _sanitize(shop_name, 100)
    business_type = _sanitize(business_type, 50)
    region        = _sanitize(region, 100)
    keyword       = _sanitize(keyword, 100)
    feature       = _sanitize(feature, 200)

    ctx = _get_context(shop_name, business_type, region, keyword, feature, tone)
    few_shot = f"[블로그 참고 예시 - 이 품질과 스타일 참고]\n{ctx['blog_example']}\n" if ctx["blog_example"] else ""

    return f"""당신은 네이버 블로그 SEO 전문가이자 소상공인 마케팅 콘텐츠 작가입니다.
{few_shot}
가게명: {shop_name} | 업종: {business_type} | 지역: {region} | 키워드: {keyword}{ctx['feature_text']}
말투: {ctx['tone_desc']}
추천 SEO 키워드: {ctx['seo_keywords']}

[SEO 규칙 - C-Rank·D.I.A+ 기준]
- 제목: 지역명+키워드 앞배치, 25자 이내, 경험성 단어 포함(추천/후기/솔직/다녀온 중 택1)
- 도입부 첫 문장에 메인 키워드 반드시 포함
- 소제목(## 형식) 4개 이상, 그 중 2개에 키워드 포함
- 메인 키워드 3~5회 자연 배치 (연속 금지)
- 연관 키워드({ctx['seo_keywords']}) 3개 이상 자연 포함
- 구체적 수치 2개 이상 (가격, 소요시간, 횟수 등)
- 3,000자 이상
- [이미지: 설명] 형식 4회 이상
- 해시태그 7개: 지역+키워드 2개, 업종 2개, 가게명 1개, 감성 2개
- 금지: 이로써, 혁신적인, 최고의, 완치, 100% 효과

아래 JSON 형식으로만 출력하세요. 다른 텍스트는 포함하지 마세요:
{{
  "title": "제목 (25자 이내, 지역명+키워드 앞배치)",
  "body": "본문 전체 (3,000자 이상, 소제목 4개, [이미지: 설명] 4회, 수치 2개, 가게 기본정보 포함)",
  "hashtags": "#태그1 #태그2 #태그3 #태그4 #태그5 #태그6 #태그7"
}}""".strip()


def build_review_prompt(
    shop_name: str,
    business_type: str,
    region: str,
    keyword: str,
    feature: str = "",
    tone: str = "friendly",
) -> str:
    shop_name     = _sanitize(shop_name, 100)
    business_type = _sanitize(business_type, 50)
    region        = _sanitize(region, 100)
    keyword       = _sanitize(keyword, 100)

    ctx = _get_context(shop_name, business_type, region, keyword, feature, tone)
    few_shot = f"[리뷰 참고 예시]\n{ctx['review_example']}\n" if ctx["review_example"] else ""

    return f"""당신은 소상공인 마케팅 콘텐츠 작가입니다.
{few_shot}
가게명: {shop_name} | 업종: {business_type} | 지역: {region} | 키워드: {keyword}
말투: {ctx['tone_desc']} | 리뷰 포인트: {ctx['review_focus']}

[플레이스 리뷰 작성 규칙]
- customer_review: 고객이 직접 쓴 것처럼 자연스럽게 (300~350자)
  * 메인 키워드 1~2회 자연 포함, 구체적 경험(직원 친절도·결과물·가격·재방문 의사)
  * 과장 표현 금지
- owner_reply_1 (감사형): 감사 + 방문 경험 공감 + 재방문 유도 (150~200자, 따뜻한 어투, 가게명+키워드 1회)
- owner_reply_2 (정보형): 구체적 서비스 언급 + 다음 방문 혜택 안내 (150~200자, 전문적 어투, 키워드 1회)

아래 JSON 형식으로만 출력하세요. 다른 텍스트는 포함하지 마세요:
{{
  "customer_review": "고객 리뷰 예시 (300~350자)",
  "owner_reply_1": "사장님 답글 1 - 감사형 (150~200자)",
  "owner_reply_2": "사장님 답글 2 - 정보형 (150~200자)"
}}""".strip()


def build_shorts_prompt(
    shop_name: str,
    business_type: str,
    region: str,
    keyword: str,
    feature: str = "",
    tone: str = "friendly",
) -> str:
    shop_name = _sanitize(shop_name, 100)
    business_type = _sanitize(business_type, 50)
    region    = _sanitize(region, 100)
    keyword   = _sanitize(keyword, 100)
    feature   = _sanitize(feature, 200)

    ctx = _get_context(shop_name, business_type, region, keyword, feature, tone)
    feature_text = f"\n가게 특징: {feature}" if feature else ""

    return f"""당신은 숏폼 영상 대본 전문 작가입니다.
가게명: {shop_name} | 업종: {business_type} | 지역: {region} | 키워드: {keyword}{feature_text}
후킹 참고: "{ctx['shorts_hook']}"

[쇼츠/릴스 대본 규칙 - 30~40초, 7컷]
0~3초: 후킹(공감 질문/상황) | 3~7초: 서비스 정면 소개 | 7~12초: 핵심 특징 클로즈업
12~18초: 차별화 포인트 | 18~24초: 사용/체험 장면 | 24~31초: Before/After 또는 결과
31~36초: 마무리 + {shop_name} 노출
- 각 컷: scene(화면), caption(자막), thumbnail_text(첫 컷만 작성, 나머지 빈 문자열)
- filming_tips: overall, must_shots(5개), caption_style, bgm, cut_transition
- instagram_body: 해시태그 포함 완성형

아래 JSON 형식으로만 출력하세요. 다른 텍스트는 포함하지 마세요:
{{
  "concept": "영상 컨셉 한 줄",
  "timeline": [
    {{"time": "0~3초", "scene": "화면 설명", "caption": "자막", "thumbnail_text": "썸네일 문구"}},
    {{"time": "3~7초", "scene": "화면 설명", "caption": "자막", "thumbnail_text": ""}},
    {{"time": "7~12초", "scene": "화면 설명", "caption": "자막", "thumbnail_text": ""}},
    {{"time": "12~18초", "scene": "화면 설명", "caption": "자막", "thumbnail_text": ""}},
    {{"time": "18~24초", "scene": "화면 설명", "caption": "자막", "thumbnail_text": ""}},
    {{"time": "24~31초", "scene": "화면 설명", "caption": "자막", "thumbnail_text": ""}},
    {{"time": "31~36초", "scene": "마무리 컷", "caption": "자막", "thumbnail_text": ""}}
  ],
  "filming_tips": {{
    "overall": "전체 촬영 포인트",
    "must_shots": ["장면1", "장면2", "장면3", "장면4", "장면5"],
    "caption_style": "자막 스타일",
    "bgm": "BGM 추천",
    "cut_transition": "컷 전환 팁"
  }},
  "caption_list": ["자막1", "자막2", "자막3", "자막4", "자막5", "자막6", "자막7", "자막8"],
  "instagram_body": "인스타그램 본문 (해시태그 포함)"
}}""".strip()


def build_thumbnail_prompt(
    shop_name: str,
    business_type: str,
    region: str,
    keyword: str,
    feature: str = "",
    tone: str = "friendly",
) -> str:
    shop_name     = _sanitize(shop_name, 100)
    business_type = _sanitize(business_type, 50)
    region        = _sanitize(region, 100)
    keyword       = _sanitize(keyword, 100)

    return f"""당신은 SNS 마케팅 썸네일 전문가입니다.
가게명: {shop_name} | 업종: {business_type} | 지역: {region} | 키워드: {keyword}

[썸네일 작성 규칙]
- copies: 3가지 패턴 (모두 15자 이내)
  * number_type: 구체적 숫자/횟수/기간 포함 (신뢰감)
  * question_type: 타겟 고민/궁금증 자극하는 질문 (공감)
  * emotion_type: 감성적 변화/발견 표현 (감성)
- main_image_guide: best_shot(클릭률 높은 장면), alternatives(대안 2개), avoid(피해야 할 장면)
- design_guide: background, font_style, point_color (업종별 최적)
- cta: 행동 유도 문구 3종 (예약형/방문형/정보형)

아래 JSON 형식으로만 출력하세요. 다른 텍스트는 포함하지 마세요:
{{
  "copies": {{
    "number_type": "숫자형 문구 (15자 이내)",
    "question_type": "질문형 문구 (15자 이내)",
    "emotion_type": "감성형 문구 (15자 이내)"
  }},
  "main_image_guide": {{
    "best_shot": "메인 썸네일 최적 장면",
    "alternatives": ["대안 장면 1", "대안 장면 2"],
    "avoid": "피해야 할 장면"
  }},
  "design_guide": {{
    "background": "배경색 추천",
    "font_style": "폰트 스타일",
    "point_color": "포인트 색상"
  }},
  "cta": ["CTA 문구1", "CTA 문구2", "CTA 문구3"]
}}""".strip()