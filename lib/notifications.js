// Per-token notifications inbox. Each push fires inserts a row here for
// every subscriber whose `files` filter matches; the dev viewer PWA
// fetches and renders them at /notifications, with read/unread state
// driving the bell-icon dot in the top nav and the in-app toast.
//
// The schema lives in lib/push.js ensureSchema (so push and notifications
// share one ensureSchema/migrate path); this file owns the CRUD helpers,
// HTTP API, and the /notifications page render.
//
// Wire shape:
//   GET /api/notifications?token=X        → {items: [{id, kind, url, title, body, ts, seen}, ...]}
//   GET /api/notifications/unread-count?token=X → {count: N}
//   POST /api/notifications/seen          → body {token, ids?: [...], all?: true}
//   GET /notifications                    → HTML page
//
// fcmOptions.link in every push gets `?n=<id>` appended so a cold-launch
// tap (iOS opens at the link directly) tells us which row to mark seen.
// The page's HEAD_TAGS reads ?n on load and POSTs /api/notifications/seen.

import { renderHead, renderNav, renderFooter } from "./shell.js";

// Append ?n=<id> (or &n=<id> if there's already a query) to a URL,
// preserving any existing query and fragment. Pure JS, no extra deps.
function appendIdParam(url, id) {
  // We treat url as path+query+hash, no scheme/host.
  let path = url, hash = "";
  const hashIdx = url.indexOf("#");
  if (hashIdx >= 0) {
    path = url.slice(0, hashIdx);
    hash = url.slice(hashIdx);
  }
  const sep = path.includes("?") ? "&" : "?";
  return path + sep + "n=" + id + hash;
}

// Insert a notification for a single token+push. Returns the row's id
// and the final URL (with `?n=<id>` baked in). Caller uses the returned
// URL for the FCM `fcmOptions.link` so the cold-launch deep link points
// at exactly this row.
export async function insertNotification(pool, { token, kind, baseUrl, title, body }) {
  const ins = await pool.query(
    `INSERT INTO notifications (token, kind, url, title, body)
     VALUES ($1, $2, $3, $4, $5)
     RETURNING id`,
    [token, kind, baseUrl, title || "", body || ""],
  );
  const id = ins.rows[0].id;
  const url = appendIdParam(baseUrl, id);
  await pool.query(`UPDATE notifications SET url = $1 WHERE id = $2`, [url, id]);
  return { id, url };
}

export async function listNotifications(pool, token) {
  const { rows } = await pool.query(
    `SELECT id, kind, url, title, body, ts, seen_at
     FROM notifications
     WHERE token = $1 AND ts > NOW() - INTERVAL '7 days'
     ORDER BY ts DESC
     LIMIT 200`,
    [token],
  );
  return rows.map((r) => ({
    id: r.id,
    kind: r.kind,
    url: r.url,
    title: r.title,
    body: r.body,
    ts: r.ts.getTime(),
    seen: r.seen_at !== null,
  }));
}

export async function countUnread(pool, token) {
  const { rows } = await pool.query(
    `SELECT COUNT(*)::int AS c FROM notifications
     WHERE token = $1 AND seen_at IS NULL AND ts > NOW() - INTERVAL '7 days'`,
    [token],
  );
  return rows[0].c;
}

export async function markSeen(pool, { token, ids, all }) {
  if (all) {
    await pool.query(
      `UPDATE notifications SET seen_at = NOW()
       WHERE token = $1 AND seen_at IS NULL`,
      [token],
    );
    return;
  }
  if (Array.isArray(ids) && ids.length > 0) {
    await pool.query(
      `UPDATE notifications SET seen_at = NOW()
       WHERE token = $1 AND id = ANY($2::bigint[]) AND seen_at IS NULL`,
      [token, ids],
    );
  }
}

export function mountNotificationsRoutes(app, pool) {
  if (!pool) return;

  app.get("/api/notifications", async (req, res) => {
    const token = String(req.query.token || "");
    if (!token) return res.json({ items: [] });
    try {
      const items = await listNotifications(pool, token);
      res.json({ items });
    } catch (e) {
      console.error("notifications list error:", e.message);
      res.json({ items: [] });
    }
  });

  app.get("/api/notifications/unread-count", async (req, res) => {
    const token = String(req.query.token || "");
    if (!token) return res.json({ count: 0 });
    try {
      const count = await countUnread(pool, token);
      res.json({ count });
    } catch (e) {
      console.error("unread-count error:", e.message);
      res.json({ count: 0 });
    }
  });

  app.post("/api/notifications/seen", async (req, res) => {
    const token = String(req.body?.token || "");
    const all = !!req.body?.all;
    const idsRaw = Array.isArray(req.body?.ids) ? req.body.ids : null;
    if (!token) return res.status(400).json({ error: "token required" });
    try {
      // Coerce ids to BigInt-compatible strings for pg's bigint[] cast.
      const ids = idsRaw
        ? idsRaw.map((v) => String(v)).filter((v) => /^\d+$/.test(v))
        : null;
      await markSeen(pool, { token, ids, all });
      res.json({ ok: true });
    } catch (e) {
      console.error("mark-seen error:", e.message);
      res.status(500).json({ error: "server error" });
    }
  });

  app.get("/notifications", (_req, res) => {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(renderNotificationsPage());
  });
}

