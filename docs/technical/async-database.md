# Async Database (postgresql+asyncpg / get_db)

본 문서는 **DdangHa** 백엔드의 비동기 DB 연결 구조를 설명한다.

- **postgresql+asyncpg 엔진**: SQLAlchemy 2.0 async + asyncpg 드라이버
- **get_db async generator**: FastAPI `Depends`용 세션 제너레이터

구현 위치: `apps/backend/app/shared/database.py`

---

## 목차

1. [postgresql+asyncpg 엔진](#1-postgresqlasyncpg-엔진)
2. [get_db async generator](#2-get_db-async-generator)
3. [환경 변수](#3-환경-변수)
4. [로컬 개발 (docker-compose)](#4-로컬-개발-docker-compose)
5. [참고](#5-참고)

---

## 1. postgresql+asyncpg 엔진

### 1.1 역할

- FastAPI 비동기 요청과 맞추기 위해 **async 전용** 엔진 사용
- `asyncpg`는 PostgreSQL용 **네이티브 비동기** 드라이버
- 동기 드라이버(psycopg2) 대신 I/O 대기 시 이벤트 루프를 블로킹하지 않음

### 1.2 URL 변환

`DATABASE_URL`은 **`.strip()` 후**에 판단한다. 공백만 있거나 비어 있으면 기본값을 쓴다.  
`postgresql://` 이면 async용으로 `postgresql+asyncpg://`로 바꾼다.

```
postgresql://user:pass@host:5432/db
    → postgresql+asyncpg://user:pass@host:5432/db
```

**규칙**

| `DATABASE_URL` (strip 후) | 변환 결과 |
|---------------------------|-----------|
| 비어 있음 (공백만 있어도 해당) | `postgresql+asyncpg://localhost:5432/ddangha_db` (기본값) |
| `postgresql://...` | `postgresql+asyncpg://...` 로 치환 |
| 이미 `postgresql+asyncpg://...` | 그대로 사용 |

### 1.3 엔진 생성

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    _url,
    echo=os.getenv("SQL_ECHO", "").lower() in ("1", "true")
)
```

- `echo=True`: SQL 로그를 stdout에 출력 (디버깅용)
- `SQL_ECHO=1` 또는 `SQL_ECHO=true`일 때만 켜짐

### 1.4 async_session_maker

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)
```

| 옵션 | 설명 |
|------|------|
| `class_=AsyncSession` | 세션 클래스를 비동기용 `AsyncSession`으로 지정 |
| `expire_on_commit=False` | `commit` 후 객체가 자동으로 만료되지 않아, 응답에서 `session`으로 조회한 객체를 그대로 사용 가능 |
| `autoflush=False` | `commit` 전 자동 flush를 끔. 트랜잭션 제어를 코드에서 명시적으로 하기 위함 |

---

## 2. get_db async generator

### 2.1 역할

- 요청 단위로 **DB 세션 한 번** 생성
- 핸들러/서비스에서 `Depends(get_db)`로 `AsyncSession` 주입
- 응답/예외 후 **commit / rollback**과 세션 정리를 한 곳에서 처리

### 2.2 시그니처

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
```

- `async` 제너레이터 → `yield`로 `AsyncSession`을 넘기고, `await` 사용 가능
- 반환 타입 `AsyncGenerator[AsyncSession, None]`은 `yield` 값이 `AsyncSession`임을 의미

### 2.3 내부 동작

```python
async with async_session_maker() as session:
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

1. `async with async_session_maker()` 로 세션 생성
2. `yield session` → 라우터/서비스가 이 `session` 사용
3. **정상 종료**: `await session.commit()`
4. **예외**: `await session.rollback()` 후 같은 예외를 다시 `raise`
5. `async with` 종료 시 세션 `close` 등 정리

### 2.4 FastAPI에서 사용

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db

@router.post("/items")
async def create_item(
    item: ItemCreate,
    session: AsyncSession = Depends(get_db)
):
    obj = ItemModel(**item.model_dump())
    session.add(obj)
    # get_db가 commit/rollback 처리
    return {"id": obj.id}
```

- `Depends(get_db)` 로 요청마다 새 세션이 생성·주입됨
- `session.add` 등만 하고, **핸들러 안에서 `commit`/`rollback`을 호출하지 않음** (get_db가 담당)

### 2.5 의존성 체인

`get_db`를 쓰는 다른 의존성(예: `get_user_repository`)을 만드는 경우:

```python
def get_user_repository(session: AsyncSession = Depends(get_db)):
    return UserRepository(session)
```

- FastAPI가 `get_db`를 먼저 실행해 `session`을 얻고, 그 `session`으로 `get_user_repository`를 호출한다.
- `get_db`는 제너레이터이므로, 요청이 끝날 때까지 세션이 유지되고, 끝나면 `commit`/`rollback` 및 `close`가 수행된다.

---

## 3. 환경 변수

| 변수 | 설명 | 예 |
|------|------|-----|
| `DATABASE_URL` | PostgreSQL 연결 URL | `postgresql://user:pass@localhost:5432/ddangha_db` |
| `SQL_ECHO` | SQL 로그 여부 | `1`, `true` (대소문자 무관) |

---

## 4. 로컬 개발 (docker-compose)

`docker-compose.yml`의 **backend** 서비스는 다음처럼 `DATABASE_URL`을 받는다.

```yaml
environment:
  - DATABASE_URL=postgresql://ddangha_user:ddangha_password@postgres:5432/ddangha_db
```

- **postgres** 컨테이너 내부 포트 5432, 호스트에는 **5433** 매핑 (`5432:5432`)
- backend는 같은 Docker 네트워크에서 `postgres:5432`로 접속
- **호스트에서 직접** uvicorn을 돌릴 때는 `localhost:5432` 사용:
  - `DATABASE_URL=postgresql://ddangha_user:ddangha_password@localhost:5433/ddangha_db`
- `env.example`의 `DATABASE_URL` 형식을 따르면 된다. `database.py`가 `postgresql+asyncpg://`로 자동 변환한다.

---

## 5. 참고

- [SQLAlchemy 2.0 Asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [asyncpg](https://magicstack.github.io/asyncpg/current/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
