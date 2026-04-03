# Makefile Patterns

A well-structured Makefile serves as the project's command center - a single entry point for all build, test, and operational tasks regardless of underlying technologies.

## Makefile Discipline

The project Makefile is the single source of truth for running operations.

1. **Always use existing targets** — If a Makefile target exists for an operation (build, test, run, migrate, etc.), use it. Never run the underlying commands directly. The target may include setup, environment variables, or flags you're not aware of.

2. **Create targets for reusable operations** — When implementing features that involve complex operations that will be repeated (rebuilding containers, running test suites, database migrations, deployments), add a Makefile target. Don't leave these as manual command sequences.

3. **Test new targets** — When you add or modify a Makefile target, test it immediately to verify it works. A broken target is worse than no target.

4. **Extract complex logic** — If target implementation exceeds a one-liner, move it to `scripts/make/`.

## Why Use a Makefile

- **Unified interface**: One command syntax for Rust, Python, Docker, scripts
- **Self-documenting**: `make help` shows all available operations
- **Discoverable**: New team members can explore capabilities immediately
- **Consistent**: Same commands work across all developer machines
- **Composable**: Complex workflows built from simple targets

## Structure Template

```makefile
# Project Makefile
# Brief description of what this project does

.PHONY: help all build test install clean
.DEFAULT_GOAL := help

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
PORT ?= 8080
ENV ?= dev

# ─────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────
help:
	@echo "Project Name"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Development:"
	@echo "  build       Build the project"
	@echo "  test        Run all tests"
	@echo "  run         Run locally (make run ARGS='--verbose')"
	@echo ""
	@echo "Deployment:"
	@echo "  install     Install locally"
	@echo "  clean       Remove build artifacts"

# ─────────────────────────────────────────────────────────────
# Development
# ─────────────────────────────────────────────────────────────
build:
	# build commands here

test:
	# test commands here

# ─────────────────────────────────────────────────────────────
# Combined Targets
# ─────────────────────────────────────────────────────────────
all: build test
```

## Key Patterns

### 1. Self-Documenting Help

Make `help` the default target so running `make` alone shows documentation:

```makefile
.DEFAULT_GOAL := help

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build    Build the application"
	@echo "  test     Run tests"
```

### 2. Domain-Prefixed Naming

Group related targets with consistent prefixes:

```makefile
# Good - clear domains
cli-build:
cli-test:
cli-run:

api-build:
api-test:
api-run:

db-migrate:
db-reset:
db-seed:

# Avoid - unclear grouping
build-cli:
run_api:
resetdb:
```

### 3. Configurable Defaults

Use `?=` for variables users might want to override:

```makefile
PORT ?= 8080
ENV ?= dev
DB ?= dev

# User can override: make api-run PORT=9000
api-run:
	uvicorn main:app --port $(PORT)
```

### 4. Parameter Passing

For targets that need arguments, use named variables:

```makefile
# Pass arbitrary arguments
cli-run:
	cargo run -- $(ARGS)
# Usage: make cli-run ARGS="--verbose --config=prod"

# Named parameters for specific operations
db-show-table:
	@test -n "$(TABLE)" || (echo "Usage: make db-show-table TABLE=users" && exit 1)
	sqlite3 app.db "SELECT * FROM $(TABLE);"
# Usage: make db-show-table TABLE=users

# Version setting
version-set:
	@test -n "$(V)" || (echo "Usage: make version-set V=1.2.3" && exit 1)
	echo "$(V)" > VERSION
# Usage: make version-set V=1.2.3
```

### 5. Conditional Logic

Select values based on environment or flags:

```makefile
ENV ?= dev
DB_FILE = $(if $(filter prod,$(ENV)),data/prod.db,data/dev.db)
API_URL = $(if $(filter prod,$(ENV)),https://api.example.com,http://localhost:8080)

run:
	@echo "Using database: $(DB_FILE)"
	./app --db $(DB_FILE)
```

### 6. Composite Targets

Build high-level workflows from primitives:

```makefile
# Primitives
api-stop:
	docker stop myapp || true

api-start:
	docker run -d --name myapp myapp:latest

# Composite
api-restart: api-stop api-start

# Full workflow
deploy: test build api-restart
	@echo "Deployed successfully"
```

### 7. Safety for Destructive Operations

Add confirmation prompts for dangerous commands:

```makefile
db-reset:
	@echo "WARNING: This will DELETE all data in $(DB_FILE)"
	@read -p "Type 'yes' to confirm: " confirm && [ "$$confirm" = "yes" ] || (echo "Aborted" && exit 1)
	rm -f $(DB_FILE)
	@echo "Database reset complete"
```

### 8. Feedback and Status

Provide clear output about what's happening:

