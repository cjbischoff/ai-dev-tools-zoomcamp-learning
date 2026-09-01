# Household Chores Tool — Product Spec

## Overview

A shared-link web app for managing one-time household chores. No accounts, no login — anyone with the URL can use it.

## Core Features

### 1. Create and assign tasks
- Anyone can add a task with a description and an assignee name
- Assignee is free-text (e.g., "Alice", "Bob") — no pre-configuration

### 2. Grouped task list
- All tasks displayed in a single page, grouped by assignee
- Each person sees a section with their assigned tasks

### 3. Mark tasks as done
- Each task has a "Done" button
- Completed tasks remain visible in their group

### 4. Persistent storage
- Task data stored in SQLite (no server restart loss)

## What's Excluded (Out of Scope)

- User accounts, login, or authentication
- Task recurrence (daily/weekly)
- Editing or deleting tasks (beyond marking done)
- Drag-and-drop reordering
- Notifications or reminders
- Mobile app

## Tech Stack

- **Framework:** Django (project + dedicated app)
- **Database:** SQLite
- **Frontend:** Minimal Django templates (no JS framework)

## Data Model

```
Task
- id: int (PK)
- description: text
- assignee: text (free-text name)
- is_done: boolean (default false)
- created_at: datetime
```

## Project Structure

```
01/
├── manage.py              # Django entry point
├── household/             # Django project config
│   ├── settings.py        # Settings (INSTALLED_APPS, DB, etc.)
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI config
├── chores/                # The app
│   ├── models.py
│   ├── views.py
│   └── tests.py
└── _docs/
    └── plan.md            # This file
```

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Task list grouped by assignee |
| POST | `/tasks/create/` | Create a new task |
| POST | `/tasks/<id>/done/` | Mark task as done |
