import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import pg from "pg";

import { mountViewerRoutes } from "./lib/viewer-routes.js";
import { mountBlogRoutes } from "./lib/blog.js";
import { mountLandingRoutes } from "./lib/landing.js";
import { mountViewerPages } from "./lib/viewer-pages.js";
import { mountSettingsRoutes } from "./lib/settings.js";
import { mountEvents } from "./lib/events.js";
import {
  initPush,
  mountPushRoutes,
  detectChangedSteps,
  detectChangedMermaid,
  detectChangedPosts,
  describeChangedPosts,
  notifyPostsChanged,
  notifyFilesChanged,
} from "./lib/push.js";
import { mountNotificationsRoutes } from "./lib/notifications.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_HARDWARE_DIR = path.join(__dirname, "hardware");
const POSTS_DIR = path.join(__dirname, "posts");
const LANDING_PUBLIC = path.join(__dirname, "public");

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
  // pushes apply ("/3d/" here) so the file path matches.
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

  // Served at root and at /3d/ so it's reachable from either scope.
  // The Service-Worker-Allowed header lets the client register with a
  // custom scope; the client picks "/3d/" so the landing page isn't
  // unnecessarily controlled by the SW. The legacy /dev/ path is still
  // served (in case an old SW registration is alive on a returning user)
  // but shouldn't be picked by new registrations.
  const swHandler = (_req, res) => {
    res.set("Content-Type", "application/javascript");
    res.set("Cache-Control", "no-cache");
    res.set("Service-Worker-Allowed", "/");
    res.send(swSource(firebaseWebConfig()));
  };
  app.get("/firebase-messaging-sw.js", swHandler);
  app.get("/3d/firebase-messaging-sw.js", swHandler);
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

  // SSE channel for server -> client push. Three event flows:
  //   - hello-on-connect: deploy detection (commit fingerprint changes
  //     across reconnects); also carries the most recent boot-diff
  //     `recent` field so a client that reconnected after the deploy
  //     gets the change list it missed during the server-down window.
  //   - files-changed (broadcast): dev chokidar fires per-save; prod
  //     fires once at boot if the diff loop found anything. Same wire
  //     format both sides.
  //   - viewer-only `posts-updated` etc are unrelated and stay as-is.
  const commit = dev
    ? "dev"
    : (process.env.RENDER_GIT_COMMIT || `local-${Date.now()}`);
  const { broadcast, setRecent } = mountEvents(app, { commit });

  initPush({
    databasePool: pool,
    serviceAccountJson: process.env.FIREBASE_SERVICE_ACCOUNT_JSON,
  });

  // URL structure is identical in dev and prod: landing at /, blog at
  // /blog, parts viewer at /3d, charts viewer at /charts, settings at
  // /settings, with LANDING_PUBLIC served at /. The localhost dev server
  // hits the same routes the public site does, so ContentViewer and
  // other LANDING_PUBLIC assets just work in dev.
  // The dev wrapper (tools/step-viewer/server.js) is purely additive: it
  // attaches chokidar + Python + the SSE broadcast for hot reload, and
  // doesn't change any routes. The only behavioral differences in dev:
  //   - commit signal is "dev" instead of the deploy SHA
  //   - the boot-time push diff is skipped (no real deploy, no FCM)
  mountViewerRoutes(app, { hardwareDir: HARDWARE_DIR });
  mountBlogRoutes(app, { postsDir: POSTS_DIR });
  mountPushRoutes(app);
  mountNotificationsRoutes(app, pool);
  mountFirebaseConfig(app);
  mountLandingRoutes(app);
  mountViewerPages(app);
  mountSettingsRoutes(app);
  attachSubscribe(app, pool);
  app.use(express.static(LANDING_PUBLIC));

  // Production-only: deploy-change push. Hash STEP + mermaid + posts in
  // parallel against per-kind tables, then fire SSE + FCM for what
  // changed. SSE has two event types (`files-changed` for step/mermaid,
  // `posts-changed` for blog) since posts carry per-item metadata
  // (title, link) that doesn't fit the bare-paths shape `files-changed`
  // uses. Both kinds get piggy-backed onto `recent` so reconnecting
  // clients (PWA was open during deploy, EventSource killed by shutdown)
  // catch up via hello. Best-effort — failures don't block the listen.
  // Skipped in dev since no real deploy event happens; chokidar fires
  // files-changed on save and there's no equivalent for posts in dev.
  if (!dev) {
    (async () => {
      try {
        const [changedSteps, changedMermaid, changedPostFiles] = await Promise.all([
          detectChangedSteps(HARDWARE_DIR),
          detectChangedMermaid(HARDWARE_DIR),
          detectChangedPosts(POSTS_DIR),
        ]);
        const changedFiles = [...changedSteps, ...changedMermaid];
        const changedPosts = describeChangedPosts({
          postsDir: POSTS_DIR,
          filenames: changedPostFiles,
        });

        if (changedFiles.length === 0 && changedPosts.length === 0) return;

        // SSE: broadcast each kind to currently-connected clients, AND
        // store on `recent` so a client reconnecting after the deploy
        // catches up via hello.
        const ts = Date.now();
        if (changedFiles.length > 0) {
          broadcast({ type: "files-changed", commit, files: changedFiles });
        }
        if (changedPosts.length > 0) {
          broadcast({ type: "posts-changed", commit, posts: changedPosts });
        }
        const snapshot = { commit, ts };
        if (changedFiles.length > 0) snapshot.files = changedFiles;
        if (changedPosts.length > 0) snapshot.posts = changedPosts;
        setRecent(snapshot);

        // FCM: one banner per kind. Files batch any mix of step/mermaid
        // into a single banner; posts go through their own notify path.
        // A deploy that touches both produces two banners — acceptable
        // and rare; if it becomes annoying we can collapse later.
        if (changedFiles.length > 0) {
          console.log(`Push: notifying for ${changedFiles.length} changed file(s)`);
          const result = await notifyFilesChanged({ files: changedFiles });
          console.log(`  sent=${result.sent} removed=${result.removed}`);
        }
        if (changedPosts.length > 0) {
          console.log(`Push: notifying for ${changedPosts.length} changed post(s)`);
          const result = await notifyPostsChanged({ postsDir: POSTS_DIR, filenames: changedPostFiles });
          console.log(`  sent=${result.sent} removed=${result.removed}`);
        }
      } catch (e) {
        console.error("Push diff error:", e.message);
      }
    })();
  }

  const defaultPort = dev ? 3000 : 3001;
  const server = app.listen(port ?? process.env.PORT ?? defaultPort, () => {
    if (dev) {
      console.log(`Dev server: http://localhost:${server.address().port}`);
      console.log("  Landing /, Updates /blog, Parts /3d, Charts /charts, Settings /settings");
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
