# Error Handling Patterns

## Centralized Error Handling System

Use the centralized error handling system for consistent error management across the application:

1. **useErrorHandler hook** - for async operations in components
2. **ErrorBoundary** - for catching render errors
3. **logger utility** - for structured logging

## useErrorHandler Hook

Use in components with async operations:

### Basic Usage

```typescript
import { useErrorHandler } from '@/hooks/useErrorHandler';

export function UserProfile({ userId }: { userId: string }) {
  const { error, handleError, createContext, runSafe } = useErrorHandler('UserProfile');
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    async function loadUser() {
      const [result, error] = await runSafe(
        fetchUser(userId),
        'loadUser',
        {
          action: 'loading user profile',
          entityId: userId,
        }
      );

      if (error) {
        // Error already logged and handled by runSafe
        return;
      }

      setUser(result);
    }

    loadUser();
  }, [userId]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (!user) {
    return <div>Loading...</div>;
  }

  return <div>{user.name}</div>;
}
```

### runSafe Return Pattern

`runSafe` returns a tuple: `[result | null, error | null]`

```typescript
// Success case
const [result, error] = await runSafe(fetchData(), 'fetchData', context);
if (error) {
  // Handle error
  return;
}
// Use result safely - TypeScript knows result is not null here

// Or destructure with different names
const [userData, userError] = await runSafe(fetchUser(id), 'fetchUser', { userId: id });
const [postsData, postsError] = await runSafe(fetchPosts(id), 'fetchPosts', { userId: id });
```

### Error Context Requirements

Provide rich context with every error for effective debugging:

```typescript
const context = {
  // Component/method name
  component: 'UserProfile',
  method: 'loadUser',

  // Action being performed
  action: 'loading user profile',

  // Entity IDs and types
  entityId: userId,
  entityType: 'user',

  // Relevant parameters
  params: { includeDetails: true }
};

const [result, error] = await runSafe(
  fetchUser(userId, { includeDetails: true }),
  'loadUser',
  context
);
```

**Required context fields:**
- `action` - What operation is being performed (user-friendly description)
- `entityId` - ID of the entity being operated on (when applicable)

**Optional but recommended:**
- `component` - Component name (auto-provided by useErrorHandler)
- `method` - Method or function name
- `entityType` - Type of entity (user, post, order, etc.)
- `params` - Relevant parameters passed to the operation

### Multiple Async Operations

```typescript
export function Dashboard() {
  const { runSafe } = useErrorHandler('Dashboard');
  const [users, setUsers] = useState<User[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    async function loadData() {
      // Load users
      const [usersData, usersError] = await runSafe(
        fetchUsers(),
        'loadUsers',
        { action: 'loading users list' }
      );

      if (!usersError && usersData) {
        setUsers(usersData);
      }

      // Load posts independently
      const [postsData, postsError] = await runSafe(
        fetchPosts(),
        'loadPosts',
        { action: 'loading posts list' }
      );

      if (!postsError && postsData) {
        setPosts(postsData);
      }
    }

    loadData();
  }, []);

  return (
    <div>
      <UserList users={users} />
      <PostList posts={posts} />
    </div>
  );
}
```

### Event Handler Errors

```typescript
export function CreateUserForm() {
  const { runSafe } = useErrorHandler('CreateUserForm');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const formData = new FormData(e.target as HTMLFormElement);
    const userData = {
      name: formData.get('name') as string,
      email: formData.get('email') as string,
    };

    const [result, error] = await runSafe(
      createUser(userData),
      'handleSubmit',
      {
        action: 'creating new user',
        params: userData,
      }
    );

    if (error) {
      // Error already handled - show user feedback
      return;
    }

    // Success - redirect or show confirmation
    window.location.href = `/users/${result.id}`;
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit">Create User</button>
    </form>
  );
}
```

## ErrorBoundary Component

Wrap key components to catch render errors:

### Basic Usage

```typescript
import { ErrorBoundary } from '@/components/ErrorBoundary';

export function App() {
  return (
    <ErrorBoundary component="App">
      <Dashboard />
    </ErrorBoundary>
  );
}
```

### Multiple Boundaries

Use multiple error boundaries for isolated error handling:

```typescript
export function Dashboard() {
  return (
    <div>
      <ErrorBoundary component="UserSection">
        <UserList />
      </ErrorBoundary>

      <ErrorBoundary component="PostSection">
        <PostList />
      </ErrorBoundary>

      <ErrorBoundary component="AnalyticsSection">
        <Analytics />
      </ErrorBoundary>
    </div>
  );
}
```

**Benefits:**
- One component's error doesn't crash the entire page
- Other sections remain functional
- Better user experience

### When to Use ErrorBoundary

