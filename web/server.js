import express from "express";
import http from "http";
import path from "path";
import fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import pg from "pg";

import { mountShortHost } from "./lib/short-host.js";
import { mountViewerRoutes } from "./lib/viewer-routes.js";
import { mountLandingRoutes } from "./lib/landing.js";
import { mountUnitRoutes } from "./lib/unit.js";
import { mountViewerPages } from "./lib/viewer-pages.js";
import { mountPartsPage } from "./lib/parts-page.js";
import { mountSpinRoutes } from "./lib/spin.js";
import { mountWeldPositionRoutes } from "./lib/weld-position.js";
import { mountPositionerRoutes } from "./lib/positioner.js";
import { mountFoamRoutes } from "./lib/foam.js";
import { mountCostRoutes } from "./lib/cost.js";
import { mountBuildRoutes } from "./lib/build.js";
import { mountUpdatesRoutes } from "./lib/updates.js";
import { mountChangesRoutes } from "./lib/changes.js";
import { mountLatestRoutes } from "./lib/latest.js";
import { mountStyleGuideRoutes } from "./lib/style-guide.js";
import { mountFirmwareRoutes } from "./lib/firmware.js";
import { mountEvents } from "./lib/events.js";
import { lockOnMain, mountArtifactsLive } from "./lib/artifacts-live.js";
import { mountObjectRoutes, mountObjectPrune } from "./lib/objects.js";
import { fillStore, storeFromEnv } from "./lib/store.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Web app lives at /web; hardware/ stays at the repo root because it's a
// separate concern (CAD scripts) that belongs to the larger project, not
// the web service.
const REPO_ROOT = path.join(__dirname, "..");
const DEFAULT_HARDWARE_DIR = path.join(REPO_ROOT, "hardware");
const UPDATES_DIR = path.join(REPO_ROOT, "updates");
const CHANGES_DIR = path.join(REPO_ROOT, "changes");
const LANDING_PUBLIC = path.join(__dirname, "public");
// The cross-boundary contract definitions (web/contracts/) are served to the
// browser at /contracts, so the viewer modules import the same event names and
// wire tags the server and builders do instead of re-declaring them. Node code
// imports these by relative path; the browser imports them by this URL — the
// same file either way.
const CONTRACTS_DIR = path.join(__dirname, "contracts");

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
      return res.status(400).json({ error: "That doesn't look like an email address." });
    }
    if (!pool) return res.status(503).json({ error: "Something went wrong on my end." });
    try {
      await pool.query(
        "INSERT INTO subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING",
        [email],
      );
      res.json({ ok: true });
    } catch (e) {
      console.error("subscribe error:", e);
      res.status(500).json({ error: "Something went wrong on my end." });
    }
  });
}

// Clears the device subscription when a previously installed push worker updates.
const RETIRE_PUSH_WORKER = `self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", event => {
  const registration = self.registration;
  event.waitUntil(Promise.allSettled([
    registration.pushManager?.getSubscription().then(subscription => subscription?.unsubscribe()),
    registration.getNotifications?.().then(notifications => notifications.forEach(notification => notification.close())),
  ]).then(() => registration.unregister()));
});
`;

function mountRetiredPushWorker(app) {
  app.get([
    "/firebase-messaging-sw.js",
    "/3d/firebase-messaging-sw.js",
    "/dev/firebase-messaging-sw.js",
  ], (_req, res) => {
    res.type("text/javascript");
    res.set("Cache-Control", "no-store");
    res.set("Service-Worker-Allowed", "/");
    res.send(RETIRE_PUSH_WORKER);
  });
}

function mountSiteIcons(app) {
  // iOS Safari looks for /apple-touch-icon.png at the domain root when the
  // user adds the page to the home screen. Without these, iOS shows a
  // letter-fallback (a white H on a black square). Serve the same artwork
  // we use elsewhere from the root paths iOS probes.
  const PWA_ICONS_DIR = path.join(LANDING_PUBLIC, "pwa-icons");
  const appleTouchIcon = path.join(PWA_ICONS_DIR, "apple-touch-icon-180.png");
  // `send` refuses any path carrying a dot-prefixed component, and a git worktree lives under
  // `.claude/worktrees/…` — so the artwork's own directory is one. All four of these paths are
  // built here out of `LANDING_PUBLIC` and take nothing from a request.
  const icon = { dotfiles: "allow" };
  app.get("/apple-touch-icon.png", (_req, res) => res.sendFile(appleTouchIcon, icon));
  app.get("/apple-touch-icon-precomposed.png", (_req, res) => res.sendFile(appleTouchIcon, icon));
  app.get("/favicon.ico", (_req, res) =>
    res.sendFile(path.join(PWA_ICONS_DIR, "favicon-32.png"), icon));
  app.get("/favicon.png", (_req, res) =>
    res.sendFile(path.join(PWA_ICONS_DIR, "favicon-64.png"), icon));
}

