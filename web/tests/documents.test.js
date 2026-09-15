import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import express from "express";
import { mountViewerRoutes } from "../lib/viewer-routes.js";

test("only the owner quick start is published even when builds restore older sidecars", async (t) => {
  const hardwareDir = fs.mkdtempSync(path.join(os.tmpdir(), "owner-guide-"));
  t.after(() => fs.rmSync(hardwareDir, { recursive: true, force: true }));
  const published = ["quickstart-codex/quick-start-codex.pdf", "install-guide/install-guide.pdf"];
  const superseded = [
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
  }
  for (const relative of published) {
    const response = await fetch(base + "/docs/" + relative);
    assert.equal(response.status, 200, relative);
    assert.match(response.headers.get("content-type"), /^application\/pdf/);
    assert.equal(await response.text(), "%PDF-1.4\n");
  }
});
