// The build tree's two joins, tested on their own:
//
//   1. A card's `.src` footer -> the procedure and step it hangs under. This is
//      the only edge between the deck and the procedure docs, and it is written
//      by hand on 94 cards, so every shape those footers actually take is here.
//   2. A procedure document -> its title, the state it takes and hands on, its
//      numbered steps, and its open items.
//
// Both are pure functions over text, so they test without a filesystem or a
// server. The seating itself (which bench stands in which band) is a table in
// the contract; what is checked here is that nothing falls through it.

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  BANDS, BAND_BY_SUBSYSTEM, UNCARDED_PROCEDURES,
  orderDrift, parseCardSource, parseProcedure, plainMarkdown, procedureForSubsystem,
} from "../contracts/build-tree.js";

test("a card footer names its procedure and step", () => {
  const s = parseCardSource("enclosure-mechanical.md §4 · foam-shell/README.md");
  assert.equal(s.doc, "enclosure-mechanical.md");
  assert.deepEqual(s.steps, [4]);
  assert.deepEqual(s.refs, ["foam-shell/README.md"]);
  assert.deepEqual(s.openItems, []);
});

test("a step range expands to every step it covers", () => {
  assert.deepEqual(parseCardSource("acceptance-and-burn-in.md §1–2").steps, [1, 2]);
  assert.deepEqual(parseCardSource("finish-pack-ship.md §6–7 · bom.md §14").steps, [6, 7]);
  // A hyphen reads the same as an en dash — the deck uses both.
  assert.deepEqual(parseCardSource("x.md §8-10").steps, [8, 9, 10]);
});

test("an open-item reference is picked out of the footer", () => {
  const s = parseCardSource("enclosure-mechanical.md §6 + Open items 4");
  assert.deepEqual(s.steps, [6]);
  assert.deepEqual(s.openItems, [4]);
});

test("a footer naming no step still names its procedure", () => {
  const s = parseCardSource("cable-assemblies.md · Procedure");
  assert.equal(s.doc, "cable-assemblies.md");
  assert.deepEqual(s.steps, []);
  assert.deepEqual(s.refs, ["Procedure"]);
});

test("only the FIRST segment names the procedure", () => {
  // gt-01 cites two procedures and a sibling card; the first one is its home.
  const s = parseCardSource("internal-plumbing.md §1 · pressure-vessel.md §1 · ip-06");
  assert.equal(s.doc, "internal-plumbing.md");
  assert.deepEqual(s.steps, [1]);
  assert.deepEqual(s.refs, ["pressure-vessel.md §1", "ip-06"]);
});

test("a missing or shapeless footer comes back empty rather than throwing", () => {
  for (const bad of [null, undefined, "", "general technique"]) {
    const s = parseCardSource(bad);
    assert.equal(s.doc, null);
    assert.deepEqual(s.steps, []);
  }
});

const PROC = `# Cold Core Assembly

The production procedure for assembling the cold core — the back-of-enclosure subsystem.

## Scope

In: one hydro-tested vessel (output of [pressure-vessel.md](/x)); TPU gaskets × 2.

Out: a fully foam-poured cold core, capped + gasketed, with [200 mm](PROT_INLET) of stub.

## Procedure

### 1. Dress the vessel wall, then wind the coil

Body text.

### 2. Press ruthex inserts into the outer shell

More body text.

## Open items

1. **The first one is open.** Detail here.
2. ~~**The second one was open.**~~ **CLOSED.** Why it closed.
`;

test("a procedure yields its title, scope, steps and open items", () => {
  const p = parseProcedure(PROC);
  assert.equal(p.title, "Cold Core Assembly");
  assert.match(p.blurb, /^The production procedure for assembling the cold core/);
  assert.match(p.scope.in, /^one hydro-tested vessel/);
  assert.match(p.scope.out, /^a fully foam-poured cold core/);
  // Docgen markers read as their value, not their tag.
  assert.match(p.scope.out, /200 mm of stub/);
  assert.deepEqual(p.steps.map((s) => s.n), [1, 2]);
  assert.equal(p.steps[0].title, "Dress the vessel wall, then wind the coil");
  assert.deepEqual(p.openItems.map((o) => [o.n, o.closed]), [[1, false], [2, true]]);
  assert.equal(p.openItems[0].headline, "The first one is open.");
});

test("a procedure with no scope, steps or open items still parses", () => {
  const p = parseProcedure("# Handwork\n\nSkilled-hand tasks.\n\n## Bend copper\n\nText.\n");
  assert.equal(p.title, "Handwork");
  assert.deepEqual(p.steps, []);
  assert.deepEqual(p.openItems, []);
  assert.equal(p.scope.in, "");
});

test("plainMarkdown strips the syntax a heading can carry", () => {
  assert.equal(plainMarkdown("CO2 supply on, leak-tight at [90 PSI](CO2_CENTERLINE)"),
               "CO2 supply on, leak-tight at 90 PSI");
  assert.equal(plainMarkdown("**bold** and `code` and ~~struck~~"), "bold and code and struck");
});

test("a subsystem's procedure is the document most of its cards name", () => {
  const cards = [
    { src: "internal-plumbing.md §1 · back-panel/README.md" },
    { src: "internal-plumbing.md §2" },
    { src: "fluid-topology.md" },
  ];
  assert.equal(procedureForSubsystem(cards), "internal-plumbing.md");
  assert.equal(procedureForSubsystem([{ src: "general technique" }]), null);
});

test("every subsystem in the band table stands in a band that exists", () => {
  const ids = new Set(BANDS.map((b) => b.id));
  for (const [key, band] of Object.entries(BAND_BY_SUBSYSTEM)) {
    assert.ok(ids.has(band), `subsystem ${key} names band ${band}, which is not in BANDS`);
  }
  for (const [doc, band] of Object.entries(UNCARDED_PROCEDURES)) {
    assert.ok(ids.has(band), `${doc} names band ${band}, which is not in BANDS`);
  }
});

test("every band declares a flow the page knows how to render", () => {
  for (const b of BANDS) {
    assert.ok(["sequence", "parallel", "anytime"].includes(b.flow), `${b.id}: ${b.flow}`);
  }
});

test("orderDrift names every pair the two orders disagree on", () => {
  const build = Object.keys(BAND_BY_SUBSYSTEM);
  // Same order, no drift.
  assert.deepEqual(orderDrift(build), []);
  // One swap, one pair reported, named build-order-first.
  const swapped = [...build];
  const i = swapped.indexOf("en"), j = swapped.indexOf("ip");
  [swapped[i], swapped[j]] = [swapped[j], swapped[i]];
  assert.deepEqual(orderDrift(swapped), [["en", "ip"]]);
  // Codes the build order does not know are ignored rather than throwing.
  assert.deepEqual(orderDrift(["zz", ...build]), []);
});
