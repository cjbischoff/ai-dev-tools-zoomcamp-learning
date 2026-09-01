# Household Chores

A shared-link web app for managing one-time household chores. No accounts, no login — anyone with the URL can use it.

Built with Django + SQLite.

## Quick Start

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Open http://127.0.0.1:8000 in a browser.

## Tests

```bash
uv run python manage.py test
```

## Homework

Answers for [AI Dev Tools Zoomcamp 2026 — Homework 1](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/main/cohorts/2026/01-overview/homework.md).

| # | Question | Answer |
|---|----------|--------|
| 1 | Coding agent | Oh My Pi (omp) — `spark-deepseek/deepseek-v4-flash` |
| 2 | Spec features | Create & assign tasks, grouped list by assignee, mark done, SQLite persistence |
| 3 | App registration file | `settings.py` (`INSTALLED_APPS`) |
| 4 | Backlog task 1 | Create the Task model |
| 5 | Dev server command | `uv run python manage.py runserver` |
| 6 | Test runner command | `python manage.py test` |
