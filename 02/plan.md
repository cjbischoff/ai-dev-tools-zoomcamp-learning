# Kanvas — Frontend Plan

## Tech Stack

| Choice | Why |
|---|---|
| **Vite** | Fast bundler, zero-config JS, instant HMR |
| **Vanilla JS (ES modules)** | No framework overhead for this scope; easy to iterate |
| **SortableJS** | Lightweight, touch-friendly, works across lists (columns) and within a list (reorder) |
| **Hash-based routing** | Simple client-side routing — no server config needed |

## Directory Structure

```
frontend/
  index.html               — entry HTML
  package.json             — dependencies, dev script
  vite.config.js           — Vite config
  src/
    main.js                — app entry, createApp, mounts router
    api.js                 — ALL backend calls centralized (mocked for now)
    state.js               — simple reactive state store
    router.js              — hash-based router (login | boards | board/:id)
    views/
      login.js             — login / register form
      board-list.js        — list of user's boards + create board
      board-detail.js      — single board with 3 Kanban columns
    components/
      kanban-card.js       — individual card DOM factory
      kanban-column.js     — single column DOM factory
      card-modal.js        — create/edit card modal
      invite-modal.js      — invite user modal
    styles/
      main.css             — base layout, colors, typography, modal
      board.css            — Kanban board layout, columns, cards
```

## Mock API (`api.js`)

All backend calls go through one module. Every function is `async` and returns the same shape a real API would.

- In-memory data store seeded with sample data
- Simulated network latency (`setTimeout`)
- Session token stored in memory after login/register
- Reflects full data model: users, boards, members, cards, positions

### Exported functions

```
login(username, password)
register(username, password)
getBoards()
createBoard(name)
renameBoard(boardId, name)
deleteBoard(boardId)
inviteMember(boardId, username)
removeMember(boardId, userId)
getBoard(boardId)           — board + columns + cards
createCard(boardId, column, title, description, dueDate, assignee)
updateCard(cardId, fields)
deleteCard(cardId)
moveCard(cardId, column, position)  — drag between columns
reorderCards(boardId, column, cardIds)  — drag within column
```

## State Store (`state.js`)

Simple pub/sub store:
- `state.user` — current user object
- `state.boards` — board list
- `state.currentBoard` — active board detail
- Subscribers re-render on change

## Routes

| Hash | View | Description |
|---|---|---|
| `#/login` | login | Login/register screen |
| `#/boards` | board-list | Board list with create/rename/delete |
| `#/board/:id` | board-detail | Kanban board with 3 columns |

Redirect to `#/login` if no user session; to `#/boards` if already logged in.

## Drag-and-Drop Flow

1. SortableJS attaches to each column's card list
2. On drop: determine source column, target column, new position
3. If same column → `reorderCards()`
4. If different column → `moveCard()` (which updates column + position)
5. Mock API updates positions of affected cards
6. Board re-renders from state

## Overdue Visual

- Each card compares `dueDate` against `new Date()`
- If `dueDate` is in the past → card gets `.overdue` CSS class (red left border / highlight)
- Check happens on render and on board load

## Start Command

```bash
cd frontend && npm install && npm run dev
```

---

# Kanvas — Backend Plan (Q4)

## OpenAPI Contract

REST API at `/api/` prefix. Auth via session cookies.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current user |
| GET | `/api/boards` | List user's boards |
| POST | `/api/boards` | Create board |
| PUT | `/api/boards/{id}` | Rename board |
| DELETE | `/api/boards/{id}` | Delete board |
| GET | `/api/boards/{id}` | Board detail with cards + members |
| POST | `/api/boards/{id}/cards` | Create card |
| PUT | `/api/cards/{id}` | Update card |
| DELETE | `/api/cards/{id}` | Delete card |
| PATCH | `/api/cards/{id}/move` | Move card between columns |
| PATCH | `/api/boards/{id}/reorder` | Reorder cards within column |
| POST | `/api/boards/{id}/members` | Invite member |
| DELETE | `/api/boards/{id}/members/{userId}` | Remove member |

## Tech Stack

| Choice | Why |
|---|---|
| **FastAPI** | Async, auto-docs, Pydantic validation |
| **uv** | Package management |
| **pytest + httpx** | Test client |
| **MockDatabaseService** | In-memory dict store → swapped for SQLAlchemy in Q6 |

## Directory Structure

```
backend/
  pyproject.toml
  app/
    __init__.py
    main.py              — FastAPI app, lifespan, CORS
    schemas.py           — Pydantic request/response models
    database.py          — Database service abstract base + mock impl
    dependencies.py      — FastAPI dependency injection (get_db, get_current_user)
    routers/
      __init__.py
      auth.py
      boards.py
      cards.py
  tests/
    __init__.py
    conftest.py          — test client fixture + mock DB
    test_auth.py
    test_boards.py
    test_cards.py
```

## Test-First Approach

1. Write tests that define expected endpoint behavior
2. Implement mock database service
3. Wire endpoints
4. Run tests green
5. Update frontend `api.js` to call real backend

## Start Command

```bash
cd backend && uv run uvicorn app.main:app --reload
```
