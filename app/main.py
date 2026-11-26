"""퍼시스그룹 공간 개설 비용 대시보드 (FastAPI).

화면은 app/static/index.html, 데이터는 app/data/ 의 JSON 스냅샷입니다.
분기마다 브랜드별 비용 시트를 읽어 만든 스냅샷으로 app/data/*.json 을 교체합니다.

보안 원칙:
- 시크릿은 환경변수에서만 읽습니다. 이 앱은 현재 시크릿을 쓰지 않습니다.
- 데이터 파일은 서버 안에서만 읽고, 오류 상세는 응답에 노출하지 않습니다.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DATASETS = ("spaces", "details", "meta")

app = FastAPI(title="퍼시스그룹 공간 개설 비용")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@lru_cache(maxsize=None)
def _load(name: str):
    with open(DATA_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    # Coolify Health Check. 데이터 파일과 무관하게 항상 200 을 반환해야 합니다.
    return {"status": "ok"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")


@app.get("/data.js")
def data_js() -> Response:
    """화면이 처음 열릴 때 읽는 데이터 스냅샷 (공간 목록·VM/SIGN 세부·기준일)."""
    try:
        body = (
            f"window.__SPACES={json.dumps(_load('spaces'), ensure_ascii=False)};"
            f"window.__DETAILS={json.dumps(_load('details'), ensure_ascii=False)};"
            f"window.__META={json.dumps(_load('meta'), ensure_ascii=False)};"
        )
    except Exception:
        raise HTTPException(status_code=500, detail="데이터를 읽지 못했어요.")
    return Response(body, media_type="application/javascript; charset=utf-8",
                    headers={"Cache-Control": "no-cache"})


@app.get("/api/{name}")
def api(name: str) -> JSONResponse:
    """데이터 스냅샷을 JSON 으로 내려줍니다 (spaces / details / meta)."""
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail="없는 데이터예요.")
    try:
        return JSONResponse(_load(name))
    except Exception:
        raise HTTPException(status_code=500, detail="데이터를 읽지 못했어요.")
