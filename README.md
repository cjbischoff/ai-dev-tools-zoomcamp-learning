# AI Dev Tools Zoomcamp — Coursework

Personal workspace for the [DataTalksClub AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp), 2026 cohort (starts August 31, 2026).

## What the Course Covers

Disciplined AI-assisted software development: comparing AI dev tools, spec-driven agent workflows, building and shipping a full-stack app, extending agents with MCP/skills/plugins, and open-source AI tooling for security, audit, and DevOps. Certificate requires completing the final project plus peer reviews (homework is graded but the certificate hinges on the project).

## Artifact Inventory

| Path | Purpose | Status |
| --- | --- | --- |
| `CLAUDE.md` | Workspace context and conventions for AI agents | Done |
| `README.md` | This inventory | Done |
| `01-todo/` | Module 1 homework: Django TODO app and learning notes | Complete — 13 functional tests and CI |
| `02-end-to-end/` | Module 2: Build and Ship an AI-Assisted Full-Stack App | README stub |
| `03-mcp/` | Module 3: MCP, Skills, Plugins, and Custom Agents | README stub |
| `04-ai-security-audit-devops/` | Module 4: AI Tools for Security, Audit, and DevOps | README stub |
| `project/` | Final project (peer-reviewed, certificate requirement) | README stub |

## Module 1 Status

The Django TODO app supports creating, editing, resolving, and deleting TODOs with due dates. Its 13 functional tests cover successful workflows, validation failures, HTTP method restrictions, missing records, and the complete create-to-delete flow.

```shell
cd 01-todo
uv sync --locked
uv run python manage.py test
uv run python manage.py runserver
```

GitHub Actions runs the Django checks, migration drift check, and test suite automatically. Module 1 was merged through [pull request #1](https://github.com/cjbischoff/ai-dev-tools-zoomcamp-learning/pull/1).

## Decisions

- Module folders follow the upstream course structure; Module 1 uses the root-level `01-todo/` submission folder required by the homework.
- Each future module starts with a README stub; notes and code are added as the cohort progresses.
- Deployment for Module 2 / final project must not use personal cloud accounts or free hosting platforms (org policy) — deployment target to be decided when Module 2 starts.

## Next Steps

1. [Register for the cohort](https://courses.datatalks.club/register/ai-dev-tools/).
2. Join the course Slack channel (#course-ai-dev-tools-zoomcamp) and Telegram announcements.
3. Submit the root-level [`01-todo/`](https://github.com/cjbischoff/ai-dev-tools-zoomcamp-learning/tree/main/01-todo) folder for Homework 1.
4. Confirm Homework 1 against the final materials when the cohort opens August 31, 2026.
5. Begin Module 2 when its 2026 materials are published.
