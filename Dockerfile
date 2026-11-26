# ──────────────────────────────────────────────────────────────
# space-cost-dashboard — Coolify 배포용 Dockerfile (FastAPI + pandas)
# ──────────────────────────────────────────────────────────────
# 빌드: docker build -t space-cost-dashboard .
# 실행: docker run -p 8000:8000 space-cost-dashboard
# ──────────────────────────────────────────────────────────────

FROM python:3.12-slim AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# pymssql 은 manylinux 휠에 FreeTDS 가 포함되어 별도 시스템 패키지가 필요 없습니다.
# (소스 빌드가 필요한 특수 환경이면 아래 주석을 해제하세요)
# RUN apt-get update && apt-get install -y --no-install-recommends freetds-dev gcc \
#  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# 비루트 사용자로 실행 (보안)
RUN useradd --system --uid 1001 appuser
USER appuser

EXPOSE 8000
# Coolify Health Check Path: /healthz
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
