---
name: typescript-coding
description: Use this skill when writing TypeScript or Node.js code. Covers project setup with pnpm, ESM modules, strict tsconfig, Vitest testing, Zod validation, CLI tools with npx, async patterns, and error handling. Use when starting a TypeScript project, writing tests, building CLI tools, or configuring TypeScript tooling.
version: 1.0.0
---

# TypeScript Coding Standards

## Golden Rules

1. **pnpm, not npm or yarn** — Use `pnpm add` for dependencies. pnpm's strict `node_modules` prevents phantom dependencies (using packages you didn't declare). Run `corepack enable` to let Node manage the pnpm version via `packageManager` in package.json.
2. **ESM-only** — All projects use `"type": "module"` in package.json and `"module": "NodeNext"` in tsconfig. No CommonJS, no dual publishing for applications. Use `.cjs` extension only for config files that require it (e.g., legacy ESLint configs).
3. **Maximum strict tsconfig** — `"strict": true` is the starting point, not the finish line. Always enable `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`. These catch undefined array access and `undefined` vs missing property bugs at compile time.
4. **Zod at trust boundaries** — TypeScript types vanish at runtime. Validate with Zod where data crosses a trust boundary: API inputs, env vars, config files, external API responses. Derive types from schemas (`z.infer<typeof schema>`), never the reverse.
5. **Vitest, not Jest** — Native TypeScript and ESM support, no transforms needed, Jest-compatible API. Configure in `vitest.config.ts`, not in package.json.
6. **Type-first project structure** — Organize `src/` by code type: `controllers/`, `services/`, `models/`, `middleware/`, `utils/`, `config/`. Group by responsibility, not by feature.

## Reference Routing Table

| Reference | Read when you need to… |
|-----------|------------------------|
| `setup-and-config.md` | Start a new project — pnpm init, ESM setup, tsconfig strict settings, type-first directory layout, Prettier, ESLint flat config |
| `type-patterns.md` | Write type-safe code — Zod schemas, discriminated unions, branded types, utility types, narrowing patterns |
| `testing.md` | Write or configure tests — Vitest setup, test patterns, mocking, coverage, TDD workflow |
| `cli-tools-and-npx.md` | Build a CLI tool — package.json `bin` field, shebang setup, npx local execution, TypeScript compilation for CLIs |
| `async-and-error-handling.md` | Handle async operations or errors — async/await patterns, error boundaries, structured error types, graceful shutdown |
