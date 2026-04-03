# Project Setup and Configuration

## Starting a New Project

```bash
# Initialize with pnpm
pnpm init

# Enable corepack so Node manages pnpm version
corepack enable
corepack use pnpm@latest
```

This adds `"packageManager": "pnpm@x.y.z"` to package.json, pinning the version for the team.

## package.json Essentials

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": ">=20"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx watch src/index.ts",
    "test": "vitest",
    "test:ci": "vitest run --coverage",
    "lint": "eslint .",
    "format": "prettier --write ."
  }
}
```

Key points:
- `"type": "module"` — all `.js` files are ESM. Use `.cjs` only for legacy config files.
- `"engines"` — declare minimum Node version. Node 20+ has stable ESM support.
- `tsx` for development — runs TypeScript directly without a build step.

## tsconfig.json — Maximum Strict

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,

    "esModuleInterop": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### What the strict flags catch

| Flag | What it prevents |
|------|-----------------|
| `strict` | Umbrella: `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, etc. |
| `noUncheckedIndexedAccess` | `arr[0]` returns `T \| undefined` instead of `T` — prevents runtime undefined access |
| `exactOptionalPropertyTypes` | `{ x?: string }` means "missing or string", NOT "missing or string or undefined" |
| `verbatimModuleSyntax` | Forces `import type` for type-only imports — cleaner output, no runtime import side effects |

## Type-First Project Structure

```
my-project/
  src/
    controllers/      # Route handlers, request/response logic
    services/         # Business logic, orchestration
    models/           # Data models, Zod schemas, type definitions
    middleware/        # Express/Fastify middleware
    utils/            # Pure utility functions
    config/           # Environment loading, app configuration
    index.ts          # Entry point
  tests/
    controllers/      # Mirror src/ structure
    services/
    utils/
  vitest.config.ts
  tsconfig.json
  package.json
  .prettierrc
  eslint.config.js
```

Rules:
- Mirror `src/` structure in `tests/` — `src/services/user.ts` → `tests/services/user.test.ts`
- One export per file for services and controllers. Utils can have multiple related exports.
- `index.ts` barrel files only at directory level, never re-export the entire tree.

## ESLint Flat Config

ESLint 9+ uses flat config (`eslint.config.js`). No more `.eslintrc`.

```js
// eslint.config.js
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/consistent-type-imports": "error",
    },
  },
  { ignores: ["dist/", "node_modules/", "coverage/"] }
);
```

## Prettier

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

Single quotes for JS/TS strings (community convention). JSX attributes use double quotes automatically regardless of this setting. Trailing commas everywhere for cleaner diffs.

## Essential Dev Dependencies

```bash
pnpm add -D typescript tsx vitest @vitest/coverage-v8
pnpm add -D eslint @eslint/js typescript-eslint
pnpm add -D prettier
```

Runtime validation:
```bash
pnpm add zod
```

## Environment Variables with Zod

```typescript
// src/config/env.ts
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
});

export const env = envSchema.parse(process.env);
export type Env = z.infer<typeof envSchema>;
```

Call `envSchema.parse(process.env)` at startup — fail fast if config is invalid.
