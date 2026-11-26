"""MSSQL 데이터베이스 연결 헬퍼.

- 접속 정보는 환경변수에서만 읽습니다 (서버사이드 전용). 절대 코드/응답에 노출 금지.
- 변수명: MSSQL_HOST / MSSQL_PORT / MSSQL_USER / MSSQL_PASSWORD / MSSQL_DATABASE
- 드라이버: pymssql (FreeTDS 기반, manylinux 휠에 FreeTDS 포함 → Docker 친화)
"""

from __future__ import annotations

import os
from typing import Any

import pymssql

_REQUIRED = (
    "MSSQL_HOST",
    "MSSQL_USER",
    "MSSQL_PASSWORD",
    "MSSQL_DATABASE",
)


def db_configured() -> bool:
    """필수 환경변수가 모두 설정되어 있는지 확인."""
    return all(os.environ.get(k) for k in _REQUIRED)


def get_connection():
    return pymssql.connect(
        server=os.environ["MSSQL_HOST"],
        port=os.environ.get("MSSQL_PORT", "1433"),
        user=os.environ["MSSQL_USER"],
        password=os.environ["MSSQL_PASSWORD"],
        database=os.environ["MSSQL_DATABASE"],
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
