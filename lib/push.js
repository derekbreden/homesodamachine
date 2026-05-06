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

let pool = null;
let adminApp = null;
let schemaReady = null;

function isIgnoredPath(p) {
  return p.includes(`${path.sep}plan-b${path.sep}`);
}

function walkFilesByExt(rootDir, exts) {
  const out = [];
  function walk(dir, rel) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (isIgnoredPath(full)) continue;
      if (entry.isDirectory()) walk(full, path.join(rel, entry.name));
      else if (exts.some((e) => entry.name.endsWith(e))) out.push(path.join(rel, entry.name));
    }
  }
  walk(rootDir, "");
  return out;
}

function walkStepFiles(rootDir) { return walkFilesByExt(rootDir, [".step"]); }
function walkMermaidFiles(rootDir) { return walkFilesByExt(rootDir, [".mmd"]); }

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
      CREATE TABLE IF NOT EXISTS post_hashes (
        file TEXT PRIMARY KEY,
        sha256 TEXT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    // Per-token "the last push for you was for this URL". Server writes after
    // FCM accepts the send, PWA fetches on load (keyed by FCM token, which
    // the client stashed in localStorage when subscribing) and redirects.
    // Bypasses iOS PWA's apparent no-op for SW push/notificationclick events
    // — start_url cold-launch goes through normal HTTP, not the SW, and a
    // server-side lookup works regardless of whether any SW event ran.
    await pool.query(`
      CREATE TABLE IF NOT EXISTS pending_navs (
        token TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
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

  // The page hits this on load and on window.focus so a tap-to-foreground
  // (PWA was backgrounded) can pick up the redirect target — iOS PWA
  // doesn't fire notificationclick or visibilitychange-to-visible, only
  // window.focus. iOS also doesn't tell us *which* notification the user
  // tapped, so we treat the most recent push for this token as the
  // intent: return its URL plus the row's `ts` so the client can dedupe
  // (each push gets a new ts; the client's saved lastTs gates whether
  // it acts on the row again on subsequent focus events). 7-day TTL is
  // generous enough that a banner tapped hours or days after it fired
  // still gets the user to the right place.
  app.get("/api/pending-nav", async (req, res) => {
    const token = String(req.query.token || "");
    const tokenPrefix = token.slice(0, 12) || "(none)";
    if (!token) {
      console.log(`[pending-nav] no-token`);
      return res.json({});
    }
    if (!pool) {
      console.log(`[pending-nav] no-pool token=${tokenPrefix}`);
      return res.json({});
    }
    try {
      await ensureSchema();
      const { rows } = await pool.query(
        `SELECT url, ts FROM pending_navs
         WHERE token = $1 AND ts > NOW() - INTERVAL '7 days'`,
        [token],
      );
      if (rows.length > 0) {
        const ts = rows[0].ts.getTime();
        console.log(`[pending-nav] HIT token=${tokenPrefix} ts=${ts} url=${rows[0].url}`);
        return res.json({ url: rows[0].url, ts });
      }
      console.log(`[pending-nav] miss token=${tokenPrefix}`);
      res.json({});
    } catch (e) {
      console.error(`[pending-nav] error token=${tokenPrefix}: ${e.message}`);
      res.json({});
    }
  });
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
const ALLOWED_HASH_TABLES = new Set(["step_hashes", "mermaid_hashes"]);

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
async function fanOutToTokens(tokens, message, errorContext, link) {
  if (tokens.length === 0) return { sent: 0, removed: 0 };
  const messaging = admin.messaging(adminApp);
  const webpushDefaults = {
    notification: {
      icon: "/pwa-icons/icon-192.png",
      badge: "/pwa-icons/icon-192.png",
    },
  };
  const fullMessage = {
    ...message,
    webpush: { ...webpushDefaults, ...(message.webpush || {}) },
  };
  let sent = 0;
  let removed = 0;
  for (const row of tokens) {
    try {
      await messaging.send({ ...fullMessage, token: row.token });
      sent++;
      if (link) {
        try {
          await pool.query(
            `INSERT INTO pending_navs (token, url, ts) VALUES ($1, $2, NOW())
             ON CONFLICT (token) DO UPDATE SET url = EXCLUDED.url, ts = NOW()`,
            [row.token, link],
          );
        } catch (e) {
          console.error("pending_navs write error:", e.message);
        }
      }
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
  );
}

// Unified notification for any viewable-file changes (STEP and/or mermaid).
// One FCM message regardless of how many files or which kinds: title and
// body are computed by countFilesByKind so a deploy that changes both
// kinds doesn't fan out into two banners. Link always points at the first
// changed file's deep link, so cold-launch tap on the system banner lands
// on something specific even for batched updates (rather than dumping the
// user at /dev/ root with no file context).
//
// All callers route through here; the boot diff loop in server.js
// detects step + mermaid changes separately and concatenates them into
// `files` for one call.
// Title language mirrors the site nav ("Prints" links to the dev viewer
// where .step files live, "Diagrams" to mermaid files), so the wording a
// user sees in a banner / toast matches the nav section they'd tap to
// browse the same content. Body is the basename only — full paths get
// long fast and the directory rarely tells the user anything they need
// at notification-glance time.
function describeFilesUpdate(files) {
  const stepCount = files.filter((f) => f.endsWith(".step")).length;
  const mermaidCount = files.filter((f) => f.endsWith(".mmd")).length;
  let title;
  if (files.length === 1) {
    if (files[0].endsWith(".step")) title = "Print updated";
    else if (files[0].endsWith(".mmd")) title = "Diagram updated";
    else title = "File updated";
  } else if (stepCount === files.length) {
    title = `${files.length} Prints updated`;
  } else if (mermaidCount === files.length) {
    title = `${files.length} Diagrams updated`;
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
  const link = `/dev/?file=${encodeURIComponent(files[0])}`;
  return fanOutToTokens(
    rows,
    {
      notification: { title, body },
      data: { count: String(files.length), link, files: files.join(",") },
      webpush: { fcmOptions: { link } },
    },
    `files (${files.length})`,
    link,
  );
}
