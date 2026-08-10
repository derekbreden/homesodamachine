// /build — the assembly of one unit as a tree, drilled down.
//
// Four levels, each read off something that already exists rather than a list
// kept here:
//
//   band      hardware/future.md "Build order", mirrored in
//             contracts/build-tree.js BANDS — the one thing neither the
//             procedures nor the deck states, which of them run beside
//             each other.
//   bench     hardware/assembly/<name>.md — its title, the state it takes and
//             the state it hands on, and its open items.
//   step      that procedure's `### N.` headings.
//   card      hardware/assembly/cards/, hung under the step its own `.src`
//             footer names. Labels and accents come from the deck's own
//             style.css by way of walk.js; the order benches stand in comes
//             from the build order, and where those two disagree the page
//             says so rather than picking one quietly.
//
// Server-rendered as nested <details>, so the whole tree is in the HTML and a
// drill-down needs no script. Dev-gated in the public nav like the other
// engineering surfaces; the route itself always responds.

import path from "path";
import fs from "fs";

import { renderHead, renderNav, renderFooter } from "./shell.js";
import { walkAssemblyCards } from "./walk.js";
import { cardAssetUrl } from "../contracts/cards.js";
import {
  BANDS, BAND_BY_SUBSYSTEM, UNCARDED_PROCEDURES, orderDrift,
  parseCardSource, parseProcedure, procedureForSubsystem,
} from "../contracts/build-tree.js";

const ASSEMBLY_REL = "assembly";

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// --- reading the tree off disk ---------------------------------------------

function readProcedures(hardwareDir) {
  const dir = path.join(hardwareDir, ASSEMBLY_REL);
  const out = new Map();
  let entries;
  try {
    entries = fs.readdirSync(dir);
  } catch {
    return out;
  }
  for (const file of entries) {
    if (!file.endsWith(".md") || file.startsWith("_")) continue;
    try {
      out.set(file, parseProcedure(fs.readFileSync(path.join(dir, file), "utf-8")));
    } catch { /* unreadable procedure: absent rather than half-read */ }
  }
  return out;
}

