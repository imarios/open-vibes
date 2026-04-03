# Type Patterns

## Zod at Trust Boundaries

### The Rule

TypeScript types exist only at compile time. Whenever data enters your application from an external source, validate it at runtime with Zod and derive the TypeScript type from the schema.

Trust boundaries where you must validate:
- API request bodies and query parameters
- Environment variables (see `setup-and-config.md`)
- Config files (JSON, YAML loaded from disk)
- External API responses
- Message queue payloads
- Database query results (if not using an ORM with built-in typing)

### Schema-First Pattern

```typescript
import { z } from "zod";

// 1. Define the schema (single source of truth)
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["admin", "user", "viewer"]),
  createdAt: z.coerce.date(),
});

// 2. Derive the type FROM the schema
type User = z.infer<typeof UserSchema>;

// 3. Validate at the boundary
function parseUser(raw: unknown): User {
  return UserSchema.parse(raw);
}

// 4. Safe parse when you need the error
function tryParseUser(raw: unknown) {
  const result = UserSchema.safeParse(raw);
  if (!result.success) {
    console.error("Validation failed:", result.error.flatten());
    return null;
  }
  return result.data;
}
```

### Composing Schemas

```typescript
// Base schema
const BaseEntitySchema = z.object({
  id: z.string().uuid(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

// Extend
const UserSchema = BaseEntitySchema.extend({
  email: z.string().email(),
  name: z.string(),
});

// Pick / Omit for request DTOs
const CreateUserSchema = UserSchema.omit({ id: true, createdAt: true, updatedAt: true });
const UpdateUserSchema = CreateUserSchema.partial(); // all fields optional

type CreateUserInput = z.infer<typeof CreateUserSchema>;
type UpdateUserInput = z.infer<typeof UpdateUserSchema>;
```

## Discriminated Unions

Use a literal `type` or `kind` field to let TypeScript narrow automatically.

```typescript
type ApiResponse =
  | { status: "success"; data: User }
  | { status: "error"; error: string; code: number }
  | { status: "loading" };

function handle(response: ApiResponse) {
  switch (response.status) {
    case "success":
      console.log(response.data); // TypeScript knows `data` exists
      break;
    case "error":
      console.error(response.error, response.code); // knows `error` and `code` exist
      break;
    case "loading":
      break;
    default:
      // Exhaustiveness check — compiler error if a case is missed
      const _exhaustive: never = response;
  }
}
```

The `never` trick at the end ensures you handle every variant. If you add a new status, TypeScript flags every switch that doesn't handle it.

## Branded Types

Prevent mixing up values that share the same base type (string, number) but have different semantics.

```typescript
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };

function createUserId(id: string): UserId {
  return id as UserId;
}

function getUser(id: UserId): User { /* ... */ }
function getOrder(id: OrderId): Order { /* ... */ }

const userId = createUserId("abc-123");
const orderId = createOrderId("def-456");

getUser(userId);   // OK
getUser(orderId);  // Compile error — OrderId is not UserId
```

Use branded types for: IDs, currency amounts, validated strings (email, URL), and any value where mixing up "which string" causes bugs.

## Utility Type Patterns

### `satisfies` — validate without widening

```typescript
const routes = {
  home: "/",
  about: "/about",
  user: "/user/:id",
} satisfies Record<string, string>;

// TypeScript knows routes.home is literally "/" (not just string)
// But also verified the shape matches Record<string, string>
```

### `as const` — literal types from objects

```typescript
const HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"] as const;
type HttpMethod = (typeof HTTP_METHODS)[number]; // "GET" | "POST" | "PUT" | "DELETE"
```

### Mapped types for API responses

```typescript
type ApiEndpoints = {
  "/users": { GET: User[]; POST: User };
  "/users/:id": { GET: User; PUT: User; DELETE: void };
};

type GetResponse<Path extends keyof ApiEndpoints> =
  ApiEndpoints[Path] extends { GET: infer R } ? R : never;

// GetResponse<"/users"> is User[]
```

## Narrowing Best Practices

### Prefer `in` operator for object narrowing

```typescript
type Dog = { bark(): void };
type Cat = { meow(): void };

function speak(animal: Dog | Cat) {
  if ("bark" in animal) {
    animal.bark(); // narrowed to Dog
  } else {
    animal.meow(); // narrowed to Cat
  }
}
```

### User-defined type guards

```typescript
function isNonNull<T>(value: T | null | undefined): value is T {
  return value != null;
}

// Filter nulls with full type safety
const results: (User | null)[] = await Promise.all(queries);
const users: User[] = results.filter(isNonNull);
```

### `noUncheckedIndexedAccess` patterns

With this flag enabled, array and object index access returns `T | undefined`:

```typescript
const items = ["a", "b", "c"];
const first = items[0]; // string | undefined

// Handle it explicitly
if (first !== undefined) {
  console.log(first.toUpperCase()); // safe
}

// Or use non-null assertion ONLY when you've verified externally
const [head, ...rest] = items;
// head is string | undefined with noUncheckedIndexedAccess
// Use destructuring with default: const [head = "default"] = items;
```
