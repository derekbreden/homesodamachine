#!/usr/bin/env node
// render-thumbnails.js — (re)render the grid thumbnail PNG for one or more
// STEP files by driving the real /3d viewer headlessly, so the committed
// thumbnail is pixel-identical to the live detail view (x-ray ghost + edges).
//
// This is what makes grid browsing cheap: the page downloads a ~tens-of-KB
// PNG per card instead of fetching the (up to ~17 MB) STEP and parsing +
// WebGL-rendering it in the browser on every visit. The thumbnail is a pure
// function of the STEP, so it's rendered once — here — when the part changes.
//
// Invoked two ways:
//   - hardware/_cadq_export.py queues each STEP it (re)writes and runs this at
//     process exit, so any script that produces a STEP — however it's run
//     (dev-server watcher, an agent, by hand) — refreshes its own thumbnail.
//   - Manually / for backfill.
//
// Usage:
//   node tools/render/render-thumbnails.js <step-path>...   # specific files
//   node tools/render/render-thumbnails.js --all            # every STEP under hardware/
//
// <step-path> may be absolute or repo-relative, and is matched against the
// content roots (hardware/ = kitchen, pie-in-the-sky/lite/ = lite). The
// output is written next to the STEP as `<file>.step.png`. Files are grouped
// by root so the viewer is booted once per root; rendering reuses one browser
// page across all of a root's files.
//
// Best-effort by design: a single file that fails to render logs a warning
// and is skipped; the process still exits 0 as long as it booted, so the
// calling export never fails over a thumbnail.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../web/server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

// Content roots the viewer can serve, in match order. Each STEP belongs to
// exactly one; the viewer is booted with hardwareDir set to that root so
// /steps/<rel> resolves against it.
const ROOTS = [
  { name: "kitchen", dir: path.join(REPO_ROOT, "hardware") },
  { name: "lite", dir: path.join(REPO_ROOT, "pie-in-the-sky", "lite") },
];

function isHidden(rel) {
  return rel.split(path.sep).some((seg) => seg.startsWith("."));
}

// Recursively collect every .step under dir, repo-relative-to-root, skipping
// dotfiles/dotdirs (atomic-write temps live as .<name>.step.<rand>.step) and
// node_modules.
function walkSteps(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walkSteps(full));
    else if (entry.name.endsWith(".step")) out.push(full);
  }
  return out;
}

// Resolve a CLI path to { root, rel, abs } or null if it isn't an existing
// .step under a known root. Accepts absolute paths (what _cadq_export passes),
// repo-relative paths, and root-relative paths (the `/steps/` convention,
// e.g. `printed-parts/.../foo.step`).
function classify(p) {
  const candidates = path.isAbsolute(p)
    ? [path.resolve(p)]
    : [path.resolve(REPO_ROOT, p), ...ROOTS.map((r) => path.resolve(r.dir, p))];
  for (const abs of candidates) {
    if (!abs.endsWith(".step") || !fs.existsSync(abs)) continue;
    for (const root of ROOTS) {
      if (abs === root.dir || abs.startsWith(root.dir + path.sep)) {
        return { root, rel: path.relative(root.dir, abs), abs };
      }
    }
  }
  return null;
}

// Render every `rel` under one root into `<root>/<rel>.png`. Boots the viewer
// pointed at that root, opens one page, and calls the viewer's own
// renderThumbnail (the same function the detail view's offscreen thumbnailer
// uses) so the PNG matches the live x-ray look exactly. Returns the count
// written.
async function renderRootGroup(root, rels) {
  const { server } = await start({ port: 0, dev: false, hardwareDir: root.dir });
  const port = server.address().port;
  let browser;
  let written = 0;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });
    const page = await browser.newPage();
    page.on("pageerror", (err) => console.error("pageerror:", err.message));

    // Load the viewer shell once; renderThumbnail awaits the occt-import-js
    // wasm internally, so we only need __hsm (set when main.js evaluates).
    await page.goto(`http://localhost:${port}/3d`, {
      waitUntil: "domcontentloaded",
      timeout: 60000,
    });
    await page.waitForFunction(() => !!window.__hsm, { timeout: 30000 });

    for (const rel of rels) {
      const relUrl = rel.split(path.sep).join("/"); // POSIX path for the URL/fetch
      try {
        const dataURL = await page.evaluate(async (file) => {
          const m = await import("/js/viewer/step.js");
          return await m.renderThumbnail(file);
        }, relUrl);
        if (!dataURL) {
          console.warn(`  ! skipped (render returned null): ${relUrl}`);
          continue;
        }
        const raw = Buffer.from(dataURL.split(",")[1], "base64");
        // Re-encode through sharp for a smaller, consistent PNG.
        const buf = await sharp(raw).png({ compressionLevel: 9 }).toBuffer();
        const outAbs = path.join(root.dir, rel + ".png");
        fs.writeFileSync(outAbs, buf);
        written++;
        console.log(`  ✓ ${relUrl} (${buf.length} bytes)`);
      } catch (e) {
        console.warn(`  ! skipped (${e.message || e}): ${relUrl}`);
      }
    }
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(() => resolve()));
  }
  return written;
}

async function main() {
  const args = process.argv.slice(2);
  let targets = [];

  if (args.includes("--all")) {
    targets = walkSteps(ROOTS[0].dir).map((abs) => ({
      root: ROOTS[0],
      rel: path.relative(ROOTS[0].dir, abs),
      abs,
    }));
  } else {
    for (const a of args) {
      const c = classify(a);
      if (!c) {
        console.warn(`skipping (not a .step under a known content root): ${a}`);
        continue;
      }
      if (isHidden(c.rel)) continue; // atomic-write temp or hidden path
      targets.push(c);
    }
  }

  if (targets.length === 0) {
    console.log("no STEP thumbnails to render");
    return;
  }

  // Group by root so the server boots once per root.
  const byRoot = new Map();
  for (const t of targets) {
    if (!byRoot.has(t.root)) byRoot.set(t.root, []);
    byRoot.get(t.root).push(t.rel);
  }

  let total = 0;
  for (const [root, rels] of byRoot) {
    console.log(`rendering ${rels.length} thumbnail(s) under ${root.name}/...`);
    total += await renderRootGroup(root, rels);
  }
  console.log(`done: ${total} thumbnail(s) written`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
