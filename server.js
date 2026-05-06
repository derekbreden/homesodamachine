import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import pg from "pg";

import { mountViewerRoutes } from "./lib/viewer-routes.js";
import { mountBlogRoutes } from "./lib/blog.js";
import { mountLandingRoutes } from "./lib/landing.js";
import { mountDevViewerRoutes } from "./lib/dev-viewer.js";
import { mountSettingsRoutes } from "./lib/settings.js";
import { mountEvents } from "./lib/events.js";
import {
  initPush,
  mountPushRoutes,
  detectChangedSteps,
  detectChangedPosts,
  notifyPostsChanged,
  notifyStepsChanged,
} from "./lib/push.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_HARDWARE_DIR = path.join(__dirname, "hardware");
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
  //
  // Notification handling, in summary (verified by an instrumented session
  // against a real iOS PWA — see lib/shell.js HEAD_TAGS for the page-side
  // half of this dance):
  //
  //   • Push display: handled by firebase-messaging-compat. We send a
  //     `notification` field in the FCM payload, so iOS / Chrome / Android
  //     show the system banner automatically. We don't override.
  //
  //   • Tap → cold launch (PWA was killed): iOS opens the PWA directly at
  //     `webpush.fcmOptions.link` from the payload. No SW or page code
  //     needed; iOS does it natively.
  //
  //   • Tap → backgrounded (PWA was open but not focused): iOS just
  //     refocuses the existing window. SW notificationclick does NOT fire
  //     on iOS PWA. visibilitychange-to-visible / pageshow / page-load do
  //     not fire either. The only event that does is the page's
  //     window.focus — the page-side listener picks it up and queries
  //     /api/pending-nav to redirect.
  //
  //   • Tap → foregrounded: nothing fires anywhere. iOS treats it as a
  //     no-op. (TODO: handle this via SSE-driven in-app toast once we
  //     have an SSE channel.)
  //
  //   • Chrome desktop / Android PWA: firebase-messaging-compat's default
  //     notificationclick handler opens fcmOptions.link via openWindow.
  //     We don't override.
  //
  // The only events we attach are install / activate, both for the
  // standard skipWaiting + clients.claim + auto-reload-stale-clients
  // pattern that gets new HEAD_TAGS into already-open pages.
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
firebase.messaging();

// skipWaiting + clients.claim let a freshly-installed SW take over open
// pages immediately, so a deploy doesn't get stranded behind an old SW
// until every client closes. The activate handler then posts a
// navigate-self message to each open client; the page-side listener
// (shell.js HEAD_TAGS) interprets that as a reload, so already-rendered
// pages pick up new HEAD_TAGS without manual refresh.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    await self.clients.claim();
    try {
      const all = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
      for (const c of all) {
        try { c.postMessage({ type: "navigate", url: c.url }); } catch {}
      }
    } catch {}
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
  const PWA_ICONS_DIR = path.join(LANDING_PUBLIC, "pwa-icons");
  const appleTouchIcon = path.join(PWA_ICONS_DIR, "apple-touch-icon-180.png");
  app.get("/apple-touch-icon.png", (_req, res) => res.sendFile(appleTouchIcon));
  app.get("/apple-touch-icon-precomposed.png", (_req, res) => res.sendFile(appleTouchIcon));
  app.get("/favicon.ico", (_req, res) => res.sendFile(path.join(PWA_ICONS_DIR, "favicon-32.png")));
  app.get("/favicon.png", (_req, res) => res.sendFile(path.join(PWA_ICONS_DIR, "favicon-64.png")));
}

