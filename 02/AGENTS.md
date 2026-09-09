# Kanvas — AI Agent Context

## Project

Multi-user Kanban board (Kanvas). Full-stack: frontend SPA, FastAPI backend, SQLite via SQLAlchemy. Built following the AI Dev Tools Zoomcamp Module 2 workflow: spec → frontend prototype → OpenAPI contract → backend (mock DB first, then SQLite) → tests.

## Files

- `_docs/specs.md` — product spec (single source of truth for behavior)
- `frontend/` — SPA frontend (backend calls centralized in one module)
- `backend/` — FastAPI backend with database-agnostic persistence layer
- `openapi.yaml` — API contract between frontend and backend
- `tests/` — test suite (endpoint tests before implementation)

## Conventions

- Answer homework questions in `README.md` (Homework Answers section).
- Commit early, commit often — one logical change per commit, conventional-commit format.
- Do not modify `_docs/specs.md` without user approval.
