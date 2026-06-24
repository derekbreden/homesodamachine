// WebSocket transport for server -> client push.
//
// Two consumers:
//   - Dev server: file-change broadcasts from chokidar (per-save).
//   - Production server: deploy-version handshake + boot-time hash-diff
//     replay so a client whose old connection died during the container
//     swap gets the change list it missed.
//
// Liveness: the client reconnects on close with backoff; the server
// pings every 30s and terminates a socket that misses its pong. A client
// that reconnects catches up on anything it missed via the `recent`
// snapshot on the next hello (below).
//
// Wire shape (JSON over text frames):
//   server -> client:
//     {type: "hello", commit, time, recent?}          — sent on every connect
//     {type: "ping", t}                                — every 30s, used as a heartbeat
//     {type: "files-changed", commit, files: [...]}   — broadcast on file change
//     {type: "posts-changed", commit, posts: [...]}   — broadcast on post change
//   client -> server: none (the boot.js client never sends).
//
// `recent` snapshot: latest boot-diff result, set by server.js after
// the production hash-diff completes. Piggy-backed onto every hello so
// a client that reconnects after a deploy gets the change list its
// previous connection missed. The client dedupes by recent.commit so a
// stable connection that already saw the deploy ignores it.

import { WebSocketServer } from "ws";

export function mountEvents(server, { commit = "unknown" } = {}) {
  const wss = new WebSocketServer({ server, path: "/ws" });
  let recent = null;

  function setRecent(snapshot) {
    const hasFiles = Array.isArray(snapshot?.files) && snapshot.files.length > 0;
    const hasPosts = Array.isArray(snapshot?.posts) && snapshot.posts.length > 0;
    recent = (hasFiles || hasPosts) ? snapshot : null;
  }

  function send(ws, msg) {
    if (ws.readyState !== 1) return;
    try {
      ws.send(JSON.stringify(msg));
    } catch {
      // socket may have just closed; the close handler will clean up.
    }
  }

  function broadcast(msg) {
    const payload = JSON.stringify(msg);
    for (const ws of wss.clients) {
      if (ws.readyState !== 1) continue;
      try { ws.send(payload); } catch {}
    }
  }

  wss.on("connection", (ws) => {
    // isAlive flag drives the ping/pong dead-connection detector below.
    // Set true on connect, flipped to false before each ping; the pong
    // handler flips it back to true. If the next ping finds it still
    // false, the socket is dead and we terminate.
    ws.isAlive = true;
    ws.on("pong", () => { ws.isAlive = true; });

    const helloMsg = { type: "hello", commit, time: Date.now() };
    if (recent) helloMsg.recent = recent;
    send(ws, helloMsg);
  });

  // Heartbeat. Every 30 seconds:
  //   1. Send a ping frame at the protocol level (the browser auto-pongs;
  //      ws.isAlive is set true on pong receipt above).
  //   2. Send a {type:"ping"} data frame so the client's onmessage handler
  //      can also observe a heartbeat — handy as a freshness check on
  //      visibility-change for boot.js. (Belt and suspenders; the
  //      protocol-level ping is the primary liveness signal.)
  //   3. If ws.isAlive is still false from the previous round (no pong
  //      came back), terminate the socket — the client's WebSocket will
  //      see a close event and reconnect.
  const heartbeat = setInterval(() => {
    for (const ws of wss.clients) {
      if (ws.isAlive === false) {
        try { ws.terminate(); } catch {}
        continue;
      }
      ws.isAlive = false;
      try {
        ws.ping();
        send(ws, { type: "ping", t: Date.now() });
      } catch {}
    }
  }, 30_000);
  // Don't keep the Node event loop alive just for the heartbeat —
  // server.close() in tests can hang otherwise. The heartbeat only
  // exists to detect dead clients on an already-running server.
  heartbeat.unref?.();

  wss.on("close", () => clearInterval(heartbeat));

  // On graceful shutdown (Render sends SIGTERM before SIGKILL on deploy),
  // close all WebSocket connections immediately so clients reconnect to
  // the new container without waiting for TCP RST when the process is
  // killed.
  process.on("SIGTERM", () => {
    for (const ws of wss.clients) {
      try { ws.close(1001, "shutdown"); } catch {}
    }
  });

  return { broadcast, setRecent, wss };
}
