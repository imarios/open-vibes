# REST API Advanced Patterns

## Authorization Pattern

### Entitlements Over Roles
Use entitlements for fine-grained control instead of role-based access:

```python
if not is_entitled(tenant_id, resource_id):
    raise PermissionError(f"Tenant {tenant_id} not entitled to {resource_id}")
```

**Benefits:**
- Fine-grained control
- Scalable across tenants
- Flexible permissions
- Easier to audit

**Example implementation:**
```python
from fastapi import Depends, HTTPException

async def check_entitlement(
    tenant_id: str,
    resource_id: str,
    entitlement_service: EntitlementService = Depends()
):
    if not await entitlement_service.is_entitled(tenant_id, resource_id):
        raise HTTPException(
            status_code=403,
            detail=f"Tenant {tenant_id} not entitled to {resource_id}"
        )
    return True

@router.post("/v1/{tenant}/mcps/{id}/invoke")
async def invoke_mcp(
    tenant: str,
    id: str,
    _: bool = Depends(check_entitlement)
):
    # Entitlement already checked
    return {"result": "..."}
```

## Performance Guidelines

### Data-Plane Optimization
For high-volume runtime operations (`/v1/...`):

**Characteristics:**
- **Minimal validation** in hot path
- **Async throughout** - all I/O operations async
- **Connection pooling** for databases and external services
- Fast response times critical

**Example:**
```python
@router.post("/v1/{tenant}/mcps/{id}/invoke")
async def invoke_mcp(tenant: str, id: str, args: InvokeArgs):
    # Minimal validation
    if not id:
        raise HTTPException(400, "ID required")

    # Async throughout
    async with pool.connection() as conn:
        result = await conn.execute(query)

    return {"result": result}
```

### Control-Plane Patterns
For administrative operations (`/admin/v1/...`):

**Characteristics:**
- **Rich validation** acceptable
- **Detailed error messages** for debugging
- **Audit logging** for all operations
- Higher latency acceptable

**Example:**
```python
@router.post("/admin/v1/{tenant}/mcps/{id}/enable")
async def enable_mcp(tenant: str, id: str, admin: Admin = Depends()):
    # Rich validation
    validate_tenant_exists(tenant)
    validate_mcp_exists(id)
    validate_admin_permissions(admin, tenant)

    # Detailed audit logging
    await audit_log.record({
        "action": "enable_mcp",
        "tenant": tenant,
        "mcp_id": id,
        "admin": admin.id,
        "timestamp": datetime.utcnow()
    })

    # Enable MCP
    result = await enable_mcp_service(id)

    return {
        "id": id,
        "enabled": True,
        "message": "MCP successfully enabled"
    }
```

## Migration Strategy

### Deprecation Headers
When deprecating endpoints, use HTTP headers to communicate:

```python
@router.get("/v1/{tenant}/old-endpoint")
async def deprecated_endpoint(response: Response):
    # Add deprecation headers
    response.headers["X-Deprecated"] = "true"
    response.headers["X-Sunset-Date"] = "2025-07-01"
    response.headers["X-Alternative"] = "/v1/{tenant}/new-endpoint"

    return {"data": "..."}
```

**Headers:**
- `X-Deprecated`: "true" to indicate deprecation
- `X-Sunset-Date`: Date when endpoint will be removed
- `X-Alternative`: New endpoint to use instead

**Benefits:**
- Clear communication to API consumers
- Programmatically detectable
- Gradual migration path

## Testing Requirements

Each endpoint should have comprehensive test coverage:

### 1. Happy Path Test
Test successful operation:

```python
async def test_create_user_success():
    response = await client.post("/v1/acme/users", json={
        "name": "John Doe",
        "email": "john@example.com"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
```

### 2. Permission Test (403)
Test authorization failure:

```python
async def test_create_user_forbidden():
    # User without proper entitlement
    response = await client.post("/v1/other-tenant/users", json={
        "name": "John Doe"
    })
    assert response.status_code == 403
    assert "not entitled" in response.json()["error"]
```

### 3. Validation Test (400)
Test input validation:

```python
async def test_create_user_invalid_email():
    response = await client.post("/v1/acme/users", json={
        "name": "John Doe",
        "email": "invalid-email"
    })
    assert response.status_code == 400
    assert "email" in response.json()["error"]
```

### 4. Method Test (405)
Test unsupported HTTP methods:

```python
async def test_users_method_not_allowed():
    response = await client.patch("/v1/acme/users/123")
    assert response.status_code == 405
    assert "Method Not Allowed" in response.json()["error"]
```

## Security

### Never Expose Sensitive Data
Never expose in API responses:
- ❌ API keys
- ❌ Database connection strings
- ❌ Stack traces
- ❌ Internal service URLs
- ❌ Passwords (even hashed)

