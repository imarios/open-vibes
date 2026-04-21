# FastAPI Async and Database Patterns

## Async and Performance

### Use async def for I/O Operations

Use `async def` and `await` for all I/O-bound operations:

```python
from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/external-data")
async def get_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### Avoid Blocking Calls

Avoid blocking calls in async functions:

**Bad:**
```python
import requests

@router.get("/data")
async def get_data():
    # Blocking call in async function!
    response = requests.get("https://api.example.com")
    return response.json()
```

**Good:**
```python
import httpx

@router.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()
```

### Performance Optimization

#### Caching

Use caching for frequently accessed or static data:

```python
from functools import lru_cache

@lru_cache()
def get_settings():
    return Settings()

# Or use Redis for distributed caching
from redis import asyncio as aioredis

async def get_cached_user(user_id: str):
    redis = await aioredis.from_url("redis://localhost")
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    # Fetch from database and cache
    user = await fetch_user(user_id)
    await redis.set(f"user:{user_id}", json.dumps(user), ex=3600)
    return user
```

#### Lazy Loading

Prefer lazy loading for large responses or datasets:

```python
from fastapi.responses import StreamingResponse

@router.get("/large-file")
async def stream_large_file():
    async def generate():
        with open("large_file.csv") as f:
            for line in f:
                yield line

    return StreamingResponse(generate(), media_type="text/csv")
```

## Database Access

### Use Async-Native Libraries

Use async-native database libraries:

- **PostgreSQL**: `asyncpg`
- **MySQL**: `aiomysql`
- **SQLAlchemy 2.0+** with async support

### SQLAlchemy 2.0+ Async

Use SQLAlchemy 2.0+ with async support:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname",
    echo=True
)

# Create session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Use in dependency
async def get_db():
    async with async_session() as session:
        yield session
```

### Non-Blocking Database Operations

Ensure all DB operations are non-blocking and use async drivers:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@router.post("/users")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

## Dependency Injection

### Implement Dependency Injection

Implement dependency injection for shared services and resources:

```python
from fastapi import Depends

# Database session dependency
async def get_db():
    async with async_session() as session:
        yield session

# Service dependencies
def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)

# Use in routes
@router.post("/users")
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user)
```

### Reusable Dependencies

Define reusable dependencies in the `dependencies/` folder:

```python
# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    user = await verify_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user
```

Use in routes:

```python
from app.dependencies.auth import get_current_user

@router.get("/me")
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

## Background Processing

### FastAPI BackgroundTasks

Use FastAPI BackgroundTasks for non-blocking, post-response logic:

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Send email (blocking operation)
    print(f"Sending email to {email}: {message}")

@router.post("/users")
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    db_user = await create_user_in_db(db, user)

    # Add background task (runs after response is sent)
    background_tasks.add_task(
        send_email,
        email=user.email,
        message="Welcome to our platform!"
    )

    return db_user
```

**Use cases for BackgroundTasks:**
- Sending emails or notifications
- Logging operations
- Cache invalidation
- Non-critical data processing

**When NOT to use BackgroundTasks:**
- Long-running tasks (use task queue like Celery, ARQ instead)
- Tasks that need retry logic
- Tasks that need result tracking

## Best Practices

### Database Session Management

Always use dependency injection for database sessions:

```python
# Good - automatic cleanup
@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    return await db.execute(select(User))

# Bad - manual session management
@router.get("/users")
async def get_users():
    async with async_session() as db:
        return await db.execute(select(User))
```

### Connection Pooling

Configure appropriate connection pool sizes:

```python
engine = create_async_engine(
    database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

### Error Handling with Async

Handle errors properly in async context:

```python
@router.post("/users")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_user = User(**user.dict())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
```
