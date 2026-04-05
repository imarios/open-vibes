---
name: frontend-coding
description: Use this skill when building frontend applications with React, Tailwind CSS, and React Testing Library. Covers React component patterns, responsive design, error handling with ErrorBoundary and useErrorHandler, Tailwind breakpoints, and file naming conventions. Use with typescript-coding skill for TypeScript fundamentals.
version: 1.1.0
dependencies:
  - typescript-coding
---

# Frontend Development Guidelines

> **Depends on `typescript-coding`** for TypeScript fundamentals: pnpm, ESM, strict tsconfig, Prettier, ESLint, Vitest setup. This skill covers React-specific patterns only.

## Golden Rules

1. **Functional components only** — No class components. Use hooks for state, effects, and context. The only exception is ErrorBoundary (React requires a class for `componentDidCatch`).
2. **Early returns for state** — Check loading, error, and empty states at the top of the render. Don't nest the happy path inside conditionals.
3. **Co-locate related files** — Keep component, test, and styles together. Use the project structure in `project-setup.md` as the baseline.
4. **Tailwind over custom CSS** — Use utility classes. Extract repeated patterns into components, not CSS abstractions.
5. **Test behavior, not implementation** — Use React Testing Library. Query by role and text, not by test ID or component internals.

## Reference Routing Table

| Reference | Read when you need to… |
|-----------|------------------------|
| `project-setup.md` | Set up a React project — component patterns, file naming (.tsx/.ts, PascalCase), project structure, path aliases, Tailwind setup, React Testing Library patterns |
| `responsive-design.md` | Implement responsive layouts — Tailwind breakpoints, table and data display patterns, multi-screen testing |
| `error-handling.md` | Implement error handling — useErrorHandler hook, ErrorBoundary, runSafe pattern, logger utility, error classification |
