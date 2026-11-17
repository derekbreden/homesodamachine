// Reconnects the live viewer and checks for deploys when a page returns to the foreground.
import { HSM_EVENTS } from "/contracts/client-events.js";
import { WS } from "/contracts/ws-frames.js";

(function () {
  // WebSocket updates
  //
  // The server sends deploy versions and changed artifact paths.
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
    if (msg.type === WS.HELLO) {
      if (seenCommit === null) {
        seenCommit = msg.commit;
        if (msg.commit) bootCommit = msg.commit;
        if (msg.recent && msg.recent.commit) seenRecentCommit = msg.recent.commit;
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
      if (msg.commit) bootCommit = msg.commit;
      window.dispatchEvent(new CustomEvent(HSM_EVENTS.DEPLOY, { detail: { commit: msg.commit, reconnect: true, commitChanged: commitChanged } }));
      if (msg.recent && msg.recent.commit && msg.recent.commit !== seenRecentCommit) {
        seenRecentCommit = msg.recent.commit;
        if (msg.recent.files) {
          window.dispatchEvent(new CustomEvent(HSM_EVENTS.FILES_CHANGED, { detail: { files: msg.recent.files } }));
        }
      }
      return;
    }
    if (msg.type === WS.FILES_CHANGED) {
      window.dispatchEvent(new CustomEvent(HSM_EVENTS.FILES_CHANGED, { detail: { files: msg.files || [] } }));
      return;
    }
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
    });
    ws.addEventListener("message", onWSMessage);
    ws.addEventListener("close", function () {
      ws = null;
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

  // Deploy version on activation
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
        if (bootCommit === null) { bootCommit = commit; return; }
        if (commit === bootCommit) return;
        // Advance first so repeated activations don't re-fire while a soft
        // viewer refresh is still settling.
        bootCommit = commit;
        window.dispatchEvent(new CustomEvent(HSM_EVENTS.DEPLOY, {
          detail: { commit: commit, reconnect: false, commitChanged: true, source: "version" },
        }));
      })
      .catch(function () { versionInFlight = false; });
  }

  // Default deploy handler for any page that hasn't claimed the refresh
  // itself. The viewer sets window.__hsmDeploySoft (it refreshes in place,
  // preserving camera + open modal); content pages reload.
  window.addEventListener(HSM_EVENTS.DEPLOY, function (e) {
    if (window.__hsmDeploySoft) return;
    if (e.detail && e.detail.commitChanged === false) return; // socket blip, not a deploy
    window.location.reload();
  });

  checkVersion();  // seed bootCommit now, independent of the socket
  connectWS();
})();
