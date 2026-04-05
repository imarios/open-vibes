# Responsive Design Patterns

## Target Screen Sizes

Optimize UI for both laptop and desktop screens:

- **Laptop**: 1366x768 (common laptop resolution)
- **Desktop**: 1920x1080 (standard desktop resolution)

**Requirements:**
- All UI components and pages must adapt to different screen sizes
- Test changes on both laptop and desktop displays before completing work
- Avoid designs that force horizontal scrolling on standard screen sizes

## Tailwind Breakpoints

Use Tailwind's responsive breakpoints consistently:

| Breakpoint | Min Width | Usage                          |
| ---------- | --------- | ------------------------------ |
| `sm:`      | 640px     | Small tablets and up           |
| `md:`      | 768px     | **Laptop-optimized** (≥768px)  |
| `lg:`      | 1024px    | **Desktop-optimized** (≥1024px)|
| `xl:`      | 1280px    | Large desktop styles (≥1280px) |
| `2xl:`     | 1536px    | Extra large screens            |

**Focus on `md:` and `lg:` for laptop/desktop optimization.**

## Responsive Layout Patterns

### Basic Responsive Grid

```typescript
export function Dashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card>Widget 1</Card>
      <Card>Widget 2</Card>
      <Card>Widget 3</Card>
    </div>
  );
}
```

**Pattern:**
- Mobile: 1 column
- Laptop (`md:`): 2 columns
- Desktop (`lg:`): 3 columns

### Responsive Spacing

Adjust spacing based on screen size:

```typescript
<div className="p-4 md:p-6 lg:p-8">
  {/* Padding: 4 (mobile), 6 (laptop), 8 (desktop) */}
</div>

<div className="space-y-2 md:space-y-4 lg:space-y-6">
  {/* Vertical spacing increases with screen size */}
</div>
```

### Responsive Typography

Use responsive font sizes:

```typescript
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Responsive Heading
</h1>

<p className="text-sm md:text-base lg:text-lg">
  Body text that scales with screen size
</p>
```

## Responsive Table Patterns

Tables with many columns require special handling:

### 1. Wrap Text Instead of Truncate

```typescript
<table className="w-full table-fixed">
  <tbody>
    <tr>
      <td className="break-words p-2">
        Long text content that wraps instead of being truncated
      </td>
    </tr>
  </tbody>
</table>
```

**Use `break-words` to wrap long content in cells.**

### 2. Hide Columns on Smaller Screens

```typescript
<table className="w-full">
  <thead>
    <tr>
      <th>Name</th>
      <th>Email</th>
      <th className="hidden md:table-cell">Phone</th>
      <th className="hidden lg:table-cell">Address</th>
      <th className="hidden lg:table-cell">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>John Doe</td>
      <td>john@example.com</td>
      <td className="hidden md:table-cell">555-1234</td>
      <td className="hidden lg:table-cell">123 Main St</td>
      <td className="hidden lg:table-cell">Important customer</td>
    </tr>
  </tbody>
</table>
```

**Pattern:**
- Essential columns always visible
- Less important columns hidden on mobile (`hidden md:table-cell`)
- Optional columns only on desktop (`hidden lg:table-cell`)

### 3. Fixed Layout with Percentage Widths

```typescript
<table className="w-full table-fixed">
  <colgroup>
    <col className="w-[30%]" />
    <col className="w-[40%]" />
    <col className="w-[30%]" />
  </colgroup>
  <thead>
    <tr>
      <th>Name</th>
      <th>Description</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td className="break-words">John Doe</td>
      <td className="break-words">Senior Software Engineer with 10 years...</td>
      <td>
        <button>Edit</button>
      </td>
    </tr>
  </tbody>
</table>
```

**Benefits:**
- `table-fixed` maintains column proportions
- Percentage widths allocate space predictably
- `break-words` prevents overflow

### 4. Horizontal Scrolling (When Needed)

```typescript
<div className="overflow-x-auto">
  <table className="min-w-full">
    <thead>
      <tr>
        <th>Col 1</th>
        <th>Col 2</th>
        <th>Col 3</th>
        <th>Col 4</th>
        <th>Col 5</th>
        <th>Col 6</th>
        <th>Col 7</th>
        <th>Col 8</th>
      </tr>
    </thead>
    <tbody>
      {/* Table content */}
    </tbody>
  </table>
</div>
```

