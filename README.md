# BTW API 미들서버

## 개요

뷰통월드 내부 시스템과 외부 API(네이버웍스 등) 사이를 중계하는 FastAPI 기반 미들웨어 서버.
크롤러 3개를 자동 스케줄 실행하고, 외부 API 호출을 단일 창구로 처리한다.

---

## 전체 구조

```
외부 서비스 (Google News, SBA, 쇼핑몰 etc.)
        ↓  크롤링
┌───────────────────────────────────────────┐
│             btw-api (FastAPI)             │
│                                           │
│  /crawler/news/run    → new_crawler       │
│  /crawler/support/run → support_crawler   │
│  /crawler/ranking/run → ranking_crawler   │
│                                           │
│  /naverworks/board/post                   │
│         ↓                                 │
│    네이버웍스 Works API                    │
└───────────────────────────────────────────┘
```

---

## 디렉토리 구조

```
btw-api/
├── main.py                  # FastAPI 앱 진입점, 스케줄러 시작
├── .env                     # 환경변수 (크롤러 경로 등)
├── .env.example             # 환경변수 템플릿
├── requirements.txt
├── routers/
│   ├── crawler.py           # /crawler/* 엔드포인트
│   └── naverworks.py        # /naverworks/* 엔드포인트
└── services/
    └── scheduler.py         # APScheduler 자동 실행 정의
```

---

## 엔드포인트 목록

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| POST | `/crawler/news/run` | 뉴스 크롤러 수동 실행 |
| POST | `/crawler/support/run` | 지원사업 크롤러 수동 실행 |
| POST | `/crawler/ranking/run` | 랭킹 크롤러 수동 실행 |
| POST | `/naverworks/board/post` | 네이버웍스 게시판 글 작성 |

Swagger UI: `http://localhost:8000/docs`

---

## 동작 방식 상세

### 1. 서버 시작 흐름

```
uvicorn main:app 실행
    └─ load_dotenv()           # .env 파일 읽기
    └─ 라우터 등록 (/crawler, /naverworks)
    └─ startup_event()
           └─ start_scheduler()
                  ├─ 뉴스 크롤러    평일 08:00 (KST)
                  ├─ 지원사업 크롤러 매일  09:00 (KST)
                  └─ 랭킹 크롤러    매일  06:00 (KST)
```

---

### 2. 크롤러 수동 실행 (`/crawler/*`)

외부에서 POST 요청을 보내면 btw-api가 해당 크롤러를 subprocess로 실행한다.

**흐름 예시 — 뉴스 크롤러 수동 실행**

```
클라이언트
  POST http://localhost:8000/crawler/news/run
        ↓
  routers/crawler.py
    crawler_dir = "/Users/mac/code/new_crawler"  # .env에서 읽음
    python_exe  = crawler_dir/venv/bin/python3   # 크롤러 전용 venv
    subprocess.run([python_exe, "main.py"], cwd=crawler_dir)
        ↓
  new_crawler/main.py 실행
    - Google 뉴스 크롤링 (셀레니움)
    - HTML 리포트 생성
    - naverworks_board.write_board_post() 호출
        → [현재] print("[주석처리]...") 후 return  # 실제 전송 없음
        ↓
  {"status": "ok", "returncode": 0, "stdout": "...", "stderr": "..."}
```

**응답 예시**

```json
{
  "status": "ok",
  "returncode": 0,
  "stdout": "크롤링 완료\n[주석처리] 네이버웍스 토큰 발급 요청 생략\n[주석처리] 네이버웍스 게시판 업로드. title=26-03-17 뷰티 / 유통 뉴스",
  "stderr": ""
}
```

**에러 시 응답 예시** (크롤러 디렉토리 경로 오류 등)

```json
{
  "status": "error",
  "returncode": 1,
  "stdout": "",
  "stderr": "ModuleNotFoundError: No module named 'selenium'"
}
```

---

### 3. 스케줄러 자동 실행

서버가 떠 있는 동안 APScheduler가 백그라운드에서 실행되며,
설정된 시간에 크롤러를 자동으로 subprocess 실행한다.

```
06:00 KST → job_ranking()  → ranking_crawler/main.py 실행
08:00 KST → job_news()     → new_crawler/main.py 실행       (평일만)
09:00 KST → job_support()  → support_bussiness_crawler/main.py 실행
```

**스케줄러 로그 예시**

```
INFO [스케줄러] 뉴스 크롤러 시작
INFO [스케줄러] 뉴스 크롤러 완료
ERROR [스케줄러] 랭킹 크롤러 오류
      Traceback ...
```

---

