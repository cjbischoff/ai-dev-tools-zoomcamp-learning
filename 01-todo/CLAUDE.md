# Module 1 Homework — Django TODO App

## Purpose

Homework 1 for the AI Dev Tools Zoomcamp: a TODO application built in Django with AI assistance. This folder is the submission target — the homework form takes a GitHub link to `01-todo/`.

## Requirements

The app must:

- Create, edit, and delete TODOs
- Assign due dates
- Mark TODOs as resolved

## Stack and Conventions

- Python managed with `uv` (course recommendation): `uv run python manage.py <cmd>` for all Django commands.
- Django project + one app; app registered in the project's `settings.py`.
- Templates: at least `base.html` and `home.html`; template directory registered in `TEMPLATES['DIRS']` or via `APP_DIRS`.
- Tests required (Question 6): run with `uv run python manage.py test`. Iterate until green before calling the homework done.
- Run server: `uv run python manage.py runserver`.

## Homework Answers to Record

As work proceeds, record the answers to the six graded questions in `ANSWERS.md` here:

1. Command used to install Django
2. File edited to include the app in the project
3. Next step after creating models
4. File where TODO logic lives
5. Where the template directory is registered
6. Command for running tests

## Workflow

- Work happens on branch `module/01-overview` with incremental commits (one logical change each).
- SQLite dev database (`db.sqlite3`) stays out of git.