// The tree: bands, each holding benches, each holding steps, each holding
// cards. `unplaced` carries anything the read could not seat — a subsystem with
// no band, a card naming a step its procedure does not have — so a gap shows on
// the page instead of vanishing out of it.
export function buildTree(hardwareDir, rootDir) {
  const procedures = readProcedures(hardwareDir);
  const cards = walkAssemblyCards(rootDir);
  const unplaced = [];

  // Cards by subsystem, in deck order (walkAssemblyCards already sorted them).
  const bySubsystem = new Map();
  for (const c of cards) {
    const key = c.subsystem || "";
    if (!bySubsystem.has(key)) bySubsystem.set(key, []);
    bySubsystem.get(key).push(c);
  }

  // Which procedure each subsystem's cards belong to, and the inverse.
  //
  // A SUBSYSTEM IN THE "anytime" BAND TAKES NO PROCEDURE. Its cards cite the
  // benches that need them — the technique deck's five name three different
  // documents between them — so the document most of them happen to name is
  // not a home, and hanging them off its steps would put a crimping card
  // inside a harness bench it does not belong to.
  const flowOf = new Map(BANDS.map((b) => [b.id, b.flow]));
  const docOf = new Map();
  for (const [key, group] of bySubsystem) {
    if (!key || flowOf.get(BAND_BY_SUBSYSTEM[key]) === "anytime") continue;
    const doc = procedureForSubsystem(group);
    if (doc) docOf.set(key, doc);
  }
  const subsystemOf = new Map([...docOf].map(([k, v]) => [v, k]));

  const benchFor = (subsystemKey, doc) => {
    const proc = doc ? procedures.get(doc) : null;
    const group = subsystemKey ? (bySubsystem.get(subsystemKey) || []) : [];
    const steps = (proc ? proc.steps : []).map((s) => ({ ...s, cards: [] }));
    const stepAt = new Map(steps.map((s) => [s.n, s]));
    const loose = [];
    for (const c of group) {
      const src = parseCardSource(c.src);
      const seats = src.steps.filter((n) => stepAt.has(n));
      if (!seats.length) {
        loose.push({ ...c, src });
        if (doc && src.steps.length) {
          unplaced.push(
            `${c.file} names ${doc} §${src.steps.join(", §")}, which that procedure does not have`,
          );
        }
        continue;
      }
      // A card rendering a span of steps hangs under the first of them and says so.
      stepAt.get(seats[0]).cards.push({ ...c, src, span: seats });
    }
    const label = group.find((c) => c.subsystemLabel)?.subsystemLabel || null;
    return { subsystem: subsystemKey || null, doc: doc || null, proc, label,
             steps, loose, cards: group };
  };

  const bands = BANDS.map((b) => ({ ...b, benches: [] }));
  const bandAt = new Map(bands.map((b) => [b.id, b]));

  // THE DECK'S OWN ORDER IS NOT THE BUILD ORDER, and the difference is worth
  // saying out loud: `walkAssemblyCards` sorts by the order style.css declares
  // its subsystems, `_build.py` prints in `future.md`'s. Benches stand here in
  // the build order, and `drift` carries every pair the two disagree on.
  const styleOrder = [];
  for (const c of cards) if (c.subsystem && !styleOrder.includes(c.subsystem)) {
    styleOrder.push(c.subsystem);
  }
  const buildOrder = Object.keys(BAND_BY_SUBSYSTEM);
  // ONE READING, not one per inverted pair: what the two orders ARE is what a
  // reader needs, and seven pairs is the same fact said seven times.
  const up = (ks) => ks.map((k) => k.toUpperCase()).join(" ");
  const drift = orderDrift(styleOrder).length ? [
    `the deck's style.css declares ${up(styleOrder)}`,
    `the build order is ${up(buildOrder.filter((k) => styleOrder.includes(k)))}`,
    `/drawings sorts by the first; the printed deck and this page by the second`,
  ] : [];
  const seenSubsystem = [...styleOrder].sort(
    (a, b) => buildOrder.indexOf(a) - buildOrder.indexOf(b));
  for (const key of seenSubsystem) {
    const bandId = BAND_BY_SUBSYSTEM[key];
    if (!bandId || !bandAt.has(bandId)) {
      unplaced.push(`subsystem "${key}" stands in no band — add it to BAND_BY_SUBSYSTEM`);
      continue;
    }
    bandAt.get(bandId).benches.push(benchFor(key, docOf.get(key) || null));
  }

  // Procedures carrying no cards of their own.
  for (const [doc, bandId] of Object.entries(UNCARDED_PROCEDURES)) {
    if (!procedures.has(doc) || !bandAt.has(bandId)) continue;
    bandAt.get(bandId).benches.push(benchFor(null, doc));
  }

  // And any procedure on disk that nothing pointed at.
  for (const doc of procedures.keys()) {
    if (subsystemOf.has(doc) || UNCARDED_PROCEDURES[doc]) continue;
    unplaced.push(`${doc} is on disk and no band claims it`);
  }

  const cover = cards.filter((c) => !c.subsystem);
  return { bands, cover, cards, procedures, unplaced, drift };
}

// --- rendering -------------------------------------------------------------

const FLOW_NOTE = {
  sequence: "in order",
  parallel: "in parallel",
  anytime: "no fixed position",
};

function renderCard(c) {
  const span = c.span && c.span.length > 1 ? ` <span class="bt-span">§${c.span[0]}–${c.span[c.span.length - 1]}</span>` : "";
  const opens = (c.src?.openItems || []).map((n) => `<span class="bt-open">open ${n}</span>`).join("");
  const refs = (c.src?.refs || []).length
    ? `<span class="bt-refs">${esc(c.src.refs.join(" · "))}</span>` : "";
  return `<li class="bt-card">` +
    `<a href="${esc(cardAssetUrl(c.path))}" target="_blank" rel="noopener">` +
    `<code>${esc(c.file.replace(/\.html$/, "").slice(0, 5))}</code>` +
    `<span class="bt-card-title">${esc(c.title)}</span></a>${span}${opens}${refs}</li>`;
}

