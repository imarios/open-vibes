# open-vibes

Open-source Claude Code skills for software development.

## Skills

### general-coding

Cross-language development principles for any codebase. Covers TDD workflows, clean code, test hygiene, code review, code quality, Makefile patterns, configuration strategy, and project setup.

### typescript-coding

TypeScript and Node.js development standards. Covers project setup with pnpm, ESM modules, strict tsconfig, Vitest testing, Zod validation, CLI tools with npx, async patterns, and error handling.

## Installation

Copy a skill directory into your project's `.claude/skills/` directory, or use [skillkit](https://github.com/anthropics/skillkit) / [aipm](https://github.com/anthropics/aipm) to install them.

```bash
# Manual installation example
cp -r skills/general-coding /path/to/your-project/.claude/skills/
cp -r skills/typescript-coding /path/to/your-project/.claude/skills/
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
