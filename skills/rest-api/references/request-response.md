# REST API Request/Response Patterns

## HTTP Methods

### GET - Read Only
Read-only operations with no state changes:

```python
@router.get("/v1/{tenant}/users/{user_id}")
async def get_user(tenant: str, user_id: str):
    return {"id": user_id, "name": "John Doe"}
```

**Rules:**
- Never modify data
- Idempotent (same result on multiple calls)
- Cacheable
- No request body

### POST - Create or Trigger Actions
Create resources or trigger actions:

```python
@router.post("/v1/{tenant}/users")
async def create_user(tenant: str, user: UserCreate):
    return {"id": "new-id", "name": user.name}

@router.post("/v1/{tenant}/mcps/{id}/invoke")
async def invoke_mcp(tenant: str, id: str, payload: InvokeRequest):
    return {"result": "...", "execution_time": 0.234}
```

**Use for:**
- Creating new resources
- Triggering actions
- Non-idempotent operations

### PUT - Full Replacement
Full replacement updates:

```python
@router.put("/v1/{tenant}/users/{user_id}")
async def update_user(tenant: str, user_id: str, user: UserUpdate):
    # Replace entire user resource
    return {"id": user_id, "name": user.name}
```

**Rules:**
- Replace entire resource
- Idempotent
- Include all fields in request

### DELETE - Remove Resources
Remove resources:

```python
@router.delete("/v1/{tenant}/users/{user_id}")
async def delete_user(tenant: str, user_id: str):
    return {"deleted": True}
```

**Rules:**
- Idempotent
- Return 404 if already deleted or doesn't exist

### Explicit 405 - Method Not Allowed
Handle unsupported methods explicitly:

```python
@router.get("/path/to/resource")
async def method_not_allowed():
    raise HTTPException(status_code=405, detail="Method Not Allowed")
```

**Benefits:**
- Clear error messages
- Prevents confusion
- Better API documentation

## Request Structure

### Flat, Explicit Field Names
Use clear, specific field names instead of generic wrappers:

**Good:**
```json
{
  "tool": "lookup_ip",
  "arguments": {"ip": "8.8.8.8"}
}
```

**Bad:**
```json
{
  "data": {
    "tool": "lookup_ip",
    "arguments": {"ip": "8.8.8.8"}
  }
}
```

**Bad:**
```json
{
  "payload": {
    "tool": "lookup_ip",
    "arguments": {"ip": "8.8.8.8"}
  }
}
```

### Avoid Generic Wrappers
Don't use generic field names like:
- ❌ `data`
- ❌ `payload`
- ❌ `body`
- ❌ `content`

**Instead:**
- ✅ Use specific, descriptive field names
- ✅ Make structure flat and explicit

## Response Structure

### Include Result and Metadata
Responses should include the result plus useful metadata:

```json
{
  "result": {
    "ip": "8.8.8.8",
    "location": "United States",
    "isp": "Google LLC"
  },
  "execution_time": 0.234,
  "timestamp": "2025-01-20T10:30:00Z"
}
```

**Useful metadata:**
- `execution_time` - How long the operation took
- `timestamp` - When the response was generated
- `request_id` - Correlation ID for debugging
- `version` - API or data version

### Success Response Examples

**Single resource:**
```json
{
  "id": "user-123",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2025-01-20T10:00:00Z"
}
```

**Collection:**
```json
{
  "items": [
    {"id": "1", "name": "Item 1"},
    {"id": "2", "name": "Item 2"}
  ],
  "total": 2,
  "page": 1,
  "page_size": 20
}
```

**Action result:**
```json
{
  "result": {"status": "completed"},
  "execution_time": 0.234,
  "request_id": "req-abc-123"
}
```

## Error Responses

### Structured with Error Codes
Errors should be structured with error codes for programmatic handling:

```json
{
  "error": "Tool not found",
  "error_code": "TOOL_NOT_FOUND",
  "context": {
    "tool_name": "invalid_tool",
    "available_tools": ["lookup_ip", "scan_port"]
  }
}
```

**Benefits:**
- Client can handle errors programmatically
- Consistent error format
- Rich context for debugging