```makefile
api-status:
	@if lsof -i :$(PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
		echo "API running on port $(PORT)"; \
		curl -s http://localhost:$(PORT)/health; \
	else \
		echo "API not running"; \
	fi

build:
	@echo "Building project..."
	cargo build --release
	@echo "Build complete: target/release/myapp"
```

## Multi-Language Projects

A single Makefile can orchestrate different tech stacks:

```makefile
# ─────────────────────────────────────────────────────────────
# CLI (Rust)
# ─────────────────────────────────────────────────────────────
cli-build:
	cd cli && cargo build

cli-test:
	cd cli && cargo test

# ─────────────────────────────────────────────────────────────
# API (Python)
# ─────────────────────────────────────────────────────────────
api-deps:
	cd api && poetry install

api-test:
	cd api && poetry run pytest

# ─────────────────────────────────────────────────────────────
# Frontend (Node)
# ─────────────────────────────────────────────────────────────
ui-deps:
	cd ui && npm install

ui-build:
	cd ui && npm run build

# ─────────────────────────────────────────────────────────────
# Combined
# ─────────────────────────────────────────────────────────────
deps: api-deps ui-deps

build: cli-build ui-build

test: cli-test api-test
```

## Common Target Categories

| Category | Targets | Purpose |
|----------|---------|---------|
| Build | `build`, `compile`, `generate` | Create artifacts |
| Test | `test`, `lint`, `check` | Verify correctness |
| Run | `run`, `run-dev`, `run-prod` | Execute locally |
| Deploy | `install`, `deploy`, `release` | Ship to environments |
| Data | `db-migrate`, `db-seed`, `db-reset` | Manage databases |
| Docker | `docker-build`, `docker-run`, `docker-stop` | Container operations |
| Utility | `clean`, `version`, `help` | Maintenance |

## Extracting Complex Logic to Scripts

When target logic exceeds a simple one-liner, extract it to a script under `scripts/make/`:

```
scripts/
  make/
    api-status.sh
    db-reset.sh
    version-sync.sh
  ci/
    deploy.sh
```

**Before** (hard to read, hard to maintain):
```makefile
api-status:
	@DEV_RUNNING=0; PROD_RUNNING=0; \
	if lsof -i :$(DEV_PORT) -sTCP:LISTEN >/dev/null 2>&1; then \
		DEV_RUNNING=1; \
		PID=$$(lsof -t -i :$(DEV_PORT) -sTCP:LISTEN); \
		echo "Dev API running on port $(DEV_PORT) (PID $$PID)"; \
		curl -s http://localhost:$(DEV_PORT)/health; echo ""; \
	fi; \
	if [ "$$DEV_RUNNING" = "0" ]; then \
		echo "API not running"; \
	fi
```

**After** (clean interface, testable script):
```makefile
api-status:
	./scripts/make/api-status.sh $(DEV_PORT) $(PROD_PORT)
```

Benefits:
- Scripts can be tested independently
- Proper shell features (functions, error handling, heredocs)
- Easier to debug and maintain
- Makefile stays readable as a command index

The script receives Make variables as positional arguments or environment variables:
```bash
#!/usr/bin/env bash
# scripts/make/api-status.sh
set -euo pipefail

DEV_PORT="${1:-8080}"
PROD_PORT="${2:-80}"

if lsof -i :"$DEV_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Dev API running on port $DEV_PORT"
else
    echo "API not running"
fi
```

## Usage Tracking

Track target invocations for analytics and to identify unused targets that can be removed:

```makefile
.PHONY: _track
_track:
	@echo "$$(date -Iseconds) $(MAKECMDGOALS)" >> .make-usage.log

build: _track
	# build commands

test: _track
	# test commands

deploy: _track
	# deploy commands
```

This logs each invocation with timestamp to `.make-usage.log`:
```
2024-03-15T10:23:45-07:00 build
2024-03-15T10:24:12-07:00 test
2024-03-15T11:05:33-07:00 build
```

Benefits:
- **Analytics** — See which targets are used most frequently
- **Aging** — Identify targets that haven't been used in months (candidates for removal)
- **Debugging** — Trace when operations were run

Add `.make-usage.log` to `.gitignore` — usage patterns are machine-specific.

## Tips

1. **Always declare `.PHONY`** - Makefile targets typically don't produce files with matching names
2. **Use `@` to suppress command echo** - Cleaner output, but show commands during debugging
3. **Quote variables with spaces** - `"$(VAR)"` prevents word splitting
4. **Use `$$` for shell variables** - Single `$` is Make syntax, `$$` passes to shell
5. **Chain with `&&`** - Ensures subsequent commands only run if previous succeeded
6. **Keep targets focused** - One clear purpose per target, compose for workflows
7. **Extract complex logic** - If it's more than a one-liner, move to `scripts/make/`