export async function start({ dev = false, port, hardwareDir } = {}) {
  // hardwareDir lets callers (e.g. the historical-render tools in
  // tools/render/) point the viewer at a git worktree's hardware/ subtree
  // instead of the live tree, so a render captures the source artifact as
  // it existed at a specific past commit.
  const HARDWARE_DIR = hardwareDir || DEFAULT_HARDWARE_DIR;

  const app = express();
  app.use(express.json());

  const pool = makePool();

  // SSE channel for server -> client push. In dev, the wrapper calls
  // broadcast() from chokidar handlers. In prod, hello-on-connect signals
  // deploys, and broadcastToToken delivers per-client pending-nav events
  // (used by the in-app toast — see shell.js HEAD_TAGS).
  const commit = dev
    ? "dev"
    : (process.env.RENDER_GIT_COMMIT || `local-${Date.now()}`);
  const { broadcast, broadcastToToken } = mountEvents(app, { commit });

  initPush({
    databasePool: pool,
    serviceAccountJson: process.env.FIREBASE_SERVICE_ACCOUNT_JSON,
    broadcastToToken,
  });

  // URL structure is identical in dev and prod: landing at /, blog at
  // /blog, dev viewer at /dev/, settings at /settings, with VIEWER_PUBLIC
  // served under /dev/ and LANDING_PUBLIC at /. The dev viewer at
  // localhost:3000/dev/ is the same page the public hits at
  // homesodamachine.com/dev/ — keeping the URL structures aligned is what
  // lets ContentViewer and other LANDING_PUBLIC assets just work in dev.
  // The dev wrapper (tools/step-viewer/server.js) is purely additive: it
  // attaches chokidar + Python + the SSE broadcast for hot reload, and
  // doesn't change any routes. The only behavioral differences in dev:
  //   - commit signal is "dev" instead of the deploy SHA
  //   - the boot-time push diff is skipped (no real deploy, no FCM)
  mountViewerRoutes(app, { hardwareDir: HARDWARE_DIR });
  mountBlogRoutes(app, { postsDir: POSTS_DIR });
  mountPushRoutes(app);
  mountFirebaseConfig(app);
  mountLandingRoutes(app);
  mountDevViewerRoutes(app, { prefix: "/dev" });
  mountSettingsRoutes(app);
  attachSubscribe(app, pool);
  app.use("/dev", express.static(VIEWER_PUBLIC));
  app.use(express.static(LANDING_PUBLIC));

  // Production-only: per-file deploy-change push. Hash every STEP / post,
  // diff against the row recorded by the previous boot, fire FCM messages
  // for what changed. notifyStepsChanged / notifyPostsChanged batch when
  // 2+ files change (one "N STEPs updated" / "N new updates" notification
  // instead of N separate ones), so a multi-edit commit or schema reset
  // doesn't burst-page subscribers. Best-effort — failures don't block
  // the listen. Skipped in dev because there's no real deploy event.
  if (!dev) {
    (async () => {
      try {
        const changed = await detectChangedSteps(HARDWARE_DIR);
        if (changed.length > 0) {
          console.log(`Push: notifying for ${changed.length} changed STEP file(s)`);
          const result = await notifyStepsChanged({ files: changed });
          console.log(`  sent=${result.sent} removed=${result.removed}`);
        }
      } catch (e) {
        console.error("Push diff error:", e.message);
      }
    })();

    (async () => {
      try {
        const changed = await detectChangedPosts(POSTS_DIR);
        if (changed.length > 0) {
          console.log(`Push: notifying for ${changed.length} changed post(s)`);
          const result = await notifyPostsChanged({ postsDir: POSTS_DIR, filenames: changed });
          console.log(`  sent=${result.sent} removed=${result.removed}`);
        }
      } catch (e) {
        console.error("Push diff error (posts):", e.message);
      }
    })();
  }

  const defaultPort = dev ? 3000 : 3001;
  const server = app.listen(port ?? process.env.PORT ?? defaultPort, () => {
    if (dev) {
      console.log(`Dev server: http://localhost:${server.address().port}`);
      console.log("  Landing /, Updates /blog, Viewer /dev/, Settings /settings");
    } else {
      console.log(`Listening on :${server.address().port}`);
    }
  });

  return { app, server, broadcast, hardwareDir: HARDWARE_DIR };
}

// If run directly (i.e. by Render as `node server.js`), boot in production mode.
const isMain = import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  start({ dev: false });
}
