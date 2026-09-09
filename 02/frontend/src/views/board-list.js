import * as api from "../api.js";
import store from "../state.js";
import router from "../router.js";

export default async function renderBoardList() {
  const app = document.getElementById("app");
  const session = api.getSession();
  if (!session) return router.navigate("/login");

  let boards = [];
  let error = "";

  async function load() {
    try {
      boards = await api.getBoards();
      render();
    } catch (err) {
      error = err.message;
      render();
    }
  }

  function render() {
    app.innerHTML = `
      <div class="board-list-page">
        <div class="board-list-header">
          <h1>My Boards</h1>
          <div class="user-info">
            <span>${api.getSession()?.username || ""}</span>
            <button class="btn btn-ghost btn-sm" id="logout-btn">Log out</button>
          </div>
        </div>
        <button class="btn btn-primary" id="create-board-btn" style="margin-bottom:16px">
          + New Board
        </button>
        ${error ? `<div class="form-error" style="margin-bottom:12px">${error}</div>` : ""}
        <div id="board-list">
          ${boards.length === 0
            ? `<div class="empty-state"><p>No boards yet. Create your first one!</p></div>`
            : `<div class="board-grid">
                ${boards.map((b) => `
                  <div class="board-card" data-board-id="${b.id}">
                    <div class="board-card-info">
                      <h3>${escapeHtml(b.name)}</h3>
                      <p>${b.memberCount} member${b.memberCount !== 1 ? "s" : ""}${b.isOwner ? " · Owner" : ""}</p>
                    </div>
                    <div class="board-card-actions">
                      ${b.isOwner ? `<button class="btn-icon" data-action="rename" title="Rename">✏️</button>` : ""}
                      ${b.isOwner ? `<button class="btn-icon" data-action="delete" title="Delete">🗑️</button>` : ""}
                    </div>
                  </div>
                `).join("")}
              </div>`
          }
        </div>
      </div>
    `;

    // Logout
    document.getElementById("logout-btn").addEventListener("click", async () => {
      await api.logout();
      store.set("user", null);
      router.navigate("/login");
    });

    // Create board
    document.getElementById("create-board-btn").addEventListener("click", () => {
      showCreateBoardModal();
    });

    // Board card click → navigate
    document.querySelectorAll(".board-card").forEach((el) => {
      el.addEventListener("click", (e) => {
        if (e.target.closest("[data-action]")) return;
        router.navigate(`/board/${el.dataset.boardId}`);
      });
    });

    // Rename
    document.querySelectorAll("[data-action='rename']").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const boardId = Number(btn.closest(".board-card").dataset.boardId);
        const board = boards.find((b) => b.id === boardId);
        if (board) showRenameBoardModal(board);
      });
    });

    // Delete
    document.querySelectorAll("[data-action='delete']").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const boardId = Number(btn.closest(".board-card").dataset.boardId);
        showDeleteBoardModal(boardId);
      });
    });
  }

  function showCreateBoardModal() {
    showModal(`
      <h2>Create Board</h2>
      <div class="form-group">
        <label for="board-name">Board name</label>
        <input type="text" id="board-name" maxlength="100" required autofocus />
      </div>
      <div class="modal-actions">
        <button class="btn btn-ghost" data-close>Cancel</button>
        <button class="btn btn-primary" id="confirm-create">Create</button>
      </div>
    `, async () => {
      const name = document.getElementById("board-name").value.trim();
      if (!name) return;
      try {
        await api.createBoard(name);
        await load();
      } catch (err) {
        alert(err.message);
      }
    });
  }

  function showRenameBoardModal(board) {
    showModal(`
      <h2>Rename Board</h2>
      <div class="form-group">
        <label for="board-name">Board name</label>
        <input type="text" id="board-name" maxlength="100" value="${escapeHtml(board.name)}" required autofocus />
      </div>
      <div class="modal-actions">
        <button class="btn btn-ghost" data-close>Cancel</button>
        <button class="btn btn-primary" id="confirm-rename">Save</button>
      </div>
    `, async () => {
      const name = document.getElementById("board-name").value.trim();
      if (!name) return;
      try {
        await api.renameBoard(board.id, name);
        await load();
      } catch (err) {
        alert(err.message);
      }
    });
  }

  function showDeleteBoardModal(boardId) {
    showModal(`
      <h2>Delete Board</h2>
      <p style="margin-bottom:16px;color:var(--color-text-muted)">
        Are you sure? All cards will be permanently deleted.
      </p>
      <div class="modal-actions">
        <button class="btn btn-ghost" data-close>Cancel</button>
        <button class="btn btn-danger" id="confirm-delete">Delete</button>
      </div>
    `, async () => {
      try {
        await api.deleteBoard(boardId);
        await load();
      } catch (err) {
        alert(err.message);
      }
    });
  }

  load();
}

// --- Modal helper ---

function showModal(html, onConfirm) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `<div class="modal">${html}</div>`;
  document.body.appendChild(overlay);

  const close = () => overlay.remove();

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  overlay.querySelectorAll("[data-close]").forEach((el) => el.addEventListener("click", close));

  const confirmBtn = overlay.querySelector("#confirm-create, #confirm-rename, #confirm-delete, #confirm-invite");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      await onConfirm();
      close();
    });
  }

  // Auto-focus first input
  const input = overlay.querySelector("input, textarea");
  if (input) setTimeout(() => input.focus(), 50);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
