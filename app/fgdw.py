"""fgdw (사내 MSSQL Data Warehouse) 연결 헬퍼.

- 접속 정보는 환경변수에서만 읽습니다 (서버사이드 전용). 절대 코드/응답/로그에 노출 금지.
- 변수명: FGDW_DB_HOST / FGDW_DB_PORT / FGDW_DB_NAME / FGDW_DB_USER / FGDW_DB_PASSWORD
- 드라이버: pymssql (FreeTDS 기반, manylinux 휠에 FreeTDS 포함 → Docker 친화. pyodbc 회피).

자격증명 운영 안내:
  - 로컬 개발 시 FGDW_DB_USER / FGDW_DB_PASSWORD 에 "본인 fgdw 개발 계정" 을 넣습니다.
  - 배포 시에는 중앙 배포 프록시가 USER/PASSWORD 를 사내 공용 시스템계정으로 강제 치환하고
    HOST/NAME 을 정규화합니다 → 실무자는 공용 비번을 몰라도 됩니다. 실제 비밀번호를
    repo 에 커밋하지 마세요(.env 는 gitignore, .env.example 만 커밋).
"""

from __future__ import annotations

import os
from typing import Any

import pymssql

_REQUIRED = (
    "FGDW_DB_HOST",
    "FGDW_DB_USER",
    "FGDW_DB_PASSWORD",
    "FGDW_DB_NAME",
)


def fgdw_configured() -> bool:
    """필수 환경변수가 모두 설정되어 있는지 확인."""
    return all(os.environ.get(k) for k in _REQUIRED)


def _server_and_port() -> tuple[str, int]:
    # FGDW_DB_HOST 는 `192.9.201.23,1672` 처럼 MSSQL 의 `server,port` 형식일 수 있습니다.
    # 쉼표가 있으면 분리하고, 없으면 FGDW_DB_PORT(기본 1672)를 사용합니다.
    host = os.environ["FGDW_DB_HOST"]
    if "," in host:
        server, port = host.split(",", 1)
        return server.strip(), int(port.strip())
    return host.strip(), int(os.environ.get("FGDW_DB_PORT", "1672"))


def get_connection():
    server, port = _server_and_port()
    return pymssql.connect(
        server=server,
        port=port,
        user=os.environ["FGDW_DB_USER"],
        password=os.environ["FGDW_DB_PASSWORD"],
        database=os.environ["FGDW_DB_NAME"],
        login_timeout=5,
        timeout=15,
    )


def query(sql: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
    """SELECT 결과를 dict 리스트로 반환. 파라미터는 %s 플레이스홀더로 바인딩(SQL 인젝션 방지)."""
    conn = get_connection()
    try:
        cur = conn.cursor(as_dict=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        conn.close()


def sample_tables() -> list[dict[str, Any]]:
    """예시 쿼리 — fgdw 의 테이블 목록 상위 5개. 실제 사용 시 SQL 을 바꿔주세요."""
    return query("SELECT TOP 5 name FROM sys.tables ORDER BY name")
