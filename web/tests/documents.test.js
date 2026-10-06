import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import express from "express";
import { mountViewerRoutes } from "../lib/viewer-routes.js";

test("Letter shop guides are published and archived decks stay retired after artifact restore", async (t) => {
  const hardwareDir = fs.mkdtempSync(path.join(os.tmpdir(), "owner-guide-"));
  t.after(() => fs.rmSync(hardwareDir, { recursive: true, force: true }));
  const published = ["install-guide/install-guide.pdf",
    "drill-and-cut-guide/drill-and-cut-guide.pdf", "mold-guide/mold-guide.pdf",
    "refrigeration-guide/refrigeration-guide.pdf",
    "assembly-letter-guide/assembly-drill-and-weld-letter.pdf"];
  const superseded = [
    "assembly/cards/deck.pdf",
    "assembly/cards/tools/deck-tools.pdf",
    "quickstart-codex/quick-start-codex.pdf",
    "quickstart/quick-start.pdf",
    "quickstart-claude/quick-start-claude.pdf",
    "quickstart-codex/edge-study.pdf",
    "quickstart-codex/contour-alternates.pdf",
  ];
  for (const relative of [...published, ...superseded]) {
    const pdf = path.join(hardwareDir, relative);
    fs.mkdirSync(path.dirname(pdf), { recursive: true });
    fs.writeFileSync(pdf, "%PDF-1.4\n");
    fs.writeFileSync(pdf + ".json", JSON.stringify({ title: relative, pages: 1 }));
  }
  const app = express();
  mountViewerRoutes(app, { hardwareDir });
  const server = app.listen(0, "127.0.0.1");
  await new Promise((resolve) => server.once("listening", resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const base = `http://127.0.0.1:${server.address().port}`;

  const shelf = await fetch(base + "/api/documents");
  assert.equal(shelf.status, 200);
  assert.deepEqual((await shelf.json()).map((doc) => doc.path).sort(), [...published].sort());
  for (const relative of superseded) {
    assert.equal((await fetch(base + "/docs/" + relative)).status, 410, relative);
    assert.equal((await fetch(base + "/read/" + relative)).status, 410, relative);
  }
  for (const relative of published) {
    const response = await fetch(base + "/docs/" + relative);
    assert.equal(response.status, 200, relative);
    assert.match(response.headers.get("content-type"), /^application\/pdf/);
    assert.equal(await response.text(), "%PDF-1.4\n");
  }
});

test("document navigation opens HTML while raw reads, ranges and downloads keep PDF bytes", async (t) => {
  const hardwareDir = fs.mkdtempSync(path.join(os.tmpdir(), "pdf-reader-"));
  t.after(() => fs.rmSync(hardwareDir, { recursive: true, force: true }));
  const relative = "manual/install guide.pdf";
  const pdf = path.join(hardwareDir, relative);
  fs.mkdirSync(path.dirname(pdf), { recursive: true });
  fs.writeFileSync(pdf, "%PDF-1.4\n");
  fs.writeFileSync(pdf + ".json", JSON.stringify({ title: 'Install <guide> & "care"' }));
  fs.writeFileSync(path.join(hardwareDir, "manual/datasheet.pdf"), "%PDF-1.4\n");
  const app = express();
  mountViewerRoutes(app, { hardwareDir });
  const server = app.listen(0, "127.0.0.1");
  await new Promise(resolve => server.once("listening", resolve));
  t.after(() => new Promise(resolve => server.close(resolve)));
  const base = `http://127.0.0.1:${server.address().port}`;
  const route = "/docs/manual/install%20guide.pdf";

  const navigation = await fetch(base + route, { headers: { Accept: "text/html,application/xhtml+xml" }, redirect: "manual" });
  assert.equal(navigation.status, 302);
  assert.equal(navigation.headers.get("location"), "/read/manual/install%20guide.pdf");
  assert.equal(navigation.headers.get("vary"), "Accept");
  const htmlResponse = await fetch(base + navigation.headers.get("location"));
  assert.match(htmlResponse.headers.get("content-type"), /^text\/html/);
  assert.equal(htmlResponse.headers.get("cache-control"), "no-cache");
  const html = await htmlResponse.text();
  assert.ok(html.includes('data-pdf-url="/docs/manual/install%20guide.pdf?raw=1"'));
  assert.ok(html.includes('Install &lt;guide&gt; &amp; &quot;care&quot;'));
  assert.doesNotMatch(html, /<(iframe|embed|object)\b|\/js\/viewer\/main\.js/);

  const raw = await fetch(base + route + "?raw=1", { headers: { Accept: "text/html" } });
  assert.match(raw.headers.get("content-type"), /^application\/pdf/);
  assert.equal(await raw.text(), "%PDF-1.4\n");
  const range = await fetch(base + route + "?raw=1", { headers: { Range: "bytes=0-3" } });
  assert.equal(range.status, 206);
  assert.equal(await range.text(), "%PDF");
  const download = await fetch(base + route + "?download=1", { headers: { Accept: "text/html" } });
  assert.match(download.headers.get("content-disposition"), /^attachment;/);
  assert.equal(await download.text(), "%PDF-1.4\n");

  for (const path of ["/read/manual/datasheet.pdf", "/read/manual/no-sidecar.pdf", "/read/manual/not-pdf.txt", "/read/%2e%2e%2fsecret.pdf"]) {
    assert.equal((await fetch(base + path)).status, 400, path);
  }
  const missing = path.join(hardwareDir, "manual/missing.pdf.json");
  fs.writeFileSync(missing, "{}");
  assert.equal((await fetch(base + "/read/manual/missing.pdf")).status, 404);

  const vendor = html.match(/data-pdfjs-base="([^"]+)"/)[1];
  for (const asset of ["legacy/build/pdf.mjs", "legacy/build/pdf.worker.mjs", "web/pdf_viewer.css", "standard_fonts/LiberationSans-Regular.ttf", "wasm/openjpeg.wasm"]) {
    const response = await fetch(`${base}${vendor}/${asset}`);
    assert.equal(response.status, 200, asset);
    assert.match(response.headers.get("cache-control"), /immutable/);
    await response.arrayBuffer();
  }
});
