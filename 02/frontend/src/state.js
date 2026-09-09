/**
 * Simple reactive state store.
 *
 * Usage:
 *   import store from "./state.js";
 *   store.user = { id: 1, username: "alice" };   // triggers subscribers
 *   store.subscribe(fn);                          // fn called on any change
 *   store.subscribe("user", fn);                  // fn called when "user" changes
 */

class Store {
  #data = {};
  #subscribers = new Map(); // key -> Set<fn>  (key = "*" means all)

  subscribe(key, fn) {
    if (typeof key === "function") {
      fn = key;
      key = "*";
    }
    if (!this.#subscribers.has(key)) {
      this.#subscribers.set(key, new Set());
    }
    this.#subscribers.get(key).add(fn);
    return () => this.#subscribers.get(key)?.delete(fn);
  }

  notify(key) {
    const fns = this.#subscribers.get(key);
    if (fns) for (const fn of fns) fn(this.#data[key]);
    const all = this.#subscribers.get("*");
    if (all) for (const fn of all) fn(key, this.#data[key]);
  }

  set(key, value) {
    this.#data[key] = value;
    this.notify(key);
    return value;
  }

  get(key) {
    return this.#data[key];
  }

  get data() {
    return this.#data;
  }
}

const store = new Store();
export default store;
