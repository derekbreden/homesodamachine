import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import pg from "pg";

import { mountViewerRoutes } from "./lib/viewer-routes.js";
import { mountBlogRoutes } from "./lib/blog.js";
import { mountEvents } from "./lib/events.js";
import {
  initPush,
  mountPushRoutes,
  detectChangedSteps,
  notifyFileChanged,
  detectChangedPosts,
  notifyPostChanged,
} from "./lib/push.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE_DIR = path.join(__dirname, "hardware");
const POSTS_DIR = path.join(__dirname, "posts");
const LANDING_PUBLIC = path.join(__dirname, "public");
const VIEWER_PUBLIC = path.join(__dirname, "tools", "step-viewer", "public");

function makePool() {
  if (!process.env.DATABASE_URL) return null;
  return new pg.Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });
}

function attachSubscribe(app, pool) {
  if (pool) {
    (async () => {
      for (let attempt = 1; attempt <= 30; attempt++) {
        try {
          await pool.query(`
            CREATE TABLE IF NOT EXISTS subscribers (
              id SERIAL PRIMARY KEY,
              email TEXT NOT NULL UNIQUE,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
          `);
          console.log("schema ready");
          return;
        } catch (e) {
          console.log(`schema init attempt ${attempt} failed: ${e.code || e.message}`);
          await new Promise((r) => setTimeout(r, 2000));
        }
      }
      console.error("schema init giving up after 30 attempts");
    })();
  }

  app.post("/api/subscribe", async (req, res) => {
    const email = String(req.body?.email || "").trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
      return res.status(400).json({ error: "Invalid email" });
    }
    if (!pool) return res.status(503).json({ error: "Database unavailable" });
    try {
      await pool.query(
        "INSERT INTO subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING",
        [email],
      );
      res.json({ ok: true });
    } catch (e) {
      console.error("subscribe error:", e);
      res.status(500).json({ error: "Server error" });
    }
  });
}

function firebaseWebConfig() {
  return {
    apiKey: process.env.FIREBASE_API_KEY || "",
    authDomain: process.env.FIREBASE_AUTH_DOMAIN || "",
    projectId: process.env.FIREBASE_PROJECT_ID || "",
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET || "",
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID || "",
    appId: process.env.FIREBASE_APP_ID || "",
    vapidKey: process.env.FIREBASE_VAPID_KEY || "",
  };
}

function mountFirebaseConfig(app) {
  // Public Firebase web-app config — embedded in every PWA/SW bundle anyway.
  // Served from env vars so the codebase doesn't pin a project ID and so
  // dev/prod can differ. Cached short to make a redeploy roll out fast.
  app.get("/api/firebase-config", (_req, res) => {
    res.set("Cache-Control", "public, max-age=60");
    res.json(firebaseWebConfig());
  });

  // Firebase requires the messaging service worker to be reachable at a
  // known URL with the config available. We serve a tiny SW that imports
  // the modular firebase-messaging-sw bundle and initializes with the
  // env-var-driven config. The SW must live at the root scope of where
  // pushes apply ("/dev/" here) so the file path matches.
  const swSource = (cfg) => `// Auto-generated. Do not edit; see server.js.
importScripts("https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js");

firebase.initializeApp(${JSON.stringify({
  apiKey: cfg.apiKey,
  authDomain: cfg.authDomain,
  projectId: cfg.projectId,
  storageBucket: cfg.storageBucket,
  messagingSenderId: cfg.messagingSenderId,
  appId: cfg.appId,
})});

const messaging = firebase.messaging();

// Background push handler. The default Firebase SW already shows a
// notification for "notification" payloads; for "data-only" payloads we
// build one here.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const link = (event.notification.data && event.notification.data.FCM_MSG &&
                event.notification.data.FCM_MSG.notification &&
                event.notification.data.FCM_MSG.notification.click_action) ||
               (event.notification.data && event.notification.data.link) ||
               "/dev/";
  event.waitUntil((async () => {
    const all = await clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of all) {
      if (c.url.includes(link) && "focus" in c) return c.focus();
    }
    if (clients.openWindow) return clients.openWindow(link);
  })());
});
`;

  // Served at root so it's reachable in both dev (viewer at /) and prod
  // (viewer at /dev/). The Service-Worker-Allowed header lets the client
  // register with a custom scope; the client picks "/" in dev and "/dev/"
  // in prod so the landing page isn't unnecessarily controlled by the SW.
  const swHandler = (_req, res) => {
    res.set("Content-Type", "application/javascript");
    res.set("Cache-Control", "no-cache");
    res.set("Service-Worker-Allowed", "/");
    res.send(swSource(firebaseWebConfig()));
  };
  app.get("/firebase-messaging-sw.js", swHandler);
  app.get("/dev/firebase-messaging-sw.js", swHandler);

  // iOS Safari looks for /apple-touch-icon.png at the domain root when the
  // user adds the page to the home screen. Without these, iOS shows a
  // letter-fallback (a white H on a black square). Serve the same artwork
  // we use elsewhere from the root paths iOS probes.
  const PWA_ICONS_DIR = path.join(VIEWER_PUBLIC, "pwa-icons");
  const appleTouchIcon = path.join(PWA_ICONS_DIR, "apple-touch-icon-180.png");
  app.get("/apple-touch-icon.png", (_req, res) => res.sendFile(appleTouchIcon));
  app.get("/apple-touch-icon-precomposed.png", (_req, res) => res.sendFile(appleTouchIcon));
  app.get("/favicon.ico", (_req, res) => res.sendFile(path.join(PWA_ICONS_DIR, "favicon-32.png")));
  app.get("/favicon.png", (_req, res) => res.sendFile(path.join(PWA_ICONS_DIR, "favicon-64.png")));
}

