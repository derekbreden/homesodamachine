// Web push for the dev viewer PWA via Firebase Cloud Messaging.
//
// Wire shape:
//   - Browser registers /firebase-messaging-sw.js, calls getToken({vapidKey})
//     to get an FCM registration token, posts {token, files: [...]} to
//     /api/push/subscribe.
//   - Server (this module) stores tokens + which files each subscription
//     watches in Postgres.
//   - On prod boot, server.js calls detectChangedSteps + detectChangedMermaid
//     against per-kind hash tables, concatenates the result, and calls
//     notifyFilesChanged once for the combined set. One FCM banner regardless
//     of how many files or which kinds changed; SSE files-changed event
//     fires alongside for in-app handling (see lib/shell.js HEAD_TAGS).
//
// Notes:
//   - The first time a hash table is empty (genuine bootstrap — first deploy
//     after schema creation, or when adding a new kind like mermaid), we
//     record hashes silently and notify nothing. Avoids paging every
//     subscriber for every existing file.
//   - Tokens that come back from FCM as not-registered or invalid are removed.

import admin from "firebase-admin";
import path from "path";
import fs from "fs";
import crypto from "crypto";
import { insertNotification } from "./notifications.js";
import { walkFiles } from "./walk.js";

let pool = null;
let adminApp = null;
let schemaReady = null;

function walkStepFiles(rootDir) { return walkFiles(rootDir, ".step"); }
function walkMermaidFiles(rootDir) { return walkFiles(rootDir, ".mmd"); }
function walkDxfFiles(rootDir) { return walkFiles(rootDir, ".dxf"); }

// Match the post filename format documented in posts/README.md
// (`YYYY-MM-DD-HHMM.md`) so docs/helpers like posts/README.md don't get
// hashed and treated as posts. The README has YAML-like example blocks
// inside it (e.g. `title: <short noun phrase, ...>`) that the title regex
// in notifyPostChanged would otherwise pick up, sending bogus notifications
// every time the README is edited.
const POST_FILENAME_RE = /^\d{4}-\d{2}-\d{2}-\d{4}\.md$/;

