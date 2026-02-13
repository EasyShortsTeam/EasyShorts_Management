# EasyShorts Management - Admin Backend (FastAPI)

관리자 페이지용 백엔드 스캐폴드(현재는 **mock/placeholder 응답** 중심)야.

- 기본 포트: **8000**
- API prefix: **/api**
- 정적 서빙: **/static/** (backend/app/static 디렉터리)

## Quickstart

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
pip install -r requirements.txt

# 환경변수(선택)
copy .env.example .env

# run
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

또는 스크립트:

```powershell
cd backend
.\scripts\run-dev.ps1
```

## Frontend 연동 포인트

프론트가 Vite를 쓸 경우(예상):
- `/api/*` → `http://localhost:8000/api/*`
- `/static/*` → `http://localhost:8000/static/*`

프론트가 `VITE_API_BASE_URL=http://localhost:8000` 로 잡으면, 프론트에서 `/api/...` 호출하는 형태로 그대로 동작.

## 제공하는 엔드포인트(현재 mock)

- `GET /api/health`
- `GET /api/auth/me`
- `GET /api/auth/login` (placeholder)
- `GET /api/auth/kakao` (placeholder)
- `GET /api/auth/kakao/callback` (placeholder)

- `GET /api/series` / `POST /api/series`
- `GET /api/series/{series_id}` / `PUT /api/series/{series_id}`

- `GET /api/episodes` / `POST /api/episodes`
- `GET /api/episodes/{episode_id}` / `PUT /api/episodes/{episode_id}`

- `GET /api/shorts` / `POST /api/shorts`
- `GET /api/shorts/{short_id}` / `PUT /api/shorts/{short_id}`
- `GET /api/shorts/{short_id}/video|story|community|ranking|choice|chat` (각각 placeholder)

- `POST /api/media/upload` (multipart stub)
- `GET /api/media/{media_id}` (download stub)

## Admin: Credits

- 프론트 페이지: `/credits`
- 관련 API: `/api/admin/credits/*`
- 설계 메모: `docs/CREDITS_DESIGN.md`

## 다음 단계(권장)

- 실제 DB 연결(`app/db/*`) + 모델/마이그레이션
- JWT/OAuth 실제 구현(`app/core/security.py`)
- 관리자 권한(roles/permissions) 기반으로 `/api/admin/*` 확장
- 크레딧은 in-memory 스캐폴드라서 DB+트랜잭션+감사로그로 교체 필요
