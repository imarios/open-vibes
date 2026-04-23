# REST API URL Design

## Core URL Pattern

```
/v1/{tenant}/{resource}/{id}/{action}
/admin/v1/{tenant}/{resource}/{id}/{action}
```

**Design principles:**
- **Version first** for clean API evolution
- **Tenant in path** for routing-level isolation and authorization
- **Resource hierarchy** makes ownership explicit
- **Actions as sub-resources** keeps operations contextual

**Examples:**
```
GET    /v1/acme-corp/users/123
POST   /v1/acme-corp/users
POST   /v1/acme-corp/mcps/abc-123/invoke
POST   /admin/v1/acme-corp/mcps/abc-123/enable
DELETE /v1/acme-corp/users/123
```

## Control vs Data Plane Separation

Separate your API into two distinct planes with different characteristics:

### Control-Plane (`/admin/v1/...`)
**Purpose:** Configuration, entitlements, health monitoring

**Characteristics:**
- Lower volume, higher latency acceptable
- Rich validation and detailed error messages
- Audit logging required
- Complex authorization checks
- Administrative operations

**Examples:**
```
POST   /admin/v1/{tenant}/mcps/{id}/enable
POST   /admin/v1/{tenant}/mcps/{id}/disable
GET    /admin/v1/{tenant}/health
POST   /admin/v1/{tenant}/entitlements
```

### Data-Plane (`/v1/...`)
**Purpose:** High-volume runtime operations

**Characteristics:**
- High volume, low latency required
- Minimal validation in hot path
- Async throughout
- Connection pooling
- Fast reads and writes

**Examples:**
```
POST   /v1/{tenant}/mcps/{id}/invoke
GET    /v1/{tenant}/tasks/{id}
POST   /v1/{tenant}/alerts
```

**Benefits of separation:**
- Different scaling strategies
- Different security requirements
- Different performance optimizations
- Clearer operational boundaries

## Naming Conventions

### Plural Collections
Use plural nouns for collections:

```
✅ /users
✅ /tasks
✅ /mcps
✅ /knowledge-units

❌ /user
❌ /task
```

### Kebab-Case
Use kebab-case for multi-word resources:

```
✅ /mcp-configs
✅ /knowledge-units
✅ /workflow-runs

❌ /mcpConfigs
❌ /mcp_configs
❌ /MCPConfigs
```

### Actions as Verbs
Use clear action verbs for operations:

```
✅ /enable
✅ /disable
✅ /invoke
✅ /execute
✅ /validate

❌ /enablement
❌ /activation
```

## Multi-Tenancy

### Tenant in Path
Place tenant ID in the URL path for routing-level isolation and authorization:

```
/v1/{tenant_id}/resources/{id}
```

**Benefits:**
- Edge routing based on tenant
- Natural authorization boundary
- Rate limiting per tenant
- Clear ownership in URLs
- Easier monitoring and logging

**Example:**
```
GET /v1/acme-corp/users/123
GET /v1/widget-inc/users/456
```

### Global Operations
Use `_` as a tenant placeholder for global/cross-tenant operations:

```
/admin/v1/_/resources/{id}/action
```

**Example:**
```
GET /admin/v1/_/system/health
GET /admin/v1/_/metrics/summary
```

### Legacy Support
Use `default` tenant for backward compatibility with non-multi-tenant APIs:

```
/v1/default/resources/{id}
```

**Example:**
```
GET /v1/default/users/123  # Legacy single-tenant behavior
```

## Versioning

### Version-First URLs
Place version at the start of the URL path for clean API evolution:

```
✅ /v1/{tenant}/users
✅ /v2/{tenant}/users

❌ /{tenant}/v1/users
❌ /{tenant}/users?version=1
```

**Benefits:**
- Clear version visibility
- Easy routing at load balancer level
- Simple deprecation strategy
- Version-specific documentation

**Evolution example:**
```
# Version 1
GET /v1/acme-corp/users/123

# Version 2 with breaking changes
GET /v2/acme-corp/users/123
```

## Router Organization

### One Router Per Concern

Organize routers with explicit prefixes to prevent conflicts:

```python
# Proxy router
proxy_router = APIRouter(prefix="/v1", tags=["proxy"])

# Admin router
admin_router = APIRouter(prefix="/admin/v1", tags=["admin"])

# Registry router
registry_router = APIRouter(prefix="/v1/registry", tags=["registry"])
```

### Include in Application

```python
app.include_router(proxy_router)
app.include_router(admin_router)
app.include_router(registry_router)
```

**Benefits:**
- Clear separation of concerns
- Prevents route conflicts
- Easier testing and maintenance
- Self-documenting API structure

## URL Structure Best Practices

### Resource Hierarchy
Make ownership explicit through URL hierarchy:

```
✅ /v1/{tenant}/workflows/{workflow_id}/runs/{run_id}
✅ /v1/{tenant}/alerts/{alert_id}/analysis

❌ /v1/{tenant}/runs/{run_id}  # Missing parent context
```

### Actions as Sub-Resources
Keep operations contextual with action sub-resources:

```
✅ POST /v1/{tenant}/mcps/{id}/invoke
✅ POST /admin/v1/{tenant}/mcps/{id}/enable

❌ POST /v1/{tenant}/invoke-mcp?id={id}
❌ POST /v1/{tenant}/mcps?action=invoke&id={id}
```

### Avoid Implementation Details
Don't expose internal implementation in URLs:

```
✅ /v1/{tenant}/users
✅ /v1/{tenant}/search

❌ /v1/{tenant}/postgres/users
❌ /v1/{tenant}/elasticsearch/search
```

## Complete URL Examples

### Data-Plane Operations
```
# Resource CRUD
GET    /v1/{tenant}/users
GET    /v1/{tenant}/users/{id}
POST   /v1/{tenant}/users
PUT    /v1/{tenant}/users/{id}
DELETE /v1/{tenant}/users/{id}

# Action operations
POST   /v1/{tenant}/mcps/{id}/invoke
POST   /v1/{tenant}/workflows/{id}/run
GET    /v1/{tenant}/tasks/{id}/status
```

### Control-Plane Operations
```
# Configuration
POST   /admin/v1/{tenant}/mcps/{id}/enable
POST   /admin/v1/{tenant}/mcps/{id}/disable
GET    /admin/v1/{tenant}/entitlements

# Health and monitoring
GET    /admin/v1/{tenant}/health
GET    /admin/v1/_/metrics
```

### Global Operations
```
GET    /admin/v1/_/system/health
GET    /admin/v1/_/metrics/summary
POST   /admin/v1/_/system/maintenance
```