function renderStep(step) {
  const cards = step.cards.map(renderCard).join("");
  const count = step.cards.length;
  const body = count
    ? `<ul class="bt-cards">${cards}</ul>`
    : `<p class="bt-empty">No card renders this step.</p>`;
  return `<details class="bt-step">` +
    `<summary><span class="bt-n">${step.n}</span>` +
    `<span class="bt-step-title">${esc(step.title)}</span>` +
    `<span class="bt-count">${count} card${count === 1 ? "" : "s"}</span></summary>` +
    body +
    `</details>`;
}

function renderBench(bench) {
  const p = bench.proc;
  const title = p ? p.title : (bench.label || (bench.subsystem || "").toUpperCase());
  const accent = bench.cards.find((c) => c.accent)?.accent;
  const style = accent ? ` style="--bt-accent:${esc(accent)}"` : "";
  const nSteps = bench.steps.length;
  const nCards = bench.cards.length;

  const scope = p && (p.scope.in || p.scope.out)
    ? `<dl class="bt-scope">` +
      (p.scope.in ? `<dt>Takes</dt><dd>${esc(p.scope.in)}</dd>` : "") +
      (p.scope.out ? `<dt>Hands on</dt><dd>${esc(p.scope.out)}</dd>` : "") +
      `</dl>`
    : "";

  const open = p && p.openItems.length
    ? `<ul class="bt-opens">` + p.openItems.map((o) =>
        `<li class="${o.closed ? "closed" : ""}"><b>${o.n}.</b> ${esc(o.headline)}` +
        `${o.closed ? " <span class=\"bt-closed\">closed</span>" : ""}</li>`).join("") +
      `</ul>`
    : "";

  const steps = bench.steps.map(renderStep).join("");
  const loose = bench.loose.length
    ? `<div class="bt-loose"><h4>${bench.steps.length ? "Cards under no step" : "Cards"}</h4>` +
      `<ul class="bt-cards">${bench.loose.map(renderCard).join("")}</ul></div>`
    : "";

  return `<details class="bt-bench"${style}>` +
    `<summary><span class="bt-code">${esc(bench.subsystem || "—")}</span>` +
    `<span class="bt-bench-title">${esc(title)}</span>` +
    `<span class="bt-count">${nSteps} step${nSteps === 1 ? "" : "s"} · ${nCards} card${nCards === 1 ? "" : "s"}</span>` +
    `</summary>` +
    (p?.blurb ? `<p class="bt-blurb">${esc(p.blurb)}</p>` : "") +
    (bench.doc ? `<p class="bt-doc"><code>hardware/assembly/${esc(bench.doc)}</code></p>` : "") +
    scope +
    (open ? `<h4 class="bt-h">Open items</h4>${open}` : "") +
    (steps ? `<h4 class="bt-h">Steps</h4><div class="bt-steps">${steps}</div>` : "") +
    loose +
    `</details>`;
}

function renderBand(band) {
  if (!band.benches.length) return "";
  return `<section class="bt-band bt-flow-${band.flow}">` +
    `<header class="bt-band-head">` +
    `<h2>${esc(band.label)}</h2>` +
    `<span class="bt-flow">${FLOW_NOTE[band.flow]}</span>` +
    `<p>${esc(band.note)}</p>` +
    `</header>` +
    `<div class="bt-benches">${band.benches.map(renderBench).join("")}</div>` +
    `</section>`;
}

export function renderBuildBody(tree) {
  const nBench = tree.bands.reduce((a, b) => a + b.benches.length, 0);
  const nSteps = tree.bands.reduce(
    (a, b) => a + b.benches.reduce((x, y) => x + y.steps.length, 0), 0);
  const nCards = tree.cards.length;

  const block = (cls, label, rows) => rows.length
    ? `<div class="${cls}"><b>${label}</b><ul>` +
      rows.map((u) => `<li>${esc(u)}</li>`).join("") + `</ul></div>`
    : "";
  const warn = block("bt-warn", "Not seated:", tree.unplaced) +
    block("bt-drift", "Two orders disagree:", tree.drift || []);

  return `<main class="bt-wrap">
  <h1 class="bt-title">Build tree</h1>
  <p class="bt-lede">One unit, as the repository currently states it: ${nBench} benches
  over ${nSteps} numbered steps and ${nCards} cards. Bands come from
  <code>hardware/future.md</code> &ldquo;Build order&rdquo;; every bench, step and
  card below is read off <code>hardware/assembly/</code> and the printed deck.</p>
  <p class="bt-lede bt-lede-dim">Grouped by <b>bench</b> &mdash; the only grouping the
  repository states today. Each bench declares the state it takes and the state it hands
  on; the steps inside it are a total order, and a card sits under the step its own
  <code>.src</code> footer names.</p>
  ${warn}
  ${tree.bands.map(renderBand).join("")}
</main>`;
}

