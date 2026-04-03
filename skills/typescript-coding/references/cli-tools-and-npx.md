# CLI Tools and npx

## How npx Resolves Local Tools

When you run `npx some-tool`, the resolution order is:

1. **Local `node_modules/.bin/`** — checks the current project first
2. **Global packages** — checks globally installed packages
3. **Remote registry** — downloads and runs if not found locally

For project tooling, you always want option 1. Install the tool as a dev dependency:

```bash
pnpm add -D some-tool
```

Then run it via:
```bash
npx some-tool          # resolves to node_modules/.bin/some-tool
pnpm exec some-tool    # pnpm equivalent (identical behavior)
pnpm some-tool         # shorthand — pnpm auto-checks .bin/
```

### npm scripts vs npx

Tools in `node_modules/.bin/` are automatically on `$PATH` inside npm scripts:

```json
{
  "scripts": {
    "lint": "eslint .",
    "format": "prettier --write ."
  }
}
```

No `npx` prefix needed inside scripts — `pnpm run lint` finds `eslint` in `.bin/` automatically.

Use `npx` for ad-hoc one-off commands outside of scripts:
```bash
npx eslint --fix src/
npx vitest run --reporter=verbose
```

## Building a CLI Tool with TypeScript

### Project structure

```
my-cli/
  src/
    cli.ts            # Entry point with argument parsing
    commands/         # Command implementations
    utils/
  dist/               # Compiled output
  package.json
  tsconfig.json
```

### package.json — the `bin` field

The `bin` field maps command names to executable files:

```json
{
  "name": "my-cli",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "my-cli": "./dist/cli.js"
  },
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/cli.ts"
  }
}
```

Key points:
- `bin` points to the **compiled** `.js` file in `dist/`, not the `.ts` source.
- `files` limits what gets published to npm — only ship the compiled output.
- Use `tsx src/cli.ts` for development to skip the build step.

### The shebang line

Every CLI entry point needs a shebang as the very first line:

```typescript
#!/usr/bin/env node

// src/cli.ts
import { parseArgs } from "node:util";

const { values, positionals } = parseArgs({
  options: {
    verbose: { type: "boolean", short: "v", default: false },
    output: { type: "string", short: "o" },
  },
  allowPositionals: true,
});

console.log("Args:", values, positionals);
```

The shebang (`#!/usr/bin/env node`) tells the OS to use Node.js as the interpreter when the file is executed directly.

### tsconfig for CLIs

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": false,
    "sourceMap": false
  },
  "include": ["src"]
}
```

No declarations or source maps needed for CLI tools — they're not consumed as a library.

### Making the compiled file executable

After building, the file needs execute permissions:

```bash
chmod +x dist/cli.js
```

Automate this in package.json:

```json
{
  "scripts": {
    "build": "tsc && chmod +x dist/cli.js"
  }
}
```

## Installing a CLI Locally

### As a project dependency

```bash
pnpm add -D my-cli
```

After installation, `my-cli` is available in `node_modules/.bin/`:

```bash
npx my-cli --help
pnpm exec my-cli --help
```

Or in scripts:

```json
{
  "scripts": {
    "generate": "my-cli generate --output src/generated"
  }
}
```

### Linking during development

While developing a CLI tool, use `pnpm link` to test it locally:

```bash
# In the CLI project directory
pnpm link --global

# In the consuming project
pnpm link --global my-cli

# Now `my-cli` resolves to your local development version
npx my-cli --help
```

To unlink:
```bash
pnpm unlink --global my-cli
```

## Argument Parsing

### Built-in: `node:util parseArgs`

For simple CLIs, Node's built-in `parseArgs` (Node 18.3+) is sufficient:

```typescript
import { parseArgs } from "node:util";

const { values, positionals } = parseArgs({
  options: {
    name: { type: "string", short: "n" },
    force: { type: "boolean", short: "f", default: false },
    count: { type: "string", short: "c", multiple: true },
  },
  allowPositionals: true,
  strict: true, // throws on unknown flags
});
```

### Commander for complex CLIs

For CLIs with subcommands, use `commander`:

```bash
pnpm add commander
```

```typescript
#!/usr/bin/env node
import { Command } from "commander";

const program = new Command()
  .name("my-cli")
  .version("1.0.0")
  .description("My awesome CLI tool");

program
  .command("generate <name>")
  .description("Generate a new component")
  .option("-t, --template <type>", "template to use", "default")
  .action((name, options) => {
    console.log(`Generating ${name} with template ${options.template}`);
  });

program.parse();
```

## Publishing a CLI to npm

```bash
# Build
pnpm build

# Test locally
node dist/cli.js --help

# Publish
npm publish
```

After publishing, users can run without installing:
```bash
npx my-cli --help
```

Or install globally:
```bash
pnpm add -g my-cli
my-cli --help
```
