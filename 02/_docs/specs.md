# Kanvas — Mini Kanban Board

## Overview

Kanvas is a lightweight, multi-user Kanban board application. Users can create boards, invite collaborators, and manage tasks across the classic three-column workflow: To Do, In Progress, Done. Cards support titles, descriptions, due dates, and assignees. Drag-and-drop handles both status transitions and within-column priority reordering.

The project follows the spec-first workflow from the AI Dev Tools Zoomcamp (Module 2): product spec, frontend prototype, OpenAPI contract, backend, database, and tests.

---

## User Stories

### Authentication

**US-1: User registration**
> As a new user, I want to create an account with a username and password so that I can access the application.

**US-2: User login**
> As a registered user, I want to log in with my credentials so that I can see my boards.

### Boards

**US-3: Create a board**
> As a logged-in user, I want to create a new Kanban board so that I can organize tasks for a project.

**US-4: View my boards**
> As a logged-in user, I want to see a list of all boards I own or have been invited to so that I can choose where to work.

**US-5: Invite a user to a board**
> As a board owner, I want to invite another registered user to my board so that we can collaborate.

**US-6: Rename a board**
> As a board member, I want to rename a board so that the title reflects the current project.

**US-7: Delete a board**
> As a board owner, I want to delete a board so that I can remove finished or abandoned projects.

### Cards

**US-8: Create a card**
> As a board member, I want to add a card with a title, optional description, optional due date, and optional assignee so that I can track a task.

**US-9: Edit a card**
> As a board member, I want to edit any field on an existing card so that I can update task details.

**US-10: Delete a card**
> As a board member, I want to delete a card so that I can remove tasks that are no longer relevant.

**US-11: Move a card between columns**
> As a board member, I want to drag a card from one column to another (To Do → In Progress → Done) so that I can update its status.

**US-12: Reorder cards within a column**
> As a board member, I want to drag cards up or down within a column so that I can prioritize tasks manually.

### Due Dates

**US-13: See overdue visual warning**
> As a board member, I want a card with a past due date to show a visual warning (e.g., red highlight) so that I can identify overdue tasks at a glance.

---

## Acceptance Criteria

### Authentication

| ID | Criterion |
|---|---|
| AC-1 | Registration requires username (unique, min 3 chars) and password (min 6 chars). |
| AC-2 | On successful registration, user is logged in and receives a session token. |
| AC-3 | Login validates credentials and returns a session token. |
| AC-4 | All board and card endpoints reject unauthenticated requests with 401. |

### Boards

| ID | Criterion |
|---|---|
| AC-5 | A board has a name (required, max 100 chars) and auto-generated creation timestamp. |
| AC-6 | Board owner can invite any registered user by their username. |
| AC-7 | Board owner can delete the board. Any board member can rename it. |
| AC-8 | Board list endpoint returns boards the current user owns or is a member of. |

### Cards

| ID | Criterion |
|---|---|
| AC-9 | A card belongs to exactly one board and one column. |
| AC-10 | Card title is required (max 200 chars). Description, due date, and assignee are optional. |
| AC-11 | Assignee is a free-text username field (does not enforce that the user is a board member). |
| AC-12 | Moving a card to `done` preserves its position in that column. |
| AC-13 | Manual reorder is persisted and survives refresh. |

### Due Dates

| ID | Criterion |
|---|---|
| AC-14 | A card whose due date is before the current time (server time) shows a visual overdue indicator in the frontend. |

---

## Data Model

```
User
  id: int (PK)
  username: str (unique, min 3 chars)
  password_hash: str

Board
  id: int (PK)
  name: str (max 100 chars)
  owner_id: int (FK → User)
  created_at: datetime

BoardMember
  id: int (PK)
  board_id: int (FK → Board)
  user_id: int (FK → User)
  role: enum(owner, member)

Card
  id: int (PK)
  board_id: int (FK → Board)
  column: enum(todo, in_progress, done)
  title: str (max 200 chars)
  description: str (optional)
  due_date: datetime (optional)
  assignee: str (optional, free text)
  position: float (for manual ordering)
  created_at: datetime
  updated_at: datetime
```

Columns are fixed: `todo`, `in_progress`, `done`. Cards are ordered by their `position` value within a column (ascending). A new card gets a position equal to `max(position) + 1` in its column. Drag-reordering updates the positions of affected cards to insert the moved card at the new spot.

---

## Non-Goals

- No password reset or email verification.
- No real-time collaboration (WebSocket). Changes appear on refresh.
- No search or filter functionality.
- No column customization (name, count).
- No card attachments, comments, or checklists.
- No rate limiting or advanced permission model beyond owner/member.
- No deployment or containerization (covered in Module 3).

---

## Technical Constraints (from Homework)

| Layer | Constraint |
|---|---|
| Frontend | Interactive single-page app in `frontend/`. Backend calls centralized in one module and mockable. |
| API contract | `openapi.yaml` as source of truth between frontend and backend. |
| Backend | Python with FastAPI and `uv`. Database-agnostic persistence layer. |
| Database | SQLite via SQLAlchemy. Mock store used first, swapped to real DB later. |
| Tests | Test endpoints before implementing them. Tests must pass after mock-to-SQLite swap. |
| Docs | `AGENTS.md`, `_docs/specs.md`, README with run instructions. |

---

## App Name

**Kanvas** — portmanteau of "Kanban" and "canvas."
