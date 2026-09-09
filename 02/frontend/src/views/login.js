import * as api from "../api.js";
import store from "../state.js";
import router from "../router.js";

export default async function renderLogin() {
  const app = document.getElementById("app");
  let mode = "login"; // "login" | "register"
  let error = "";

  function build() {
    app.innerHTML = `
      <div class="auth-page">
        <div class="auth-card">
          <h1>Kanvas</h1>
          <p class="subtitle">Kanban board for your projects</p>
          <div class="auth-tabs">
            <button class="auth-tab ${mode === "login" ? "active" : ""}" data-tab="login">Sign In</button>
            <button class="auth-tab ${mode === "register" ? "active" : ""}" data-tab="register">Register</button>
          </div>
          <form id="auth-form">
            <div class="form-group">
              <label for="username">Username</label>
              <input type="text" id="username" name="username" required minlength="3" autocomplete="username" />
            </div>
            <div class="form-group">
              <label for="password">Password</label>
              <input type="password" id="password" name="password" required minlength="6" autocomplete="${mode === "login" ? "current-password" : "new-password"}" />
            </div>
            ${error ? `<div class="form-error">${error}</div>` : ""}
            <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:8px">
              ${mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    `;

    // Tab switching
    app.querySelectorAll(".auth-tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        mode = btn.dataset.tab;
        error = "";
        build();
      });
    });

    // Form submit
    document.getElementById("auth-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("username").value.trim();
      const password = document.getElementById("password").value;

      try {
        const result = mode === "login"
          ? await api.login(username, password)
          : await api.register(username, password);

        store.set("user", result.user);
        router.navigate("/boards");
      } catch (err) {
        error = err.message;
        build();
      }
    });
  }

  build();
}
