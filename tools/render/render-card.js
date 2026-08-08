#!/usr/bin/env node
// render-card.js — render a local HTML file to a PNG at an exact pixel size.
// For print artifacts (4x6 assembly instruction cards) where the pixel grid
// IS the deliverable: no device emulation, no trimming, no resampling.
//
// Usage:
//   node tools/render/render-card.js <input.html> <output-png> [options]
//   node tools/render/render-card.js --batch <dir> <out-dir> [options]
//
// Options:
//   --size WxH   viewport = output pixels at DPR 1. Default 1800x1200 (6x4in @ 300dpi)
//   --dpr f      deviceScaleFactor; output = size · dpr. Default 1
//                (1.2 → 2160x1440 = 360dpi, the EcoTank's native grid)
//
// Batch mode renders every *.html in <dir> (sorted) to <out-dir>/<name>.png in
// one browser session, and reports any card whose content overflows the
// viewport, or spills out of its own header/main/footer band into a
// neighbouring one — either is a layout bug, not a printable card.

import path from "path";
import fs from "fs";
import { pathToFileURL } from "url";
import { closeBrowser, launchBrowser, sweepAbandonedBrowsers } from "./browser.js";

function usage(msg) {
  if (msg) console.error(`render-card: ${msg}`);
  console.error(
    "usage: node tools/render/render-card.js <input.html> <output-png> [--size WxH] [--dpr f]\n" +
      "       node tools/render/render-card.js --batch <dir> <out-dir> [--size WxH] [--dpr f]",
  );
  process.exit(1);
}

function parseArgs(argv) {
  const positional = [];
  const opts = { width: 1800, height: 1200, dpr: 1, batch: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => (a.includes("=") ? a.split("=").slice(1).join("=") : argv[++i]);
    if (a.startsWith("--size")) {
      const m = String(val()).match(/^(\d+)x(\d+)$/);
      if (!m) usage("bad --size");
      opts.width = Number(m[1]);
      opts.height = Number(m[2]);
    } else if (a.startsWith("--dpr")) opts.dpr = Number(val());
    else if (a === "--batch") opts.batch = true;
    else positional.push(a);
  }
  if (!Number.isFinite(opts.dpr) || opts.dpr <= 0) usage("bad --dpr");
  return { positional, opts };
}

