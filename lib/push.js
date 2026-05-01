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
}

// Hash every STEP under hardwareDir, compare to step_hashes, return list of
// files whose hash changed since last boot. Records hashes for files seen
// for the first time but does not include them in the returned list.
export async function detectChangedSteps(hardwareDir) {
  if (!pool) return [];
  await ensureSchema();

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

    if (prev) changed.push(file);

    await pool.query(
      `INSERT INTO step_hashes (file, sha256, updated_at)
       VALUES ($1, $2, NOW())
       ON CONFLICT (file) DO UPDATE SET sha256 = EXCLUDED.sha256, updated_at = NOW()`,
      [file, sha],
    );
  }

  return changed;
}

export async function notifyFileChanged(file) {
  if (!pool || !adminApp) return { sent: 0, removed: 0 };
  await ensureSchema();

  const { rows } = await pool.query(
    `SELECT token FROM push_subscriptions WHERE $1 = ANY(files)`,
    [file],
  );
  if (rows.length === 0) return { sent: 0, removed: 0 };

  const messaging = admin.messaging(adminApp);
  const link = `/dev/?file=${encodeURIComponent(file)}`;
  let sent = 0;
  let removed = 0;

  for (const row of rows) {
    try {
      await messaging.send({
        token: row.token,
        notification: {
          title: "STEP updated",
          body: file,
        },
        data: { file, link },
        webpush: {
          fcmOptions: { link },
          notification: {
            icon: "/dev/icons/icon-192.png",
            badge: "/dev/icons/icon-192.png",
          },
        },
      });
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
        console.error(`FCM send error for ${file}:`, e.message);
      }
    }
  }

  return { sent, removed };
}
