# Backlog — Household Chores Tool

## Task 1: Create the Task model
- Define `Task` model in `chores/models.py` with fields: `description`, `assignee`, `is_done`, `created_at`
- Create and run migrations

## Task 2: Wire URL routing
- Create `chores/urls.py`
- Include it in `household/urls.py` under the root path

## Task 3: Build the views
- `task_list` view — query all tasks, group by assignee, render template
- `create_task` view — handle POST form submission, create new task, redirect
- `mark_done` view — handle POST to toggle a task as done, redirect

## Task 4: Create the templates
- `chores/templates/chores/task_list.html` — grouped list with create form and done buttons

## Task 5: Verify it runs
- Start dev server, add a task, mark it done, confirm persistence across restart
