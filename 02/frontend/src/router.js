/**
 * Simple hash-based router.
 *
 * Routes are registered as:
 *   router.on("/boards", renderFn)
 *   router.on("/board/:id", renderFn)  — params available in renderFn({ id })
 *
 * Navigate: router.navigate("/boards")
 * Start:   router.init()
 */

class Router {
  #routes = [];
  #currentCleanup = null;

  on(pattern, render) {
    const names = [];
    const regexStr = pattern.replace(/:(\w+)/g, (_, name) => {
      names.push(name);
      return "([^/]+)";
    });
    this.#routes.push({ pattern, regex: new RegExp(`^${regexStr}$`), names, render });
    return this;
  }

  // Derives the active route, calls its render, cleans up previous
  async resolve() {
    if (this.#currentCleanup) {
      this.#currentCleanup();
      this.#currentCleanup = null;
    }
    const hash = location.hash.slice(1) || "/login";
    for (const route of this.#routes) {
      const m = hash.match(route.regex);
      if (m) {
        const params = {};
        route.names.forEach((name, i) => {
          params[name] = decodeURIComponent(m[i + 1]);
        });
        const maybeCleanup = await route.render(params);
        if (typeof maybeCleanup === "function") {
          this.#currentCleanup = maybeCleanup;
        }
        return;
      }
    }
    // fallback
    navigate("/login");
  }

  navigate(path) {
    location.hash = `#${path}`;
  }

  init() {
    window.addEventListener("hashchange", () => this.resolve());
    this.resolve();
  }
}

const router = new Router();
export default router;
