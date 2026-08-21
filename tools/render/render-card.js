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
//   --pdf WxHin  also write <output>.pdf at this page size in inches (e.g. 6x4).
//                The same page visit, printed rather than captured: type stays
//                type and the rules stay rules, so the deck a person reads on a
//                screen is a tenth the size of the same pages as pixels and is
//                sharper than the printer's own grid. The PNG is still what the
//                printer is handed, and it is still what the checks below read.
//
// Batch mode renders every *.html in <dir> (sorted) to <out-dir>/<name>.png in
// one browser session, and reports any card whose content overflows the
// viewport, or spills out of its own header/main/footer band into a
// neighbouring one — either is a layout bug, not a printable card.

import path from "path";
import os from "os";
import fs from "fs";
import { pathToFileURL } from "url";
import { closeBrowser, finish, launchBrowser, sweepAbandonedBrowsers } from "./browser.js";

function usage(msg) {
  if (msg) console.error(`render-card: ${msg}`);
  console.error(
    "usage: node tools/render/render-card.js <input.html> <output-png> [--size WxH] [--dpr f] [--pdf WxHin]\n" +
      "       node tools/render/render-card.js --batch <dir> <out-dir> [--size WxH] [--dpr f] [--pdf WxHin]",
  );
  process.exit(1);
}

