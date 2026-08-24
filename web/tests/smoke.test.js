// Boot-time + route smoke tests.
//
// The single most valuable assertion here is the `import { start }` at the
// top: if server.js fails to evaluate (the way it did when a stray
// VIEWER_DEFAULTS ReferenceError took down a deploy before commit 8611dfa),
// the test errors immediately. That one import is the safety net every
// future change crosses on its way to production.
//
// Around that, a table of GET routes verifies status + content-type prefix
// for every public surface that doesn't depend on Postgres. Routes that
// require DATABASE_URL (push subscribe, notifications inbox) are
// deliberately omitted — running this file with no DB still has to pass.
//
// Tests use only stdlib (`node:test` + `node:assert`) and native fetch.
// No supertest, no jest, no extra deps.

import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { start } from "../server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// The web app is rooted at .../web; the larger repo root holds hardware/,
// tools/, etc. Tests need both paths.
const WEB_ROOT  = path.resolve(__dirname, "..");
const REPO_ROOT = path.resolve(__dirname, "..", "..");

let server;
let baseUrl;

before(async () => {
  // port: 0 lets the OS pick a free port — the test never collides with a
  // running dev server. dev: false matches the production code path.
  const started = await start({ dev: false, port: 0 });
  server = started.server;
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  if (!server) return;
  // The WebSocket server holds a 30s ping interval and the open sockets.
  // closeAllConnections() forces those sockets shut so server.close()'s
  // promise resolves immediately instead of waiting on the keepalive
  // interval (~30s).
  server.closeAllConnections?.();
  await new Promise((resolve) => server.close(resolve));
});

// Routes that should respond on a stock production boot with no DB.
//
// expect: integer (single status) or array of acceptable statuses.
// ct: required prefix on the Content-Type header (omit for redirects /
//     binary passthroughs where we don't pin the value).
const routes = [
  // HTML pages
  { path: "/",         expect: 200, ct: "text/html" },
  { path: "/3d",       expect: 200, ct: "text/html" },
  { path: "/charts",   expect: 200, ct: "text/html" },
  { path: "/drawings", expect: 200, ct: "text/html" },
  { path: "/cost",     expect: 200, ct: "text/html" },
  { path: "/tour",     expect: 200, ct: "text/html" },
  { path: "/settings", expect: 200, ct: "text/html" },

  // Legacy redirects (301). Don't pin Content-Type — express renders a
  // tiny HTML body for browsers but the assertion that matters is the
  // redirect itself.
  { path: "/dev",          expect: 301 },
  { path: "/dev/diagrams", expect: 301 },
  { path: "/dev/mermaid",  expect: 301 },
  { path: "/dev/settings", expect: 301 },

  // JSON APIs that don't touch Postgres
  { path: "/api/steps",           expect: 200, ct: "application/json" },
  { path: "/api/dxf",             expect: 200, ct: "application/json" },
  { path: "/api/mermaid",         expect: 200, ct: "application/json" },
  { path: "/api/documents",       expect: 200, ct: "application/json" },
  { path: "/api/firebase-config", expect: 200, ct: "application/json" },

  // Service worker variants — same body, three URLs (root, /3d, legacy /dev)
  { path: "/firebase-messaging-sw.js",     expect: 200, ct: "text/javascript" },
  { path: "/3d/firebase-messaging-sw.js",  expect: 200, ct: "text/javascript" },
  { path: "/dev/firebase-messaging-sw.js", expect: 200, ct: "text/javascript" },

  // PWA / favicon images — express sets image/* content-type from extension.
  { path: "/apple-touch-icon.png",             expect: 200, ct: "image/png" },
  { path: "/apple-touch-icon-precomposed.png", expect: 200, ct: "image/png" },
  { path: "/favicon.ico",                      expect: 200, ct: "image/png" },
  { path: "/favicon.png",                      expect: 200, ct: "image/png" },

  // Static JS bundles served via express.static(public/). Each one is
  // imported by at least one HTML surface; if one disappears the page
  // breaks at runtime with a console-only error, so a 404 here is a
  // real regression. Content-Type comes from express's mime db.
  { path: "/boot.js",             expect: 200, ct: "text/javascript" },
  { path: "/landing.js",          expect: 200, ct: "text/javascript" },
  { path: "/settings.js",         expect: 200, ct: "text/javascript" },
  { path: "/pan-zoom.js",         expect: 200, ct: "text/javascript" },
  { path: "/content-viewer.js",   expect: 200, ct: "text/javascript" },
  { path: "/js/tour/main.js",     expect: 200, ct: "text/javascript" },
  { path: "/css/tour.css",        expect: 200, ct: "text/css" },
  { path: "/glass-animation.js",  expect: 200, ct: "text/javascript" },

  // Contract definitions served to the browser: web/contracts/ mounted at
  // /contracts. The viewer imports HSM_EVENTS + WS from these at runtime, so a
  // 404 here breaks boot.js and the pickers with a module-load error. (Only the
  // .js contracts are browser-imported; the .ts ones are builder-side.)
  { path: "/contracts/client-events.js", expect: 200, ct: "text/javascript" },
  { path: "/contracts/ws-frames.js",     expect: 200, ct: "text/javascript" },
  { path: "/contracts/cards.js",         expect: 200, ct: "text/javascript" },
  { path: "/contracts/tour-water.js",    expect: 200, ct: "text/javascript" },
];

