# Async Patterns and Error Handling

## Async/Await Fundamentals

### Always await or return — never fire and forget

```typescript
// WRONG — unhandled rejection if sendEmail throws
async function createUser(input: CreateUserInput) {
  const user = await db.users.create(input);
  sendWelcomeEmail(user.email); // missing await!
  return user;
}

// CORRECT
async function createUser(input: CreateUserInput) {
  const user = await db.users.create(input);
  await sendWelcomeEmail(user.email);
  return user;
}
```

If you intentionally don't want to wait, use `void` operator and handle the error:

```typescript
void sendWelcomeEmail(user.email).catch((err) => {
  logger.error("Failed to send welcome email", { userId: user.id, err });
});
```

### Parallel execution with `Promise.all` and `Promise.allSettled`

```typescript
// All must succeed — fails fast on first rejection
const [users, orders] = await Promise.all([
  fetchUsers(),
  fetchOrders(),
]);

// Partial failures OK — get results for each
const results = await Promise.allSettled([
  fetchUsers(),
  fetchOrders(),
  fetchInventory(),
]);

for (const result of results) {
  if (result.status === "fulfilled") {
    process(result.value);
  } else {
    logger.error("Fetch failed", { reason: result.reason });
  }
}
```

### Concurrency control

When processing many items, limit concurrency to avoid overwhelming resources:

```typescript
async function processInBatches<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  concurrency: number,
): Promise<R[]> {
  const results: R[] = [];
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(fn));
    results.push(...batchResults);
  }
  return results;
}

// Process 100 items, 10 at a time
await processInBatches(items, processItem, 10);
```

## Error Handling Patterns

### Structured error classes

Define error classes with machine-readable codes, not just messages:

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly context?: Record<string, unknown>,
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} ${id} not found`, "NOT_FOUND", 404, { resource, id });
  }
}

class ValidationError extends AppError {
  constructor(message: string, public readonly fields: Record<string, string[]>) {
    super(message, "VALIDATION_ERROR", 400, { fields });
  }
}

class ConflictError extends AppError {
  constructor(message: string) {
    super(message, "CONFLICT", 409);
  }
}
```

### Catching errors — narrow the type

TypeScript catch blocks receive `unknown`, not `Error`:

```typescript
try {
  await riskyOperation();
} catch (err) {
  // WRONG — err is `unknown`, not `Error`
  // console.error(err.message);

  // CORRECT — narrow first
  if (err instanceof AppError) {
    logger.error(err.message, { code: err.code, context: err.context });
  } else if (err instanceof Error) {
    logger.error("Unexpected error", { message: err.message, stack: err.stack });
  } else {
    logger.error("Unknown error", { err });
  }
}
```

### Error boundaries — handle at the right layer

```
Controller  →  catches AppError, returns HTTP response
Service     →  throws AppError with business context
Repository  →  catches DB errors, wraps in AppError
```

Each layer catches errors it knows how to handle and lets others bubble up:

```typescript
// Repository — wraps database errors
async function findUserById(id: string): Promise<User> {
  try {
    const row = await db.query("SELECT * FROM users WHERE id = $1", [id]);
    if (!row) throw new NotFoundError("User", id);
    return row;
  } catch (err) {
    if (err instanceof AppError) throw err; // re-throw known errors
    throw new AppError("Database query failed", "DB_ERROR", 500, { originalError: String(err) });
  }
}

// Controller — converts to HTTP response
async function getUserHandler(req: Request, res: Response) {
  try {
    const user = await userService.getUser(req.params.id);
    res.json(user);
  } catch (err) {
    if (err instanceof AppError) {
      res.status(err.statusCode).json({ error: err.code, message: err.message });
    } else {
      res.status(500).json({ error: "INTERNAL_ERROR", message: "Something went wrong" });
    }
  }
}
```

## Graceful Shutdown

Handle `SIGTERM` and `SIGINT` to clean up resources:

```typescript
async function startServer() {
  const server = app.listen(env.PORT);
  const connections = new Set<Socket>();

  server.on("connection", (conn) => {
    connections.add(conn);
    conn.on("close", () => connections.delete(conn));
  });

  async function shutdown(signal: string) {
    logger.info(`Received ${signal}, shutting down gracefully...`);

    // Stop accepting new connections
    server.close();

    // Close existing connections
    for (const conn of connections) {
      conn.end();
    }

    // Close database pool, message queues, etc.
    await db.end();

    logger.info("Shutdown complete");
    process.exit(0);
  }

  process.on("SIGTERM", () => shutdown("SIGTERM"));
  process.on("SIGINT", () => shutdown("SIGINT"));

  // Catch unhandled rejections — log and exit
  process.on("unhandledRejection", (reason) => {
    logger.error("Unhandled rejection", { reason });
    process.exit(1);
  });

  logger.info(`Server listening on port ${env.PORT}`);
}
```

## Retry with Backoff

For transient failures (network timeouts, rate limits):

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  options: { maxRetries?: number; baseDelayMs?: number } = {},
): Promise<T> {
  const { maxRetries = 3, baseDelayMs = 1000 } = options;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxRetries) throw err;

      const delay = baseDelayMs * Math.pow(2, attempt) + Math.random() * 100;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw new Error("Unreachable");
}

// Usage
const data = await withRetry(() => fetchFromApi("/users"), { maxRetries: 3 });
```

## Timeouts

Wrap long-running operations with `AbortController`:

```typescript
async function fetchWithTimeout(url: string, timeoutMs: number = 5000): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}
```
