// The build tree's shape — what the appliance is assembled out of, and in what
// order, read off the two artifacts that already say so.
//
//   * hardware/assembly/<name>.md — one procedure per bench. Its `## Scope`
//     carries the finished state that bench hands on (`Out:`) and what it takes
//     (`In:`); its `### N.` headings are its steps; its `## Open items` are the
//     questions still open against it.
//   * hardware/assembly/cards/ — one card per hand operation. Every card's
//     `.src` footer names the procedure and the step it renders, which is the
//     edge that hangs a card under a step.
//
// Deck order, labels and accents are NOT here: web/lib/walk.js reads them off
// the deck's own style.css, so the tree cannot drift from the paper deck. What
// is here is the one thing neither artifact carries — which stages run in
// sequence and which run beside each other.

// The bands, in the order hardware/future.md "Build order" states them:
// "vessel, cold core, refrigerant loop, then three benches that run in parallel
// with that chain and feed the chassis — cable assemblies, electronics shelf,
// faucet and umbilical — then enclosure, internal plumbing, wiring,
// commissioning, burn-in, pack and ship."
//
// `flow` is what a band says about its own children: "sequence" is one after
// another, "parallel" is at once, "anytime" is whenever the work calls for it.
export const BANDS = [
  {
    id: "subsystems",
    label: "Subsystem benches",
    flow: "sequence",
    note: "The vessel and everything built around it, each taking the one before.",
  },
  {
    id: "feeders",
    label: "Feeder benches",
    flow: "parallel",
    note: "Three benches beside the chain, each finishing a unit the chassis takes later.",
  },
  {
    id: "chassis",
    label: "Chassis and commissioning",
    flow: "sequence",
    note: "The box, what is run inside it, and every test on the finished unit.",
  },
  {
    id: "anytime",
    label: "Referenced from anywhere",
    flow: "anytime",
    note: "Craft that belongs to no single bench, cited by the cards that need it.",
  },
];

// Which band each card subsystem stands in, IN BUILD ORDER. Keys are the
// two-letter codes the deck's style.css declares; a code missing here is
// reported rather than dropped, so a subsystem added to the deck cannot go
// quietly unplaced.
//
// The order of these keys is the order the deck prints in — `_build.py`'s
// SUBSYSTEM_ORDER, which is hardware/future.md "Build order". It is not the
// order style.css declares them in, and `orderDrift` below is what says so.
export const BAND_BY_SUBSYSTEM = {
  pv: "subsystems", cc: "subsystems", rl: "subsystems",
  ca: "feeders", es: "feeders", fu: "feeders",
  en: "chassis", ip: "chassis", wr: "chassis",
  fc: "chassis", ab: "chassis", fs: "chassis",
  sa: "anytime", gt: "anytime",
};

// Where the build order and the deck's own stylesheet disagree about which
// subsystem comes first. `walkAssemblyCards` sorts by style.css, so a pair
// listed here is a pair the site and the paper deck show in opposite orders.
export function orderDrift(styleOrder) {
  const build = Object.keys(BAND_BY_SUBSYSTEM);
  const rank = new Map(build.map((k, i) => [k, i]));
  const seen = styleOrder.filter((k) => rank.has(k));
  const out = [];
  for (let i = 0; i < seen.length; i++) {
    for (let j = i + 1; j < seen.length; j++) {
      if (rank.get(seen[i]) > rank.get(seen[j])) out.push([seen[j], seen[i]]);
    }
  }
  return out;
}

// Procedures that carry no cards of their own. `handwork.md` summarizes the
// skilled-hand tasks across several benches and states its own order as loose
// ("Order isn't strict"), so it stands in the band that claims no position.
export const UNCARDED_PROCEDURES = { "handwork.md": "anytime" };

// --- the card footer -------------------------------------------------------