async function renderPage(page, htmlAbs, outAbs, opts) {
  await page.goto(pathToFileURL(htmlAbs).href, {
    waitUntil: "networkidle0",
    timeout: 60000,
  });
  // Fonts can land after networkidle0; block on the font readiness promise.
  await page.evaluate(() => document.fonts.ready);

  // A card that scrolls is a card that will be cropped at print — and so is
  // one whose flex/grid children get clipped inside an overflow:hidden root
  // without ever growing scrollWidth/Height. Catch both: scan every element's
  // border box against the canvas (2px grace for antialiased edges).
  const overflow = await page.evaluate(() => {
    const W = document.documentElement.clientWidth;
    const H = document.documentElement.clientHeight;
    let x = document.documentElement.scrollWidth - W;
    let y = document.documentElement.scrollHeight - H;
    const clipped = [];
    for (const el of document.querySelectorAll("body *")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      const over = Math.max(r.right - W, r.bottom - H);
      if (over > 2) {
        clipped.push(
          `${el.tagName.toLowerCase()}${el.className ? "." + String(el.className).split(" ")[0] : ""}+${Math.round(over)}px`,
        );
        x = Math.max(x, r.right - W);
        y = Math.max(y, r.bottom - H);
      }
    }
    return { x: Math.max(0, Math.round(x)), y: Math.max(0, Math.round(y)), clipped: clipped.slice(0, 5) };
  });

  // The canvas check above only sees content leaving the page. A card is three
  // stacked bands — header / main / footer — and content that outgrows its band
  // lands on the next one while staying well inside the canvas: the tools strip
  // printed across the DONE-WHEN rule. That is a collision between two bands'
  // boxes, so measure it as one — how far an element reaches into a band it does
  // not belong to. The slack a band leaves inside itself (main's bottom padding,
  // the footer's top margin) is breathing room, not a second canvas: crossing it
  // is tight, entering the next band is a printed overlap.
  const spills = await page.evaluate(() => {
    const bands = [...document.querySelectorAll(".card > header, .card > main, .card > footer")].map(
      (el) => ({ el, name: el.tagName.toLowerCase(), box: el.getBoundingClientRect() }),
    );
    const out = [];
    for (const band of bands) {
      const others = bands.filter((o) => o !== band);
      let worst = null;
      for (const el of band.el.querySelectorAll("*")) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        for (const o of others) {
          // Vertically stacked, full-bleed bands: the overlap is the vertical one.
          const into = Math.min(r.bottom, o.box.bottom) - Math.max(r.top, o.box.top);
          if (into > 2 && (!worst || into > worst.into)) {
            worst = {
              into: Math.round(into),
              onto: o.name,
              el: `${el.tagName.toLowerCase()}${el.className ? "." + String(el.className).split(" ")[0] : ""}`,
            };
          }
        }
      }
      if (worst) out.push(`${band.name}'s ${worst.el} ${worst.into}px into ${worst.onto}`);
    }
    return out;
  });

  // The quiet twin of a spill: a panel is overflow:hidden, so content its own
  // box cannot hold is not printed over — it is not printed at all. A caption
  // eaten this way leaves no mark on the page to notice.
  const clipped = await page.evaluate(() => {
    const out = [];
    for (const el of document.querySelectorAll("body *")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      for (let p = el.parentElement; p; p = p.parentElement) {
        const ps = getComputedStyle(p);
        if (ps.overflowX === "visible" && ps.overflowY === "visible") continue;
        const pr = p.getBoundingClientRect();
        // 4px of grace: an SVG <text>'s box carries its leading above the ink,
        // so a label sitting on the viewBox edge measures a hair outside it.
        const lost = Math.max(r.bottom - pr.bottom, r.right - pr.right, pr.top - r.top, pr.left - r.left);
        if (lost > 4) {
          out.push(
            `${el.tagName.toLowerCase()}${el.className ? "." + String(el.className).split(" ")[0] : ""}` +
              ` -${Math.round(lost)}px by ${p.tagName.toLowerCase()}${p.className ? "." + String(p.className).split(" ")[0] : ""}`,
          );
        }
        break; // nearest clipping ancestor decides
      }
    }
    return [...new Set(out)].slice(0, 4);
  });

  // With the caption holding its ground, an over-full column shows up as a
  // render pressed below its own aspect ratio. Nothing is lost, so nothing
  // looks wrong — but the picture the card was built around is shrinking, and
  // that is the column asking for a shorter card.
  const squeezed = await page.evaluate(() => {
    const out = [];
    for (const el of document.querySelectorAll(".panel img, .panel svg")) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      let aspect = 0;
      if (el.tagName === "IMG") {
        if (!el.naturalWidth) continue;
        aspect = el.naturalHeight / el.naturalWidth;
      } else {
        const vb = el.viewBox?.baseVal;
        if (!vb || !vb.width) continue;
        aspect = vb.height / vb.width;
      }
      const natural = r.width * aspect;
      const pct = Math.round((100 * r.height) / natural);
      if (pct < 96) out.push(`${el.tagName.toLowerCase()} at ${pct}% of aspect height`);
    }
    return out.slice(0, 3);
  });

  await page.screenshot({
    path: outAbs,
    type: "png",
    clip: { x: 0, y: 0, width: opts.width, height: opts.height },
  });
  return { ...overflow, spills, clipped, squeezed };
}

