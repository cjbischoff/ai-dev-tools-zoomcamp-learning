# Module 01 — Household Chores App (Homework)

## Purpose

Homework for [module 01 — overview](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/tree/main/cohorts/2026/01-overview).

Turn one vague idea — "a tool for managing shared household chores" — into a written spec, a backlog, and a working Django application. Build it with a coding agent, then cover it with tests.

The point of the exercise is the workflow, not Django expertise: spec first, backlog second, code third, tests last.

## Homework flow

Do the steps in order. Each step has one output.

1. **Spec.** Brainstorm the scope with a chat assistant. Ask it one question at a time. Save the result to `_docs/plan.md`.
2. **Backlog.** Give the agent `_docs/plan.md`. Ask it to propose a small backlog of Django tasks. Save to `_docs/backlog.md`.
3. **Django setup.** Install Django. Create one project and one app. Register the app.
4. **Build.** Implement backlog tasks one at a time. Say "Implement task #1 from backlog.md", then task #2, and so on.
5. **Tests.** Ask the agent which scenarios to cover. Check they make sense. Let it write and run the tests.

## Tech stack

- Python with `uv` for environment and running commands.
- Django (latest stable).
- `python manage.py test` for tests (Django's built-in test runner). No pytest unless a later need forces it.

## Structure

The app lives under this `01/` folder. Keep the homework artifacts here:

| Path | Holds |
| --- | --- |
| `_docs/plan.md` | The spec — features and scope. |
| `_docs/backlog.md` | The task backlog derived from the spec. |
| `.gitignore` | Python and Django ignores. |
| `manage.py`, `<project>/`, `<app>/` | The Django project and app. |

## Homework answers (project facts)

These are the correct answers for the module 01 questions. They are also true project constraints — follow them when building.

- **Register the app in `settings.py`.** Add the app to `INSTALLED_APPS`. (`urls.py` wires routes, not app registration.)
- **Start the dev server with `uv run python manage.py runserver`.**
- **Run tests with `python manage.py test`.**

## Conventions

- One logical change per commit, conventional-commit format, GPG-signed, no AI attribution.
- Full docstrings on public functions, classes, and modules (Google-style for Python).
- New behavior gets a test. Django's `TestCase` and `python manage.py test`.
- Do not commit secrets, the `.venv/`, or `db.sqlite3`.

## Key links

- Homework: https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/main/cohorts/2026/01-overview/homework.md
- Submission: https://courses.datatalks.club/ai-dev-tools-2026/homework/hw1
