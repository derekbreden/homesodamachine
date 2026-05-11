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
const REPO_ROOT = path.resolve(__dirname, "..");

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
  // The SSE handler holds a setInterval and a long-lived response open.
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
  { path: "/api/steps",           expect: 200, ct: "application/json" },
  { path: "/api/dxf",             expect: 200, ct: "application/json" },
  { path: "/api/mermaid",         expect: 200, ct: "application/json" },
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

// SSE channel. The endpoint is a long-lived stream, so we open the
// connection, verify headers + the initial `hello` event, then abort.
test("GET /api/events emits hello on connect", async () => {
  const ctrl = new AbortController();
  const res = await fetch(baseUrl + "/api/events", { signal: ctrl.signal });
  try {
    assert.equal(res.status, 200);
    assert.match(res.headers.get("content-type") || "", /^text\/event-stream/);

    // Read just enough to see the first event frame.
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    // Stream events are separated by `\n\n` per the SSE spec.
    while (!buf.includes("\n\n")) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
    }
    assert.match(buf, /^data: \{/m, "expected an SSE data frame");
    const dataLine = buf.split("\n").find((l) => l.startsWith("data: "));
    const payload = JSON.parse(dataLine.slice("data: ".length));
    assert.equal(payload.type, "hello");
    assert.equal(typeof payload.commit, "string");
  } finally {
    ctrl.abort();
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

// Phase 4 viewer split (/css/viewer.css, /js/viewer/*.js) is in flight on
// a parallel branch. Test what's there today; skip what isn't so this
// suite keeps passing while the split lands.
test("GET /css/viewer.css", async (t) => {
  const file = path.join(REPO_ROOT, "public", "css", "viewer.css");
  if (!fs.existsSync(file)) return t.skip("viewer.css not yet present");
  const res = await fetch(baseUrl + "/css/viewer.css");
  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") || "", /^text\/css/);
});

test("GET /js/viewer/main.js", async (t) => {
  const file = path.join(REPO_ROOT, "public", "js", "viewer", "main.js");
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
