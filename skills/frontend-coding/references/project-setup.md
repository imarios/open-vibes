# Frontend Project Setup

> **TypeScript fundamentals** (pnpm, ESM, tsconfig, Prettier, ESLint, Vitest) are covered by the `typescript-coding` skill. This reference covers React-specific patterns only.

## React Component Patterns

**Functional components with hooks:**
```typescript
import { useState, useEffect } from 'react';

interface Props {
  userId: string;
}

export function UserProfile({ userId }: Props) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  if (!user) return <div>Loading...</div>;

  return <div>{user.name}</div>;
}
```

**Key patterns:**
- Functional components only (no class components)
- React hooks for state and side effects
- Props typed with TypeScript interfaces
- Early returns for loading/error states

## File Naming Conventions

**Components (PascalCase):**
```
UserProfile.tsx
DataTable.tsx
ErrorBoundary.tsx
```

**Utilities (camelCase):**
```
apiClient.ts
formatDate.ts
useErrorHandler.ts
```

**Rules:**
- `.tsx` for files with JSX
- `.ts` for utilities without JSX
- One component per file
- Co-locate related files

## Project Structure

```
src/
├── components/     # React components (PascalCase.tsx)
│   ├── common/     # Shared components (ErrorBoundary, etc.)
│   └── __tests__/  # Component tests
├── pages/          # Page/route components
├── hooks/          # Custom hooks (useSomething.ts)
├── services/       # API clients and data fetching
├── store/          # State management (Zustand, etc.)
├── utils/          # Utility functions (camelCase.ts)
├── types/          # Shared TypeScript type definitions
├── styles/         # Global styles
└── __tests__/      # Integration tests
```

## Path Aliases

Configure path aliases for cleaner imports:

```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@mocks/*": ["./mocks/*"]
    }
  }
}
```

```typescript
// Good — path alias
import { UserProfile } from '@/components/UserProfile';
import { mockUser } from '@mocks/users';

// Avoid — relative paths for deep imports
import { UserProfile } from '../../../components/UserProfile';
```

## Styling with Tailwind CSS

```typescript
export function Button({ children, onClick }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
    >
      {children}
    </button>
  );
}
```

**Best practices:**
- Use Tailwind utilities over custom CSS
- Extract repeated patterns into components
- Use responsive modifiers (`md:`, `lg:`)
- Leverage Tailwind's design tokens

## Component Testing with React Testing Library

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('renders user name', () => {
    const user = { id: '1', name: 'John Doe', email: 'john@example.com' };
    render(<UserProfile user={user} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<UserProfile user={null} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
```

**Testing patterns:**
- React Testing Library for component testing
- Focus on user behavior, not implementation details
- Test accessibility and user interactions
- Use `screen.getByRole` over `getByTestId` when possible
