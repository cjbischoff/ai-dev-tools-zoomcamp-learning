/**
 * Kanvas API — centralized backend calls.
 *
 * Makes real HTTP requests to the FastAPI backend at http://localhost:8000.
 * Session is managed via httponly cookie (kanvas_session).
 *
 * Functions maintain the same signatures as the original mock so views
 * work without changes.
 */

const BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Session cache — populated on login/register, cleared on logout,
// initialized on page load via initSession().
// ---------------------------------------------------------------------------

let sessionCache = null;

/** Call on app startup to check for an existing session cookie. */
export async function initSession() {
  try {
    const data = await apiFetch("/api/auth/me");
    sessionCache = { userId: data.user.id, username: data.user.username };
  } catch {
    sessionCache = null;
  }
}

export function getSession() {
  return sessionCache;
}

// ---------------------------------------------------------------------------
// HTTP helpers
// ---------------------------------------------------------------------------

async function apiFetch(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // use default
    }
    throw new Error(detail);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Response mappers — convert backend snake_case to frontend camelCase
// ---------------------------------------------------------------------------

function mapUser(u) {
  return { id: u.id, username: u.username };
}

function mapBoard(b) {
  return {
    id: b.id,
    name: b.name,
    ownerId: b.owner_id,
    createdAt: b.created_at,
    memberCount: b.member_count,
    isOwner: b.is_owner,
  };
}

function mapMember(m) {
  return { userId: m.user_id, username: m.username, role: m.role };
}

function mapCard(c) {
  return {
    id: c.id,
    boardId: c.board_id,
    column: c.column,
    title: c.title,
    description: c.description,
    dueDate: c.due_date,
    assignee: c.assignee,
    position: c.position,
    createdAt: c.created_at,
    updatedAt: c.updated_at,
  };
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(username, password) {
  const data = await apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  sessionCache = { userId: data.user.id, username: data.user.username };
  return { user: mapUser(data.user) };
}

export async function register(username, password) {
  const data = await apiFetch("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  sessionCache = { userId: data.user.id, username: data.user.username };
  return { user: mapUser(data.user) };
}

export async function logout() {
  await apiFetch("/api/auth/logout", { method: "POST" });
  sessionCache = null;
}

// ---------------------------------------------------------------------------
// Boards
// ---------------------------------------------------------------------------

export async function getBoards() {
  const data = await apiFetch("/api/boards");
  return data.map(mapBoard);
}

export async function createBoard(name) {
  const data = await apiFetch("/api/boards", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
  return mapBoard({ ...data, member_count: 1, is_owner: true });
}

export async function renameBoard(boardId, name) {
  const data = await apiFetch(`/api/boards/${boardId}`, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
  return mapBoard(data);
}

export async function deleteBoard(boardId) {
  return apiFetch(`/api/boards/${boardId}`, { method: "DELETE" });
}

export async function getBoard(boardId) {
  const data = await apiFetch(`/api/boards/${boardId}`);
  return {
    id: data.id,
    name: data.name,
    ownerId: data.owner_id,
    createdAt: data.created_at,
    members: (data.members || []).map(mapMember),
    cards: (data.cards || []).map(mapCard),
    isOwner: sessionCache ? data.owner_id === sessionCache.userId : false,
  };
}

// ---------------------------------------------------------------------------
// Cards
// ---------------------------------------------------------------------------

export async function createCard(boardId, column, title, description, dueDate, assignee) {
  const data = await apiFetch(`/api/boards/${boardId}/cards`, {
    method: "POST",
    body: JSON.stringify({
      column,
      title,
      description: description || "",
      due_date: dueDate || "",
      assignee: assignee || "",
    }),
  });
  return mapCard(data);
}

export async function updateCard(cardId, fields) {
  const body = {};
  if (fields.title !== undefined) body.title = fields.title;
  if (fields.description !== undefined) body.description = fields.description;
  if (fields.dueDate !== undefined) body.due_date = fields.dueDate;
  if (fields.assignee !== undefined) body.assignee = fields.assignee;

  const data = await apiFetch(`/api/cards/${cardId}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
  return mapCard(data);
}

export async function deleteCard(cardId) {
  return apiFetch(`/api/cards/${cardId}`, { method: "DELETE" });
}

export async function moveCard(cardId, newColumn, newPosition) {
  const data = await apiFetch(`/api/cards/${cardId}/move`, {
    method: "PATCH",
    body: JSON.stringify({ new_column: newColumn, new_position: newPosition }),
  });
  return mapCard(data);
}

export async function reorderCards(boardId, column, cardIdsInOrder) {
  return apiFetch(`/api/boards/${boardId}/reorder`, {
    method: "PATCH",
    body: JSON.stringify({ column, card_ids: cardIdsInOrder }),
  });
}

// ---------------------------------------------------------------------------
// Members
// ---------------------------------------------------------------------------

export async function inviteMember(boardId, username) {
  return apiFetch(`/api/boards/${boardId}/members`, {
    method: "POST",
    body: JSON.stringify({ username }),
  });
}

export async function removeMember(boardId, userId) {
  return apiFetch(`/api/boards/${boardId}/members/${userId}`, {
    method: "DELETE",
  });
}