const BUILD_CSS = `
.bt-wrap { max-width: 60rem; margin: 0 auto; padding: 1.5rem 1rem 5rem; }
.bt-title { font-size: 1.6rem; margin: 0 0 .5rem; }
.bt-lede { color: var(--text-2); line-height: 1.55; margin: 0 0 .6rem; font-size: .92rem; }
.bt-lede-dim { font-size: .86rem; }
.bt-wrap code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .85em; }

.bt-warn { border: 1px solid var(--err); background: rgba(217,112,112,.10);
  border-radius: 6px; padding: .6rem .8rem; margin: 1rem 0; font-size: .85rem; }
.bt-warn ul, .bt-drift ul { margin: .3rem 0 0; padding-left: 1.1rem; }
.bt-drift { border: 1px solid var(--warn); background: rgba(217,162,76,.10);
  border-radius: 6px; padding: .6rem .8rem; margin: 1rem 0; font-size: .85rem; }

.bt-band { margin: 2rem 0 0; border-top: 1px solid var(--border); padding-top: 1rem; }
.bt-band-head h2 { font-size: 1.05rem; margin: 0; display: inline-block; }
.bt-band-head p { color: var(--text-2); font-size: .85rem; margin: .25rem 0 .8rem; }
.bt-flow { font-size: .7rem; text-transform: uppercase; letter-spacing: .08em;
  border: 1px solid currentColor; border-radius: 99px; padding: .1rem .5rem;
  margin-left: .6rem; color: var(--text-2); vertical-align: 2px; }
.bt-flow-parallel .bt-flow { color: var(--warn); }
.bt-flow-anytime .bt-flow { color: var(--text-3); }

.bt-benches { display: flex; flex-direction: column; gap: .4rem; }
.bt-flow-parallel .bt-benches { display: grid; gap: .4rem;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); align-items: start; }

details.bt-bench { border: 1px solid var(--border); border-left: 3px solid
  var(--bt-accent, var(--border)); border-radius: 5px; background: rgba(255,255,255,.02); }
details.bt-bench > summary { cursor: pointer; padding: .55rem .7rem; display: flex;
  gap: .55rem; align-items: baseline; flex-wrap: wrap; list-style: none; }
details.bt-bench > summary::-webkit-details-marker { display: none; }
details.bt-bench > summary::before { content: "▸"; color: var(--text-2); font-size: .8em; }
details.bt-bench[open] > summary::before { content: "▾"; }
.bt-code { font-family: ui-monospace, monospace; font-size: .72rem; text-transform: uppercase;
  letter-spacing: .06em; color: var(--bt-accent, var(--text-2)); }
.bt-bench-title { font-weight: 600; }
.bt-count { color: var(--text-2); font-size: .78rem; margin-left: auto; white-space: nowrap; }
.bt-blurb, .bt-doc { margin: 0 .8rem .5rem; color: var(--text-2); font-size: .84rem; line-height: 1.5; }
.bt-h { margin: .8rem .8rem .35rem; font-size: .74rem; text-transform: uppercase;
  letter-spacing: .08em; color: var(--text-2); }

.bt-scope { margin: 0 .8rem .6rem; font-size: .82rem; line-height: 1.5; }
.bt-scope dt { font-size: .7rem; text-transform: uppercase; letter-spacing: .08em;
  color: var(--bt-accent, var(--text-2)); margin-top: .45rem; }
.bt-scope dd { margin: .1rem 0 0; color: var(--text-2); }

.bt-opens { margin: 0 .8rem .6rem; padding-left: 1.1rem; font-size: .82rem; line-height: 1.5; }
.bt-opens li { color: var(--text); }
.bt-opens li.closed { color: var(--text-2); text-decoration: line-through; }
.bt-closed { text-decoration: none; font-size: .68rem; text-transform: uppercase;
  letter-spacing: .06em; color: var(--ok); }

.bt-steps { margin: 0 .55rem .6rem; display: flex; flex-direction: column; gap: .2rem; }
details.bt-step { border-left: 2px solid var(--border); }
details.bt-step > summary { cursor: pointer; padding: .3rem .55rem; display: flex;
  gap: .5rem; align-items: baseline; list-style: none; font-size: .87rem; }
details.bt-step > summary::-webkit-details-marker { display: none; }
.bt-n { font-family: ui-monospace, monospace; font-size: .75rem; color: var(--text-2);
  min-width: 1.1rem; }
.bt-step-title { flex: 1; }

ul.bt-cards { list-style: none; margin: 0 0 .4rem; padding: 0 0 0 2.1rem;
  display: flex; flex-direction: column; gap: .12rem; }
.bt-card { font-size: .84rem; display: flex; gap: .45rem; align-items: baseline; flex-wrap: wrap; }
.bt-card a { display: flex; gap: .45rem; align-items: baseline; text-decoration: none;
  color: var(--text); }
.bt-card a:hover .bt-card-title { text-decoration: underline; }
.bt-card code { color: var(--bt-accent, var(--text-2)); font-size: .74rem;
  text-transform: uppercase; }
.bt-span, .bt-open, .bt-refs { font-size: .72rem; color: var(--text-2); }
.bt-open { color: var(--warn); border: 1px solid currentColor; border-radius: 99px;
  padding: 0 .4rem; }
.bt-empty { margin: 0 0 .4rem 2.1rem; font-size: .8rem; color: var(--text-2); font-style: italic; }
.bt-loose { margin: .4rem .8rem .6rem; }
.bt-loose h4 { font-size: .74rem; text-transform: uppercase; letter-spacing: .08em;
  color: var(--text-2); margin: 0 0 .25rem; }
`;

