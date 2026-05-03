// Settings page — reachable via the gear in the top-right of every nav.
//
// Two rows, both rendered with the .ios-toggle pill from shell.js:
//   1. Dev mode — always visible. Toggling on adds Prints / Diagrams to
//      the public nav (sets html.dev-mode + persists in localStorage).
//      No async work; the slide is instant.
//   2. Notifications — only visible inside the installed PWA, since iOS
//      web push only works in standalone mode and the toggle is inert
//      otherwise. Same FCM-backed flow that lived on /dev/ before:
//      first-time enable shows a warning modal, requests permission,
//      registers the SW, gets a token, POSTs files=["*"] so any STEP
//      change pushes; turning off DELETEs the subscription.

import { renderHead, renderNav, renderFooter } from "./shell.js";

const PAGE_STYLES = `
.wrap {
  flex: 1;
  width: 100%;
  max-width: 36rem;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
}
header.page { margin-bottom: 1.5rem; }
h1 {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.02em;
}
.modal-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.modal-backdrop.open { display: flex; }
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  max-width: 420px;
  width: 100%;
  padding: 20px;
  color: var(--text);
}
.modal h2 { font-size: 17px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.modal p { font-size: 14px; line-height: 1.5; margin-bottom: 10px; color: var(--text-2); }
.modal p em { font-style: normal; color: var(--text); font-weight: 600; }
.modal .actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
.modal button {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}
.modal button:hover { background: var(--border); }
.modal button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.modal button.primary:hover { background: #5599ff; border-color: #5599ff; }
`;

