// The short host redirects, and nothing else does.
//
// `hosm.us` reaches this process as a Host header — it is a second custom domain
// on the one Render service — so the test is a request to the local server
// carrying that header. `node:http` is used rather than fetch because the test
// sets `Host` itself and reads the 301 without following it; both are things
// fetch takes away.

import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";

import { start } from "../server.js";

let server;
let port;

before(async () => {
  const started = await start({ dev: false, port: 0 });
  server = started.server;
  port = server.address().port;
});

after(async () => {
  if (!server) return;
  server.closeAllConnections?.();
  await new Promise((resolve) => server.close(resolve));
});

function get(path, host) {
  return new Promise((resolve, reject) => {
    const req = http.request(
      { host: "127.0.0.1", port, path, method: "GET", headers: { Host: host } },
      (res) => {
        res.resume();
        res.on("end", () =>
          resolve({ status: res.statusCode, location: res.headers.location }));
      },
    );
    req.on("error", reject);
    req.end();
  });
}

// Every path on the short host lands on the same path on the canonical one.
const carried = [
  ["/0001", "https://homesodamachine.com/0001"],
  ["/", "https://homesodamachine.com/"],
  ["/3d", "https://homesodamachine.com/3d"],
  ["/updates?tag=cad", "https://homesodamachine.com/updates?tag=cad"],
  // A path that is not a route here is still a route there, and either way the
  // short host does not decide that — it never looks.
  ["/nothing-here", "https://homesodamachine.com/nothing-here"],
];

for (const [path, location] of carried) {
  test(`hosm.us${path} -> ${location}`, async () => {
    const res = await get(path, "hosm.us");
    assert.equal(res.status, 301);
    assert.equal(res.location, location);
  });
}

test("www.hosm.us redirects the same way", async () => {
  const res = await get("/0001", "www.hosm.us");
  assert.equal(res.status, 301);
  assert.equal(res.location, "https://homesodamachine.com/0001");
});

test("the host match is case-insensitive", async () => {
  const res = await get("/0001", "HOSM.US");
  assert.equal(res.status, 301);
  assert.equal(res.location, "https://homesodamachine.com/0001");
});

test("a port on the Host header does not defeat the match", async () => {
  const res = await get("/0001", "hosm.us:443");
  assert.equal(res.status, 301);
  assert.equal(res.location, "https://homesodamachine.com/0001");
});

// Certificate validation asks about the host it was sent to. A redirect to a
// different host answers about the wrong one, so this path stays put.
test("/.well-known/ is not redirected", async () => {
  const res = await get("/.well-known/acme-challenge/token", "hosm.us");
  assert.notEqual(res.status, 301);
});

// The canonical host and Render's own hostname are untouched.
test("the canonical host is served, not redirected", async () => {
  const res = await get("/", "homesodamachine.com");
  assert.equal(res.status, 200);
});

test("the render hostname is served, not redirected", async () => {
  const res = await get("/", "homesodamachine.onrender.com");
  assert.equal(res.status, 200);
});

// A host that merely ends in the short one is a different host.
test("a lookalike host is not redirected", async () => {
  const res = await get("/", "nothosm.us");
  assert.equal(res.status, 200);
});
