// Server-Sent Events transport for server -> client push.
// Used by both the dev server (file-change notifications from chokidar) and
// the production server (deploy-version handshake on connect). EventSource
// on the client side handles reconnect and gap-recovery for free.
//
// Wire shape:
//   On connect, server sends a `hello` event carrying an opaque commit
//   fingerprint. The client compares the fingerprint across reconnects; a
//   change means the server restarted with new code and the client should
//   refetch whatever it's currently displaying.
//
//   Dev passes a constant fingerprint (so dev-server restarts don't trigger
//   spurious refetches — chokidar handles dev refresh per-file).
//   Production passes RENDER_GIT_COMMIT (or a boot-time fallback for local
//   `npm start`).

export function mountEvents(app, { commit = "unknown" } = {}) {
  const subscribers = new Set();
  // Most-recent boot diff result. Set by server.js after the prod boot
  // hash diff completes; piggy-backed onto every `hello` payload so a
  // client that reconnects after a deploy (its previous EventSource was
  // killed when the old server shut down) gets the change list it would
  // otherwise have missed. The client dedupes by recent.commit so a
  // stable connection that already saw the deploy ignores it.
  //
  // Snapshot shape: {commit, ts, files?, posts?}. Either or both arrays
  // may be present; null clears.
  let recent = null;

  function setRecent(snapshot) {
    const hasFiles = Array.isArray(snapshot?.files) && snapshot.files.length > 0;
    const hasPosts = Array.isArray(snapshot?.posts) && snapshot.posts.length > 0;
    recent = (hasFiles || hasPosts) ? snapshot : null;
  }

  function send(res, msg) {
    try {
      res.write(`data: ${JSON.stringify(msg)}\n\n`);
    } catch {
      // res may have closed; the close handler will clean up.
    }
  }

  function broadcast(msg) {
    const payload = `data: ${JSON.stringify(msg)}\n\n`;
    for (const res of subscribers) {
      try {
        res.write(payload);
      } catch {
        // ignore; close handler will remove
      }
    }
  }

  app.get("/api/events", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache, no-transform");
    res.setHeader("Connection", "keep-alive");
    // Disable proxy buffering on the off chance an nginx-style proxy is in
    // front of us (Render's edge ignores this header but it doesn't hurt).
    res.setHeader("X-Accel-Buffering", "no");
    res.flushHeaders?.();
    req.socket.setNoDelay(true);

    subscribers.add(res);
    const helloMsg = { type: "hello", commit, time: Date.now() };
    if (recent) helloMsg.recent = recent;
    send(res, helloMsg);

    // Periodic ping every 30s. Two purposes:
    //   - Comment-style keepalive (`:keepalive\n\n`) defeats idle timeouts
    //     at intermediate proxies (Render/Cloudflare edge typically idle
    //     around ~100s for streaming responses).
    //   - Real `data:` ping fires the client's EventSource message handler
    //     so client code has an observable heartbeat. Comment lines are
    //     consumed by the EventSource parser and never reach the page.
    //     Boot.js uses this to detect Safari's silent-disconnect mode
    //     (TCP died but readyState stays OPEN) and force a reconnect.
    const keepalive = setInterval(() => {
      try {
        res.write(`:keepalive\n\n`);
        send(res, { type: "ping", t: Date.now() });
      } catch {
        clearInterval(keepalive);
      }
    }, 30_000);

    req.on("close", () => {
      clearInterval(keepalive);
      subscribers.delete(res);
    });
  });

  // On graceful shutdown (Render sends SIGTERM before SIGKILL on deploy),
  // close all SSE connections immediately so clients reconnect to the new
  // container without waiting for the TCP RST when the process is killed.
  process.on("SIGTERM", () => {
    for (const res of subscribers) {
      try { res.end(); } catch {}
    }
    subscribers.clear();
  });

  return { broadcast, setRecent, subscribers };
}