**DO wrap:**
- ✅ Root application component
- ✅ Major sections/features
- ✅ Complex components with lots of logic
- ✅ Third-party component integrations
- ✅ Components that render user-generated content

**DON'T wrap:**
- ❌ Every single component (too granular)
- ❌ Simple presentational components
- ❌ Components already wrapped by a parent boundary

## Logger Utility

Use the logger utility for structured logging:

### Log Levels

```typescript
import { logger } from '@/utils/logger';

// Error - for failures and exceptions
logger.error('Failed to load user', error, {
  component: 'UserProfile',
  userId: '123',
  action: 'loading user data',
});

// Warn - for non-critical issues
logger.warn('API deprecated endpoint used', null, {
  endpoint: '/api/v1/users',
  alternative: '/api/v2/users',
});

// Info - for successful operations
logger.info('User created successfully', { userId: '123' }, {
  component: 'CreateUserForm',
  action: 'user creation',
});

// Debug - for detailed debugging information
logger.debug('Cache hit', { key: 'user:123', ttl: 3600 }, {
  component: 'CacheService',
});
```

### Logging with Context

Always provide context for debugging:

```typescript
// Good - rich context
logger.error('Failed to save order', error, {
  component: 'CheckoutForm',
  method: 'handleSubmit',
  action: 'saving customer order',
  entityId: orderId,
  entityType: 'order',
  userId: currentUser.id,
  totalAmount: order.total,
});

// Bad - minimal context
logger.error('Save failed', error);
```

### API Call Logging

Always log API calls with error handling:

```typescript
async function fetchUser(userId: string): Promise<User> {
  const context = {
    component: 'apiClient',
    method: 'fetchUser',
    action: 'fetching user data',
    entityId: userId,
    entityType: 'user',
  };

  try {
    const response = await fetch(`/api/users/${userId}`);

    if (!response.ok) {
      const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
      logger.error('API request failed', error, {
        ...context,
        status: response.status,
        statusText: response.statusText,
      });
      throw error;
    }

    const data = await response.json();
    logger.info('User fetched successfully', { userId }, context);
    return data;

  } catch (error) {
    logger.error('Network error during user fetch', error, context);
    throw error;
  }
}
```

## Error Classification

The error handling system generates appropriate user messages based on error classification:

### Network Errors
```typescript
// Automatic classification
if (error.message.includes('Network') || error.message.includes('fetch')) {
  // User sees: "Network error. Please check your connection."
}
```

### Validation Errors
```typescript
// 400 Bad Request
if (response.status === 400) {
  // User sees: Error message from API response
}
```

### Authorization Errors
```typescript
// 401/403 status codes
if (response.status === 401 || response.status === 403) {
  // User sees: "You don't have permission to perform this action."
}
```

### Server Errors
```typescript
// 500 status codes
if (response.status >= 500) {
  // User sees: "Server error. Please try again later."
}
```

## Complete Error Handling Example

```typescript
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { logger } from '@/utils/logger';

export function UserManagement() {
  return (
    <ErrorBoundary component="UserManagement">
      <UserList />
    </ErrorBoundary>
  );
}

function UserList() {
  const { error, runSafe } = useErrorHandler('UserList');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUsers() {
      setLoading(true);

      const [result, error] = await runSafe(
        fetchUsers(),
        'loadUsers',
        { action: 'loading users list' }
      );

      setLoading(false);

      if (error) {
        // Error already logged by runSafe
        return;
      }

      setUsers(result);
      logger.info('Users loaded', { count: result.length }, {
        component: 'UserList',
        action: 'loading users',
      });
    }

    loadUsers();
  }, []);

  async function handleDelete(userId: string) {
    const [result, error] = await runSafe(
      deleteUser(userId),
      'handleDelete',
      {
        action: 'deleting user',
        entityId: userId,
        entityType: 'user',
      }
    );

    if (error) {
      // Error shown to user automatically
      return;
    }

    // Update UI
    setUsers(users.filter(u => u.id !== userId));
    logger.info('User deleted', { userId }, {
      component: 'UserList',
      action: 'user deletion',
    });
  }

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {users.map(user => (
        <div key={user.id}>
          {user.name}
          <button onClick={() => handleDelete(user.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

## Error Handling Checklist

- ✅ Use `useErrorHandler` hook in components with async operations
- ✅ Wrap key components with `ErrorBoundary`
- ✅ Provide rich context with every error
- ✅ Include action, entityId, and other relevant details
- ✅ Use appropriate logger severity levels
- ✅ Handle API call errors consistently
- ✅ Show user-friendly error messages
- ✅ Log errors for debugging
- ✅ Don't expose sensitive data in error messages
- ✅ Test error scenarios to ensure proper handling
