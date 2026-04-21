# FastAPI Routing and Models

## Routing

### Path Operation Decorators

Use path operation decorators for all endpoints:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def get_users():
    return []

@router.post("/users")
async def create_user(user: UserCreate):
    return user

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"id": user_id}
```

### Route Handlers in Routers

Define route handlers in `routers/` using named exports:

```python
# app/routers/users.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/users")
async def list_users():
    return []

@router.post("/users")
async def create_user(user: UserCreate):
    return user
```

Then include in `main.py`:

```python
from app.routers import users

app.include_router(users.router, prefix="/api/v1", tags=["users"])
```

### Return Type Annotations

Include clear return type annotations for every route:

```python
from typing import List

@router.get("/users", response_model=List[UserResponse])
async def get_users() -> List[UserResponse]:
    return []

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate) -> UserResponse:
    return user
```

## Request/Response Models

### Use Pydantic Models

Use Pydantic models for all input and output schemas:

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # For SQLAlchemy models
```

### Pydantic Validators

Leverage Pydantic validators to enforce constraints:

```python
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    username: str
    password: str

    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('must be at least 8 characters')
        return v
```

### RORO Pattern (Receive an Object, Return an Object)

Follow the RORO pattern - always use structured objects:

**Good:**
```python
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate) -> UserResponse:
    # Input is an object (UserCreate)
    # Output is an object (UserResponse)
    return UserResponse(...)
```

**Bad:**
```python
@router.post("/users")
async def create_user(username: str, email: str):
    # Input is raw parameters
    # Output is a raw dictionary
    return {"username": username, "email": email}
```

### Avoid Raw Dictionaries

Avoid using raw dictionaries for input or output:

**Bad:**
```python
@router.post("/users")
async def create_user(data: dict):
    return {"id": "123", "username": data["username"]}
```

**Good:**
```python
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate) -> UserResponse:
    return UserResponse(id="123", username=user.username)
```

## OpenAPI Automatic Documentation

FastAPI automatically generates interactive API documentation from your Pydantic models and route definitions.

### Accessing Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Customizing OpenAPI

Add metadata to routes and models:

```python
@router.post(
    "/users",
    response_model=UserResponse,
    summary="Create a new user",
    description="Create a new user with the provided information",
    response_description="The created user",
    tags=["users"]
)
async def create_user(user: UserCreate) -> UserResponse:
    """
    Create a new user:

    - **username**: unique username
    - **email**: valid email address
    - **age**: user age (0-150)
    """
    return user
```

### Schema Examples

Add examples to Pydantic models:

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    age: int

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "age": 30
            }
        }
```

### OpenAPI Metadata

Configure application metadata:

```python
app = FastAPI(
    title="My API",
    description="API for managing users and resources",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    }
)
```

## Validation Best Practices

### Never Trust Client Data

Never trust headers, cookies, or client-supplied data without validation:

```python
from fastapi import Header

@router.get("/users")
async def get_users(
    authorization: str = Header(...),  # Validated header
    page: int = Query(1, ge=1, le=100)  # Validated query param
):
    # authorization and page are guaranteed to be valid
    return []
```

### Use JSON Schema

Validate input/output using JSON Schema and Pydantic metadata:

```python
class UserFilter(BaseModel):
    age_min: int = Field(0, ge=0, le=150)
    age_max: int = Field(150, ge=0, le=150)
    roles: List[str] = Field(default_factory=list)

    @validator('age_max')
    def check_age_range(cls, v, values):
        if 'age_min' in values and v < values['age_min']:
            raise ValueError('age_max must be >= age_min')
        return v
```
