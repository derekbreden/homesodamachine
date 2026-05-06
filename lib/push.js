// Web push for the dev viewer PWA via Firebase Cloud Messaging.
//
// Wire shape:
//   - Browser registers /firebase-messaging-sw.js, calls getToken({vapidKey})
//     to get an FCM registration token, posts {token, files: [...]} to
//     /api/push/subscribe.
//   - Server (this module) stores tokens + which files each subscription
//     watches in Postgres.
//   - On prod boot, server.js calls detectChangedSteps() to diff every
//     hardware/**/*.step against the hash recorded on the previous boot;
//     for every changed file it calls notifyFileChanged().
//
// Notes:
//   - The first time a file is seen (no row in step_hashes), we record the
//     hash and skip the notify. Otherwise any schema reset would page every
//     subscriber for every file.
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

function walkStepFiles(rootDir) {
  const out = [];
  function walk(dir, rel) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (isIgnoredPath(full)) continue;
      if (entry.isDirectory()) walk(full, path.join(rel, entry.name));
      else if (entry.name.endsWith(".step")) out.push(path.join(rel, entry.name));
    }
  }
  walk(rootDir, "");
  return out;
}

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

export function initPush({ databasePool, serviceAccountJson }) {
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

  // PWA on cold-launch asks "is there a recent push waiting for me?" and
  // redirects if so. Single-use: row is deleted on read. 5-minute TTL keeps
  // a stale row from hijacking a manual reopen long after the push fired.
  // Logs the trigger query param so we can see which page-side event fired
  // the check even when the cliLog beacon gets dropped during unload.
  app.get("/api/pending-nav", async (req, res) => {
    const token = String(req.query.token || "");
    const trigger = String(req.query.trigger || "?").slice(0, 32);
    const tokenPrefix = token.slice(0, 12) || "?";
    console.log(`[pending-nav] trigger=${trigger} tokenPrefix=${tokenPrefix}`);
    if (!token) return res.json({});
    if (!pool) return res.json({});
    try {
      await ensureSchema();
      const { rows } = await pool.query(
        `SELECT url FROM pending_navs
         WHERE token = $1 AND ts > NOW() - INTERVAL '5 minutes'`,
        [token],
      );
      if (rows.length > 0) {
        await pool.query("DELETE FROM pending_navs WHERE token = $1", [token]);
        console.log(`[pending-nav] HIT trigger=${trigger} url=${rows[0].url}`);
        return res.json({ url: rows[0].url });
      }
      console.log(`[pending-nav] miss trigger=${trigger}`);
      res.json({});
    } catch (e) {
      console.error("pending-nav error:", e.message);
      res.json({});
    }
  });
}

// Hash every STEP under hardwareDir, compare to step_hashes, return list of
// files whose hash changed since last boot.
//
// First-seen handling mirrors detectChangedPosts: a file seen for the first
// time IS a publish event we want to notify on (a new part is part of the
// project the same way a new post is). The only case we suppress is the
// genuine bootstrap — first deploy after schema creation, when every
// existing file is "first-seen" but is really backlog. Detect that by
// checking whether step_hashes is empty before iterating; if so, record
// hashes silently and notify nothing.
export async function detectChangedSteps(hardwareDir) {
  if (!pool) return [];
  await ensureSchema();

  const { rows: countRows } = await pool.query(
    "SELECT COUNT(*)::int AS c FROM step_hashes",
  );
  const isBootstrap = countRows[0].c === 0;

  const files = walkStepFiles(hardwareDir);
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
      "SELECT sha256 FROM step_hashes WHERE file = $1",
      [file],
    );
    const prev = rows[0]?.sha256;

    if (prev === sha) continue;

    if (prev || !isBootstrap) changed.push(file);

    await pool.query(
      `INSERT INTO step_hashes (file, sha256, updated_at)
       VALUES ($1, $2, NOW())
       ON CONFLICT (file) DO UPDATE SET sha256 = EXCLUDED.sha256, updated_at = NOW()`,
      [file, sha],
    );
  }

  return changed;
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

