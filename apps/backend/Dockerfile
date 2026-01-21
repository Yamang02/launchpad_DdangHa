FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      fastapi "uvicorn[standard]" pydantic pydantic-settings \
      sqlalchemy psycopg2-binary asyncpg python-dotenv \
      bcrypt python-ulid email-validator alembic

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 개발 모드 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
