# EC2 배포 가이드

이 문서는 현재 저장소를 AWS EC2에 올려서 `docker compose`로 실행하는 기준입니다.

## 1. EC2 인스턴스 준비

- Ubuntu 22.04 LTS 인스턴스를 생성합니다.
- 보안 그룹에서 최소 아래 포트를 엽니다.
- `22` : SSH
- `80` : HTTP
- `443` : HTTPS
- `8000` : 테스트 중 직접 접근할 때만 임시 허용

## 2. EC2 접속 후 패키지 설치

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

권한 반영을 위해 한 번 로그아웃 후 다시 접속합니다.

## 3. 코드 받기

```bash
git clone https://github.com/gyullby11/owner_bot.git
cd owner_bot
```

## 4. 운영용 환경변수 만들기

```bash
cp backend/.env.prod.example backend/.env.prod
nano backend/.env.prod
```

필수로 바꿔야 하는 값:

- `OPENAI_API_KEY`
- `SECRET_KEY`
- `DATABASE_URL`

## 5. 컨테이너 실행

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

확인:

```bash
docker compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

정상 응답 예시:

```json
{"status":"ok"}
```

## 6. 배포 후 자주 쓰는 명령어

```bash
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

## 7. 다음 단계

오늘은 EC2에서 앱이 떠 있는 상태까지를 목표로 합니다.

다음 작업:

- nginx reverse proxy 연결
- certbot으로 HTTPS 적용
- 운영용 DB 분리
- 시크릿 관리 방식 정리