for (const r of routes) {
  test(`GET ${r.path}`, async () => {
    const res = await fetch(baseUrl + r.path, { redirect: "manual" });
    const acceptable = Array.isArray(r.expect) ? r.expect : [r.expect];
    assert.ok(
      acceptable.includes(res.status),
      `expected ${acceptable.join(" or ")}, got ${res.status}`,
    );
    if (r.ct) {
      const got = res.headers.get("content-type") || "";
      assert.match(got, new RegExp(`^${r.ct.replace(/\//g, "\\/")}`),
        `expected content-type ${r.ct}, got ${got}`);
    }
  });
}

// The WebSocket senders must emit frame types via the WS contract, exactly as
// the client matches them (web/contracts/ws-frames.js). A reintroduced literal
// would still work today but drift silently if a tag is ever renamed in one
// place. events.js is guarded implicitly (it imports WS or fails to boot);
// these broadcasters only fire on a dev save or a prod deploy diff, so a source
// check is the cheap guard.
test("WebSocket broadcasters emit frame types via the WS contract", () => {
  for (const rel of ["server.js", "dev-server/server.js"]) {
    const src = fs.readFileSync(path.join(WEB_ROOT, rel), "utf8");
    assert.match(
      src,
      /import\s*\{[^}]*\bWS\b[^}]*\}\s*from\s*["'][^"']*contracts\/ws-frames\.js["']/,
      `${rel} must import WS from the ws-frames contract`,
    );
    assert.doesNotMatch(
      src,
      /broadcast\(\s*\{\s*type:\s*["']files-changed["']/,
      `${rel} broadcasts a frame type by literal instead of WS`,
    );
  }
});

// WebSocket channel. Open a connection, wait for the initial `hello`
// frame, then close. Anything broken at the upgrade pipeline or the
// JSON contract trips this test before any UI test runs.
test("WS /ws emits hello on connect", async () => {
  const wsUrl = baseUrl.replace(/^http/, "ws") + "/ws";
  const ws = new WebSocket(wsUrl);
  try {
    const payload = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("timeout waiting for hello")), 3000);
      ws.addEventListener("message", (ev) => {
        clearTimeout(timer);
        try { resolve(JSON.parse(ev.data)); } catch (e) { reject(e); }
      }, { once: true });
      ws.addEventListener("error", (e) => { clearTimeout(timer); reject(new Error("ws error")); }, { once: true });
    });
    assert.equal(payload.type, "hello");
    assert.equal(typeof payload.commit, "string");
  } finally {
    try { ws.close(); } catch {}
  }
});

// /api/mermaid-content/* and /steps/* and /dxfs/* are passthroughs to a
// real file under hardware/. Probe one of each, but only if the tree has
// at least one such file — a stripped-down checkout shouldn't fail the
// suite. The route's own behavior is a 400 / 404 for invalid paths,
// already exercised by the dev viewer in the wild.
async function firstFileWithExt(rootDir, ext) {
  if (!fs.existsSync(rootDir)) return null;
  const stack = [rootDir];
  while (stack.length) {
    const dir = stack.pop();
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
    catch { continue; }
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.name.endsWith(ext)) {
        return path.relative(rootDir, full).split(path.sep).join("/");
      }
    }
  }
  return null;
}

