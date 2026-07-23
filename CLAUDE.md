# AI Dev Tools Zoomcamp — Learning Workspace

## Purpose

Coursework for [DataTalksClub AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp) (2026 cohort, starts August 31, 2026). Free course on AI-native software engineering: spec-driven development with coding agents, full-stack build/deploy, MCP/skills/plugins, and AI security/audit/DevOps tooling.

Core course workflow: give AI tools the right context, use them for the right job, review what they produce, test the result, ship with guardrails.

## Structure

Folders mirror the course repo modules:

| Folder | Module |
| --- | --- |
| `01-overview/` | AI-Native Developer Workflow — spec, backlog, AGENTS.md, agent roles |
| `01-todo/` | Module 1 homework: Django TODO app (root-level folder per homework instructions — submission form takes a link to this folder) |
| `02-end-to-end/` | Full-stack app: spec, frontend, OpenAPI, FastAPI/Django backend, DB, tests, Docker, deploy, CI/CD |
| `03-mcp/` | MCP, skills, plugins, hooks, subagents, custom agent extensions |
| `04-ai-security-audit-devops/` | PR review, security scanning, audit, diagnostics tooling |
| `project/` | Final project — end-to-end app, peer-reviewed for certificate |

## Conventions

- One branch per module (e.g. `module/01-overview`), covering that module's learning notes AND homework. Merge to main when the module wraps.
- Incremental commits within the branch — one logical change each (lesson notes, homework step, etc.), conventional-commit format.
- Homework and notes live inside the matching module folder.
- Each module gets its own README as work accumulates.
- Global rules apply: conventional commits, GPG-signed, feature branches for work, no AI attribution in commits, TDD for new Python/TS/Go code, full docstrings on public functions.
- Deployment constraint (org policy): no hosting on personal cloud accounts, random VPS, or free platforms (Vercel/Heroku/Netlify). Choose deployment targets for Module 2 and the final project accordingly — discuss options before deploying.

## Key Links

- Course platform: https://courses.datatalks.club/ai-dev-tools-2026/
- Materials: https://github.com/DataTalksClub/ai-dev-tools-zoomcamp
- Videos: https://www.youtube.com/playlist?list=PL3MmuxUbc_hLuyafXPyhTdbF4s_uNhc43
- FAQ: https://datatalks.club/faq/ai-dev-tools-zoomcamp.html
- Slack channel: #course-ai-dev-tools-zoomcamp on DataTalks.Club Slack