function parseArgs(argv) {
  const positional = [];
  const opts = { width: 1800, height: 1200, dpr: 1, batch: false, pdf: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => (a.includes("=") ? a.split("=").slice(1).join("=") : argv[++i]);
    if (a.startsWith("--size")) {
      const m = String(val()).match(/^(\d+)x(\d+)$/);
      if (!m) usage("bad --size");
      opts.width = Number(m[1]);
      opts.height = Number(m[2]);
    } else if (a.startsWith("--dpr")) opts.dpr = Number(val());
    else if (a.startsWith("--pdf")) {
      const m = String(val()).match(/^([\d.]+)x([\d.]+)(in)?$/);
      if (!m) usage("bad --pdf");
      opts.pdf = { width: `${m[1]}in`, height: `${m[2]}in` };
    } else if (a === "--batch") opts.batch = true;
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

  // An image is fetched before it is decoded, and the capture reads decoded pixels.
  await page.evaluate(() =>
    Promise.all(
      Array.from(document.images).map((img) =>
        (img.complete
          ? Promise.resolve()
          : new Promise((done) => {
              img.onload = done;
              img.onerror = done;
            })
        ).then(() => (img.decode ? img.decode().catch(() => {}) : undefined)),
      ),
    ),
  );

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
  // The print path, off the same laid-out page.
  //
  // CHROME PRINTS IN CSS PIXELS AT 96 TO THE INCH, and a card is authored at
  // 300 — so an unscaled `page.pdf` at 6 x 4 in takes the top-left 576 x 384 of
  // an 1800 x 1200 canvas and paginates the rest away. `scale` is the ratio
  // between the two, read off the page size asked for and the canvas rendered.
  //
  // `pageRanges: "1"` is what keeps this a page and not a document: content
  // that outgrew the canvas paginates, and the overflow report above is where
  // that is said out loud.
  if (opts.pdf) {
    await page.pdf({
      path: outAbs.replace(/\.png$/, ".pdf"),
      width: opts.pdf.width,
      height: opts.pdf.height,
      scale: (parseFloat(opts.pdf.width) * 96) / opts.width,
      printBackground: true,
      pageRanges: "1",
      preferCSSPageSize: false,
    });
  }
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

  await sweepAbandonedBrowsers("render-card");
  const browser = await launchBrowser({
    // THIS IS THE BUDGET FOR A PAGE THAT NEVER COMES BACK, AND IT IS SIZED TO CAP WHAT
    // ONE COSTS. `bs-band-saw` is such a page on a runner: `Page.captureScreenshot` does
    // not return, and one card that did not come back is a red target, which is a carry
    // that does not happen, which is every derived output describing the commit before.
    //
    // AND THE ENVIRONMENT CANNOT RAISE IT WHERE IT MATTERS. A genrule sees only what
    // `.bazelrc` hands it with `--action_env` — PATH, PUPPETEER_CACHE_DIR,
    // BLENDER_USER_RESOURCES and two flags — so `HSM_CARD_TIMEOUT` set in a workflow
    // reaches nothing at all. It is here for a hand run. The default is what CI gets.
    //
    // AND `bs-band-saw` IS A PAGE THAT NEVER COMES BACK, WHICH IS WHY THIS NUMBER IS
    // SMALL. It was raised to `PARSE_TIMEOUT + 60000` — 960 s, what the other two
    // renderers carry — on the reading that contention was eating a budget sized for a
    // hung page. Derive 32463988242 measured it: `//:tools-build` went 270 s -> 1926 s,
    // the build's critical path 452 s -> 1949.8 s, and a SECOND card reached the same
    // hang instead of the run ending at the first. 2 x 960 s is the 1926 s. A capture
    // that never returns does not finish given longer; it costs longer.
    //
    // So the budget is back where it caps that failure at four minutes a card. WHAT
    // HANGS IS OPEN, and two measurements narrow it by ruling their own answers out.
    //
    // CONTENTION IS NOT IT. In 32463988242 `//:cards-build` began 08:39:37 and ran
    // 198 s, `//:tools-build` began 08:43:38 and ran 1926 s, and `//:render-scenes` was
    // a disk-cache hit that never executed — so the target that hung had the runner to
    // itself for half an hour.
    //
    // SIZE ALONE IS NOT IT. `//:tools-build` captures 3300x2550 at dpr 1.2 — 12.1
    // megapixels a capture, seven times the main deck's, which passes. The same thirteen
    // cards at that size render on the authoring Mac in 15.9 s all told, exit 0, taken
    // with 80 MB free and 3.7 GB of swap in use.
    //
    // What is left is the container, and it is POSITIONAL: sorted first in each deck is
    // `bs-band-saw` and `00-cover`, and those are the two that hang, in both decks, every
    // run. They share nothing but position — one is 9 KB with three images, the other is
    // a cover. `warmUp` below is what stops a card ever being the first capture.
    protocolTimeout: Number(process.env.HSM_CARD_TIMEOUT || 240000),
  });
  let overflowed = 0;
  const unrendered = [];
  try {
    if (!(await warmUp(browser))) {
      console.error("render-card: no capture returned on a cold browser");
    }
    let page = await newCardPage(browser, opts);
    // THE FIRST CARD IN A DECK PAYS FOR ALL OF THEM AND IT IS THE ONE THAT DOES NOT COME BACK.
    // One browser draws a whole deck, so the first capture is the one that starts the
    // compositor, takes the first shared-memory frame, and fetches and parses the ten vendored
    // `cards/fonts/*.woff2` every later card then already has. In a container that lands on
    // card one: `00-cover.html` heads the main deck and `bs-band-saw.html` heads the tools
    // deck, and those are the two that time out, every run, while the hundred behind them draw.
    //
    // So the deck's first page is drawn onto a throwaway. It is the same visit a card gets —
    // the fonts, a capture at the same size — and what it costs is one page nobody keeps.
    await renderPage(page, jobs[0].htmlAbs, path.join(os.tmpdir(), `hsm-warm.${process.pid}.png`), opts)
      .catch(() => { /* a warm-up that fails is a card that is about to fail out loud */ });
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
        try { fs.rmSync(job.outAbs.replace(/\.png$/, ".pdf"), { force: true }); } catch { /* nor this */ }
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

//: How long a throwaway capture gets before it is treated as the hung one, and how
//: many pages get a turn. Three at ten seconds is thirty seconds spent in the worst
//: case, against a target that fails.
const WARM_MS = 10000;
const WARM_TRIES = 3;

// The first `Page.captureScreenshot` a cold browser is asked for in the CI container
// does not return, and a fresh page clears it: after the sorted-first card hangs, the
// `recycle` below draws every remaining card. So the run spends its first capture on
// an 8x8 blank page nobody keeps.
//
// The wait is this function's own rather than `protocolTimeout`'s, because the point
// is to find out cheaply. A capture that has not answered in ten seconds is the one
// this exists for; the page it is stuck in is closed, which is what rejects it, and
// the next attempt gets a page of its own. Returns false when none of them answered,
// which is a browser the deck is not going to come out of.
async function warmUp(browser) {
  for (let attempt = 1; attempt <= WARM_TRIES; attempt++) {
    let page;
    try {
      page = await browser.newPage();
      await page.setViewport({ width: 8, height: 8, deviceScaleFactor: 1 });
    } catch {
      return false;                       // the browser itself is gone
    }
    const shot = page
      .screenshot({ type: "png", clip: { x: 0, y: 0, width: 8, height: 8 } })
      .then(() => true, () => false);
    let timer;
    const deadline = new Promise((done) => { timer = setTimeout(() => done(false), WARM_MS); });
    const answered = await Promise.race([shot, deadline]);
    clearTimeout(timer);
    shot.catch(() => {});                 // the losing capture settles into nothing
    try { await page.close(); } catch { /* it is already past closing */ }
    if (answered) {
      if (attempt > 1) console.log(`render-card: cold capture answered on attempt ${attempt}`);
      return true;
    }
    console.log(`render-card: cold capture ${attempt} did not return in ${WARM_MS} ms`);
  }
  return false;
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

main().then(
  () => finish(0),
  (err) => {
    console.error(err.message || err);
    finish(1);
  },
);
