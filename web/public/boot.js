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
//        - every server push over the WebSocket (see §4)
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
//   3. WebSocket owner.
//      Single WebSocket (/ws) for the page. Two roles:
//        - live-update bridge — dispatch hsm:files-changed,
//          hsm:posts-changed and hsm:deploy DOM events for the parts
//          viewer's per-file refresh and the deploy reload logic.
//        - notifications signal — refetch /api/notifications on
//          every message so the bell + toast track new pushes in
//          real time.
//
//   4. Deploy/version activation check.
//      iOS suspends the WebSocket (§3) whenever the PWA isn't frontmost,
//      so a deploy that ships while it's backgrounded never reaches the
//      page over the socket. On load we record the live commit from
//      GET /api/version; on every activation (focus / pageshow /
//      visibilitychange-to-visible — the events iOS fires for a
//      foregrounded PWA) we re-check it. A changed commit means a new
//      build shipped: the viewer refreshes in place (hsm:deploy, soft),
//      every other page reloads.
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
  // Only for "page just (re)gained focus" events, NOT for live
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

  // ===== 3. WebSocket owner =====
  //
  // Server -> client push transport. Used by both the dev server
  // (file-change broadcasts from chokidar) and the production server
  // (deploy-version handshake on connect + boot-time diff replay).
  //
  // Liveness rests on three mechanisms:
  //   - onclose drives a reconnect loop with exponential backoff
  //   - server-side ping/pong (web/lib/events.js sends a protocol-level
  //     ping every 30s; the browser auto-pongs; a missed pong has the
  //     server terminate() the socket, firing the client's onclose)
  //   - a {type:"ping"} data frame alongside the protocol ping that the
  //     onmessage handler observes as a freshness signal, so
  //     visibility-change catches a silently dead socket even where
  //     readyState lies
  //
  // Wire shape and reconnect behavior:
  //   - On connect, server sends {type:"hello", commit, time, recent?}.
  //   - On the FIRST hello we record `seenCommit`. On any later hello
  //     we treat it as a deploy/reconnect signal and fire hsm:deploy
  //     so the page refreshes whatever it's showing — covers both the
  //     prod-deploy case (new commit) and the dev-blip case (same
  //     commit but we missed broadcasts during the disconnect).
  //   - onclose schedules connectWS again with exponential backoff
  //     (1s, 2s, 4s, capped at 8s).
  //   - visibilitychange/focus/pageshow checks: if readyState isn't
  //     OPEN, force a fresh connect immediately (don't wait for the
  //     backoff timer). If readyState is OPEN but no activity in >60s,
  //     close-and-reconnect — the 30s heartbeat means anything past
  //     that is a stuck socket.
  var ws = null;
  var seenCommit = null;
  var seenRecentCommit = null;
  // Last build commit this page knows is live. Seeded from /api/version on
  // load (and from the WS hello), re-checked on every activation; drives
  // the deploy reload when it changes.
  var bootCommit = null;
  var lastActivityAt = 0;

  // Debug logging + on-screen panel, driven by the "Live-reload debug"
  // setting (localStorage hsmLiveDebug, toggled from /settings). dbg()
  // always keeps a short in-memory tail so flipping the setting on shows
  // recent history; when on it also mirrors to the console and the panel.
  // The panel shows live state (socket health, commit, seconds since the
  // last frame) so it reads true whenever you look — not just the boot
  // lines that scroll past before an inspector can attach.
  var liveLog = [];
  var overlayEl = null;
  var overlayTick = null;

  function liveDebugOn() {
    try { return !!localStorage.getItem("hsmLiveDebug"); } catch (e) { return false; }
  }
  function dbg() {
    var args = [].slice.call(arguments);
    liveLog.push(args.join(" "));
    if (liveLog.length > 40) liveLog.shift();
    if (!liveDebugOn()) return;
    try { console.info.apply(console, ["[hsm-live]"].concat(args)); } catch (e) {}
    renderOverlay();
  }
  function noteCommit(c) { if (c) bootCommit = c; }

  function wsLabel() {
    if (ws && ws.readyState === 1) return "open";
    if (ws && ws.readyState === 0) return "connecting";
    return "closed";
  }
  function renderOverlay() {
    if (!overlayEl) return;
    var label = wsLabel();
    var dot = label === "open" ? "#39d353" : (label === "connecting" ? "#d9a800" : "#f85149");
    var since = lastActivityAt ? Math.round((Date.now() - lastActivityAt) / 1000) + "s" : "—";
    var commit = bootCommit ? String(bootCommit).slice(0, 7) : "—";
    overlayEl.firstChild.innerHTML =
      '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;' +
      'margin-right:6px;vertical-align:middle;background:' + dot + '"></span>' +
      "ws:" + label + " · " + commit + " · " + since;
    overlayEl.lastChild.textContent = liveLog.slice(-8).join("\n");
  }
  function ensureOverlay() {
    if (overlayEl) return;
    if (!document.body) { document.addEventListener("DOMContentLoaded", ensureOverlay, { once: true }); return; }
    overlayEl = document.createElement("div");
    overlayEl.setAttribute("aria-hidden", "true");
    overlayEl.style.cssText =
      "position:fixed;left:8px;z-index:2147483646;max-width:72vw;" +
      "bottom:calc(env(safe-area-inset-bottom,0px) + 8px);" +
      "font:11px/1.35 ui-monospace,Menlo,monospace;color:#e6edf3;" +
      "background:rgba(13,17,23,.86);border:1px solid rgba(240,246,252,.18);" +
      "border-radius:7px;padding:6px 8px;-webkit-backdrop-filter:blur(3px);" +
      "backdrop-filter:blur(3px);";
    var head = document.createElement("div");
    head.style.cssText = "font-weight:600;";
    var log = document.createElement("pre");
    log.style.cssText = "margin:4px 0 0;padding:0;font:inherit;color:#9aa4ad;white-space:pre-wrap;max-height:9em;overflow:auto;";
    overlayEl.appendChild(head);
    overlayEl.appendChild(log);
    // Tap the panel to collapse to just the status line.
    overlayEl.addEventListener("click", function () {
      log.style.display = log.style.display === "none" ? "" : "none";
    });
    document.body.appendChild(overlayEl);
    if (!overlayTick) overlayTick = setInterval(renderOverlay, 1000);
    renderOverlay();
  }
  function removeOverlay() {
    if (overlayTick) { clearInterval(overlayTick); overlayTick = null; }
    if (overlayEl) { overlayEl.remove(); overlayEl = null; }
  }
  // /settings (public/settings.js) flips the panel live through this.
  window.__hsmLiveDebug = {
    set: function (on) {
      try { if (on) localStorage.setItem("hsmLiveDebug", "1"); else localStorage.removeItem("hsmLiveDebug"); } catch (e) {}
      if (on) ensureOverlay(); else removeOverlay();
    },
    isOn: liveDebugOn,
  };
  var reconnectDelayMs = 1000;
  var reconnectMaxMs = 8000;
  var reconnectTimer = null;
  var STALE_MS = 60_000;

  function wsUrl() {
    var proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return proto + "//" + window.location.host + "/ws";
  }

  function onWSMessage(ev) {
    lastActivityAt = Date.now();
    var msg;
    try { msg = JSON.parse(ev.data); } catch (e) { return; }
    if (msg.type === "hello") {
      if (seenCommit === null) {
        seenCommit = msg.commit;
        noteCommit(msg.commit);
        if (msg.recent && msg.recent.commit) seenRecentCommit = msg.recent.commit;
        dbg("hello (first)", msg.commit);
        return;
      }
      // Reconnect: any non-first hello means the connection had
      // dropped; we may have missed broadcasts during the disconnect.
      // Refetch as if it were a fresh deploy. commitChanged distinguishes
      // a real new deploy (prod SHA changed) from a mere socket blip
      // (same commit) — only the former hard-reloads non-viewer pages;
      // the viewer refetches either way to catch missed dev broadcasts.
      var commitChanged = msg.commit !== seenCommit;
      seenCommit = msg.commit;
      noteCommit(msg.commit);
      dbg("hello (reconnect)", msg.commit, "changed=" + commitChanged);
      window.dispatchEvent(new CustomEvent("hsm:deploy", { detail: { commit: msg.commit, reconnect: true, commitChanged: commitChanged } }));
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
    // type === "ping" and anything else: lastActivityAt already bumped at
    // the top of this handler. Log the 30s heartbeat so the panel's
    // "seconds since last frame" reads as a visible pulse.
    if (msg.type === "ping") dbg("ping");
  }

  function clearReconnectTimer() {
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
  }

  function connectWS() {
    clearReconnectTimer();
    if (ws) {
      try { ws.close(); } catch (e) {}
      ws = null;
    }
    try {
      ws = new WebSocket(wsUrl());
    } catch (e) {
      // Construction itself failed (rare — bad URL, etc.). Retry on backoff.
      scheduleReconnect();
      return;
    }
    lastActivityAt = Date.now();
    ws.addEventListener("open", function () {
      // Successful handshake. Reset the backoff so the next reconnect
      // starts fast.
      reconnectDelayMs = 1000;
      lastActivityAt = Date.now();
      dbg("ws open", wsUrl());
    });
    ws.addEventListener("message", onWSMessage);
    ws.addEventListener("error", function () {
      // The close event will follow; nothing extra to do here.
      dbg("ws error");
    });
    ws.addEventListener("close", function () {
      ws = null;
      dbg("ws close");
      scheduleReconnect();
    });
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    var delay = reconnectDelayMs;
    reconnectDelayMs = Math.min(reconnectDelayMs * 2, reconnectMaxMs);
    reconnectTimer = setTimeout(function () {
      reconnectTimer = null;
      connectWS();
    }, delay);
  }

  function ensureWSAlive() {
    if (!ws || ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
      // Force an immediate reconnect attempt — don't wait for the
      // backoff timer that scheduled on close.
      reconnectDelayMs = 1000;
      connectWS();
      return;
    }
    if (ws.readyState === WebSocket.OPEN && Date.now() - lastActivityAt > STALE_MS) {
      // OPEN but no bytes in over a minute despite the 30s server
      // heartbeat — socket is silently dead. Close to force onclose +
      // reconnect through the normal path.
      try { ws.close(); } catch (e) {}
    }
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") { ensureWSAlive(); checkVersion(); }
  });
  window.addEventListener("focus", function () { ensureWSAlive(); checkVersion(); });
  window.addEventListener("pageshow", function () { ensureWSAlive(); checkVersion(); });

  // ===== 4. Deploy/version activation check (see header §4) =====
  //
  // /api/version is cheap and never cached. The first call seeds
  // bootCommit; later calls (one per activation) compare. A changed
  // commit means a new build shipped: the viewer claims the refresh via
  // window.__hsmDeploySoft + hsm:deploy, every other page falls through
  // to the reload listener below.
  var versionInFlight = false;
  function checkVersion() {
    if (versionInFlight) return;
    versionInFlight = true;
    fetch("/api/version", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        versionInFlight = false;
        var commit = d && d.commit ? d.commit : null;
        if (!commit) return;
        if (bootCommit === null) { bootCommit = commit; dbg("version seeded", commit); return; }
        if (commit === bootCommit) return;
        dbg("version changed", bootCommit, "->", commit);
        // Advance first so repeated activations don't re-fire while a soft
        // viewer refresh is still settling.
        bootCommit = commit;
        window.dispatchEvent(new CustomEvent("hsm:deploy", {
          detail: { commit: commit, reconnect: false, commitChanged: true, source: "version" },
        }));
      })
      .catch(function () { versionInFlight = false; });
  }

  // Default deploy/posts handler for any page that hasn't claimed the
  // refresh itself. The viewer sets window.__hsmDeploySoft (it refreshes
  // in place, preserving camera + open modal); content pages reload.
  window.addEventListener("hsm:deploy", function (e) {
    if (window.__hsmDeploySoft) return;
    if (e.detail && e.detail.commitChanged === false) return; // socket blip, not a deploy
    dbg("deploy -> reload");
    window.location.reload();
  });
  window.addEventListener("hsm:posts-changed", function () {
    if (window.__hsmDeploySoft) return;
    dbg("posts-changed -> reload");
    window.location.reload();
  });

  checkVersion();  // seed bootCommit now, independent of the socket
  connectWS();
  if (liveDebugOn()) ensureOverlay();  // show the debug panel if the setting is on
})();
