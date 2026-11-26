# AGENTS.md — AI 코딩 도구 작업 지침 (데이터 분석 / FastAPI)

이 파일은 Claude Code 등 AI 코딩 도구가 본 프로젝트에서 작업할 때 따르는 규칙입니다. 본 프로젝트는 **퍼시스홀딩스 사내 표준 스캐폴드 `@fursys/create-app`** 의 **데이터 분석(FastAPI)** 프리셋으로 생성되었고, 사내 Coolify 배포 정책을 따릅니다.

---

## 1. 프로젝트 정체

- **이름**: `space-cost-dashboard`
- **스택**: FastAPI + uvicorn + pandas + Jinja2 (Python 3.12)
- **용도**: 엑셀/CSV 업로드 분석, MSSQL 데이터베이스 조회/집계, 데이터 시각화
- **배포**: 사내 Coolify (단일 컨테이너, 비루트, 8000 포트)
- **외부 호스팅 의존성**: 0 (Streamlit Community Cloud·Vercel 등 외부 호스팅 사용 금지)
- **사용자**: 사내 비개발자 또는 주니어 — 학습 곡선이 낮게 유지되도록 신경

---

## 2. 시크릿 규칙 (가장 중요 — 반드시 준수)

### 절대 금지
- ❌ 시크릿(DB 자격증명, API Key 등)을 코드/응답/로그에 노출
- ❌ 클라이언트로 내려가는 HTML/JS 에 시크릿 포함
- ❌ 오류 응답에 스택 트레이스·내부 경로·쿼리 원문 노출

### 올바른 패턴
- ✅ 시크릿은 **환경변수에서만** 읽기 (`os.environ[...]`). 로컬은 `.env`, 운영은 Coolify env(Locked)
- ✅ DB/외부 호출은 모두 **서버(FastAPI) 안에서만**
- ✅ MSSQL 접속 변수: `MSSQL_HOST` / `MSSQL_PORT` / `MSSQL_USER` / `MSSQL_PASSWORD` / `MSSQL_DATABASE`

### MSSQL 접속
- `app/db.py` 의 `pymssql` 헬퍼를 사용. 새 자격증명을 코드에 하드코딩하지 말 것.
- SQL 파라미터는 `%s` 플레이스홀더로 바인딩 (SQL 인젝션 방지). 문자열 포매팅으로 쿼리 조립 금지.
- 새 환경변수를 추가하면 `.env.example` 도 함께 갱신(주석 + 예시).

---

## 3. API / 엔드포인트 패턴

```python
@app.post("/your-endpoint")
async def handler(...):
    # HTTP 메서드/입력 검증 먼저
    # 시크릿은 os.environ 으로만 접근, 외부 호출은 서버에서만
    # 실패 시 적절한 status code + 안전한 메시지 (상세 오류 비노출)
    return JSONResponse({...})
```

### 헬스 체크 보호
- `GET /healthz` 는 Coolify Health Check 가 호출합니다. **삭제 금지**, 200 + `{"status": "ok"}` 유지.
- 헬스 체크에 **DB/외부 의존성을 추가하지 마세요** (의존성이 죽으면 컨테이너가 unhealthy 처리됨).

### 파일 업로드
- 업로드 파일은 가능하면 **메모리에서 처리**(`io.BytesIO`). 디스크 저장이 필요하면 경로/용량/확장자를 검증.
- 지원 형식 외에는 400 으로 거절.

---

## 4. 데이터 / UI 작성 규칙

- 분석은 **pandas** 우선 사용 (AI 친화·표준). 무거운 의존성 추가는 신중히.
- 화면은 `app/templates/index.html` (Jinja2). 차트는 **Chart.js**(CDN) 사용.
- 본격 UI 가 필요하면 정적 자산을 `app/static/` 에 두고 mount.
- ❌ 사용자 입력을 그대로 HTML 에 삽입 금지(XSS). Jinja2 자동 이스케이프 유지.

---

### 이 프로젝트의 예외 (space-cost-dashboard)
- 화면은 Jinja2 템플릿 대신 `app/static/index.html` 정적 페이지 + d3(로컬 파일 `app/static/d3.min.js`)를 씁니다. 외부 CDN 을 쓰지 않습니다.
- 데이터는 `app/data/*.json` 스냅샷만 읽습니다. DB·fgdw·구글 시트에 접속하지 않습니다.
- `spaces.json` 필드 이름을 바꾸면 화면이 깨집니다.

---

## 5. 인증 / 접근 통제 (주의)

- 본 템플릿은 **기본 인증이 없습니다.** 사내망(Coolify) 안에서만 접근되는 것을 전제로 합니다.
- ⚠️ **민감 데이터를 다루고 접근 범위가 넓다면**, 최소한의 보호(예: 환경변수 기반 단순 토큰/비밀번호 게이트, 또는 사내 네트워크 제한)를 검토하세요.
- 풀 SSO/로그인 시스템은 현재 사내 표준이 없으므로, 필요해지면 별도로 논의 후 추가하세요.

---

## 6. Coolify 배포 표준 유지

### 절대 깨뜨리지 말 것
- ✅ `Dockerfile` 의 `python:3.12-slim` + 비루트 `appuser` 실행 유지
- ✅ `EXPOSE 8000`, `--host 0.0.0.0` 유지 (Coolify 포트 호환)
- ✅ `/healthz` 라우트 유지
- ✅ 의존성은 `requirements.txt` 에 **버전 고정**

### Docker Compose 금지
사내 Coolify 정책상 `docker-compose.yml` 사용 불가. 추가 서비스가 필요하면 별도 Coolify Application 으로 분리.

### 의존성 추가 시
- `requirements.txt` 에 버전 고정 후 `docker build` 통과 확인.
- 네이티브 빌드가 필요한 패키지는 slim 이미지 호환성(필요 시 `apt-get` 추가)을 확인.

---

## 7. 응답 톤 (AI 가 사람에게 답할 때)

- **한국어로 응답**, 정중하고 부드러운 어조 (`~해주시면 좋아요`)
- 기술 용어는 풀어쓰기
- 위험한 작업(운영 환경 변경, 대량 쿼리 등)은 명확히 경고 후 사용자 확인

---

## 8. 변경 시 함께 업데이트할 파일

| 변경 사항 | 함께 업데이트 |
|---------|-------------|
| 새 환경변수 사용 | `.env.example` (주석 + 예시) |
| 새 엔드포인트 | `README.md` 엔드포인트 표 |
| 의존성 추가 | `requirements.txt` + `docker build` 확인 |
| 보안 영향 변경 | 본 `AGENTS.md` 에 규칙 추가 |

---

> 본 파일은 `@fursys/create-app` 스캐폴드가 자동 생성했어요. 프로젝트가 진화하면 규칙을 추가/갱신하셔도 좋습니다.
