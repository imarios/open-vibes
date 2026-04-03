# open-vibes

Open-source Claude Code skills for software development.

## Structure

```
skills/
  <skill-name>/
    SKILL.md              # Skill definition (frontmatter + routing table)
    references/           # Reference documents loaded on demand
      *.md
```

## Conventions

- Each skill has a `SKILL.md` with YAML frontmatter (`name`, `description`, `version`)
- Reference documents are routed via the routing table in `SKILL.md`
- All content must be generic and language/framework-agnostic where possible
- No internal project references, API keys, or proprietary information