### Error Code Examples

```python
# Not found
{
  "error": "User not found",
  "error_code": "USER_NOT_FOUND",
  "context": {"user_id": "123"}
}

# Validation error
{
  "error": "Invalid email format",
  "error_code": "VALIDATION_ERROR",
  "context": {"field": "email", "value": "invalid"}
}

# Permission denied
{
  "error": "Tenant not entitled to resource",
  "error_code": "PERMISSION_DENIED",
  "context": {"tenant_id": "acme", "resource_id": "mcp-123"}
}
```

## Status Codes

Use HTTP status codes appropriately:

### Success Codes
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST that creates a resource
- **202 Accepted**: Request accepted for async processing
- **204 No Content**: Successful DELETE

### Client Error Codes
- **400 Bad Request**: Invalid request format or validation error
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **405 Method Not Allowed**: HTTP method not supported
- **409 Conflict**: Resource conflict (e.g., duplicate)
- **422 Unprocessable Entity**: Semantic validation error

### Server Error Codes
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Service temporarily unavailable

**Implementation example:**
```python
from fastapi import HTTPException, status

# 200 - Success
@router.get("/users/{id}")
async def get_user(id: str):
    return {"id": id, "name": "John"}

# 400 - Bad Request
if not valid:
    raise HTTPException(status_code=400, detail="Invalid input")

# 403 - Forbidden
if not authorized:
    raise HTTPException(status_code=403, detail="Permission denied")

# 404 - Not Found
if not found:
    raise HTTPException(status_code=404, detail="User not found")

# 405 - Method Not Allowed
@router.post("/read-only-resource")
async def not_allowed():
    raise HTTPException(status_code=405, detail="Method Not Allowed")

# 503 - Service Unavailable
if service_down:
    raise HTTPException(status_code=503, detail="Service unavailable")
```

## State-Changing Operations

### Use POST with Action Verbs
For state-changing operations, use POST with explicit action verbs instead of complex PATCH operations:

**Good (explicit actions):**
```
POST /admin/v1/{tenant}/mcps/{id}/enable
POST /admin/v1/{tenant}/mcps/{id}/disable
POST /v1/{tenant}/mcps/{id}/invoke
POST /v1/{tenant}/workflows/{id}/run
```

**Bad (complex PATCH):**
```
PATCH /mcps/{id} {"enabled": true}
PATCH /mcps/{id} {"action": "invoke"}
```

**Benefits:**
- Clearer intent
- Self-documenting URLs
- Easier to understand and maintain
- Better fits RESTful actions

### Action Verb Examples

```python
# Enable/disable
@router.post("/admin/v1/{tenant}/mcps/{id}/enable")
async def enable_mcp(tenant: str, id: str):
    return {"id": id, "enabled": true}

# Invoke/execute
@router.post("/v1/{tenant}/mcps/{id}/invoke")
async def invoke_mcp(tenant: str, id: str, args: InvokeArgs):
    return {"result": "...", "execution_time": 0.234}

# Run/start
@router.post("/v1/{tenant}/workflows/{id}/run")
async def run_workflow(tenant: str, id: str):
    return {"run_id": "run-123", "status": "started"}
```

## Request/Response Best Practices

1. ✅ Use appropriate HTTP methods (GET, POST, PUT, DELETE)
2. ✅ Handle unsupported methods with explicit 405
3. ✅ Use flat, explicit field names (not generic wrappers)
4. ✅ Include result and metadata in responses
5. ✅ Structure errors with error codes for programmatic handling
6. ✅ Use appropriate HTTP status codes
7. ✅ Use POST with action verbs for state changes
8. ✅ Make API contracts clear and self-documenting

## Anti-Patterns to Avoid

❌ **Generic field names:**
```json
{"data": {...}, "payload": {...}}
```

❌ **GET requests that change state:**
```
GET /users/{id}/delete  ❌
```

❌ **Query parameters for complex data:**
```
POST /invoke?data={"complex":"json"}  ❌
```

❌ **Mixing concerns in single endpoint:**
```
POST /do-everything?action=create&type=user&...  ❌
```
