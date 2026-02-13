# EasyShorts Management - Frontend (Admin)

EasyShorts 백엔드(`Easyshorts_backend`)를 관리/모니터링하기 위한 관리자 페이지(React + Vite + TS).

## 요구사항
- Node.js LTS

## 설정
```bash
cd frontend
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000 등 설정
```

## 실행
```bash
npm install
npm run dev
```

## 현재 로그인 방식(임시)
백엔드에 관리자 전용 로그인/권한 API가 아직 없어, 우선 **Access Token(JWT) 붙여넣기 로그인**으로 시작해.

권장 확장:
- 백엔드에 `role=admin` + `/api/admin/*` 엔드포인트 추가
- 관리자 전용 로그인(또는 기존 OAuth 로그인 후 role 체크)

## 관리자 기능(제안)
- 유저 전체 조회/검색/비활성화
- 플랜/크레딧 관리
- 에피소드 전체 조회 + 결과물(S3) 정리
- 잡 모니터링(최근 pending/started/failed) + cancel
- 워커 상태(/api/health/worker) + 알림
