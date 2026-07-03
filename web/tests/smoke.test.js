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
// posts/, etc. Tests need both paths.
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
  { path: "/blog",     expect: 200, ct: "text/html" },
  { path: "/settings", expect: 200, ct: "text/html" },

  // Legacy redirects (301). Don't pin Content-Type — express renders a
  // tiny HTML body for browsers but the assertion that matters is the
  // redirect itself.
  { path: "/dev",          expect: 301 },
  { path: "/dev/diagrams", expect: 301 },
  { path: "/dev/mermaid",  expect: 301 },
  { path: "/dev/settings", expect: 301 },

  // JSON APIs that don't touch Postgres
  { path: "/blog/posts?offset=0", expect: 200, ct: "application/json" },
  { path: "/api/steps",           expect: 200, ct: "application/json" },
  { path: "/api/dxf",             expect: 200, ct: "application/json" },
  { path: "/api/mermaid",         expect: 200, ct: "application/json" },
  { path: "/api/drawings",        expect: 200, ct: "application/json" },
  { path: "/api/firebase-config", expect: 200, ct: "application/json" },

  // Service worker variants — same body, three URLs (root, /3d, legacy /dev)
  { path: "/firebase-messaging-sw.js",     expect: 200, ct: "application/javascript" },
  { path: "/3d/firebase-messaging-sw.js",  expect: 200, ct: "application/javascript" },
  { path: "/dev/firebase-messaging-sw.js", expect: 200, ct: "application/javascript" },

  // PWA / favicon images — express sets image/* content-type from extension.
  { path: "/apple-touch-icon.png",             expect: 200, ct: "image/png" },
  { path: "/apple-touch-icon-precomposed.png", expect: 200, ct: "image/png" },
  { path: "/favicon.ico",                      expect: 200, ct: "image/png" },
  { path: "/favicon.png",                      expect: 200, ct: "image/png" },

  // Static JS bundles served via express.static(public/). Each one is
  // imported by at least one HTML surface; if one disappears the page
  // breaks at runtime with a console-only error, so a 404 here is a
  // real regression. Content-Type comes from express's mime db.
  { path: "/boot.js",             expect: 200, ct: "application/javascript" },
  { path: "/landing.js",          expect: 200, ct: "application/javascript" },
  { path: "/settings.js",         expect: 200, ct: "application/javascript" },
  { path: "/blog.js",             expect: 200, ct: "application/javascript" },
  { path: "/pan-zoom.js",         expect: 200, ct: "application/javascript" },
  { path: "/content-viewer.js",   expect: 200, ct: "application/javascript" },
  { path: "/glass-animation.js",  expect: 200, ct: "application/javascript" },

  // Contract definitions served to the browser: web/contracts/ mounted at
  // /contracts. The viewer imports HSM_EVENTS + WS from these at runtime, so a
  // 404 here breaks boot.js and the pickers with a module-load error. (Only the
  // .js contracts are browser-imported; the .ts ones are builder-side.)
  { path: "/contracts/client-events.js", expect: 200, ct: "application/javascript" },
  { path: "/contracts/ws-frames.js",     expect: 200, ct: "application/javascript" },
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
      /broadcast\(\s*\{\s*type:\s*["'](?:files-changed|posts-changed)["']/,
      `${rel} broadcasts a frame type by literal instead of WS`,
    );
  }
});

// Blog infinite-scroll contract. /blog/posts hands the client rendered
// HTML plus the cursor for the next request; the client appends html and
// stops when hasMore goes false. Shape has to hold even on an empty tree
// (no posts/ dir): html "", nextOffset 0, hasMore false.
test("GET /blog/posts returns a paginated JSON page", async () => {
  const res = await fetch(`${baseUrl}/blog/posts?offset=0`);
  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(typeof data.html, "string");
  assert.equal(typeof data.nextOffset, "number");
  assert.equal(typeof data.hasMore, "boolean");
  // Any image in the feed must be lazy — that's the whole point of paging,
  // and an eager <img> would drag the up-front payload back in.
  if (data.html.includes("<img")) {
    assert.match(data.html, /<img[^>]*loading="lazy"/);
  }
  // A negative/garbage offset must clamp to 0 rather than error.
  const bad = await fetch(`${baseUrl}/blog/posts?offset=-5`);
  assert.equal(bad.status, 200);
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

// Line-art SVG passthrough. Walk hardware/ for a .svg inside any
// drawings/ directory; skip if none exist (a stripped checkout). The
// content-type is image/svg+xml so the browser inlines it correctly when
// the modal injects it via DOMParser.
async function firstDrawingPath(rootDir) {
  if (!fs.existsSync(rootDir)) return null;
  const stack = [{ dir: rootDir, inDrawings: false }];
  while (stack.length) {
    const { dir, inDrawings } = stack.pop();
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { continue; }
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      const childInDrawings = inDrawings || entry.name === "drawings";
      if (entry.isDirectory()) stack.push({ dir: full, inDrawings: childInDrawings });
      else if (inDrawings && entry.name.endsWith(".svg")) {
        return path.relative(rootDir, full).split(path.sep).join("/");
      }
    }
  }
  return null;
}

test("GET /api/drawing-content/* returns SVG when a drawing exists", async (t) => {
  const rel = await firstDrawingPath(path.join(REPO_ROOT, "hardware"));
  if (!rel) return t.skip("no drawings/ SVGs under hardware/");
  const res = await fetch(`${baseUrl}/api/drawing-content/${rel}`);
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^image\/svg\+xml/);
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
  assert.match(res.headers.get("content-type") || "", /^application\/javascript/);
});

// Routes we deliberately don't test:
//   POST /api/subscribe        — needs Postgres; bails 503 without DATABASE_URL
//   POST /api/push/subscribe   — same
//   POST /api/push/unsubscribe — same
//   GET  /api/push/subscription — returns {files: []} without DB; not load-bearing
//   GET  /notifications        — only mounted when pool is non-null
//   GET  /api/notifications*   — same
//   POST /api/notifications/seen — same
//
// These need a real database fixture and FCM credentials; that's a
// different layer of test (integration, not smoke) and out of scope.
