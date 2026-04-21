# open-vibes

[![checks](https://github.com/imarios/open-vibes/actions/workflows/checks.yml/badge.svg)](https://github.com/imarios/open-vibes/actions/workflows/checks.yml)
[![latest tag](https://img.shields.io/github/v/tag/imarios/open-vibes)](https://github.com/imarios/open-vibes/tags)
[![license](https://img.shields.io/github/license/imarios/open-vibes)](LICENSE)
[![last commit](https://img.shields.io/github/last-commit/imarios/open-vibes)](https://github.com/imarios/open-vibes/commits/main)
[![skills](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/imarios/open-vibes/main/.github/badges/skills.json)](#skills)

Open-source Claude Code skills for software development.

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| [cybersecurity-analyst](skills/cybersecurity-analyst/) | 0.2.0 | SOC analyst workflows: SIEM alert triage, malware/phishing/brute-force/web-attack investigation, log and network traffic analysis, threat intelligence enrichment. |
| [docker-dev](skills/docker-dev/) | 1.0.0 | Docker and Docker Compose for local development. Covers dev-focused Dockerfiles, live reload, volume mounting, dependency caching, and multi-service orchestration. |
| [fastapi-coding](skills/fastapi-coding/) | 1.0.0 | FastAPI development standards. Covers project structure, Pydantic routing/validation, async SQLAlchemy, dependency injection, security, and pytest patterns. |
| [frontend-coding](skills/frontend-coding/) | 1.1.0 | React, Tailwind CSS, and React Testing Library patterns. Covers component design, responsive layout, error handling, and file naming conventions. |
| [general-coding](skills/general-coding/) | 1.0.0 | Cross-language development principles. Covers TDD workflows, clean code, test hygiene, code review, Makefile patterns, and configuration strategy. |
| [kubernetes](skills/kubernetes/) | 1.0.0 | Kubernetes workflows: manifests, Helm, kubectl, k9s, Kustomize, local dev, EKS operations, observability (OTEL/Grafana LGTM), security, and networking. |
| [ocsf-detection-finding](skills/ocsf-detection-finding/) | 0.1.0 | Parse, validate, and map OCSF Detection Finding events (Class 2004 v1.8.0). Covers attributes, finding_info, MITRE ATT&CK mappings, observables/evidence, and profiles. |
| [python-coding](skills/python-coding/) | 1.0.0 | Python development standards. Covers Poetry dependency management, PEP 8 style, pytest testing patterns, type hints with mypy, and asyncio. |
| [terraform-security-review](skills/terraform-security-review/) | 0.1.0 | Terraform/OpenTofu security review across the lifecycle: Trivy/Checkov/KICS static analysis, OPA/Sentinel policy-as-code, secrets/drift detection, OIDC hardening, CI/CD gates. |
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
