# FastAPI Security and Testing

## Error Handling

### HTTPException for Expected Errors

Raise `HTTPException` for expected errors with appropriate status codes:

```python
from fastapi import HTTPException, status

@router.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### Middleware for Unexpected Errors

Handle unexpected errors via middleware and logging:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logging.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
```

### Structured Error Responses

Model structured error responses using Pydantic BaseModel:

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: str

@router.get("/users/{user_id}", responses={404: {"model": ErrorResponse}})
async def get_user(user_id: str):
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )
```

## Security

### FastAPI Security Utilities

Use FastAPI's built-in security utilities for authentication and authorization:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    # Verify JWT token
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload

@router.get("/protected")
async def protected_route(user = Depends(verify_token)):
    return {"user": user}
```

### Input Validation

Sanitize and validate all user input via Pydantic:

```python
from pydantic import BaseModel, validator, Field

class UserInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    bio: str = Field("", max_length=500)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('must be alphanumeric')
        return v.lower()

    @validator('bio')
    def sanitize_bio(cls, v):
        # Strip HTML tags
        return re.sub(r'<[^>]+>', '', v)
```

### Never Trust Client Data

Never trust headers, cookies, or client-supplied data without validation:

```python
from fastapi import Header, Cookie

@router.get("/data")
async def get_data(
    authorization: str = Header(...),  # Required header
    user_id: str = Cookie(None),       # Optional cookie
    page: int = Query(1, ge=1, le=100) # Validated query param
):
    # All inputs are validated
    return {"page": page}
```

## Testing

### Implement Unit and Integration Tests

Implement unit and integration tests across all endpoints and services:

```python
# app/tests/test_users.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={"username": "testuser", "email": "test@example.com"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_nonexistent_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/nonexistent")
        assert response.status_code == 404
```

### Test Structure

Structure tests under `app/tests/` using pytest:

```
app/
└── tests/
    ├── conftest.py           # Test fixtures
    ├── test_users.py         # User endpoint tests
    ├── test_auth.py          # Auth tests
    └── test_services.py      # Service layer tests
```

### Test Fixtures

Use pytest fixtures for reusable test setup:

```python
# app/tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database import Base

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()

@pytest.fixture
async def client(db_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

## Observability

### Logging

Use middleware to integrate logging with structured JSON format:

```python
import logging
import json
from datetime import datetime

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()

    log_data = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration": duration,
        "timestamp": start_time.isoformat()
    }

    logging.info(json.dumps(log_data))
    response.headers["X-Request-ID"] = request_id
    return response
```

### Include request_id

All logs should include a request_id:

```python
from fastapi import Request

@router.get("/users")
async def get_users(request: Request):
    request_id = request.state.request_id
    logging.info(f"Fetching users", extra={"request_id": request_id})
    return []
```

### Structured JSON Format

Use structured JSON format for log ingestion:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        return json.dumps(log_data)

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

### Metrics and Error Monitoring

Integrate metrics and error monitoring tools:

```python
# Example: Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

## ID Conventions

### Tenant ID

Use VARCHAR(255) strings for tenant IDs:

```python
from pydantic import BaseModel

class TenantBase(BaseModel):
    tenant_id: str = Field(..., max_length=255)
```

### Resource IDs

Use PostgreSQL UUID v4 for resource IDs:

```python
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False)
```

In Pydantic schemas:

```python
from pydantic import BaseModel
from uuid import UUID

class UserResponse(BaseModel):
    id: UUID
    tenant_id: str
    username: str
```
