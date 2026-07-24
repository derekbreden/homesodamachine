// Source-level guards for the grid's windowed thumbnail content
// (web/public/js/viewer/lazy.js). The window itself needs a browser — two
// IntersectionObservers and real layout — so, like contracts-browser.test.js,
// this asserts the properties the source has to hold for it to be correct.
//
// The two invariants below are the ones that break silently. A collapsed host
// doesn't throw, it just makes the page jump under the reader's thumb; and a
// kind that goes back to mount-once doesn't throw either, it just quietly holds
// every thumbnail it ever showed.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC = path.resolve(__dirname, "..", "public");
const read = (rel) => fs.readFileSync(path.join(PUBLIC, rel), "utf8");

// Every host the grid mounts thumbnail content into. Releasing content empties
// these, so each one's size has to come from CSS rather than from what's inside
// it. `.card img` covers the STEP kind, whose "host" is the <img> itself.
const THUMB_HOSTS = [
  ".card img",
  ".card .placeholder",
  ".card .mmd-thumb",
  ".card .drawing-thumb",
  ".card .pcb-thumb",
  ".card .card-thumb",
];

// Pull one rule block's body out of a stylesheet by exact selector.
function ruleBody(css, selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const m = new RegExp(`(^|\\n)\\s*${escaped}\\s*\\{([^}]*)\\}`).exec(css);
  return m ? m[2] : null;
}

test("every thumbnail host holds its box with content released", () => {
  const css = read("css/viewer.css");
  for (const host of THUMB_HOSTS) {
    const body = ruleBody(css, host);
    assert.ok(body, `${host} has no rule in viewer.css`);
    // An explicit aspect-ratio is what lets an emptied host occupy exactly the
    // space a full one did. Without it, releasing content mid-scroll collapses
    // the card and the page jumps under the reader.
    assert.match(
      body,
      /aspect-ratio\s*:/,
      `${host} must declare an aspect-ratio — the grid empties it when content is released`,
    );
  }
});

test("the card-thumb host is positioned, so its frame can leave the flow", () => {
  const css = read("css/viewer.css");
  const body = ruleBody(css, ".card .card-thumb");
  // cards.js absolutely positions the card iframe at its host's top-left, both
  // to scale it and so its 1200px unscaled height can't push the host taller.
  // That only works against a positioned ancestor.
  assert.match(body, /position\s*:\s*relative/, ".card-thumb must be position: relative");
});

test("no grid kind reverts to mounting once and never releasing", () => {
  const grid = read("js/viewer/grid.js");
  // `unobserve` was how every kind used to stop watching after its first
  // intersection, which is exactly the mount-once behaviour the window
  // replaced. The shared observers in lazy.js keep watching for the release.
  assert.doesNotMatch(
    grid,
    /\.unobserve\(/,
    "grid.js should window content through lazy.js, not unobserve after first mount",
  );
  assert.match(grid, /windowContent\(/, "grid.js should mount thumbnails through windowContent");
});

test("live.js refuses to repaint a released card", () => {
  const live = read("js/viewer/live.js");
  // Painting a released card leaves content in a card the window is no longer
  // tracking, so nothing will ever free it. Every per-file refresh has to check.
  const refreshes = live.match(/^function refresh\w+\(file\) \{[\s\S]*?^\}/gm) || [];
  assert.ok(refreshes.length >= 6, `expected the per-kind refreshers, found ${refreshes.length}`);
  for (const fn of refreshes) {
    const name = /^function (\w+)/.exec(fn)[1];
    assert.match(fn, /isMounted\(card\)/, `${name} must skip a released card`);
  }
});

test("the window's margins leave room for hysteresis", async () => {
  const src = read("js/viewer/lazy.js");
  const near = Number(/NEAR_SCREENS\s*=\s*([\d.]+)/.exec(src)[1]);
  const far = Number(/FAR_SCREENS\s*=\s*([\d.]+)/.exec(src)[1]);
  // Mount has to happen before the reader arrives, and release strictly after
  // mount — equal margins would mount and release at the same boundary, so a
  // card resting there would thrash on every pixel of scroll.
  assert.ok(near > 0, "content must mount before it is on screen");
  assert.ok(far > near, `release margin (${far}) must be wider than mount margin (${near})`);
});