function walkPostFiles(postsDir) {
  if (!fs.existsSync(postsDir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(postsDir, { withFileTypes: true })) {
    if (entry.isFile() && POST_FILENAME_RE.test(entry.name)) out.push(entry.name);
  }
  return out;
}

function ensureSchema() {
  if (!pool) return Promise.resolve();
  if (schemaReady) return schemaReady;
  schemaReady = (async () => {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS push_subscriptions (
        id SERIAL PRIMARY KEY,
        token TEXT NOT NULL UNIQUE,
        files TEXT[] NOT NULL DEFAULT '{}',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS push_subscriptions_files_idx
        ON push_subscriptions USING GIN (files)
    `);
    await pool.query(`
      CREATE TABLE IF NOT EXISTS step_hashes (
        file TEXT PRIMARY KEY,
        sha256 TEXT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    await pool.query(`
      CREATE TABLE IF NOT EXISTS mermaid_hashes (
        file TEXT PRIMARY KEY,
        sha256 TEXT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    await pool.query(`
      CREATE TABLE IF NOT EXISTS dxf_hashes (
        file TEXT PRIMARY KEY,
        sha256 TEXT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    await pool.query(`
      CREATE TABLE IF NOT EXISTS post_hashes (
        file TEXT PRIMARY KEY,
        sha256 TEXT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    // Notifications inbox: one row per push per token, with seen state.
    // Replaces the old single-row-per-token `pending_navs` table — that
    // worked for "warm tap → most recent push" but couldn't represent a
    // queue, which we want now for the in-app /notifications list.
    //
    // pending_navs is dropped here; its data was always ephemeral (5-min
    // TTL originally, 7-day later) so there's nothing to migrate.
    await pool.query(`DROP TABLE IF EXISTS pending_navs`);
    await pool.query(`
      CREATE TABLE IF NOT EXISTS notifications (
        id BIGSERIAL PRIMARY KEY,
        token TEXT NOT NULL,
        kind TEXT NOT NULL,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL DEFAULT '',
        ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        seen_at TIMESTAMPTZ
      )
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS notifications_token_ts_idx
        ON notifications (token, ts DESC)
    `);
    await pool.query(`
      CREATE INDEX IF NOT EXISTS notifications_token_unread_idx
        ON notifications (token) WHERE seen_at IS NULL
    `);
    // Daily-ish prune of old notifications. 7-day retention (matches what
    // we promised the user). Quick best-effort sweep at boot — not a
    // background job, just one query when ensureSchema runs.
    await pool.query(`DELETE FROM notifications WHERE ts < NOW() - INTERVAL '7 days'`);
  })();
  return schemaReady;
}

export function initPush({ databasePool, serviceAccountJson } = {}) {
  pool = databasePool || null;

  if (serviceAccountJson) {
    try {
      const parsed = typeof serviceAccountJson === "string"
        ? JSON.parse(serviceAccountJson)
        : serviceAccountJson;
      adminApp = admin.initializeApp(
        { credential: admin.credential.cert(parsed) },
        "push",
      );
      console.log(`Firebase Admin SDK initialized for project ${parsed.project_id}`);
    } catch (e) {
      console.error("Firebase Admin init failed:", e.message);
      adminApp = null;
    }
  }

  return { ready: !!(pool && adminApp) };
}

export function mountPushRoutes(app) {
  app.post("/api/push/subscribe", async (req, res) => {
    const { token, files } = req.body || {};
    if (typeof token !== "string" || token.length < 20 || token.length > 4096) {
      return res.status(400).json({ error: "Invalid token" });
    }
    if (!Array.isArray(files) || files.some((f) => typeof f !== "string" || f.length > 512)) {
      return res.status(400).json({ error: "Invalid files" });
    }
    if (!pool) return res.status(503).json({ error: "Database unavailable" });
    try {
      await ensureSchema();
      await pool.query(
        `INSERT INTO push_subscriptions (token, files, updated_at)
         VALUES ($1, $2, NOW())
         ON CONFLICT (token) DO UPDATE SET files = EXCLUDED.files, updated_at = NOW()`,
        [token, files],
      );
      res.json({ ok: true, count: files.length });
    } catch (e) {
      console.error("subscribe error:", e);
      res.status(500).json({ error: "Server error" });
    }
  });

  app.post("/api/push/unsubscribe", async (req, res) => {
    const { token } = req.body || {};
    if (typeof token !== "string") return res.status(400).json({ error: "Invalid token" });
    if (!pool) return res.status(503).json({ error: "Database unavailable" });
    try {
      await pool.query("DELETE FROM push_subscriptions WHERE token = $1", [token]);
      res.json({ ok: true });
    } catch (e) {
      console.error("unsubscribe error:", e);
      res.status(500).json({ error: "Server error" });
    }
  });

  app.get("/api/push/subscription", async (req, res) => {
    const token = String(req.query.token || "");
    if (!token) return res.json({ files: [] });
    if (!pool) return res.json({ files: [] });
    try {
      await ensureSchema();
      const { rows } = await pool.query(
        "SELECT files FROM push_subscriptions WHERE token = $1",
        [token],
      );
      res.json({ files: rows[0]?.files || [] });
    } catch (e) {
      res.json({ files: [] });
    }
  });

  // /api/pending-nav, the old single-row-most-recent endpoint, is gone.
  // Its job is now done by GET /api/notifications (full inbox) — see
  // lib/notifications.js. Page-side decides between auto-redirect (1
  // unread) and aggregate toast (2+ unread) from that data.
}

// Hash every viewable file under hardwareDir, compare to its hash table,
// return paths whose hash changed since last boot.
//
// First-seen handling mirrors detectChangedPosts: a file seen for the first
// time IS a publish event we want to notify on (a new part is part of the
// project the same way a new post is). The only case we suppress is the
// genuine bootstrap — first deploy after schema creation, when every
// existing file is "first-seen" but is really backlog. Detect that by
// checking whether the hash table is empty before iterating; if so, record
// hashes silently and notify nothing. Each table bootstraps independently
// so adding a new viewable kind (mermaid alongside steps) doesn't trigger
// a notification flood for files that already existed.
//
// Allowed table names are hardcoded — no SQL injection risk despite the
// template-string interpolation, since callers pick from this whitelist.
const ALLOWED_HASH_TABLES = new Set(["step_hashes", "mermaid_hashes", "dxf_hashes"]);

async function detectChangedFilesInTable(tableName, walker, hardwareDir) {
  if (!ALLOWED_HASH_TABLES.has(tableName)) {
    throw new Error(`detectChangedFilesInTable: bad table "${tableName}"`);
  }
  if (!pool) return [];
  await ensureSchema();

  const { rows: countRows } = await pool.query(
    `SELECT COUNT(*)::int AS c FROM ${tableName}`,
  );
  const isBootstrap = countRows[0].c === 0;

  const files = walker(hardwareDir);
  const changed = [];

  for (const file of files) {
    const abs = path.join(hardwareDir, file);
    let buf;
    try {
      buf = fs.readFileSync(abs);
    } catch {
      continue;
    }
    const sha = crypto.createHash("sha256").update(buf).digest("hex");

    const { rows } = await pool.query(
      `SELECT sha256 FROM ${tableName} WHERE file = $1`,
      [file],
    );
    const prev = rows[0]?.sha256;

    if (prev === sha) continue;

    if (prev || !isBootstrap) changed.push(file);

    await pool.query(
      `INSERT INTO ${tableName} (file, sha256, updated_at)
       VALUES ($1, $2, NOW())
       ON CONFLICT (file) DO UPDATE SET sha256 = EXCLUDED.sha256, updated_at = NOW()`,
      [file, sha],
    );
  }

  return changed;
}

export function detectChangedSteps(hardwareDir) {
  return detectChangedFilesInTable("step_hashes", walkStepFiles, hardwareDir);
}

export function detectChangedMermaid(hardwareDir) {
  return detectChangedFilesInTable("mermaid_hashes", walkMermaidFiles, hardwareDir);
}

export function detectChangedDxf(hardwareDir) {
  return detectChangedFilesInTable("dxf_hashes", walkDxfFiles, hardwareDir);
}

// Hash every post under postsDir, compare to post_hashes, return list of
// posts whose hash changed since last boot.
//
// First-seen handling differs from detectChangedSteps. A post seen for the
// first time normally IS a publish event the README promises will page
// every subscriber, so we want to notify. The only case we suppress is the
// genuine bootstrap — first deploy after schema creation, when every
// existing post is "first-seen" but is really backlog. Detect that by
// checking whether post_hashes is empty before iterating; if so, record
// hashes silently and notify nothing.
export async function detectChangedPosts(postsDir) {
  if (!pool) return [];
  await ensureSchema();

  const { rows: countRows } = await pool.query(
    "SELECT COUNT(*)::int AS c FROM post_hashes",
  );
  const isBootstrap = countRows[0].c === 0;

  const files = walkPostFiles(postsDir);
  const changed = [];

  for (const file of files) {
    const abs = path.join(postsDir, file);
    let buf;
    try {
      buf = fs.readFileSync(abs);
    } catch {
      continue;
    }
    const sha = crypto.createHash("sha256").update(buf).digest("hex");

    const { rows } = await pool.query(
      "SELECT sha256 FROM post_hashes WHERE file = $1",
      [file],
    );
    const prev = rows[0]?.sha256;

    if (prev === sha) continue;

    if (prev || !isBootstrap) changed.push(file);

    await pool.query(
      `INSERT INTO post_hashes (file, sha256, updated_at)
       VALUES ($1, $2, NOW())
       ON CONFLICT (file) DO UPDATE SET sha256 = EXCLUDED.sha256, updated_at = NOW()`,
      [file, sha],
    );
  }

  return changed;
}

// Single source of truth for the FCM fan-out + dead-token cleanup loop.
// Every notify* function builds a message and hands it here; this keeps
// the retry/error path consistent and frees the callers to focus on
// what to send (single post vs batched count vs single STEP vs etc).
//
// `kind` distinguishes step / mermaid / post for the in-app notifications
// list (icon picker, etc). For mixed-kind file batches it's "files".
//
// `link` is the BASE URL (no `?n=<id>`). For each token, we insert a
// notifications row, get back the row id, and use the URL with
// `?n=<id>` baked in for the FCM `fcmOptions.link` so a cold-launch
// tap on the resulting banner can mark exactly that row read.
async function fanOutToTokens(tokens, message, errorContext, link, kind) {
  if (tokens.length === 0) return { sent: 0, removed: 0 };
  const messaging = admin.messaging(adminApp);
  const webpushDefaults = {
    notification: {
      icon: "/pwa-icons/icon-192.png",
      badge: "/pwa-icons/icon-192.png",
    },
  };
  const title = (message.notification && message.notification.title) || "";
  const body = (message.notification && message.notification.body) || "";
  let sent = 0;
  let removed = 0;
  for (const row of tokens) {
    try {
      // 1. Insert notification row (gets id), get the per-token URL with
      //    n=<id> baked in. The same URL goes into FCM so the banner
      //    points at exactly this notification.
      let perTokenLink = link;
      if (link && kind) {
        try {
          const ins = await insertNotification(pool, {
            token: row.token,
            kind,
            baseUrl: link,
            title,
            body,
          });
          perTokenLink = ins.url;
        } catch (e) {
          console.error("notifications insert error:", e.message);
        }
      }

      // 2. Build the FCM message with this token's specific link.
      const fullMessage = {
        ...message,
        data: { ...(message.data || {}), link: perTokenLink },
        webpush: {
          ...webpushDefaults,
          ...(message.webpush || {}),
          fcmOptions: { ...(message.webpush?.fcmOptions || {}), link: perTokenLink },
        },
        token: row.token,
      };

      await messaging.send(fullMessage);
      sent++;
    } catch (e) {
      const code = e.code || "";
      if (
        code === "messaging/registration-token-not-registered" ||
        code === "messaging/invalid-registration-token" ||
        code === "messaging/invalid-argument"
      ) {
        await pool.query("DELETE FROM push_subscriptions WHERE token = $1", [row.token]);
        removed++;
      } else {
        console.error(`FCM send error (${errorContext}):`, e.message);
      }
    }
  }
  return { sent, removed };
}

// Cheap regex frontmatter parse — the format is a single `title: ...` line,
// tolerant of optional surrounding quotes. Avoids pulling in gray-matter
// just for one field. Falls back to "New blog post" if the file can't be
// read or has no title line.
function extractPostTitle(postsDir, filename) {
  try {
    const raw = fs.readFileSync(path.join(postsDir, filename), "utf-8");
    const m = raw.match(/^title:\s*(.+?)\s*$/m);
    if (m) {
      const t = m[1].replace(/^["']|["']$/g, "").trim();
      if (t) return t;
    }
  } catch {}
  return "New blog post";
}

// Resolve each changed post into the metadata the SSE broadcast needs
// (title for the toast body, link for tap-through). Exported so server.js
// can hand the same metadata to both the SSE broadcast and the FCM call.
export function describeChangedPosts({ postsDir, filenames }) {
  return filenames.map((filename) => ({
    filename,
    title: extractPostTitle(postsDir, filename),
    link: `/blog#post-${filename.replace(/\.md$/, "")}`,
  }));
}

// Unified post-update notification. Mirrors notifyFilesChanged: one FCM
// message regardless of how many posts changed; batch link points at the
// first post's anchor (cold-launch tap lands on something specific instead
// of dumping the user at /blog root).
export async function notifyPostsChanged({ postsDir, filenames }) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  if (filenames.length === 0) return { sent: 0, removed: 0 };
  await ensureSchema();

  // The dev viewer's single Notifications toggle subscribes with `*`,
  // intent: "tell me about anything new on the project, posts included".
  const { rows } = await pool.query(
    `SELECT token FROM push_subscriptions WHERE files && ARRAY['*']::text[]`,
  );

  const posts = describeChangedPosts({ postsDir, filenames });
  let title, body;
  if (posts.length === 1) {
    title = posts[0].title;
    body = "New entry on the blog";
  } else {
    title = `${posts.length} new updates`;
    const head = posts.slice(0, 3).map((p) => p.title).join(", ");
    body = posts.length > 3 ? `${head}, …` : head;
  }
  const link = posts[0].link;

  return fanOutToTokens(
    rows,
    {
      notification: { title, body },
      data: { count: String(posts.length), link },
      webpush: { fcmOptions: { link } },
    },
    `posts (${posts.length})`,
    link,
    "post",
  );
}

// Unified notification for any viewable-file changes (STEP and/or mermaid).
// One FCM message regardless of how many files or which kinds: title and
// body are computed by countFilesByKind so a deploy that changes both
// kinds doesn't fan out into two banners. Link always points at the first
// changed file's deep link, so cold-launch tap on the system banner lands
// on something specific even for batched updates (rather than dumping the
// user at /3d root with no file context).
//
// All callers route through here; the boot diff loop in server.js
// detects step + mermaid changes separately and concatenates them into
// `files` for one call.
// Title is per-kind ("Print updated" for STEP, "Diagram updated" for
// mermaid). Body is the basename only — full paths get long fast and the
// directory rarely tells the user anything they need at notification-
// glance time.
function describeFilesUpdate(files) {
  const stepCount = files.filter((f) => f.endsWith(".step")).length;
  const mermaidCount = files.filter((f) => f.endsWith(".mmd")).length;
  const dxfCount = files.filter((f) => f.endsWith(".dxf")).length;
  let title;
  if (files.length === 1) {
    if (files[0].endsWith(".step")) title = "Print updated";
    else if (files[0].endsWith(".mmd")) title = "Diagram updated";
    else if (files[0].endsWith(".dxf")) title = "Cut updated";
    else title = "File updated";
  } else if (stepCount === files.length) {
    title = `${files.length} Prints updated`;
  } else if (mermaidCount === files.length) {
    title = `${files.length} Diagrams updated`;
  } else if (dxfCount === files.length) {
    title = `${files.length} Cuts updated`;
  } else {
    title = `${files.length} Files updated`;
  }
  const names = files.map((f) => path.basename(f));
  const head = names.slice(0, 3).join(", ");
  const body = names.length === 1 ? names[0] : (names.length > 3 ? `${head}, …` : head);
  return { title, body };
}

export async function notifyFilesChanged({ files }) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  if (files.length === 0) return { sent: 0, removed: 0 };
  await ensureSchema();

  // Match '*' subscriptions OR per-file subscriptions overlapping our list.
  // Array overlap (&&) on the union of changed files + '*' covers both
  // cases in a single query.
  const { rows } = await pool.query(
    `SELECT DISTINCT token FROM push_subscriptions WHERE files && ($1::text[] || ARRAY['*'])`,
    [files],
  );

  const { title, body } = describeFilesUpdate(files);
  // STEP and DXF files both live on /3d (Prints + Cuts sections), mermaid
  // files on /charts. Pick the deep link based on the first file's
  // extension so a single-file notification lands the user on the right
  // page; mixed batches are rare enough that we just send them to /3d
  // (the "default" parts page).
  const firstFile = files[0];
  const basePath = firstFile.endsWith(".mmd") ? "/charts" : "/3d";
  const link = `${basePath}?file=${encodeURIComponent(firstFile)}`;
  // Pick a kind for the notifications-list icon. Pure step / mermaid /
  // dxf / (mixed → "files"); inferred from the file list rather than
  // passed separately so callers don't have to think about it.
  const stepCount = files.filter((f) => f.endsWith(".step")).length;
  const mermaidCount = files.filter((f) => f.endsWith(".mmd")).length;
  const dxfCount = files.filter((f) => f.endsWith(".dxf")).length;
  const kind = stepCount === files.length ? "step"
             : mermaidCount === files.length ? "mermaid"
             : dxfCount === files.length ? "dxf"
             : "files";
  return fanOutToTokens(
    rows,
    {
      notification: { title, body },
      data: { count: String(files.length), link, files: files.join(",") },
      webpush: { fcmOptions: { link } },
    },
    `files (${files.length})`,
    link,
    kind,
  );
}
