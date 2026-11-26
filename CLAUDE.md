# CLAUDE.md

본 프로젝트(`space-cost-dashboard`) 의 AI 작업 지침은 [`AGENTS.md`](./AGENTS.md) 를 참조해주세요.

## 가장 중요한 3가지 (반드시 준수)

1. **시크릿은 환경변수(`os.environ`)에서만** — DB 자격증명·API Key 를 코드/응답/로그에 절대 노출하지 마세요. MSSQL 변수는 `MSSQL_*`, SQL 은 `%s` 파라미터 바인딩.
2. **`/healthz` 는 DB 의존성 없이 200 유지** — Coolify Health Check 용이라 삭제 금지.
3. **분석은 pandas, 화면은 Jinja2 + Chart.js** — 외부 호출/DB 접근은 모두 FastAPI 서버 안에서만.

자세한 규칙(엔드포인트 패턴, 인증 주의, Coolify 배포 표준 등)은 `AGENTS.md` 에 정리되어 있어요.