### Always Include
Always include in responses/logs:
- ✅ Correlation IDs (`request_id`)
- ✅ Tenant validation
- ✅ Input sanitization
- ✅ Appropriate error messages (without sensitive details)

**Example:**
```python
@router.post("/v1/{tenant}/resource")
async def create_resource(tenant: str, data: ResourceCreate, request: Request):
    # Validate tenant
    if not tenant_exists(tenant):
        raise HTTPException(404, "Tenant not found")

    # Sanitize input
    sanitized_data = sanitize(data)

    try:
        result = await create(sanitized_data)
        return {
            "result": result,
            "request_id": request.state.request_id  # Correlation ID
        }
    except Exception as e:
        # Don't expose internal error details
        log.error(f"Error creating resource: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
```

## Anti-Patterns to Avoid

### ❌ Query Parameters for Complex Data
```python
# Bad
POST /invoke?data={"complex":"json","nested":{"values":true}}

# Good
POST /invoke
Body: {"complex": "json", "nested": {"values": true}}
```

### ❌ Mixing Concerns in Single Endpoint
```python
# Bad
POST /do-everything?action=create&type=user&mode=async

# Good
POST /users
POST /users/{id}/async-process
```

### ❌ Exposing Implementation Details in URLs
```python
# Bad
GET /postgres/users
GET /elasticsearch/search

# Good
GET /users
GET /search
```

### ❌ Generic Field Names
```python
# Bad
{"data": {...}, "payload": {...}}

# Good
{"user": {...}, "settings": {...}}
```

### ❌ GET Requests That Change State
```python
# Bad
GET /users/{id}/delete
GET /mcps/{id}/enable

# Good
DELETE /users/{id}
POST /mcps/{id}/enable
```

## Key Design Decisions

1. **Tenant in path** over header for clearer isolation
2. **Explicit actions** over RESTful purism for clarity
3. **Entitlements** over roles for scalability
4. **Structured errors** with codes for programmatic handling
5. **Version-first** URLs for clean evolution

## Future Work

These capabilities are planned but not yet implemented. Design current services with these in mind:

### 1. Pagination & Filtering

Add support for pagination and field filtering:

```
GET /v1/{tenant}/resources?limit=20&offset=0&fields=id,name,status
```

**Guidelines:**
- Use consistent pagination parameters across all endpoints
- Support field filtering to reduce payload size
- Consider cursor-based pagination for large datasets

**Example response:**
```json
{
  "items": [...],
  "total": 1000,
  "limit": 20,
  "offset": 0,
  "next": "/v1/{tenant}/resources?limit=20&offset=20"
}
```

### 2. Rate Limiting Headers

Expose rate limit information to clients:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Implementation:**
- Implement per-tenant limits at the API gateway
- Return 429 with Retry-After header when exceeded

**Example:**
```python
response.headers["X-RateLimit-Limit"] = "100"
response.headers["X-RateLimit-Remaining"] = "95"
response.headers["X-RateLimit-Reset"] = "1640995200"

# When exceeded
if rate_limit_exceeded:
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded",
        headers={"Retry-After": "60"}
    )
```

### 3. Caching Strategy

Implement HTTP caching with ETags:

```
ETag: "33a64df551"
Cache-Control: private, max-age=3600
If-None-Match: "33a64df551"
```

**Guidelines:**
- Use ETags for resource versioning
- Return 304 Not Modified when content unchanged
- Consider Redis for application-level caching

**Example:**
```python
@router.get("/v1/{tenant}/users/{id}")
async def get_user(id: str, if_none_match: str = Header(None)):
    user = await get_user(id)
    etag = generate_etag(user)

    # Client has current version
    if if_none_match == etag:
        return Response(status_code=304)

    # Return user with ETag
    return Response(
        content=user.json(),
        headers={
            "ETag": etag,
            "Cache-Control": "private, max-age=3600"
        }
    )
```

### 4. Authentication & Authorization

#### Authentication (JWT/OAuth2)
- JWT tokens in Authorization header
- OAuth2 flows for user authentication
- Service accounts for machine-to-machine

**Example:**
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/v1/{tenant}/protected")
async def protected(credentials = Depends(security)):
    token = credentials.credentials
    user = verify_jwt(token)
    return {"user": user}
```

#### Authorization (OPA/Rego)
- OPA sidecars for policy enforcement
- Rego policies loaded from S3 or similar
- Centralized policy management across services

**Design considerations for OPA integration:**
```python
# Future authorization check
# OPA sidecar will evaluate: can {tenant} perform {action} on {resource}?
if not await opa_client.authorize(tenant_id, action, resource):
    raise HTTPException(403)
```

**Keep authorization points clearly marked in code for future OPA integration.**