async function main() {
  const { positional, opts } = parseArgs(process.argv.slice(2));
  const [inRel, outRel] = positional;
  if (!inRel || !outRel) usage("missing arguments");

  const jobs = [];
  if (opts.batch) {
    const dir = path.resolve(inRel);
    const outDir = path.resolve(outRel);
    fs.mkdirSync(outDir, { recursive: true });
    const files = fs
      .readdirSync(dir)
      .filter((f) => f.endsWith(".html"))
      .sort();
    if (!files.length) usage(`no .html files in ${dir}`);
    for (const f of files) {
      jobs.push({
        htmlAbs: path.join(dir, f),
        outAbs: path.join(outDir, f.replace(/\.html$/, ".png")),
      });
    }
  } else {
    const outAbs = path.resolve(outRel);
    fs.mkdirSync(path.dirname(outAbs), { recursive: true });
    jobs.push({ htmlAbs: path.resolve(inRel), outAbs });
  }

  sweepAbandonedBrowsers("render-card");
  const browser = await launchBrowser({
    args: ["--force-color-profile=srgb"],
    // A card is a local HTML file with local images and no script — it draws in
    // about a second, and puppeteer's 180 s default is a ceiling nothing here
    // can reach on purpose. Held down so a card that has stopped answering
    // costs the deck a fifth of a minute rather than three, ninety-five times:
    // this is the budget for a page that never comes back, not for a slow one.
    protocolTimeout: Number(process.env.HSM_CARD_TIMEOUT || 60000),
  });
  let overflowed = 0;
  const unrendered = [];
  try {
    let page = await newCardPage(browser, opts);
    for (const job of jobs) {
      let overflow;
      try {
        overflow = await renderPage(page, job.htmlAbs, job.outAbs, opts);
      } catch (err) {
        // A card the browser could not draw is one page short of a deck, and a
        // deck short a page is something to look at — not a reason to throw
        // away the ninety-four that drew. It is named here and counted with
        // the overflows, and the caller assembles what there is.
        unrendered.push(`${path.basename(job.htmlAbs)}: ${err.message || err}`);
        console.log(`FAILED ${job.outAbs}  ${err.message || err}`);
        // An earlier run's PNG is still sitting there, and left alone it goes
        // into the deck as a page of a card this run could not draw — the one
        // failure nothing downstream can see. Removing it turns a silent stale
        // page into a named missing one.
        try { fs.rmSync(job.outAbs, { force: true }); } catch { /* nothing to drop */ }
        // Whatever wedged the page — a capture that never came back, a load
        // that never settled — is still wedging it. A fresh tab is what makes
        // the next card an independent attempt rather than the same failure
        // ninety-four more times.
        page = await recycle(browser, page, opts);
        if (!page) {
          for (const rest of jobs.slice(jobs.indexOf(job) + 1)) {
            unrendered.push(`${path.basename(rest.htmlAbs)}: browser gone`);
          }
          break;
        }
        continue;
      }
      let flag =
        overflow.x > 0 || overflow.y > 0
          ? `  OVERFLOW x=${overflow.x}px y=${overflow.y}px [${overflow.clipped.join(", ")}]`
          : "";
      if (overflow.spills.length) flag += `  SPILL [${overflow.spills.join(", ")}]`;
      if (overflow.clipped.length) flag += `  CLIPPED [${overflow.clipped.join(", ")}]`;
      if (flag) overflowed++;
      // A squeeze costs no content — the render just carries less of the page
      // than it was drawn for — so it reports without failing the build.
      const note = overflow.squeezed.length ? `  squeezed: ${overflow.squeezed.join(", ")}` : "";
      console.log(`wrote ${job.outAbs}${flag}${note}`);
    }
  } finally {
    await closeBrowser(browser);
  }
  for (const line of unrendered) console.error(`render-card: ${line}`);
  if (overflowed || unrendered.length) {
    const parts = [];
    if (overflowed) {
      parts.push(
        `${overflowed} card(s) overflow the ${opts.width}x${opts.height} canvas or spill out of a band`,
      );
    }
    if (unrendered.length) parts.push(`${unrendered.length} card(s) did not render`);
    console.error(parts.join("; "));
    process.exit(2);
  }
}

async function newCardPage(browser, opts) {
  const page = await browser.newPage();
  await page.setViewport({
    width: opts.width,
    height: opts.height,
    deviceScaleFactor: opts.dpr,
  });
  return page;
}

// Returns the replacement page, or null when the browser itself is the thing
// that went — in which case there is no card left to attempt.
async function recycle(browser, page, opts) {
  try { await page.close(); } catch { /* it is already past closing */ }
  try {
    return await newCardPage(browser, opts);
  } catch {
    return null;
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
