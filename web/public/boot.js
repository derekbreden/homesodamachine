// Per-page boot script loaded on every server-rendered page via the
// <script src="/boot.js" defer> tag in lib/shell.js HEAD_TAGS. Three
// responsibilities, run in this order:
//
//   1. SW → page navigate-message bridge.
//      The Firebase messaging SW posts {type:"navigate", url} after
//      activate (so a deploy can force open clients to reload onto
//      the new shell + HEAD_TAGS) and on notificationclick for
//      Chrome desktop / Android (iOS PWA never reaches that path,
//      but the listener is harmless on iOS).
//
//   2. Notifications inbox state + bell + toast + warm-tap redirect.
//      The server-side inbox (lib/notifications.js) is the single
//      source of truth: GET /api/notifications returns the user's
//      list (token-keyed, 7-day window, with seen state). We refetch
//      on:
//        - initial page load
//        - window.focus / pageshow / visibilitychange-to-visible
//          (covers iOS PWA warm-tap; the only event iOS fires when
//          the user taps the dock icon to foreground)
//        - every SSE message from /api/events
//      State drives three things:
//        a. .has-unread class on .nav-bell (CSS shows the accent dot).
//        b. The bottom toast: 0 unread → none; 1 → kind-specific
//           (tap = navigate, ✕ = mark seen); 2+ → aggregate ("N
//           unread", body = first 3 titles, tap → /notifications, ✕
//           = mark all seen).
//        c. Warm-tap auto-redirect: if a focus/pageshow event
//           activates the page and exactly one row is unread,
//           navigate to it (and mark seen). 2+ unread → leave it
//           for the aggregate toast to disambiguate.
//      Cold-launch (?n=<id>): iOS opens the PWA at the FCM link
//      directly, so the page already shows the target. We mark
//      that one row seen on load. URL stays as-is.
//
//   3. SSE owner.
//      Single EventSource for the page. Two roles:
//        - live-update bridge — dispatch hsm:files-changed and
//          hsm:deploy DOM events for the parts viewer's per-file
//          refresh logic.
//        - notifications signal — refetch /api/notifications on
//          every message so the bell + toast track new pushes in
//          real time.
//
// What's NOT in here: the synchronous pre-paint CSS class flip for
// dev-mode and notifs-enabled. That has to run during <head> parse
// (before first paint) or the public nav flashes the dev links and
// the bell flashes hidden. The flip stays inline in lib/shell.js;
// this module is deferred (module scripts run after parse).
//
// State ownership note: the notifications mirror lives in module-
// local `state` here, not on window. window.__hsm is reserved for
// the /3d viewer's Puppeteer escape hatch (see viewer-body.html);
// these two used to collide and the viewer's reassignment clobbered
// the notification mirror until the next /api/notifications fetch
// re-populated state.items.

