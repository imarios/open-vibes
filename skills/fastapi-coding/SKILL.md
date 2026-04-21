---
name: fastapi-coding
description: Use this skill when building FastAPI applications. Provides FastAPI-specific best practices including project structure, routing with Pydantic models, async database patterns, dependency injection, security, and testing.
version: 1.0.0
---

# FastAPI Coding Standards

Comprehensive FastAPI development practices covering project structure, routing, async patterns, database access, security, and testing.

## When to Use This Skill

Use this skill when:
- Building a new FastAPI application
- Structuring FastAPI project folders and routers
- Working with Pydantic models for request/response validation
- Implementing async database operations with SQLAlchemy
- Setting up dependency injection and middleware
- Adding security and authentication to FastAPI endpoints
- Testing FastAPI applications with pytest

## Reference Routing Table

| Reference | Read when you need to… |
|-----------|------------------------|
| `project-structure.md` | Set up a new FastAPI project — folder organization (routers/, models/, schemas/, services/), app initialization, middleware, API versioning |
| `routing-and-models.md` | Create API endpoints — Pydantic models and validators, RORO pattern, OpenAPI documentation |
| `async-and-database.md` | Implement database operations — async patterns with SQLAlchemy 2.0+, dependency injection, background tasks, caching |
| `security-and-testing.md` | Add auth/authz, error handling, input validation — testing patterns with pytest, observability, logging |
