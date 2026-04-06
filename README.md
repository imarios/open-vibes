# open-vibes

Open-source Claude Code skills for software development.

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| [frontend-coding](skills/frontend-coding/) | 1.1.0 | React, Tailwind CSS, and React Testing Library patterns. Covers component design, responsive layout, error handling, and file naming conventions. |
| [general-coding](skills/general-coding/) | 1.0.0 | Cross-language development principles. Covers TDD workflows, clean code, test hygiene, code review, Makefile patterns, and configuration strategy. |
| [typescript-coding](skills/typescript-coding/) | 1.0.0 | TypeScript and Node.js development standards. Covers pnpm, ESM modules, strict tsconfig, Vitest testing, Zod validation, CLI tools, and async patterns. |

## Installation

Copy a skill directory into your project's `.claude/skills/` directory, or use [skilltree](https://github.com/imarios/skilltree) to install them.

```bash
# Register as a registry, then add by name
skilltree registry add github.com/imarios/open-vibes --name open-vibes
skilltree add general-coding

# Or add directly without registering
skilltree add general-coding --repo github.com/imarios/open-vibes --path skills/general-coding

# Manual installation
cp -r skills/general-coding /path/to/your-project/.claude/skills/
```

## Structure

Each skill follows the same layout:

```
skills/<name>/
  SKILL.md              # Skill definition with metadata and routing table
  references/           # Detailed reference documents loaded on demand
    *.md
```

## License

MIT