export async function start({ port, hardwareDir } = {}) {
  // hardwareDir lets callers (e.g. the historical-render tools in
  // tools/render/) point the viewer at a git worktree's hardware/ subtree
  // instead of the live tree, so a render captures the source artifact as
  // it existed at a specific past commit.
  const HARDWARE_DIR = hardwareDir || DEFAULT_HARDWARE_DIR;
  const app = express();
  // THE SHORT HOST STANDS FIRST. `hosm.us` carries no route of its own — every
  // path on it is a redirect to the same path here (web/lib/short-host.js) — so
  // it is answered before a body is parsed and before any route is consulted.
  mountShortHost(app);
  app.use(express.json());

  const pool = makePool();

  // The viewer reconnects across deploys and follows published files over /ws.
  const deployed = Boolean(process.env.RENDER_GIT_COMMIT);
  const commit = process.env.RENDER_GIT_COMMIT || `local-${Date.now()}`;
  const server = http.createServer(app);
  // THE OBJECT STORE (web/lib/store.js): Cloudflare R2 when render.yaml names the account and
  // key pair, the disk when it names a directory. Every member the pointer file names is held
  // there by hash; a machine that cut one puts it here (web/lib/objects.js).
  const store = await storeFromEnv();
  const pointersPath = path.join(REPO_ROOT, "hardware", "cad-artifacts.json");
  if (store) {
    console.log(`[objects] store: ${store.kind}`);
    mountObjectRoutes(app, { store });
    if (deployed) mountObjectPrune({ store, pointersPath, mainPointers: lockOnMain });
  }

  const { broadcast, setRecent } = mountEvents(server, { commit });

  mountViewerRoutes(app, { hardwareDir: HARDWARE_DIR, store, pointersPath });
  mountRetiredPushWorker(app);
  mountSiteIcons(app);
  mountLandingRoutes(app);
  mountUnitRoutes(app);
  mountViewerPages(app);
  mountPartsPage(app, { hardwareDir: HARDWARE_DIR, pointersPath });
  mountSpinRoutes(app);
  mountWeldPositionRoutes(app);
  mountPositionerRoutes(app);
  mountFoamRoutes(app);
  mountCostRoutes(app, { hardwareDir: HARDWARE_DIR });
  mountBuildRoutes(app, { hardwareDir: HARDWARE_DIR });
  mountUpdatesRoutes(app, { updatesDir: UPDATES_DIR, publicDir: LANDING_PUBLIC });
  // The feed's entries reach a deployed container without a deploy (web/lib/changes.js), and only
  // there: `RENDER_GIT_COMMIT` is Render's alone, for the reason `mountArtifactsLive` gives below.
  // Anywhere else the feed is the `changes/` on this disk.
  const changes = mountChangesRoutes(app, {
    changesDir: CHANGES_DIR,
    carry: deployed,
  });
  mountLatestRoutes(app, { changesDir: CHANGES_DIR, changes, updatesDir: UPDATES_DIR, publicDir: LANDING_PUBLIC });
  mountStyleGuideRoutes(app, { hardwareDir: HARDWARE_DIR });
  mountFirmwareRoutes(app, { commit });
  attachSubscribe(app, pool);

  // Live build commit, for boot.js's activation check: boot.js records it
  // on load and re-checks on focus/visibility/pageshow, refreshing the
  // page when it changed. This is how a backgrounded iOS PWA — whose
  // WebSocket iOS suspended — finds out a deploy shipped. No DB, never
  // cached.
  app.get("/api/version", (_req, res) => {
    res.set("Cache-Control", "no-store");
    res.json({ commit });
  });

  app.use("/contracts", express.static(CONTRACTS_DIR));
  const simplifier = fileURLToPath(import.meta.resolve("meshoptimizer/simplifier"));
  app.get("/vendor/meshoptimizer/simplifier.js", (_req, res) =>
    res.links({ license: "/vendor/meshoptimizer/LICENSE.md" }).sendFile(simplifier));
  app.get("/vendor/meshoptimizer/LICENSE.md", (_req, res) =>
    res.type("text/plain").sendFile(path.join(path.dirname(simplifier), "LICENSE.md")));
  app.use(express.static(LANDING_PUBLIC));

  // Published files reach the viewer as the running site adopts their pointer file.
  if (deployed) mountArtifactsLive(app, { broadcast, setRecent, commit });

  // AND THE STORE CATCHES UP BEHIND THE PORT. A container serves off its own disk from the
  // moment it boots; what the store is missing goes up after that, so a fill of 401 members
  // never stands between a deploy and the port it binds.
  if (store && deployed) {
    server.on("listening", () => {
      (async () => {
        try {
          const pointers = JSON.parse(await fs.promises.readFile(pointersPath, "utf-8"));
          await fillStore({ store, root: REPO_ROOT, pointers });
        } catch (e) {
          console.error(`[objects] fill skipped: ${e.message}`);
        }
      })();
    });
  }

  server.listen(port ?? process.env.PORT ?? 3001, () => {
    console.log(`Listening on :${server.address().port}`);
  });

  return { app, server, broadcast, hardwareDir: HARDWARE_DIR };
}

// If run directly (i.e. by Render as `node server.js`), boot in production mode. A run that
// names no script — `node -e`, the REPL, a test that imports this to boot it on its own port —
// has no `argv[1]` to be, and importing the module is not running it.
const isMain = !!process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  start();
}
