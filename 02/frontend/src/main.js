/**
 * Kanvas — Frontend Entry Point
 */

import "./styles/board.css";
import router from "./router.js";
import store from "./state.js";
import * as api from "./api.js";
import renderLogin from "./views/login.js";
import renderBoardList from "./views/board-list.js";
import renderBoardDetail from "./views/board-detail.js";

// Define routes
router.on("/login", async () => {
  const session = api.getSession();
  if (session) {
    router.navigate("/boards");
    return;
  }
  renderLogin();
});

router.on("/boards", async () => {
  const session = api.getSession();
  if (!session) {
    router.navigate("/login");
    return;
  }
  renderBoardList();
});

router.on("/board/:id", async (params) => {
  const session = api.getSession();
  if (!session) {
    router.navigate("/login");
    return;
  }
  renderBoardDetail(params);
});

// Initialize session from cookie, then start router
async function start() {
  await api.initSession();
  router.init();
}
start();
