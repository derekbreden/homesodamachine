import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { start } from "../server.js";

let server, baseUrl;
before(async () => {
  ({ server } = await start({ dev: false, port: 0 }));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  server?.closeAllConnections?.();
  if (server) await new Promise(resolve => server.close(resolve));
});

test("the nameplate opens a machine page with working navigation, artwork and guides", async () => {
  const localLinks = new Set();
  for (const route of ["/0001", "/0001/get-started", "/0001/guides"]) {
    const response = await fetch(baseUrl + route);
    assert.equal(response.status, 200, route);
    assert.match(response.headers.get("content-type"), /^text\/html/);
    const html = await response.text();
    assert.match(html, /data-unit="0001"/);
    assert.ok(html.includes(`href="${route}" aria-current="page"`), route);
    assert.ok(html.includes(`rel="canonical" href="https://homesodamachine.com${route}"`));
    for (const match of html.matchAll(/(?:href|src)="(\/[^"#]*)(?:#[^"]*)?"/g)) {
      localLinks.add(match[1]);
    }
  }
  for (const link of localLinks) {
    const response = await fetch(baseUrl + link, { method: "HEAD" });
    assert.equal(response.status, 200, `unit page links to ${link}`);
    if (link.endsWith(".pdf")) assert.match(response.headers.get("content-type"), /^application\/pdf/);
    if (link.endsWith(".webp")) assert.match(response.headers.get("content-type"), /^image\/webp/);
  }
});

test("only registered four-digit units and their named pages resolve", async () => {
  for (const route of ["/0000", "/0002", "/9999/guides", "/001", "/00001", "/0001/unknown", "/0001/get-started/extra"]) {
    const response = await fetch(baseUrl + route);
    assert.equal(response.status, 404, route);
  }
});

test("trailing slashes canonicalize while retaining the query", async () => {
  for (const route of ["/0001", "/0001/get-started", "/0001/guides"]) {
    const response = await fetch(`${baseUrl}${route}/?from=plate&label=one%20machine`, { redirect: "manual" });
    assert.equal(response.status, 301);
    assert.equal(response.headers.get("location"), `${route}?from=plate&label=one%20machine`);
  }
});