**Use `overflow-x-auto` when:**
- Table has many essential columns that can't be hidden
- All columns must be accessible on all screen sizes
- Data is primarily viewed on desktop

### 5. Complete Responsive Table Example

```typescript
export function DataTable({ data }: { data: User[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed">
        <colgroup>
          <col className="w-[25%]" />
          <col className="w-[35%]" />
          <col className="w-[20%] hidden md:table-column" />
          <col className="w-[20%] hidden lg:table-column" />
        </colgroup>
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Name</th>
            <th className="p-2 text-left">Email</th>
            <th className="p-2 text-left hidden md:table-cell">Phone</th>
            <th className="p-2 text-left hidden lg:table-cell">Status</th>
          </tr>
        </thead>
        <tbody>
          {data.map((user) => (
            <tr key={user.id} className="border-b">
              <td className="p-2 break-words">{user.name}</td>
              <td className="p-2 break-words">{user.email}</td>
              <td className="p-2 break-words hidden md:table-cell">{user.phone}</td>
              <td className="p-2 hidden lg:table-cell">{user.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## Visual Hierarchy

Implement clear visual hierarchy that works at different screen sizes:

```typescript
export function PageLayout() {
  return (
    <div className="container mx-auto px-4">
      {/* Header - larger on desktop */}
      <header className="py-4 md:py-6 lg:py-8">
        <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
          Page Title
        </h1>
      </header>

      {/* Main content - responsive grid */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
        {/* Primary content - full width on mobile, 2/3 on desktop */}
        <section className="lg:col-span-2">
          <Card>Main content</Card>
        </section>

        {/* Sidebar - stacks below on mobile, sidebar on desktop */}
        <aside className="lg:col-span-1">
          <Card>Sidebar</Card>
        </aside>
      </main>
    </div>
  );
}
```

## Responsive Component Examples

### Responsive Navigation

```typescript
export function Navigation() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4">
        {/* Mobile menu button */}
        <button
          className="md:hidden p-2"
          onClick={() => setIsOpen(!isOpen)}
        >
          Menu
        </button>

        {/* Navigation links - hidden on mobile, always visible on desktop */}
        <div className={`
          ${isOpen ? 'block' : 'hidden'}
          md:flex md:space-x-4
        `}>
          <a href="/">Home</a>
          <a href="/about">About</a>
          <a href="/contact">Contact</a>
        </div>
      </div>
    </nav>
  );
}
```

### Responsive Card Grid

```typescript
export function CardGrid({ items }: { items: Item[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {items.map((item) => (
        <div key={item.id} className="bg-white rounded shadow p-4">
          <h3 className="text-lg md:text-xl font-semibold">{item.title}</h3>
          <p className="text-sm md:text-base text-gray-600">{item.description}</p>
        </div>
      ))}
    </div>
  );
}
```

## Testing Requirements

Before completing work:

1. **Test on laptop resolution** (1366x768)
   - Verify layout works without horizontal scrolling
   - Check that important content is visible
   - Ensure interactive elements are accessible

2. **Test on desktop resolution** (1920x1080)
   - Verify content uses available space effectively
   - Check that layout doesn't look sparse or stretched
   - Ensure responsive breakpoints activate correctly

3. **Test responsive transitions**
   - Resize browser window to check breakpoint behavior
   - Verify smooth transitions between layouts
   - Check that no content is lost or hidden unexpectedly

## Responsive Design Checklist

- ✅ Use Tailwind breakpoints consistently (`md:`, `lg:`, `xl:`)
- ✅ Test on both laptop (1366x768) and desktop (1920x1080)
- ✅ Avoid forced horizontal scrolling on standard screens
- ✅ Use responsive font sizes and spacing
- ✅ Hide less important table columns on smaller screens
- ✅ Wrap text with `break-words` instead of truncating
- ✅ Use `table-fixed` with percentage widths for tables
- ✅ Implement clear visual hierarchy at all screen sizes
- ✅ Test responsive transitions by resizing browser
