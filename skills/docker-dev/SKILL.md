---
name: docker-dev
description: Use this skill when setting up Docker and Docker Compose for local development. Provides development-specific patterns for Dockerfiles and Docker Compose including live reload, volume mounting, and rapid iteration workflows.
version: 1.0.0
---

# Docker for Development

Development-focused Docker and Docker Compose practices prioritizing fast iteration and rapid development over production optimization.

## When to Use This Skill

Use this skill when:
- Creating Dockerfiles for local development
- Setting up Docker Compose for microservices development
- Configuring live reload and hot reloading in Docker
- Optimizing Docker builds for development speed
- Managing multi-service applications with Docker Compose
- Setting up development databases and external services

## Reference Routing Table

| Reference | Read when you need to… |
|-----------|------------------------|
| `dockerfile-dev.md` | Create development Dockerfiles — live reload setup, volume mounting, dependency caching, .dockerignore, dev vs production separation |
| `docker-compose-dev.md` | Set up multi-service development environments — service config, orchestration, volumes, env vars, networking, essential commands |
