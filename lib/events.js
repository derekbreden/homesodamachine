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
    send(res, { type: "hello", commit, time: Date.now() });

    // Comment-line keepalive every 30s. EventSource ignores comment lines.
    // This defeats idle timeouts at intermediate proxies (Render/Cloudflare
    // edge typically idle around ~100s for streaming responses).
    const keepalive = setInterval(() => {
      try {
        res.write(`:keepalive\n\n`);
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

  return { broadcast, subscribers };
}
