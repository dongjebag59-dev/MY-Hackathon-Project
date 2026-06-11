# 사장봇 (SajangBot)

> **"ChatGPT는 글을 써주지만, 사장봇은 네이버에서 검색되는 글을 써줍니다."**

소상공인을 위한 AI 마케팅 콘텐츠 자동 생성 플랫폼.
가게명 · 업종 · 지역 · 키워드만 입력하면 **블로그 포스팅 · 플레이스 리뷰 · 쇼츠 대본 · 썸네일 문구** 4종을 1분 안에 생성합니다.

---

## 핵심 기능

| 기능 | 설명 |
|---|---|
| **네이버 SEO 최적화 블로그** | C-Rank · D.I.A+ 로직 내재화, 3,000자 이상, 소제목 4개, 해시태그 7개 자동 생성 |
| **플레이스 리뷰** | 고객 리뷰 예시 + 사장님 답글 2종 (감사형 · 정보형) |
| **쇼츠 / 릴스 대본** | 7컷 타임라인, 촬영팁, 자막 목록, 인스타그램 본문 완성형 |
| **썸네일 문구** | 숫자형 · 질문형 · 감성형 3종 + 디자인 가이드 + CTA 문구 |
| **12개 업종 Few-Shot** | 음식점 · 카페 · 헤어샵 · 피부관리 · 네일 · 학원 · 필라테스 등 업종별 최적화 |
| **크레딧 기반 결제** | 가입 시 3회 무료 체험, 이후 건당 결제 (라이트 / 베이직 / 프로) |
| **병렬 생성 + 실시간 스트리밍** | 4종 콘텐츠를 동시에 생성, 완료된 항목부터 즉시 표시 (SSE) |

---

## 기술 스택

```
Backend   FastAPI (Python) · SQLite + SQLAlchemy ORM · JWT 인증 · Pydantic v2
AI        OpenAI GPT-4o-mini · Few-Shot Prompting · JSON Mode · asyncio 병렬 처리
Frontend  HTML / CSS / JavaScript · Tailwind CSS · Fetch Streaming (SSE)
Infra     AWS EC2 · Docker Compose · GitHub Actions CI/CD · nginx 리버스 프록시
```

---

## 로컬 실행

### 1. 클론

```bash
git clone https://github.com/dongjebag59-dev/MY-Hackathon-Project.git
cd MY-Hackathon-Project
```

### 2. 환경변수 설정

```bash
cd backend
cp .env.example .env
```

`.env` 파일을 열어 `OPENAI_API_KEY` 값을 입력합니다.

```env
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

> API 키는 [platform.openai.com/api-keys](https://platform.openai.com/api-keys) 에서 발급받을 수 있습니다.

### 3. 실행

```bash
# 프로젝트 루트에서
docker-compose up
```

| 주소 | 설명 |
|---|---|
| http://localhost:8000 | 서비스 메인 |
| http://localhost:8000/docs | FastAPI 자동 API 문서 |
| http://localhost:8000/health | 헬스체크 |

---

## EC2 운영 배포

```bash
cp backend/.env.prod.example backend/.env.prod
# .env.prod에 실제 값 입력

touch backend/owner_bot.db   # DB 파일 미리 생성
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

상세 배포 가이드: [`docs/ec2-deploy.md`](docs/ec2-deploy.md)

---

## 프로젝트 구조

```
MY-Hackathon-Project/
├── backend/
│   ├── api/
│   │   └── router.py               # API 라우터 통합
│   ├── modules/
│   │   ├── generate/
│   │   │   ├── prompt_builder.py   # 12개 업종 × 4종 콘텐츠 Few-Shot 프롬프트
│   │   │   ├── service.py          # 병렬 생성(asyncio.gather) + SSE 스트리밍
│   │   │   ├── router.py           # POST /generate, POST /generate/stream
│   │   │   ├── crud.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── history/                # 생성 이력 · 재생성 · 크레딧 트랜잭션
│   │   ├── mypage/                 # 마이페이지 · 충전 패키지
│   │   └── user/                   # 회원가입 · 로그인 · JWT
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── nginx.conf
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── .env.prod.example
├── frontend/
│   ├── index.html                  # 랜딩 페이지
│   ├── generate.html               # 콘텐츠 생성 화면 (실시간 스트리밍 UI)
│   ├── login.html / register.html
│   ├── mypage.html
│   ├── css/my_styles.css
│   └── js/
│       ├── generate.js             # SSE 스트리밍 fetch + 진행 상태 UI
│       ├── api.js / auth.js / common.js
│       ├── history.js / mypage.js / index.js
├── docs/
│   └── ec2-deploy.md
├── docker-compose.yml              # 로컬 개발용
├── docker-compose.prod.yml         # EC2 운영 배포용
└── .github/workflows/deploy.yml   # GitHub Actions CI/CD
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/api/generate` | 4종 콘텐츠 병렬 생성 (JSON 응답) |
| `POST` | `/api/generate/stream` | 4종 콘텐츠 병렬 생성 (SSE 스트리밍) |
| `POST` | `/api/auth/register` | 회원가입 |
| `POST` | `/api/auth/login` | 로그인 (JWT 발급) |
| `GET` | `/api/history` | 생성 이력 목록 |
| `POST` | `/api/history/{id}/regenerate` | 이력 기반 재생성 |
| `GET` | `/api/mypage/me` | 내 정보 · 크레딧 조회 |
| `POST` | `/api/mypage/credits/charge` | 크레딧 충전 |

---

## 요금제

| 플랜 | 금액 | 크레딧 | 단가 |
|---|---|---|---|
| 무료 체험 | 0원 | 가입 시 3회 | - |
| 라이트 | 3,900원 | 3회 | 1,300원/회 |
| 베이직 | 9,900원 | 10회 | 990원/회 |
| 프로 | 19,900원 | 25회 | 796원/회 |

> 현장 인터뷰(담다살롱 · 피드헤어 · 타코집 · 가인미가) 기반으로 월 구독 대신 건당 결제 모델로 설계했습니다.

---

## 개발 배경

소상공인은 블로그 글 1편 작성에 평균 1~2시간을 소요하며, 네이버 SEO 로직(C-Rank · D.I.A+)을 모르면 직접 써도 검색에 노출되지 않습니다. 마케팅 대행은 월 30~50만 원 이상으로 부담이 크고, 쇼츠 대본 작성은 진입 장벽이 높아 포기하는 경우가 많습니다.

사장봇은 이 문제를 **키워드 입력 하나**로 해결합니다.

---

## 팀

| 이름 | 역할 |
|---|---|
| 유가영 | PM · AI 프롬프트 설계 · DevOps (CI/CD · EC2) |
| 박동제 | Backend — JWT 인증 · 크레딧 시스템 · 이력 API |
| 이제민 | Frontend — UI 구현 · 마이페이지 · 히스토리 |
| 김정원 | Backend / Infra — EC2 배포 · nginx |
| 유동주 | React 모바일 버전 개발 |

---

*2팀 해커톤 프로젝트 · 2026년 5월*