test("GET /steps/* returns a STEP file when one exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".step");
  if (!rel) return t.skip("no .step files under hardware/");
  const res = await fetch(`${baseUrl}/steps/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/octet-stream/);
});

test("GET /dxfs/* returns a DXF file when one exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".dxf");
  if (!rel) return t.skip("no .dxf files under hardware/");
  const res = await fetch(`${baseUrl}/dxfs/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/octet-stream/);
});

test("GET /api/mermaid-content/* returns text when a .mmd exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".mmd");
  if (!rel) return t.skip("no .mmd files under hardware/");
  const res = await fetch(`${baseUrl}/api/mermaid-content/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^text\/plain/);
});

// The deck's own pages, served so a card's relative style.css and img/… resolve
// when the printed deck is assembled off them. Skipped on a checkout with no
// cards. A card page must come back as HTML (the browser parses it as a
// document); build machinery in the same directory must not come back at all.
test("GET /cards/* serves a card page but not the deck's build machinery", async (t) => {
  const dir = path.join(REPO_ROOT, "hardware", "assembly", "cards");
  const card = fs.existsSync(dir)
    ? fs.readdirSync(dir).sort().find((f) => f.endsWith(".html") && !f.startsWith("_"))
    : null;
  if (!card) return t.skip("no assembly cards under hardware/");
  const res = await fetch(`${baseUrl}/cards/assembly/cards/${card}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^text\/html/);

  const blocked = await fetch(`${baseUrl}/cards/assembly/cards/_build.py`);
  assert.equal(blocked.status, 400);
});

// A document is a PDF the site hands over whole, and what makes one reachable
// is its sidecar — /docs refuses a PDF that has none, whatever else it is.
// Skipped on a checkout that has built no document.
test("GET /docs/* serves a document but not a PDF with no sidecar", async (t) => {
  const docs = await fetch(`${baseUrl}/api/documents`).then((r) => r.json());
  if (docs.length === 0) return t.skip("no documents under hardware/");
  const res = await fetch(`${baseUrl}/docs/${docs[0].path}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/pdf/);
  assert.match(res.headers.get("content-disposition") || "", /^inline/);

  // Its cover comes through the same route every other picture under hardware/
  // does, so a listing that names one is a listing whose covers load.
  if (docs[0].cover) {
    const cover = await fetch(`${baseUrl}/thumbs/${docs[0].cover}`);
    assert.equal(cover.status, 200);
    assert.match(cover.headers.get("content-type") || "", /^image\/png/);
  }

  const blocked = await fetch(`${baseUrl}/docs/assembly/cards/nothing-here.pdf`);
  assert.equal(blocked.status, 400);
});

// Inner copper planes of a multi-layer board. /api/pcb advertises them in
// `inners`; the content gate must let those filenames through (it's stricter
// than the fixed Top/Bottom/Overlay). Skip when no board has inner layers (a
// repo of only 2-layer boards).
test("GET /api/pcb-content/* serves an inner copper plane", async (t) => {
  const boards = await fetch(`${baseUrl}/api/pcb`).then((r) => r.json());
  const withInner = boards.find((b) => b.inners && b.inners.length);
  if (!withInner) return t.skip("no board with inner planes");
  const inner = withInner.inners[0];
  assert.match(inner, /\.inner\d+\.svg$/, "inners[] should be inner-plane SVG paths");
  const res = await fetch(`${baseUrl}/api/pcb-content/${inner}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^image\/svg\+xml/);
});

// The rest of the wildcard family. Each of these takes the whole tail of the URL
// as one path relative to the content root, and each is the only way its file type
// reaches the page — /models/* alone carries every .glb the 3D grid draws. They are
// tested here because the tail is the argument: a router that hands the route a
// different shape than it expects fails on exactly these, and fails quietly, by
// serving a 400 where a file should be.
test("GET /models/* returns a GLB when one exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".glb");
  if (!rel) return t.skip("no .glb files under hardware/");
  const res = await fetch(`${baseUrl}/models/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/octet-stream/);
});

// `.step.mesh` siblings are written by every export and are not committed, so a
// fresh checkout has none — skip rather than fail.
test("GET /meshes/* returns a tessellation when one exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".mesh");
  if (!rel) return t.skip("no .mesh sidecars under hardware/ (not committed)");
  const res = await fetch(`${baseUrl}/meshes/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/octet-stream/);
});