(function () {
  // ===== 1. SW → page navigate bridge =====
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.addEventListener("message", function (e) {
      if (!(e.data && e.data.type === "navigate" && e.data.url)) return;
      try {
        var u = new URL(e.data.url, window.location.origin);
        if (u.href === window.location.href) {
          window.location.reload();
        } else if (
          u.pathname === window.location.pathname &&
          u.search === window.location.search
        ) {
          window.location.hash = u.hash;
          window.location.reload();
        } else {
          window.location.replace(u.href);
        }
      } catch (err) {
        window.location.href = e.data.url;
      }
    });
  }

  // ===== 2. Notifications state + UI =====
  var state = { items: [], unread: 0 };

  function getToken() {
    try {
      return localStorage.getItem("hsmFcmToken") || "";
    } catch (e) {
      return "";
    }
  }

  function postSeen(payload) {
    var url = "/api/notifications/seen";
    var body = JSON.stringify(payload);
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(url, new Blob([body], { type: "application/json" }));
        return Promise.resolve();
      }
    } catch (e) {}
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body,
      keepalive: true,
    }).catch(function () {});
  }

  function recompute() {
    var unread = 0;
    for (var i = 0; i < state.items.length; i++) {
      if (!state.items[i].seen) unread++;
    }
    state.unread = unread;
    document.documentElement.classList.toggle("notifs-enabled", !!getToken());
    var bell = document.querySelector(".nav-bell");
    if (bell) bell.classList.toggle("has-unread", unread > 0);
    window.dispatchEvent(
      new CustomEvent("hsm:notifications-updated", {
        detail: { items: state.items.slice(), unread: unread },
      }),
    );
  }

  function fetchNotifications() {
    var t = getToken();
    if (!t) {
      state.items = [];
      recompute();
      return Promise.resolve();
    }
    return fetch("/api/notifications?token=" + encodeURIComponent(t))
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (d) {
        state.items = (d && d.items) || [];
        recompute();
      })
      .catch(function () {});
  }

  function markSeenLocal(ids) {
    var idSet = {};
    for (var i = 0; i < ids.length; i++) idSet[String(ids[i])] = true;
    for (var j = 0; j < state.items.length; j++) {
      if (idSet[String(state.items[j].id)]) state.items[j].seen = true;
    }
    recompute();
  }
  function markAllSeenLocal() {
    for (var j = 0; j < state.items.length; j++) state.items[j].seen = true;
    recompute();
  }
  function markSeen(ids) {
    markSeenLocal(ids);
    return postSeen({ token: getToken(), ids: ids });
  }
  function markAllSeen() {
    markAllSeenLocal();
    return postSeen({ token: getToken(), all: true });
  }

  // ----- Toast -----
  function dismissToast() {
    var t = document.querySelector(".hsm-toast");
    if (t) t.remove();
  }
  function showToast(opts) {
    dismissToast();
    var place = function () {
      var toast = document.createElement("div");
      toast.className = "hsm-toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      var link = document.createElement("a");
      link.className = "hsm-toast-link";
      link.href = opts.url;
      if (opts.onTap) link.addEventListener("click", opts.onTap);
      var title = document.createElement("div");
      title.className = "hsm-toast-title";
      title.textContent = opts.title;
      var body = document.createElement("div");
      body.className = "hsm-toast-body";
      body.textContent = opts.body || "";
      link.appendChild(title);
      link.appendChild(body);
      var close = document.createElement("button");
      close.className = "hsm-toast-close";
      close.setAttribute("aria-label", "Dismiss");
      close.textContent = "✕";
      close.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (opts.onDismiss) opts.onDismiss();
        toast.remove();
      });
      toast.appendChild(link);
      toast.appendChild(close);
      document.body.appendChild(toast);
    };
    if (document.body) place();
    else document.addEventListener("DOMContentLoaded", place, { once: true });
  }

  // Re-render toast based on current state. Idempotent: same state →
  // same toast (replaced, not duplicated).
  function renderToast() {
    var unread = [];
    for (var i = 0; i < state.items.length; i++) {
      if (!state.items[i].seen) unread.push(state.items[i]);
    }
    if (unread.length === 0) {
      dismissToast();
      return;
    }
    if (unread.length === 1) {
      var n = unread[0];
      showToast({
        title: n.title,
        body: n.body,
        url: n.url,
        onTap: function () { markSeen([n.id]); },
        onDismiss: function () { markSeen([n.id]); },
      });
    } else {
      var head = unread.slice(0, 3).map(function (n) { return n.title; }).join(", ");
      var body = unread.length > 3 ? head + ", …" : head;
      showToast({
        title: unread.length + " unread",
        body: body,
        url: "/notifications",
        onTap: null,
        onDismiss: function () { markAllSeen(); },
      });
    }
  }
  window.addEventListener("hsm:notifications-updated", renderToast);

  // ----- Warm-tap auto-redirect -----
  // Only for "page just (re)gained focus" events, NOT for SSE-driven
  // refetches (during active use the user is in the middle of
  // something; toast is the right surface there). 1 unread → redirect
  // to that file. 2+ → leave it; the toast offers /notifications.
  function maybeAutoRedirect() {
    var unread = [];
    for (var i = 0; i < state.items.length; i++) {
      if (!state.items[i].seen) unread.push(state.items[i]);
    }
    if (unread.length !== 1) return;
    var n = unread[0];
    try {
      var u = new URL(n.url, window.location.origin);
      if (u.href === window.location.href) return;
      // Mark seen with sendBeacon-flavored postSeen so the request
      // survives the unload triggered by replace().
      postSeen({ token: getToken(), ids: [n.id] });
      window.location.replace(u.href);
    } catch (e) {}
  }
  function refetchAndMaybeRedirect() {
    fetchNotifications().then(maybeAutoRedirect);
  }

  // ----- Cold-launch ?n=<id> mark-as-seen -----
  // iOS opens PWAs at the FCM link directly on cold launch, so when the
  // page boots and ?n=<id> is in the query, mark that one read. Server
  // is idempotent on already-seen rows.
  try {
    var qs = new URLSearchParams(window.location.search);
    var nId = qs.get("n");
    if (nId && /^\d+$/.test(nId) && getToken()) {
      postSeen({ token: getToken(), ids: [nId] });
    }
  } catch (e) {}

  // ----- Initial fetch + activation hooks -----
  refetchAndMaybeRedirect();
  window.addEventListener("focus", refetchAndMaybeRedirect);
  window.addEventListener("pageshow", refetchAndMaybeRedirect);
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") refetchAndMaybeRedirect();
  });

  // ===== 3. SSE owner =====
  // EventSource has built-in retry, but two failure modes need explicit
  // help:
  //   1. After an auto-reconnect, the server's second `hello` carries
  //      the SAME commit fingerprint as the first (especially in dev
  //      where it's the constant "dev"). With the old "only fire
  //      hsm:deploy on commit change" logic, that silently swallowed
  //      every files-changed event the client missed during the
  //      disconnect window — the user sees no live reload until they
  //      manually refresh. Now: any non-first hello fires hsm:deploy
  //      so the page refreshes whatever it's showing.
  //   2. Safari (and rarely other browsers) can keep an EventSource in
  //      OPEN state after the underlying TCP connection has actually
  //      died — no error event, no auto-reconnect. When the page
  //      regains focus, we check the readyState AND the freshness of
  //      the last message; if either looks stale, force a reconnect.
  //
  // The server keeps connections alive with a 30s :keepalive comment
  // (see web/lib/events.js). Any message — data or comment — counts
  // as activity; the 60s stale threshold is generous on top of that.
  if ("EventSource" in window) {
    var es = null;
    var seenCommit = null;
    var seenRecentCommit = null;
    var lastActivityAt = 0;
    var STALE_MS = 60_000;

    function onSSEMessage(ev) {
      lastActivityAt = Date.now();
      var msg;
      try { msg = JSON.parse(ev.data); } catch (e) { return; }
      if (msg.type === "hello") {
        if (seenCommit === null) {
          seenCommit = msg.commit;
          if (msg.recent && msg.recent.commit) seenRecentCommit = msg.recent.commit;
          return;
        }
        // Reconnect — server fingerprint may or may not have changed
        // (it does on prod deploy; in dev it's always "dev"). Either
        // way, the client missed any broadcasts during the disconnect,
        // so refetch as if it were a fresh deploy.
        seenCommit = msg.commit;
        window.dispatchEvent(new CustomEvent("hsm:deploy", { detail: { commit: msg.commit, reconnect: true } }));
        if (msg.recent && msg.recent.commit && msg.recent.commit !== seenRecentCommit) {
          seenRecentCommit = msg.recent.commit;
          if (msg.recent.files) {
            window.dispatchEvent(new CustomEvent("hsm:files-changed", { detail: { files: msg.recent.files } }));
          }
          if (msg.recent.posts) {
            window.dispatchEvent(new CustomEvent("hsm:posts-changed", { detail: { posts: msg.recent.posts } }));
          }
        }
        fetchNotifications();
        return;
      }
      if (msg.type === "files-changed") {
        window.dispatchEvent(new CustomEvent("hsm:files-changed", { detail: { files: msg.files || [] } }));
        fetchNotifications();
        return;
      }
      if (msg.type === "posts-changed") {
        window.dispatchEvent(new CustomEvent("hsm:posts-changed", { detail: { posts: msg.posts || [] } }));
        fetchNotifications();
        return;
      }
      // type === "ping" and anything else: lastActivityAt already
      // bumped at the top of this handler, nothing else to do.
    }

    function connectSSE() {
      if (es) {
        try { es.close(); } catch (e) {}
      }
      es = new EventSource("/api/events");
      lastActivityAt = Date.now();
      es.addEventListener("message", onSSEMessage);
      // The browser's built-in retry handles transient errors; we log
      // for debugging and trust EventSource to come back. The
      // visibility-change check below handles the case where it
      // doesn't.
      es.addEventListener("error", function () {
        // EventSource transitions: 0=CONNECTING, 1=OPEN, 2=CLOSED.
        // No-op here — we only listen so silent errors are visible in
        // devtools network panel if needed.
      });
    }

    function ensureSSEAlive() {
      if (!es || es.readyState === EventSource.CLOSED) {
        connectSSE();
        return;
      }
      if (es.readyState === EventSource.OPEN && Date.now() - lastActivityAt > STALE_MS) {
        // OPEN but no bytes in over a minute despite the 30s server
        // keepalive — connection is silently dead. Force-reconnect.
        connectSSE();
      }
    }

    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") ensureSSEAlive();
    });
    window.addEventListener("focus", ensureSSEAlive);
    window.addEventListener("pageshow", ensureSSEAlive);

    connectSSE();
  }
})();
