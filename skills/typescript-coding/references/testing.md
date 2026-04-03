# Testing with Vitest

## Setup

```bash
pnpm add -D vitest @vitest/coverage-v8
```

### vitest.config.ts

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["tests/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      include: ["src/**/*.ts"],
      exclude: ["src/index.ts", "src/**/*.d.ts"],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
});
```

Key points:
- `globals: true` — `describe`, `it`, `expect` available without import (add `/// <reference types="vitest/globals" />` to a `.d.ts` file or use `types: ["vitest/globals"]` in tsconfig).
- `environment: "node"` for backend. Use `"jsdom"` or `"happy-dom"` for frontend components.
- Coverage thresholds enforce minimum coverage in CI.

### tsconfig for tests

If tests need different settings, use a `tsconfig.test.json`:

```json
{
  "extends": "./tsconfig.json",
  "include": ["src", "tests"],
  "compilerOptions": {
    "noUnusedLocals": false,
    "noUnusedParameters": false
  }
}
```

## Test Patterns

### Arrange-Act-Assert

```typescript
describe("UserService", () => {
  it("creates a user with valid input", async () => {
    // Arrange
    const input = { email: "test@example.com", name: "Test User" };
    const repo = createMockRepo();

    // Act
    const user = await createUser(repo, input);

    // Assert
    expect(user.email).toBe("test@example.com");
    expect(user.id).toBeDefined();
  });
});
```

### Test naming convention

Use descriptive names that read as sentences:
```typescript
describe("calculateDiscount", () => {
  it("returns 0 for orders under $50", () => { /* ... */ });
  it("applies 10% for orders between $50 and $100", () => { /* ... */ });
  it("throws for negative amounts", () => { /* ... */ });
});
```

## Mocking

### Mock modules

```typescript
import { vi } from "vitest";

// Mock an entire module
vi.mock("./database.js", () => ({
  query: vi.fn(),
  connect: vi.fn(),
}));

// Import after mock declaration
import { query } from "./database.js";

it("queries the database", async () => {
  vi.mocked(query).mockResolvedValue([{ id: 1 }]);

  const result = await getUsers();

  expect(query).toHaveBeenCalledWith("SELECT * FROM users");
  expect(result).toHaveLength(1);
});
```

### Mock dependencies via injection

Prefer dependency injection over module mocking when possible:

```typescript
// src/services/user.ts
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<User>;
}

export function createUserService(repo: UserRepository) {
  return {
    async getUser(id: string) {
      const user = await repo.findById(id);
      if (!user) throw new NotFoundError(`User ${id} not found`);
      return user;
    },
  };
}

// tests/services/user.test.ts
it("throws NotFoundError for missing user", async () => {
  const mockRepo: UserRepository = {
    findById: vi.fn().mockResolvedValue(null),
    save: vi.fn(),
  };
  const service = createUserService(mockRepo);

  await expect(service.getUser("abc")).rejects.toThrow(NotFoundError);
});
```

### Spy on methods

```typescript
const spy = vi.spyOn(console, "error").mockImplementation(() => {});

doSomethingThatLogs();

expect(spy).toHaveBeenCalledWith(expect.stringContaining("failed"));
spy.mockRestore();
```

## Async Testing

```typescript
// Resolved values
it("fetches data", async () => {
  const data = await fetchData();
  expect(data).toEqual({ id: 1 });
});

// Rejected promises
it("rejects with network error", async () => {
  await expect(fetchData()).rejects.toThrow("Network error");
});

// Timers
it("debounces calls", async () => {
  vi.useFakeTimers();

  const fn = vi.fn();
  const debounced = debounce(fn, 100);

  debounced();
  debounced();
  debounced();

  vi.advanceTimersByTime(100);
  expect(fn).toHaveBeenCalledTimes(1);

  vi.useRealTimers();
});
```

## Snapshot Testing

Use sparingly — only for stable output like serialized configs or error messages:

```typescript
it("generates expected config", () => {
  const config = generateConfig({ env: "production" });
  expect(config).toMatchSnapshot();
});

// Inline snapshots for small values
it("formats error message", () => {
  const msg = formatError(new NotFoundError("User 123"));
  expect(msg).toMatchInlineSnapshot(`"Error: User 123 not found"`);
});
```

## TDD Workflow

1. Write a failing test that describes the desired behavior
2. Run `pnpm test` — confirm it fails for the right reason
3. Write the minimal code to make it pass
4. Refactor while keeping tests green
5. Repeat

Use `vitest --watch` during development — it re-runs only affected tests using Vite's module graph (not git diff heuristics like Jest).

## Test Utilities

### Factory functions over fixtures

```typescript
// tests/factories/user.ts
function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    email: "test@example.com",
    name: "Test User",
    role: "user",
    createdAt: new Date(),
    ...overrides,
  };
}

// Usage
it("promotes user to admin", () => {
  const user = buildUser({ role: "user" });
  const promoted = promoteToAdmin(user);
  expect(promoted.role).toBe("admin");
});
```

### Custom matchers

```typescript
expect.extend({
  toBeValidEmail(received: string) {
    const pass = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(received);
    return {
      pass,
      message: () => `expected ${received} ${pass ? "not " : ""}to be a valid email`,
    };
  },
});

// Usage
expect(user.email).toBeValidEmail();
```
