/**
 * Kanvas API — centralized backend calls.
 *
 * Currently mocked with in-memory data and simulated latency.
 * When the real backend exists, swap the implementation of each
 * function — callers stay unchanged.
 */

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

let nextId = 100;
const id = () => nextId++;

const delay = (ms = 200) => new Promise((r) => setTimeout(r, ms));

let users = [
  { id: id(), username: "alice", passwordHash: "pass" },
  { id: id(), username: "bob", passwordHash: "pass" },
];

let boards = [
  { id: id(), name: "Sprint 24", ownerId: 1, createdAt: new Date().toISOString() },
  { id: id(), name: "Ideas", ownerId: 1, createdAt: new Date().toISOString() },
];

let boardMembers = [
  { id: id(), boardId: 1, userId: 1, role: "owner" },
  { id: id(), boardId: 1, userId: 2, role: "member" },
  { id: id(), boardId: 2, userId: 1, role: "owner" },
];

let cards = [
  { id: id(), boardId: 1, column: "todo", title: "Design landing page", description: "Create mockups for the new landing page", dueDate: "2026-09-20", assignee: "", position: 1, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: id(), boardId: 1, column: "todo", title: "Set up CI pipeline", description: "", dueDate: "", assignee: "bob", position: 2, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: id(), boardId: 1, column: "in_progress", title: "API rate limiting", description: "Add rate limiting middleware to the API gateway", dueDate: "2026-09-10", assignee: "", position: 1, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: id(), boardId: 1, column: "in_progress", title: "User dashboard", description: "Build the user dashboard with activity charts", dueDate: "2026-09-15", assignee: "alice", position: 2, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: id(), boardId: 1, column: "done", title: "User authentication", description: "Implement login and registration", dueDate: "2026-09-05", assignee: "", position: 1, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
  { id: id(), boardId: 2, column: "todo", title: "Read about AI agents", description: "", dueDate: "", assignee: "", position: 1, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() },
];

let session = null; // { userId, username }

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function findUser(username) {
  return users.find((u) => u.username === username);
}

function requireAuth() {
  if (!session) throw new Error("Unauthorized");
  return session;
}

function getBoardOrThrow(boardId) {
  const board = boards.find((b) => b.id === boardId);
  if (!board) throw new Error("Board not found");
  const memberIds = boardMembers
    .filter((m) => m.boardId === boardId)
    .map((m) => m.userId);
  if (!memberIds.includes(session.userId)) throw new Error("Not a board member");
  return board;
}

function nextPosition(boardId, column) {
  const colCards = cards.filter((c) => c.boardId === boardId && c.column === column);
  return colCards.length === 0 ? 1 : Math.max(...colCards.map((c) => c.position)) + 1;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function login(username, password) {
  await delay();
  const user = findUser(username);
  if (!user || user.passwordHash !== password) {
    throw new Error("Invalid username or password");
  }
  session = { userId: user.id, username: user.username };
  return { user: { id: user.id, username: user.username } };
}

export async function register(username, password) {
  await delay();
  if (username.length < 3) throw new Error("Username must be at least 3 characters");
  if (password.length < 6) throw new Error("Password must be at least 6 characters");
  if (findUser(username)) throw new Error("Username already taken");
  const user = { id: id(), username, passwordHash: password };
  users.push(user);
  session = { userId: user.id, username: user.username };
  return { user: { id: user.id, username: user.username } };
}

export async function logout() {
  await delay(50);
  session = null;
}

export function getSession() {
  return session;
}

export async function getBoards() {
  await delay();
  requireAuth();
  const memberBoardIds = boardMembers
    .filter((m) => m.userId === session.userId)
    .map((m) => m.boardId);
  return boards
    .filter((b) => memberBoardIds.includes(b.id))
    .map((b) => ({
      ...b,
      memberCount: boardMembers.filter((m) => m.boardId === b.id).length,
      isOwner: b.ownerId === session.userId,
    }));
}

export async function createBoard(name) {
  await delay();
  requireAuth();
  if (!name || name.length > 100) throw new Error("Board name is required (max 100 chars)");
  const board = {
    id: id(),
    name,
    ownerId: session.userId,
    createdAt: new Date().toISOString(),
  };
  boards.push(board);
  boardMembers.push({ id: id(), boardId: board.id, userId: session.userId, role: "owner" });
  return board;
}

export async function renameBoard(boardId, name) {
  await delay();
  requireAuth();
  const board = boards.find((b) => b.id === boardId);
  if (!board) throw new Error("Board not found");
  if (!name || name.length > 100) throw new Error("Invalid name");
  const member = boardMembers.find((m) => m.boardId === boardId && m.userId === session.userId);
  if (!member) throw new Error("Not a board member");
  board.name = name;
  return { ...board };
}

export async function deleteBoard(boardId) {
  await delay();
  requireAuth();
  const board = boards.find((b) => b.id === boardId);
  if (!board) throw new Error("Board not found");
  if (board.ownerId !== session.userId) throw new Error("Only the owner can delete a board");
  boards = boards.filter((b) => b.id !== boardId);
  boardMembers = boardMembers.filter((m) => m.boardId !== boardId);
  cards = cards.filter((c) => c.boardId !== boardId);
  return { success: true };
}

export async function getBoard(boardId) {
  await delay();
  requireAuth();
  const board = getBoardOrThrow(boardId);
  const memberList = boardMembers
    .filter((m) => m.boardId === boardId)
    .map((m) => {
      const user = users.find((u) => u.id === m.userId);
      return { userId: m.userId, username: user ? user.username : "unknown", role: m.role };
    });
  const boardCards = cards
    .filter((c) => c.boardId === boardId)
    .map(({ passwordHash, ...rest }) => rest)
    .sort((a, b) => a.position - b.position);
  return { ...board, members: memberList, cards: boardCards };
}

export async function createCard(boardId, column, title, description, dueDate, assignee) {
  await delay();
  requireAuth();
  getBoardOrThrow(boardId);
  if (!title || title.length > 200) throw new Error("Title is required (max 200 chars)");
  const validColumns = ["todo", "in_progress", "done"];
  if (!validColumns.includes(column)) throw new Error("Invalid column");
  const card = {
    id: id(),
    boardId,
    column,
    title,
    description: description || "",
    dueDate: dueDate || "",
    assignee: assignee || "",
    position: nextPosition(boardId, column),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  cards.push(card);
  return { ...card };
}

export async function updateCard(cardId, fields) {
  await delay();
  requireAuth();
  const card = cards.find((c) => c.id === cardId);
  if (!card) throw new Error("Card not found");
  getBoardOrThrow(card.boardId);
  if (fields.title !== undefined && (!fields.title || fields.title.length > 200)) {
    throw new Error("Invalid title");
  }
  Object.assign(card, fields);
  card.updatedAt = new Date().toISOString();
  return { ...card };
}

export async function deleteCard(cardId) {
  await delay();
  requireAuth();
  const card = cards.find((c) => c.id === cardId);
  if (!card) throw new Error("Card not found");
  getBoardOrThrow(card.boardId);
  cards = cards.filter((c) => c.id !== cardId);
  return { success: true };
}

export async function moveCard(cardId, newColumn, newPosition) {
  await delay();
  requireAuth();
  const card = cards.find((c) => c.id === cardId);
  if (!card) throw new Error("Card not found");
  getBoardOrThrow(card.boardId);
  const oldColumn = card.column;
  card.column = newColumn;
  card.updatedAt = new Date().toISOString();

  // Reorder positions within target column
  const colCards = cards
    .filter((c) => c.boardId === card.boardId && c.column === newColumn && c.id !== cardId)
    .sort((a, b) => a.position - b.position);

  colCards.splice(newPosition - 1, 0, card);
  colCards.forEach((c, i) => {
    c.position = i + 1;
  });

  return { ...card };
}

export async function reorderCards(boardId, column, cardIdsInOrder) {
  await delay();
  requireAuth();
  getBoardOrThrow(boardId);
  const colCards = cards.filter(
    (c) => c.boardId === boardId && c.column === column
  );
  const idSet = new Set(cardIdsInOrder);
  for (const c of colCards) {
    if (!idSet.has(c.id)) throw new Error("Card list mismatch");
  }
  cardIdsInOrder.forEach((cid, i) => {
    const card = cards.find((c) => c.id === cid);
    if (card) card.position = i + 1;
  });
  return { success: true };
}

export async function inviteMember(boardId, username) {
  await delay();
  requireAuth();
  const board = boards.find((b) => b.id === boardId);
  if (!board) throw new Error("Board not found");
  if (board.ownerId !== session.userId) throw new Error("Only the owner can invite members");
  const user = findUser(username);
  if (!user) throw new Error("User not found");
  const already = boardMembers.find((m) => m.boardId === boardId && m.userId === user.id);
  if (already) throw new Error("User is already a member");
  boardMembers.push({ id: id(), boardId, userId: user.id, role: "member" });
  return { success: true };
}

export async function removeMember(boardId, userId) {
  await delay();
  requireAuth();
  const board = boards.find((b) => b.id === boardId);
  if (!board) throw new Error("Board not found");
  if (board.ownerId !== session.userId) throw new Error("Only the owner can remove members");
  if (userId === board.ownerId) throw new Error("Cannot remove the owner");
  boardMembers = boardMembers.filter(
    (m) => !(m.boardId === boardId && m.userId === userId)
  );
  return { success: true };
}
