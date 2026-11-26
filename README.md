# space-cost-dashboard — 퍼시스그룹 공간 개설 비용

퍼시스그룹 6개 브랜드(퍼시스·일룸·시디즈·데스커·알로소·슬로우)와 컬렉티브 매장의 공간 개설 비용을 보여주는 **읽기 전용 대시보드**입니다. 사내 표준 스캐폴드(데이터 분석 프리셋)로 만들었고 사내 Coolify 로 배포합니다.

- 관리자: 공간경험디자인팀 김성화
- 데이터: 브랜드별 비용 스프레드시트를 분기마다 읽어 만든 **JSON 스냅샷** (서버가 시트에 직접 접속하지 않음)

## 시작하기

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload      # → http://localhost:8000
```

## 구성

| 경로 | 역할 |
|------|------|
| `app/main.py` | FastAPI 앱 |
| `app/static/index.html` | 대시보드 화면 (필터·차트·표·상세) |
| `app/static/shim.js` | 화면이 데이터를 읽는 연결 코드 |
| `app/static/d3.min.js`, `tokens.css`, `fonts/` | 차트 라이브러리(d3 7.9.0), 색상·글꼴(Pretendard) |
| `app/data/spaces.json` | 공간별 비용 (1행 = 1공간 1회 공사) |
| `app/data/details.json` | VM·SIGN 세부 내역 (공간 id 기준) |
| `app/data/meta.json` | 스냅샷 기준일·행 수 |
| `app/fgdw.py`, `app/db.py` | 스캐폴드 기본 DB 헬퍼 (현재 사용 안 함) |

## 엔드포인트

| 경로 | 내용 |
|------|------|
| `GET /` | 대시보드 화면 |
| `GET /data.js` | 화면이 읽는 데이터 스냅샷 |
| `GET /api/spaces`, `/api/details`, `/api/meta` | 같은 데이터를 JSON 으로 |
| `GET /healthz` | 헬스 체크 (항상 200) |

## 분기 데이터 갱신

1. 브랜드별 비용 시트(퍼시스 `[F] 매장개설비용`, 데스커 `[D] 매장개설비용` 등)를 읽어 `spaces.json`·`details.json` 을 다시 만든다.
2. `meta.json` 의 `snapshot_date` 와 `rows` 를 바꾼다.
3. 저장 후 GitHub 에 올리면 자동으로 다시 배포된다.

`spaces.json` 필드: `id, 브랜드, 연도, 월, 공간명, 카테고리, 공사유형, 지역, 면적_평, 설계비, 파사드, 인테리어, VM, 그래픽_사인, 총비용, 비용범위, 인테리어업체, VM업체, 그래픽업체, 원본시트, 비고, 세부유형, 컬렉티브`. 필드 이름을 바꾸면 화면이 깨지니 바꾸지 마세요.

---

문의: 공간경험디자인팀 / 배포 문의: IT본부 AI추진팀
