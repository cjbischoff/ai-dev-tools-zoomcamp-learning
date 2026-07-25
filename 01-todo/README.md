# Django TODO App

A small, tested Django application for managing TODOs with due dates. It is the
Module 1 homework submission for the
[DataTalksClub AI Dev Tools Zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/tree/main/01-overview)
and demonstrates a complete spec-to-tested-code workflow.

## Quick Start

Requirements:

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)

From the repository root:

```shell
cd 01-todo
uv sync --locked
uv run python manage.py migrate
uv run python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser.

The SQLite development database is created locally as `db.sqlite3` and is
excluded from git.

## How It Works

```text
Browser
  → config/urls.py
  → todos/urls.py
  → todos/views.py
  → TodoForm and Todo model
  → SQLite and Django templates
  → HTTP response
```

The Django project and application have separate responsibilities:

- `config/` contains project-wide settings, root URLs, and WSGI/ASGI entry points.
- `todos/` contains the model, form, views, routes, templates, migration, and tests.
- `Todo` stores a title, due date, and resolved state.
- `TodoForm` validates title and due-date input.
- Views use POST/Redirect/GET after successful mutations.
- Resolve and delete views use `@require_POST`.
- Templates include CSRF tokens for every modifying request.

### Routes

- `GET /` — display the create form and all TODOs
- `POST /` — create a TODO
- `GET /<id>/edit/` — display a populated edit form
- `POST /<id>/edit/` — update a TODO
- `POST /<id>/resolve/` — mark a TODO as resolved
- `POST /<id>/delete/` — delete a TODO

## Project Structure

```text
01-todo/
├── config/
│   ├── settings.py        # Installed apps, templates, middleware, SQLite
│   └── urls.py            # Root URL routing
├── todos/
│   ├── migrations/        # Reproducible database schema
│   ├── templates/todos/   # Base, list/create, and edit templates
│   ├── forms.py           # Model-backed input validation
│   ├── models.py          # Todo database model
│   ├── tests.py           # 13 functional tests
│   ├── urls.py            # Application routes
│   └── views.py           # Create, edit, resolve, and delete behavior
├── ANSWERS.md             # Answers to the six graded questions
├── CLAUDE.md              # Homework specification and agent context
├── manage.py              # Django command entry point
├── pyproject.toml         # Python and Django requirements
└── uv.lock                # Reproducible dependency versions
```

## Testing

Run the complete suite:

```shell
uv run python manage.py test
```

Run the same checks used by CI:

```shell
uv sync --locked
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test
```

The 13 tests cover:

- Empty-list rendering
- Valid and invalid creation
- Edit-form population
- Valid and invalid editing
- Due-date rendering
- Resolving TODOs
- Resolved-state rendering
- Deleting TODOs
- POST-only mutation endpoints
- Missing-record responses
- The complete create → edit → resolve → delete workflow

## Continuous Integration

The [TODO test workflow](../.github/workflows/todo-tests.yml) runs on relevant
pushes and pull requests and can also be started manually.

It:

1. Installs dependencies from `uv.lock`.
2. checks Django configuration.
3. rejects model changes without a migration.
4. runs all 13 functional tests.

## Design Scope

This is intentionally the simplest application that satisfies the homework.
It uses function-based views, Django templates, and SQLite with no additional
runtime dependencies.

It is development-only and does not include authentication, per-user TODOs,
pagination, styling, deployment configuration, or production settings.

## Homework References

- [Homework answers](ANSWERS.md)
- [Homework specification](CLAUDE.md)
- [2026 course page](https://courses.datatalks.club/ai-dev-tools-2026/)
- [Module 1 pull request](https://github.com/cjbischoff/ai-dev-tools-zoomcamp-learning/pull/1)