// The page itself is mostly a shell — the actual list comes from
// /api/notifications keyed by the FCM token in localStorage. Empty
// state, "Mark all as read" button visibility, and per-row formatting
// are all client-side because the server can't tell from the request
// which token to render for (no token in cookies, only localStorage).
function renderNotificationsPage() {
  return (
    renderHead({
      title: "Notifications",
      pageStyles: `
.notifs-page {
  flex: 1;
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
  padding: 16px calc(env(safe-area-inset-right, 0px) + 16px) 32px calc(env(safe-area-inset-left, 0px) + 16px);
  display: flex;
  flex-direction: column;
}
.notifs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.notifs-title { font-size: 20px; font-weight: 600; margin: 0; }
.notifs-mark-all {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
}
.notifs-mark-all:hover { background: var(--surface); }
.notifs-mark-all[hidden] { display: none; }
.notifs-list { list-style: none; margin: 0; padding: 0; }
.notifs-empty {
  color: var(--text-2);
  text-align: center;
  padding: 48px 16px;
  font-size: 14px;
}
.notif-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}
.notif-row:hover { background: var(--surface-2); }
.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  margin-top: 8px;
  flex-shrink: 0;
}
.notif-row.unread .notif-dot { background: var(--accent); }
.notif-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--text-2);
}
.notif-row.unread .notif-icon { color: var(--accent); }
.notif-text { flex: 1; min-width: 0; }
.notif-title {
  font-weight: 600;
  font-size: 14px;
  margin: 0 0 2px 0;
}
.notif-row.unread .notif-title { color: var(--text); }
.notif-row:not(.unread) .notif-title { color: var(--text-2); }
.notif-body {
  font-size: 13px;
  color: var(--text-2);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.notif-time {
  font-size: 12px;
  color: var(--text-3);
  flex-shrink: 0;
  margin-top: 2px;
}
`,
    }) +
    renderNav({ surface: "public", active: null }) +
    `<main class="notifs-page" id="notifs-page">
  <div class="notifs-header">
    <h1 class="notifs-title">Notifications</h1>
    <button class="notifs-mark-all" id="notifs-mark-all" type="button" hidden>Mark all as read</button>
  </div>
  <ul class="notifs-list" id="notifs-list" aria-live="polite"></ul>
  <div class="notifs-empty" id="notifs-empty" hidden>No notifications yet.</div>
</main>
<script>
(function(){
  var listEl = document.getElementById("notifs-list");
  var emptyEl = document.getElementById("notifs-empty");
  var markAllBtn = document.getElementById("notifs-mark-all");

  function token() {
    try { return localStorage.getItem("hsmFcmToken") || ""; } catch (e) { return ""; }
  }

  function relTime(ts) {
    var diff = Math.max(0, Date.now() - ts);
    var s = Math.floor(diff / 1000);
    if (s < 60) return s + "s ago";
    var m = Math.floor(s / 60);
    if (m < 60) return m + "m ago";
    var h = Math.floor(m / 60);
    if (h < 24) return h + "h ago";
    var d = Math.floor(h / 24);
    return d + "d ago";
  }

  function iconSvg(kind) {
    // Step (cube), Dxf (scissors), Mermaid (chart), Post (newspaper) — feather-ish.
    if (kind === "step") {
      return '<svg class="notif-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>';
    }
    if (kind === "dxf") {
      return '<svg class="notif-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="6" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><line x1="20" y1="4" x2="8.12" y2="15.88"></line><line x1="14.47" y1="14.48" x2="20" y2="20"></line><line x1="8.12" y1="8.12" x2="12" y2="12"></line></svg>';
    }
    if (kind === "mermaid") {
      return '<svg class="notif-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>';
    }
    if (kind === "post") {
      return '<svg class="notif-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8M15 18h-5M10 6h8v4h-8z"></path></svg>';
    }
    return '<svg class="notif-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>';
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});
  }

  function render(items) {
    listEl.innerHTML = "";
    if (!items || items.length === 0) {
      emptyEl.hidden = false;
      markAllBtn.hidden = true;
      return;
    }
    emptyEl.hidden = true;
    var anyUnread = false;
    for (var i = 0; i < items.length; i++) {
      var n = items[i];
      if (!n.seen) anyUnread = true;
      var li = document.createElement("li");
      li.className = "notif-row" + (n.seen ? "" : " unread");
      li.innerHTML =
        '<div class="notif-dot"></div>' +
        iconSvg(n.kind) +
        '<div class="notif-text">' +
          '<p class="notif-title">' + escapeHtml(n.title) + '</p>' +
          '<p class="notif-body">' + escapeHtml(n.body) + '</p>' +
        '</div>' +
        '<span class="notif-time">' + escapeHtml(relTime(n.ts)) + '</span>';
      (function(notif){
        li.addEventListener("click", function(){
          // Optimistic: mark seen client-side, navigate, fire-and-forget POST.
          fetch("/api/notifications/seen", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({token: token(), ids: [notif.id]}),
            keepalive: true
          }).catch(function(){});
          window.location.href = notif.url;
        });
      })(n);
      listEl.appendChild(li);
    }
    markAllBtn.hidden = !anyUnread;
  }

  function refresh() {
    var t = token();
    if (!t) { render([]); return; }
    fetch("/api/notifications?token=" + encodeURIComponent(t))
      .then(function(r){ return r.ok ? r.json() : {items: []}; })
      .then(function(d){ render(d.items || []); })
      .catch(function(){ render([]); });
  }

  markAllBtn.addEventListener("click", function(){
    var t = token();
    if (!t) return;
    fetch("/api/notifications/seen", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({token: t, all: true})
    }).then(function(){ refresh(); window.dispatchEvent(new CustomEvent("hsm:notifications-changed")); });
  });

  // Refresh on focus / pageshow / SSE-driven update.
  window.addEventListener("focus", refresh);
  window.addEventListener("pageshow", refresh);
  window.addEventListener("hsm:notifications-changed", refresh);
  refresh();
})();
</script>` +
    renderFooter()
  );
}
