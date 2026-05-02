# open-vibes

Open-source agent skills for software development, operations, and cybersecurity.

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

## Committing

Do not commit a new or modified skill without first verifying its contents. Manually scan `SKILL.md` and every reference file for leaked product names, internal hostnames, credentials, project codenames, ticket IDs, or training-platform identifiers. The automated pre-commit checks (`scripts/check-readme-skills.sh`, `scripts/check-no-date-metadata.sh`, `scripts/check-skills-badge.sh`) are necessary but not sufficient — content scrubbing is a separate manual pass.