export async function start({ dev = false, port } = {}) {
  const app = express();
  app.use(express.json());

  const pool = makePool();
  initPush({
    databasePool: pool,
    serviceAccountJson: process.env.FIREBASE_SERVICE_ACCOUNT_JSON,
  });

  mountViewerRoutes(app, { hardwareDir: HARDWARE_DIR });
  mountBlogRoutes(app, { postsDir: POSTS_DIR });
  mountPushRoutes(app);
  mountFirebaseConfig(app);

  // SSE channel for server -> client push. In dev, the wrapper calls
  // broadcast() from chokidar handlers. In prod, only the hello-on-connect
  // is used — clients detect a deploy by the commit field changing across
  // reconnects and refetch what they're viewing.
  const commit = dev
    ? "dev"
    : (process.env.RENDER_GIT_COMMIT || `local-${Date.now()}`);
  const { broadcast } = mountEvents(app, { commit });

  let server;

  if (dev) {
    // Dev mode: viewer is the front page. Watcher + Python + WebSocket are
    // attached by the dev wrapper after start() returns.
    app.use(express.static(VIEWER_PUBLIC));
    server = app.listen(port ?? process.env.PORT ?? 3000, () => {
      console.log(`Dev viewer: http://localhost:${server.address().port}`);
    });
  } else {
    // Production: landing page at /, dev viewer behind /dev/, signup endpoint.
    app.use(express.static(LANDING_PUBLIC));
    app.get("/dev", (_req, res) => res.sendFile(path.join(VIEWER_PUBLIC, "index.html")));
    app.get("/dev/mermaid", (_req, res) => res.sendFile(path.join(VIEWER_PUBLIC, "mermaid.html")));
    app.use("/dev", express.static(VIEWER_PUBLIC));
    attachSubscribe(app, pool);

    // Per-file deploy-change push: hash every STEP, diff against the row
    // recorded by the previous boot, fire FCM messages for what changed.
    // Best-effort — failures don't block the listen.
    (async () => {
      try {
        const changed = await detectChangedSteps(HARDWARE_DIR);
        if (changed.length > 0) {
          console.log(`Push: notifying for ${changed.length} changed STEP file(s)`);
          for (const file of changed) {
            const result = await notifyFileChanged(file);
            console.log(`  ${file}: sent=${result.sent} removed=${result.removed}`);
          }
        }
      } catch (e) {
        console.error("Push diff error:", e.message);
      }
    })();

    // Same per-file diff for blog posts: any new or edited markdown in
    // posts/ fires an FCM message to the same `*` global subscribers as
    // STEP changes. First-seen posts are recorded without notifying so
    // the initial deploy doesn't page everyone for the existing backlog.
    (async () => {
      try {
        const changed = await detectChangedPosts(POSTS_DIR);
        if (changed.length > 0) {
          console.log(`Push: notifying for ${changed.length} changed post(s)`);
          for (const file of changed) {
            const result = await notifyPostChanged({ postsDir: POSTS_DIR, filename: file });
            console.log(`  ${file}: sent=${result.sent} removed=${result.removed}`);
          }
        }
      } catch (e) {
        console.error("Push diff error (posts):", e.message);
      }
    })();

    server = app.listen(port ?? process.env.PORT ?? 3001, () => {
      console.log(`Listening on :${server.address().port}`);
    });
  }

  return { app, server, broadcast, hardwareDir: HARDWARE_DIR };
}

// If run directly (i.e. by Render as `node server.js`), boot in production mode.
const isMain = import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  start({ dev: false });
}
