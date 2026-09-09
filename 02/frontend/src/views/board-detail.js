import Sortable from "sortablejs";
import * as api from "../api.js";
import router from "../router.js";
import { createColumnElement } from "../components/kanban-column.js";
import { showCardModal } from "../components/card-modal.js";
import { showInviteModal } from "../components/invite-modal.js";

const COLUMNS = ["todo", "in_progress", "done"];

export default async function renderBoardDetail(params) {
  const app = document.getElementById("app");
  const session = api.getSession();
  if (!session) return router.navigate("/login");

  const boardId = Number(params.id);
  let board = null;
  let loading = true;
  let error = "";
  let sortableInstances = [];

  async function load() {
    loading = true;
    error = "";
    render();
    try {
      board = await api.getBoard(boardId);
      loading = false;
      render();
    } catch (err) {
      error = err.message;
      loading = false;
      render();
    }
  }

  function render() {
    if (loading && !board) {
      app.innerHTML = `<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--color-text-muted)">Loading…</div>`;
      return;
    }

    if (error && !board) {
      app.innerHTML = `
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">
          <p style="color:var(--color-danger)">${escapeHtml(error)}</p>
          <button class="btn btn-ghost" id="back-btn">← Back to boards</button>
        </div>
      `;
      document.getElementById("back-btn")?.addEventListener("click", () => router.navigate("/boards"));
      return;
    }

    // Destroy prior Sortable instances before re-render
    sortableInstances.forEach((s) => s.destroy());
    sortableInstances = [];

    app.innerHTML = `
      <div class="board-page">
        <div class="board-topbar">
          <button class="btn btn-ghost btn-sm" id="back-btn">← Boards</button>
          <h1>${escapeHtml(board.name)}</h1>
          <div class="board-actions">
            <button class="btn btn-ghost btn-sm" id="invite-btn">+ Invite</button>
            <button class="btn btn-ghost btn-sm" id="rename-btn">Rename</button>
            ${board.isOwner ? `<button class="btn btn-ghost btn-sm btn-danger" id="delete-board-btn">Delete</button>` : ""}
          </div>
        </div>
        <div class="board-columns" id="board-columns"></div>
      </div>
    `;

    const columnsContainer = document.getElementById("board-columns");

    // Render each column
    COLUMNS.forEach((colKey) => {
      const colCards = (board.cards || [])
        .filter((c) => c.column === colKey)
        .sort((a, b) => a.position - b.position);

      const colEl = createColumnElement(colKey, colCards, {
        onAddCard: (column) => handleAddCard(column),
        onEditCard: (cardId) => handleEditCard(cardId),
        onDeleteCard: (cardId) => handleDeleteCard(cardId),
      });
      columnsContainer.appendChild(colEl);
    });

    // Back
    document.getElementById("back-btn").addEventListener("click", () => router.navigate("/boards"));

    // Invite
    document.getElementById("invite-btn").addEventListener("click", () => {
      showInviteModal({
        onInvite: async (username) => {
          try {
            await api.inviteMember(boardId, username);
            await load();
          } catch (err) {
            alert(err.message);
          }
        },
      });
    });

    // Rename
    document.getElementById("rename-btn").addEventListener("click", () => {
      showRenameModal();
    });

    // Delete board
    const deleteBtn = document.getElementById("delete-board-btn");
    if (deleteBtn) {
      deleteBtn.addEventListener("click", () => {
        if (confirm("Delete this board and all its cards?")) {
          api.deleteBoard(boardId).then(() => router.navigate("/boards"));
        }
      });
    }

    // Init SortableJS on each column
    document.querySelectorAll(".card-list").forEach((list) => {
      const sortable = Sortable.create(list, {
        group: "kanban",
        animation: 200,
        ghostClass: "sortable-ghost",
        chosenClass: "sortable-chosen",
        dragClass: "sortable-drag",
        onEnd: async (evt) => {
          const fromColumn = evt.from.dataset.column;
          const toColumn = evt.to.dataset.column;
          const cardId = Number(evt.item.dataset.cardId);

          if (fromColumn === toColumn) {
            // Same column — reorder
            const cardIds = [];
            evt.to.querySelectorAll(".kanban-card").forEach((li) => {
              cardIds.push(Number(li.dataset.cardId));
            });
            try {
              await api.reorderCards(boardId, fromColumn, cardIds);
              board = await api.getBoard(boardId);
              render();
            } catch (err) {
              alert(err.message);
              render();
            }
          } else {
            // Different column — move
            const newPosition = evt.newIndex + 1;
            try {
              await api.moveCard(cardId, toColumn, newPosition);
              board = await api.getBoard(boardId);
              render();
            } catch (err) {
              alert(err.message);
              render();
            }
          }
        },
      });
      sortableInstances.push(sortable);
    });
  }

  function showRenameModal() {
    showSimpleModal(`
      <h2>Rename Board</h2>
      <div class="form-group">
        <label for="rename-board-name">Board name</label>
        <input type="text" id="rename-board-name" maxlength="100" value="${escapeHtml(board.name)}" required autofocus />
      </div>
      <div class="modal-actions">
        <button class="btn btn-ghost" data-close>Cancel</button>
        <button class="btn btn-primary" id="confirm-rename">Save</button>
      </div>
    `, async () => {
      const name = document.getElementById("rename-board-name").value.trim();
      if (!name) return;
      try {
        await api.renameBoard(boardId, name);
        await load();
      } catch (err) {
        alert(err.message);
      }
    });
  }

  function handleAddCard(column) {
    showCardModal({ column, isEdit: false }, {
      onSave: async (fields) => {
        try {
          await api.createCard(boardId, column, fields.title, fields.description, fields.dueDate, fields.assignee);
          board = await api.getBoard(boardId);
          render();
        } catch (err) {
          alert(err.message);
        }
      },
    });
  }

  function handleEditCard(cardId) {
    const card = (board.cards || []).find((c) => c.id === cardId);
    if (!card) return;

    showCardModal({
      title: card.title,
      description: card.description,
      dueDate: card.dueDate,
      assignee: card.assignee,
      isEdit: true,
    }, {
      onSave: async (fields) => {
        try {
          await api.updateCard(cardId, {
            title: fields.title,
            description: fields.description,
            dueDate: fields.dueDate,
            assignee: fields.assignee,
          });
          board = await api.getBoard(boardId);
          render();
        } catch (err) {
          alert(err.message);
        }
      },
    });
  }

  function handleDeleteCard(cardId) {
    if (!confirm("Delete this card?")) return;
    api.deleteCard(cardId).then(() => {
      api.getBoard(boardId).then((b) => {
        board = b;
        render();
      });
    });
  }

  load();
}

// --- Simple modal helper (reused) ---

function showSimpleModal(html, onConfirm) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `<div class="modal">${html}</div>`;
  document.body.appendChild(overlay);

  const close = () => overlay.remove();

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  overlay.querySelectorAll("[data-close]").forEach((el) => el.addEventListener("click", close));

  const confirmBtn = overlay.querySelector("#confirm-rename");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      await onConfirm();
      close();
    });
  }

  setTimeout(() => overlay.querySelector("input")?.focus(), 50);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
