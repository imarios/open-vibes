---
name: general-coding
description: Cross-language development principles for any codebase. Covers TDD workflows, clean code, test hygiene, code review, code quality, Makefile patterns, configuration strategy, and project setup. Use when writing tests, reviewing code, setting up dev workflows, or deciding how to configure application settings.
version: 1.0.0
---

# General Coding Standards

Provide guidance on universal software development principles that apply across all programming languages and frameworks.

## When to Use This Skill

Apply this skill when:
- Starting a new feature or bug fix
- Writing or reviewing tests
- Making code changes in any codebase
- Reviewing code quality and maintainability
- Setting up development workflows
- Deciding how to configure application settings (env vars, config files, code)

## Reference Routing Table

| Reference | Read when you need to… |
|-----------|------------------------|
| `development-principles.md` | Plan an approach to a task — code structure decisions, refactoring vs features, TDD workflows |
| `testing-standards.md` | Write or debug tests — test isolation, fixture patterns, flakiness, test suite organization |
| `code-quality.md` | Finalize code for production — documentation, security concerns, resource management, dependency handling |
| `makefile-patterns.md` | Create or modify Makefile targets — naming conventions, parameter passing, multi-language builds |

## Configuration Strategy

**Secrets + local overrides → `.env`**
- Never committed (`.gitignore`)
- Provide `.env.example` template (committed)
- Examples: `API_KEY`, `DB_PASSWORD`, local dev URLs

**Deployment-specific values → Environment variables**
- Set by deployment platform/infrastructure
- Examples: `DATABASE_URL`, `REDIS_URL`, `ENVIRONMENT=production`

**Application defaults/constants → Code**
- Version controlled business logic
- Examples: pagination limits, timeouts, feature defaults

**Complex structured config → YAML/TOML**
- Version controlled, can be overridden by env vars
- Examples: logging config, multi-level settings, lookup tables