test("GET /thumbs/* returns a PNG thumbnail when one exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".png");
  if (!rel) return t.skip("no .png thumbnails under hardware/");
  const res = await fetch(`${baseUrl}/thumbs/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^image\/png/);
});

// Pick data is advertised per board by /api/pcb; the route gates on the
// `pcb/…/out/*.picks.json` shape rather than serving arbitrary JSON.
test("GET /api/pcb-picks/* serves a board's pick data", async (t) => {
  const boards = await fetch(`${baseUrl}/api/pcb`).then((r) => r.json());
  const withPicks = boards.find((b) => b.picks);
  if (!withPicks) return t.skip("no board advertises pick data");
  const res = await fetch(`${baseUrl}/api/pcb-picks/${withPicks.picks}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/json/);

  const blocked = await fetch(`${baseUrl}/api/pcb-picks/ledger/bom.json`);
  assert.equal(blocked.status, 400, "JSON outside a board's out/ is not pick data");
});

test("GET /api/step-scorecard/* serves a scorecard sidecar when one exists", async (t) => {
  const rel = await firstFileWithExt(path.join(REPO_ROOT, "hardware"), ".scorecard.json");
  if (!rel) return t.skip("no .scorecard.json sidecars under hardware/");
  const res = await fetch(`${baseUrl}/api/step-scorecard/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^application\/json/);
});

// CONFINEMENT IS THE ONE BEHAVIOUR OF THE TAIL THAT MUST NOT MOVE. Every route above
// resolves its tail against the content root and must refuse to leave it, whether the
// climb is written plainly or percent-encoded — the router decodes before the route
// ever sees it, so both arrive as the same string and both have to be turned away.
test("the wildcard routes stay inside the content root", async () => {
  const climbs = [
    "../../etc/passwd.step",
    "%2e%2e%2f%2e%2e%2fetc%2fpasswd.step",
    "a/../../../../etc/passwd.step",
  ];
  for (const climb of climbs) {
    for (const route of ["/steps", "/models", "/meshes", "/dxfs"]) {
      const res = await fetch(`${baseUrl}${route}/${climb}`);
      assert.ok(
        res.status === 400 || res.status === 404,
        `${route}/${climb} answered ${res.status}; a climb must be refused`,
      );
    }
  }
});

// Phase 4 viewer split (/css/viewer.css, /js/viewer/*.js) is in flight on
// a parallel branch. Test what's there today; skip what isn't so this
// suite keeps passing while the split lands.
test("GET /css/viewer.css", async (t) => {
  const file = path.join(WEB_ROOT, "public", "css", "viewer.css");
  if (!fs.existsSync(file)) return t.skip("viewer.css not yet present");
  const res = await fetch(baseUrl + "/css/viewer.css");
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^text\/css/);
});

test("GET /js/viewer/main.js", async (t) => {
  const file = path.join(WEB_ROOT, "public", "js", "viewer", "main.js");
  if (!fs.existsSync(file)) return t.skip("viewer/main.js not yet present");
  const res = await fetch(baseUrl + "/js/viewer/main.js");
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^text\/javascript/);
});

// EVERY PAGE THE SHELL DRAWS CARRIES THE BELL, so the route it points at is a route this
// boot serves. `renderNav` puts `/notifications` in the nav unconditionally; a boot with no
// DATABASE_URL has no pool and holds no rows, which is the empty answer these give.
test("the nav bell leads somewhere on a boot with no database", async () => {
  const page = await fetch(baseUrl + "/notifications");
  assert.equal(page.status, 200, "the bell in every page's nav must not 404");

  const shell = await (await fetch(baseUrl + "/3d")).text();
  assert.ok(shell.includes('href="/notifications"'), "the nav renders the bell");

  for (const [route, want] of [
    ["/api/notifications?token=x", { items: [] }],
    ["/api/notifications/unread-count?token=x", { count: 0 }],
  ]) {
    const res = await fetch(baseUrl + route);
    assert.equal(res.status, 200, route);
    assert.deepEqual(await res.json(), want, `${route} answers empty without a pool`);
  }
});

// Routes we deliberately don't test:
//   POST /api/subscribe        — needs Postgres; bails 503 without DATABASE_URL
//   POST /api/push/subscribe   — same
//   POST /api/push/unsubscribe — same
//   GET  /api/push/subscription — returns {files: []} without DB; not load-bearing
//
// These need a real database fixture and FCM credentials; that's a
// different layer of test (integration, not smoke) and out of scope.
