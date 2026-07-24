// The assembly deck's two load-bearing conventions (web/contracts/cards.js,
// web/lib/walk.js):
//
//   1. Deck order is read from the deck's own style.css, not hardcoded here.
//      The `body.xx { --accent }` block is what the printed cards colour
//      themselves from, so the grid's subsystem order, labels, and accents can
//      never drift from the paper deck — and a subsystem added to the deck
//      needs no second edit to appear in the right place on the site.
//   2. /cards/* serves the pages and what they embed, and nothing else. The
//      deck directory also holds build machinery (_build.py) and the rendered
//      output (out/deck.pdf); neither is reachable through the route.
//
// Built against a fake deck in a tmpdir so the assertions don't move every time
// the real deck grows a card.

import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import { walkAssemblyCards } from "../lib/walk.js";
import { isCardAssetPath, isCardPath, cardAssetUrl, CARDS_DIR_REL } from "../contracts/cards.js";

// A deck whose style.css declares subsystems in a deliberately non-alphabetical
// build order, so a result that merely sorted by name would fail.
const FAKE_STYLE = `
:root { --accent: #46628a; }
body.pv { --accent: #46628a; }  /* pressure vessel — steel */
body.cc { --accent: #0f8bab; }  /* cold core — ice */
body.ab { --accent: #2e8540; }  /* acceptance + burn-in — pass */
`;

function card(root, file, { subsystem, code, title, deckpos } = {}) {
  const dir = path.join(root, ...CARDS_DIR_REL.split("/"));
  fs.mkdirSync(dir, { recursive: true });
  const body = subsystem ? `<body class="${subsystem}">` : "<body>";
  fs.writeFileSync(
    path.join(dir, file),
    `<!doctype html><html><head><link rel="stylesheet" href="style.css"></head>${body}` +
      `<div class="card"><header>` +
      (code ? `<div class="code">${code}</div>` : "") +
      (title ? `<h1>${title}</h1>` : "") +
      (deckpos ? `<div class="deckpos"><b>${deckpos}</b>Kitchen edition</div>` : "") +
      `</header></div></body></html>\n`,
  );
}

function fakeDeck(root) {
  const dir = path.join(root, ...CARDS_DIR_REL.split("/"));
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "style.css"), FAKE_STYLE);
  return dir;
}

test("walkAssemblyCards orders by the deck's own build order, not by name", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-cards-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fakeDeck(root);

  // Written in an order that is neither the deck order nor alphabetical.
  card(root, "cc-02-foil.html", { subsystem: "cc", code: "CC-02" });
  card(root, "ab-01-burn-in.html", { subsystem: "ab", code: "AB-01" });
  card(root, "pv-02-tap.html", { subsystem: "pv", code: "PV-02" });
  card(root, "cc-01-wind.html", { subsystem: "cc", code: "CC-01" });
  card(root, "pv-01-chamfer.html", { subsystem: "pv", code: "PV-01" });

  const codes = walkAssemblyCards(root).map((c) => c.code);
  assert.deepEqual(codes, ["PV-01", "PV-02", "CC-01", "CC-02", "AB-01"]);
});

test("walkAssemblyCards labels and colours subsystems from style.css", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-cards-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fakeDeck(root);
  card(root, "cc-01-wind.html", { subsystem: "cc", code: "CC-01" });

  const [c] = walkAssemblyCards(root);
  assert.equal(c.subsystem, "cc");
  assert.equal(c.subsystemLabel, "Cold core");
  assert.equal(c.accent, "#0f8bab");
});

test("walkAssemblyCards reads the identity a card prints on itself", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-cards-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fakeDeck(root);
  card(root, "pv-02-tap.html", {
    subsystem: "pv",
    code: "PV-02",
    // Entities and inline markup, both of which appear in real card titles.
    title: 'Tap 1/4&Prime;-18 NPT <br> &mdash; four ports',
    deckpos: "Pressure vessel &#183; 02/14",
  });

  const [c] = walkAssemblyCards(root);
  assert.equal(c.path, "assembly/cards/pv-02-tap.html");
  assert.equal(c.code, "PV-02");
  assert.equal(c.title, 'Tap 1/4″-18 NPT — four ports');
  assert.equal(c.deckpos, "Pressure vessel · 02/14");
});

test("walkAssemblyCards leads with a card that names no subsystem", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-cards-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fakeDeck(root);
  card(root, "pv-01-chamfer.html", { subsystem: "pv", code: "PV-01" });
  card(root, "00-cover.html", { title: "Assembly deck" });

  const cards = walkAssemblyCards(root);
  assert.equal(cards[0].file, "00-cover.html");
  assert.equal(cards[0].subsystem, null);
  assert.equal(cards[0].subsystemLabel, "Deck");
  assert.equal(cards[0].accent, null);
  assert.equal(cards[0].title, "Assembly deck");
});

test("walkAssemblyCards skips build machinery and rendered output", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-cards-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const dir = fakeDeck(root);
  card(root, "pv-01-chamfer.html", { subsystem: "pv", code: "PV-01" });
  // Underscore-prefixed helpers, docs, and the rendered deck all share the
  // directory; none of them is a card.
  fs.writeFileSync(path.join(dir, "_build.py"), "# builder\n");
  fs.writeFileSync(path.join(dir, "_scratch.html"), "<html></html>\n");
  fs.writeFileSync(path.join(dir, "README.md"), "# deck\n");
  fs.mkdirSync(path.join(dir, "out"), { recursive: true });
  fs.writeFileSync(path.join(dir, "out", "index.html"), "<html></html>\n");

  assert.deepEqual(walkAssemblyCards(root).map((c) => c.file), ["pv-01-chamfer.html"]);
});

test("walkAssemblyCards returns nothing for a root with no deck", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "walk-cards-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  assert.deepEqual(walkAssemblyCards(root), []);
});

test("/cards/* serves the deck's pages and their assets, and nothing else", () => {
  // Servable: the card, the shared stylesheet, the renders a card embeds.
  assert.ok(isCardAssetPath("assembly/cards/pv-05-cut-level-rods.html"));
  assert.ok(isCardAssetPath("assembly/cards/style.css"));
  assert.ok(isCardAssetPath("assembly/cards/img/coil-mandrel.png"));
  assert.ok(isCardAssetPath("assembly/cards/img/en01-shell.svg"));

  // Not servable: build machinery, escapes, and anything outside the deck.
  assert.ok(!isCardAssetPath("assembly/cards/_build.py"));
  assert.ok(!isCardAssetPath("assembly/cards/README.md"));
  assert.ok(!isCardAssetPath("assembly/cards/../../../etc/passwd.html"));
  assert.ok(!isCardAssetPath("assembly/pressure-vessel.md"));
  assert.ok(!isCardAssetPath("printed-parts/enclosure/enclosure.step"));
});

test("a card is a page directly in the deck, not any .html under it", () => {
  assert.ok(isCardPath("assembly/cards/cc-01-wind-coil.html"));
  // The out/ deck and any nested page are assets at most, never cards — this is
  // the id the broadcast, the push deep link, and the `card:` hash carry.
  assert.ok(!isCardPath("assembly/cards/out/index.html"));
  assert.ok(!isCardPath("assembly/cards/style.css"));
  assert.ok(!isCardPath("posts/2026-01-01-0000.md"));
});

test("cardAssetUrl is the path the viewer's iframe loads", () => {
  assert.equal(
    cardAssetUrl("assembly/cards/cc-01-wind-coil.html"),
    "/cards/assembly/cards/cc-01-wind-coil.html",
  );
});