// A card's `.src` footer, decoded to text: the procedure it renders, the step
// or steps within it, any open item it stands against, and whatever else it
// cites. Segments are separated by "·"; the first names the procedure.
//
//   "enclosure-mechanical.md §6 + Open items 4"
//     -> { doc: "enclosure-mechanical.md", steps: [6], openItems: [4], refs: [] }
//   "acceptance-and-burn-in.md §1–2"
//     -> { doc: "acceptance-and-burn-in.md", steps: [1, 2], openItems: [], refs: [] }
//   "cold-core.md §4 · handwork.md · reservoir.py"
//     -> { doc: "cold-core.md", steps: [4], openItems: [],
//          refs: ["handwork.md", "reservoir.py"] }
//   "cable-assemblies.md · Procedure"
//     -> { doc: "cable-assemblies.md", steps: [], openItems: [], refs: ["Procedure"] }
//
// A footer naming no `.md` at all comes back with `doc: null` — the card is
// real and hangs off its subsystem, it just names no step to sit under.
export function parseCardSource(src) {
  const empty = { doc: null, steps: [], openItems: [], refs: [] };
  if (!src) return empty;
  const segments = String(src).split("·").map((s) => s.trim()).filter(Boolean);
  if (!segments.length) return empty;

  const head = segments[0];
  const docMatch = /^([A-Za-z0-9._-]+\.md)\b/.exec(head);
  const doc = docMatch ? docMatch[1] : null;
  const tail = docMatch ? head.slice(docMatch[0].length) : head;

  const steps = [];
  // "§6", "§1–2", "§8-9", "§3—5" — an en/em dash or a hyphen all read as a range.
  const stepRe = /§\s*(\d+)\s*(?:[–—-]\s*(\d+))?/g;
  let m;
  while ((m = stepRe.exec(tail))) {
    const from = Number(m[1]);
    const to = m[2] === undefined ? from : Number(m[2]);
    for (let n = Math.min(from, to); n <= Math.max(from, to); n++) {
      if (!steps.includes(n)) steps.push(n);
    }
  }

  const openItems = [];
  const openRe = /Open items?\s+(\d+)/gi;
  while ((m = openRe.exec(tail))) {
    if (!openItems.includes(Number(m[1]))) openItems.push(Number(m[1]));
  }

  return { doc, steps, openItems, refs: segments.slice(1) };
}

// --- the procedure ---------------------------------------------------------

// Strip the docgen marker syntax `[value](NAME)` back to its value, so a
// heading or a scope clause reads as prose here the way it does on the page.
export function plainMarkdown(text) {
  return String(text)
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\*\*([^*]*)\*\*/g, "$1")
    .replace(/~~([^~]*)~~/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

// The body under one `## ` heading, up to the next one or the end of the
// document. Split rather than matched: the last section of a file has no
// following heading to stop against, and a lookahead written for one silently
// skips it.
export function section(md, name) {
  const parts = String(md).split(/^##\s+/m);
  for (const part of parts.slice(1)) {
    const nl = part.indexOf("\n");
    const heading = (nl < 0 ? part : part.slice(0, nl)).trim();
    if (heading.toLowerCase() === name.toLowerCase()) return nl < 0 ? "" : part.slice(nl + 1);
  }
  return "";
}

// One procedure document, as the tree reads it: its title and opening line, the
// state it takes and the state it hands on, its numbered steps, and the
// questions still open against it.
export function parseProcedure(md) {
  const text = String(md);
  const title = plainMarkdown((/^#\s+(.+)$/m.exec(text) || [, ""])[1]);

  // The first paragraph after the title, which every procedure opens with.
  const afterTitle = text.replace(/^#\s+.+$/m, "");
  const blurb = plainMarkdown(
    (afterTitle.split(/\n\s*\n/).map((p) => p.trim()).find((p) => p && !p.startsWith("#")) || ""),
  );

  const scope = { in: "", out: "" };
  const scopeBody = section(text, "Scope");
  for (const [key, re] of [["in", /^In:\s*([\s\S]*?)(?=\n\s*\n|$)/m],
                           ["out", /^Out:\s*([\s\S]*?)(?=\n\s*\n|$)/m]]) {
    const hit = re.exec(scopeBody);
    if (hit) scope[key] = plainMarkdown(hit[1]);
  }

  const steps = [];
  const stepRe = /^###\s+(\d+)\.\s+(.+)$/gm;
  let m;
  while ((m = stepRe.exec(text))) steps.push({ n: Number(m[1]), title: plainMarkdown(m[2]) });

  const openItems = [];
  const openBody = section(text, "Open items");
  // Each item runs to the head of the next one, so the CLOSED an item carries
  // is read against that item and not against its neighbour's.
  const heads = [...openBody.matchAll(/^(\d+)\.\s+(~~)?\*\*(.+?)\*\*/gm)];
  heads.forEach((h, i) => {
    const body = openBody.slice(h.index, i + 1 < heads.length ? heads[i + 1].index : undefined);
    // A struck headline or a CLOSED lead, either of which marks one answered.
    openItems.push({
      n: Number(h[1]),
      headline: plainMarkdown(h[3]),
      closed: Boolean(h[2]) || /\bCLOSED\b/.test(body),
    });
  });

  return { title, blurb, scope, steps, openItems };
}

// --- assembling the tree ---------------------------------------------------

// The procedure each subsystem's cards belong to: the `.md` the most of them
// name. Derived rather than tabulated, so a bench renamed on disk carries its
// cards with it. A subsystem whose cards agree on nothing comes back unmapped.
export function procedureForSubsystem(cards) {
  const tally = new Map();
  for (const c of cards) {
    const doc = parseCardSource(c.src).doc;
    if (doc) tally.set(doc, (tally.get(doc) || 0) + 1);
  }
  let best = null;
  for (const [doc, n] of tally) if (!best || n > best[1]) best = [doc, n];
  return best ? best[0] : null;
}