### 4. 네이버웍스 게이트웨이 (`/naverworks/board/post`)

내부 서비스가 이 엔드포인트를 호출하면 btw-api가 네이버웍스 API를 대신 호출한다.
크롤러가 직접 연동하는 것과 달리, **어느 시스템에서든 이 창구 하나로** 게시판 업로드가 가능하다.

**흐름**

```
클라이언트 (크롤러 or 다른 서비스)
  POST http://localhost:8000/naverworks/board/post
  Body: {
    "board_id": "4070000000183117580",
    "title":    "26-03-17 뷰티 뉴스",
    "content":  "<html>...</html>"
  }
        ↓
  routers/naverworks.py
    1. _get_access_token()
         → JWT 생성 (RS256, 만료 1시간)
         → [현재] "MOCK_TOKEN" 반환  # 실제 API 호출 없음
         → [실서버] POST auth.worksmobile.com/oauth2/v2.0/token
    2. board_post()
         → [현재] print("[주석처리]...") 후 mock 응답 반환
         → [실서버] POST www.worksapis.com/v1.0/boards/{board_id}/posts
        ↓
```

**현재(MOCK) 응답 예시**

```json
{
  "status": "ok",
  "message": "MOCK - 실제 전송 안 됨",
  "board_id": "4070000000183117580",
  "title": "26-03-17 뷰티 뉴스"
}
```

**실서버 전환 후 응답 예시**

```json
{
  "status": "ok",
  "post_id": "123456789"
}
```

---

## 현재 MOCK 상태 정리

외부 연동이 실수로 실행되는 것을 막기 위해 아래 4개 파일의 외부 호출 코드를 주석 처리했다.

| 파일 | 차단된 동작 | 대체 동작 |
|------|------------|----------|
| `new_crawler/naverworks_board.py` | 네이버웍스 API 호출 | `print + return` |
| `support_bussiness_crawler/naverworks_board_upload.py` | 네이버웍스 API 호출 | `print + return` |
| `ranking_crawler/db_insertion.py` | AWS RDS INSERT | `print + return` |
| `new_crawler/shorten_link.py` | is.gd URL 단축 | 원본 URL 그대로 반환 |
| `btw-api/routers/naverworks.py` | 네이버웍스 API 호출 | `print + mock 응답` |

### 실서버 전환 방법

각 파일에서 아래 패턴을 찾아 `print + return` 2줄을 삭제하고 주석을 해제한다.

```python
# 현재 (MOCK)
print(f"[주석처리] 네이버웍스 게시판 업로드. title={title}")
return

# --- 실서버 사용 시 위 2줄 삭제 ---
# response = requests.post(url, headers=headers, json=body)
# ...

# 전환 후 (실서버)
response = requests.post(url, headers=headers, json=body)
# ...
```

---

## 로컬 실행

```bash
cd /Users/mac/code/btw-api
venv/bin/uvicorn main:app --reload --port 8000
```

접속:
- 상태 확인: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`

curl 예시:

```bash
# 뉴스 크롤러 수동 실행
curl -X POST http://localhost:8000/crawler/news/run

# 네이버웍스 게시판 글 작성
curl -X POST http://localhost:8000/naverworks/board/post \
  -H "Content-Type: application/json" \
  -d '{
    "board_id": "4070000000183117580",
    "title": "테스트 제목",
    "content": "<p>테스트 본문</p>"
  }'
```

---

## 서버 배포 (Ubuntu)

### 디렉토리 구조

```
/home/ubuntu/
├── btw-api/
├── new_crawler/
├── support_bussiness_crawler/
└── ranking_crawler/
```

### 서버 .env

```
NEW_CRAWLER_DIR=/home/ubuntu/new_crawler
SUPPORT_CRAWLER_DIR=/home/ubuntu/support_bussiness_crawler
RANKING_CRAWLER_DIR=/home/ubuntu/ranking_crawler
```

### systemd 서비스 (`/etc/systemd/system/btw-api.service`)

```ini
[Unit]
Description=BTW API Middleware (FastAPI)
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/btw-api
EnvironmentFile=/home/ubuntu/btw-api/.env
ExecStart=/home/ubuntu/btw-api/venv/bin/uvicorn main:app \
        --uds /tmp/api.sock \
        --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx 추가 블록 (기존 btw 설정 파일에 추가)

```nginx
location /api/ {
    include proxy_params;
    proxy_pass http://unix:/tmp/api.sock;
    proxy_read_timeout 600s;
    proxy_connect_timeout 10s;
    proxy_send_timeout 600s;
}
```

접속: `https://api.viewtongworld.com/health`