// Single-post notification. Pulls the post's title from frontmatter for the
// heading and deep-links to the post anchor. Used when exactly one post
// changed in this deploy.
async function notifyPostChanged({ postsDir, filename }) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  await ensureSchema();

  // Cheap regex avoids importing gray-matter here; the format is a single
  // `title: ...` line and we're tolerant of optional surrounding quotes.
  let title = "New blog post";
  try {
    const raw = fs.readFileSync(path.join(postsDir, filename), "utf-8");
    const m = raw.match(/^title:\s*(.+?)\s*$/m);
    if (m) title = m[1].replace(/^["']|["']$/g, "").trim() || title;
  } catch {}

  // Reuse the same `*` global subscription that STEP changes fan out to:
  // the dev viewer's single Notifications toggle subscribes with `*` and
  // the user's intent there is "tell me about anything new on the
  // project," posts included.
  const { rows } = await pool.query(
    `SELECT token FROM push_subscriptions WHERE files && ARRAY['*']::text[]`,
  );

  const slug = filename.replace(/\.md$/, "");
  const link = `/blog#post-${slug}`;
  return fanOutToTokens(
    rows,
    {
      notification: { title, body: "New entry on the blog" },
      data: { post: filename, link },
      webpush: { fcmOptions: { link } },
    },
    `post ${filename}`,
    link,
  );
}

// Batched post notification — used when 2+ posts change in one deploy
// (multi-file edit commit, or any case where the diff loop returns a
// list). Collapses the fan-out into a single "N new updates" message so
// subscribers don't get a flurry on a bulk edit.
async function notifyPostsBatch(count) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  await ensureSchema();

  const { rows } = await pool.query(
    `SELECT token FROM push_subscriptions WHERE files && ARRAY['*']::text[]`,
  );

  return fanOutToTokens(
    rows,
    {
      notification: {
        title: `${count} new updates`,
        body: "New entries on the blog",
      },
      data: { count: String(count), link: "/blog" },
      webpush: { fcmOptions: { link: "/blog" } },
    },
    `posts batch (${count})`,
    "/blog",
  );
}

export async function notifyPostsChanged({ postsDir, filenames }) {
  if (filenames.length === 0) return { sent: 0, removed: 0 };
  if (filenames.length === 1) {
    return notifyPostChanged({ postsDir, filename: filenames[0] });
  }
  return notifyPostsBatch(filenames.length);
}

// Single-STEP notification — body is the file path so the user can see
// which part changed without opening the link.
async function notifyFileChanged(file) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  await ensureSchema();

  // files is either an explicit list of paths, or ['*'] meaning "every
  // STEP". Array overlap (&&) covers both: a row with ['*'] always matches,
  // a row with [file] matches only that file.
  const { rows } = await pool.query(
    `SELECT token FROM push_subscriptions WHERE files && ARRAY[$1::text, '*']`,
    [file],
  );

  const link = `/dev/?file=${encodeURIComponent(file)}`;
  return fanOutToTokens(
    rows,
    {
      notification: { title: "STEP updated", body: file },
      data: { file, link },
      webpush: { fcmOptions: { link } },
    },
    `STEP ${file}`,
    link,
  );
}

// Batched STEP notification — body shows up to three filenames so the
// user has some idea of what changed; the link drops them at /dev/ root.
async function notifyStepsBatch(files) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  await ensureSchema();

  // Match either '*' or any of the per-file subscriptions for the changed
  // files; an `&&` overlap with the union covers both.
  const { rows } = await pool.query(
    `SELECT DISTINCT token FROM push_subscriptions WHERE files && ($1::text[] || ARRAY['*'])`,
    [files],
  );

  const head = files.slice(0, 3).join(", ");
  const body = files.length > 3 ? `${head}, …` : head;
  return fanOutToTokens(
    rows,
    {
      notification: {
        title: `${files.length} STEPs updated`,
        body,
      },
      data: { count: String(files.length), link: "/dev/" },
      webpush: { fcmOptions: { link: "/dev/" } },
    },
    `STEPs batch (${files.length})`,
    "/dev/",
  );
}

export async function notifyStepsChanged({ files }) {
  if (files.length === 0) return { sent: 0, removed: 0 };
  if (files.length === 1) {
    return notifyFileChanged(files[0]);
  }
  return notifyStepsBatch(files);
}
