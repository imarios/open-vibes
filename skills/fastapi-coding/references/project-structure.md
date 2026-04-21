# FastAPI Project Structure

## Folder Structure

Follow this standard folder structure for FastAPI applications:

```
app/
├── main.py              # Application entry point
├── models/              # Database models (SQLAlchemy)
├── schemas/             # Pydantic models for request/response
├── routers/             # API route handlers
├── dependencies/        # Reusable dependency injection functions
├── services/            # Business logic layer
└── tests/               # Test files
```

**Key Principles:**
- **Separation of concerns**: Each directory has a single responsibility
- **Routers**: Handle HTTP routing and request/response
- **Services**: Contain business logic (keep routers thin)
- **Models**: Database ORM models (SQLAlchemy)
- **Schemas**: API contracts (Pydantic models for validation)
- **Dependencies**: Shared resources (DB sessions, auth, etc.)

## Application Initialization

Initialize FastAPI in `main.py`:

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Use lifespan context manager (recommended over @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting up...")
    yield
    # Shutdown logic
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

### Middleware Configuration

Configure middleware, CORS, and exception handlers in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### Lifespan Context Managers

Use lifespan context managers **instead of** `@app.on_event("startup")` and `@app.on_event("shutdown")`:

**Old pattern (deprecated):**
```python
@app.on_event("startup")
async def startup():
    # Setup code
    pass

@app.on_event("shutdown")
async def shutdown():
    # Cleanup code
    pass
```

**New pattern (recommended):**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await setup_database()
    yield
    # Shutdown
    await cleanup_database()

app = FastAPI(lifespan=lifespan)
```

## API Versioning

Group routes by version for maintainability:

```python
from fastapi import APIRouter

# Create versioned routers
v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
v1_router.include_router(users_router, prefix="/users", tags=["users"])
v1_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])

# Add to app
app.include_router(v1_router)
```

**URL structure:**
- `/api/v1/users`
- `/api/v1/alerts`

## Code Clarity

### Keep Route Handlers Short

Route handlers should be thin - delegate business logic to services:

**Bad:**
```python
@router.post("/users")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 50 lines of business logic here
    # Database operations
    # Validation
    # Email sending
    # etc.
```

**Good:**
```python
@router.post("/users")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends()
):
    return await user_service.create_user(db, user)
```

### File Organization

- **Co-locate related models and schemas**: Keep related code together
- **Keep files short and focused**: Each file should have a single, clear purpose
- **Use clear naming**: File names should indicate their purpose

### Concise Code

Use concise one-line conditionals where appropriate:

```python
if condition: do_something()
```

Avoid unnecessary curly braces and verbosity.

## Static Content & Types

### Static Assets

Serve static assets via FastAPI's static routing:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Shared Types

Place shared types and enums in a centralized `types/` module:

```python
# app/types/enums.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
```

## Reference Documentation

Regularly refer to the [FastAPI documentation](https://fastapi.tiangolo.com/) for updates and examples.
