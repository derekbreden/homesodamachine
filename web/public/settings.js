// Settings-page boot script loaded via <script src="/settings.js" defer>
// from lib/settings.js. Three rows:
//   1. Dev mode — instant localStorage flip + html.dev-mode class so the
//      public nav's Prints / Diagrams links appear/disappear right away.
//   2. Notifications — PWA-only. Lazy-imports Firebase Messaging,
//      registers the SW, requests permission, and POSTs files=["*"] for
//      a global subscription. Off DELETEs the subscription.
//   3. Live-reload debug — dev-mode-only. Flips boot.js's on-screen panel
//      via window.__hsmLiveDebug (localStorage hsmLiveDebug).
//   4. Edition — dev-mode-only. Picks which machine's content root the
//      viewer serves (lib/editions.js) via localStorage hsmEdition + the
//      mirrored hsmEdition cookie the server reads.

(function () {
  // --- Dev mode (always shown) ---
  // Persist to localStorage and toggle html.dev-mode so the public nav's
  // Prints / Diagrams links appear/disappear immediately. The same flag is
  // applied by an inline head script on every page (see public/boot.js)
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
    syncLiveDebugRow();
    syncEditionRow();
  });

  // --- Live-reload debug (dev-mode only) ---
  // Toggles boot.js's on-screen panel (socket health, build commit, deploy
  // events). Hidden unless dev mode is on, since it's a developer
  // diagnostic. window.__hsmLiveDebug.set flips the panel without a reload;
  // the localStorage fallback covers the panel appearing on next load if
  // boot.js hasn't run yet.
  const liveDebugRow = document.getElementById("row-livedebug");
  const liveDebugToggle = document.getElementById("livedebug-toggle");
  function liveDebugIsOn() {
    try { return !!localStorage.getItem("hsmLiveDebug"); } catch (e) { return false; }
  }
  function syncLiveDebugRow() {
    liveDebugRow.hidden = !document.documentElement.classList.contains("dev-mode");
    const on = liveDebugIsOn();
    liveDebugToggle.classList.toggle("on", on);
    liveDebugToggle.setAttribute("aria-checked", on ? "true" : "false");
  }
  syncLiveDebugRow();
  liveDebugToggle.addEventListener("click", () => {
    const next = !liveDebugIsOn();
    if (window.__hsmLiveDebug) {
      window.__hsmLiveDebug.set(next);
    } else {
      try {
        if (next) localStorage.setItem("hsmLiveDebug", "1");
        else localStorage.removeItem("hsmLiveDebug");
      } catch (e) {}
    }
    syncLiveDebugRow();
  });

  // --- Edition (dev-mode only) ---
  // Picks which machine the viewer shows — one content root each. The segments
  // are rendered server-side from lib/editions.js, so this code never names an
  // edition: it reads the ids off the buttons. localStorage hsmEdition is the
  // source of truth; the pre-paint head script (shell.js) mirrors it into the
  // hsmEdition cookie the server reads to pick the root. We also write the
  // cookie here so the choice is live on the next viewer navigation without
  // waiting for that script to re-run. Hidden unless dev mode is on, like the
  // live-debug row.
  const editionRow = document.getElementById("row-edition");
  const editionHelp = document.getElementById("edition-help");
  const segments = Array.from(document.querySelectorAll("#edition-segmented .segment"));
  const editionIds = segments.map((b) => b.dataset.edition);
  const defaultEdition = editionIds[0];
  function currentEdition() {
    let id = null;
    try { id = localStorage.getItem("hsmEdition"); } catch (e) {}
    return editionIds.indexOf(id) === -1 ? defaultEdition : id;
  }
  function syncEditionRow() {
    editionRow.hidden = !document.documentElement.classList.contains("dev-mode");
    const active = currentEdition();
    for (const b of segments) {
      const on = b.dataset.edition === active;
      b.setAttribute("aria-checked", on ? "true" : "false");
      if (on) editionHelp.textContent = b.dataset.help || "";
    }
  }
  syncEditionRow();
  for (const b of segments) {
    b.addEventListener("click", () => {
      const value = b.dataset.edition;
      try { localStorage.setItem("hsmEdition", value); } catch (e) {}
      try { document.cookie = "hsmEdition=" + value + ";path=/;max-age=31536000;samesite=lax"; } catch (e) {}
      for (const id of editionIds) {
        document.documentElement.classList.toggle("edition-" + id, id === value);
      }
      syncEditionRow();
    });
  }

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
    // Stash token so the home-page cold-launch redirect script can identify
    // this client to /api/pending-nav. Only meaningful once the user has
    // successfully subscribed at least once.
    try { localStorage.setItem("hsmFcmToken", token); } catch {}
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
    // Drop the localStorage marker so the nav bell hides on next paint.
    // The token is still recoverable via getToken() if the user toggles
    // notifications back on; we just don't want a stale "you have an
    // inbox" affordance for a user who's no longer subscribed.
    try { localStorage.removeItem("hsmFcmToken"); } catch {}
    document.documentElement.classList.remove("notifs-enabled");
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
})();