const BODY = `<div class="wrap">
  <header class="page"><h1>Settings</h1></header>

  <div class="settings-card">
    <div class="setting-row" id="row-devmode">
      <div>
        <div class="setting-label">Dev mode</div>
        <div class="setting-help">Show Prints and Diagrams in the navigation.</div>
      </div>
      <button id="devmode-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Dev mode"></button>
    </div>

    <div class="setting-row" id="row-notifs" hidden>
      <div>
        <div class="setting-label">Notifications</div>
        <div class="setting-help">Push when STEP files or posts change.</div>
      </div>
      <button id="notifs-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Notifications">
        <span class="ios-toggle-spinner"></span>
      </button>
    </div>
  </div>
</div>

<div id="subscribe-modal" class="modal-backdrop" role="dialog" aria-modal="true">
  <div class="modal">
    <h2>Notify on every update?</h2>
    <p>This will notify on <em>every</em> update, and there are times when this happens several times an hour.</p>
    <div class="actions">
      <button id="subscribe-cancel" type="button">Cancel</button>
      <button id="subscribe-confirm" type="button" class="primary">Subscribe</button>
    </div>
  </div>
</div>

<script>
  // --- Dev mode (always shown) ---
  // Persist to localStorage and toggle html.dev-mode so the public nav's
  // Prints / Diagrams links appear/disappear immediately. The same flag is
  // applied by an inline head script on every page (see shell.js HEAD_TAGS)
  // before first paint, so reloading any page picks it up without a flash.
  const devToggle = document.getElementById("devmode-toggle");
  function syncDevToggle() {
    const on = document.documentElement.classList.contains("dev-mode");
    devToggle.classList.toggle("on", on);
    devToggle.setAttribute("aria-checked", on ? "true" : "false");
  }
  syncDevToggle();
  devToggle.addEventListener("click", () => {
    const next = !document.documentElement.classList.contains("dev-mode");
    document.documentElement.classList.toggle("dev-mode", next);
    try { localStorage.setItem("devMode", next ? "1" : "0"); } catch {}
    syncDevToggle();
  });

  // --- Notifications (PWA-only) ---
  function pushSupported() {
    return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  }
  function isStandalone() {
    return window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone === true;
  }

  const notifsRow = document.getElementById("row-notifs");
  const notifsToggle = document.getElementById("notifs-toggle");
  const subscribeModal = document.getElementById("subscribe-modal");

  const pushState = {
    config: null,
    messaging: null,
    swRegistration: null,
    token: null,
    subscribedAll: false,
    available: false,
  };

  async function loadFirebaseConfig() {
    try {
      const r = await fetch("/api/firebase-config");
      const cfg = await r.json();
      if (!cfg.apiKey || !cfg.vapidKey) return null;
      return cfg;
    } catch {
      return null;
    }
  }

  async function attachMessaging() {
    if (pushState.messaging) return;
    const [{ initializeApp }, { getMessaging, getToken, isSupported }] = await Promise.all([
      import("https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js"),
      import("https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging.js"),
    ]);
    if (!(await isSupported())) throw new Error("FCM not supported in this browser");
    const app = initializeApp({
      apiKey: pushState.config.apiKey,
      authDomain: pushState.config.authDomain,
      projectId: pushState.config.projectId,
      storageBucket: pushState.config.storageBucket,
      messagingSenderId: pushState.config.messagingSenderId,
      appId: pushState.config.appId,
    });
    const reg = await navigator.serviceWorker.register("/firebase-messaging-sw.js", { scope: "/" });
    await navigator.serviceWorker.ready;
    pushState.swRegistration = reg;
    pushState.messaging = getMessaging(app);
    const token = await getToken(pushState.messaging, {
      vapidKey: pushState.config.vapidKey,
      serviceWorkerRegistration: reg,
    });
    if (!token) throw new Error("Empty FCM token");
    pushState.token = token;
  }

  async function syncSubscriptionFromServer() {
    if (!pushState.token) return;
    const r = await fetch("/api/push/subscription?token=" + encodeURIComponent(pushState.token));
    const j = await r.json();
    pushState.subscribedAll = (j.files || []).includes("*");
  }

  async function persistSubscribed() {
    if (!pushState.token) return;
    await fetch("/api/push/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: pushState.token, files: ["*"] }),
    });
  }

  async function persistUnsubscribed() {
    if (!pushState.token) return;
    await fetch("/api/push/unsubscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: pushState.token }),
    });
  }

  function refreshNotifs() {
    notifsToggle.classList.toggle("on", pushState.subscribedAll);
    notifsToggle.setAttribute("aria-checked", pushState.subscribedAll ? "true" : "false");
  }

  function showSubscribeModal() {
    return new Promise((resolve) => {
      subscribeModal.classList.add("open");
      const onCancel = () => { cleanup(); resolve(false); };
      const onConfirm = () => { cleanup(); resolve(true); };
      function cleanup() {
        subscribeModal.classList.remove("open");
        document.getElementById("subscribe-cancel").removeEventListener("click", onCancel);
        document.getElementById("subscribe-confirm").removeEventListener("click", onConfirm);
        subscribeModal.removeEventListener("click", onBackdrop);
      }
      function onBackdrop(e) { if (e.target === subscribeModal) onCancel(); }
      document.getElementById("subscribe-cancel").addEventListener("click", onCancel);
      document.getElementById("subscribe-confirm").addEventListener("click", onConfirm);
      subscribeModal.addEventListener("click", onBackdrop);
    });
  }

  async function toggleNotifications() {
    if (!pushState.available) return;

    if (pushState.subscribedAll) {
      pushState.subscribedAll = false;
      refreshNotifs();
      persistUnsubscribed().catch((e) => console.warn("unsubscribe error:", e));
      return;
    }

    const confirmed = await showSubscribeModal();
    if (!confirmed) return;

    if (Notification.permission === "granted" && pushState.token) {
      pushState.subscribedAll = true;
      refreshNotifs();
      persistSubscribed().catch((e) => {
        pushState.subscribedAll = false;
        refreshNotifs();
        alert("Couldn't enable notifications: " + e.message);
      });
      return;
    }

    notifsToggle.classList.add("loading");
    notifsToggle.disabled = true;
    try {
      if (Notification.permission !== "granted") {
        const perm = await Notification.requestPermission();
        if (perm !== "granted") {
          alert("Notifications were blocked. Enable them in your browser/PWA settings to subscribe.");
          return;
        }
      }
      await attachMessaging();
      await persistSubscribed();
      pushState.subscribedAll = true;
    } catch (e) {
      alert("Couldn't enable notifications: " + e.message);
    } finally {
      notifsToggle.classList.remove("loading");
      notifsToggle.disabled = false;
      refreshNotifs();
    }
  }

  notifsToggle.addEventListener("click", toggleNotifications);

  (async function initNotifsRow() {
    if (!pushSupported() || !isStandalone()) return;
    const cfg = await loadFirebaseConfig();
    if (!cfg) return;
    pushState.config = cfg;
    pushState.available = true;
    notifsRow.hidden = false;
    if (Notification.permission === "granted") {
      try {
        await attachMessaging();
        await syncSubscriptionFromServer();
      } catch (e) {
        console.warn("FCM silent attach failed:", e.message);
      }
    }
    refreshNotifs();
  })();
</script>
`;

export function mountSettingsRoutes(app, { surface = "public" } = {}) {
  app.get("/settings", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.send(
      renderHead({
        title: "Settings · Home Soda Machine",
        pageStyles: PAGE_STYLES,
      }) +
      renderNav({ surface, active: "settings" }) +
      BODY +
      renderFooter(),
    );
  });
}