// One content root serves both halves: the procedures under `assembly/` and the
// deck under `assembly/cards/` are the same machine's documents, so the tree is
// per-edition the moment there is a second edition and takes no resolver until
// then.
export function mountBuildRoutes(app, { hardwareDir }) {
  app.get("/api/build-tree", (_req, res) => {
    res.set("Cache-Control", "no-cache");
    const tree = buildTree(hardwareDir, hardwareDir);
    // The wire shape drops the parsed procedure objects' prose bodies; what a
    // consumer needs is the structure and the ids.
    res.json({
      bands: tree.bands.map((b) => ({
        id: b.id, label: b.label, flow: b.flow,
        benches: b.benches.map((x) => ({
          subsystem: x.subsystem, doc: x.doc,
          title: x.proc ? x.proc.title : null,
          takes: x.proc ? x.proc.scope.in : null,
          handsOn: x.proc ? x.proc.scope.out : null,
          openItems: x.proc ? x.proc.openItems : [],
          steps: x.steps.map((s) => ({
            n: s.n, title: s.title,
            cards: s.cards.map((c) => ({ file: c.file, title: c.title, path: c.path })),
          })),
          loose: x.loose.map((c) => ({ file: c.file, title: c.title, path: c.path })),
        })),
      })),
      unplaced: tree.unplaced,
      drift: tree.drift,
    });
  });

  app.get("/build", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    let body;
    try {
      body = renderBuildBody(buildTree(hardwareDir, hardwareDir));
    } catch {
      // A stripped checkout shouldn't 500 — render the empty state.
      body = `<main class="bt-wrap"><h1 class="bt-title">Build tree</h1>` +
             `<p class="bt-lede">Assembly documents unavailable.</p></main>`;
    }
    res.send(
      renderHead({ title: "Build · Home Soda Machine", pageStyles: BUILD_CSS }) +
      renderNav({ surface: "dev", active: "build" }) +
      body +
      renderFooter(),
    );
  });
}
