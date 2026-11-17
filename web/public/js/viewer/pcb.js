// PCB board module. A board carries its rendered copper views — Top (front),
// Bottom (back, seen from above through the board), any inner copper planes of a
// multi-layer board, and Overlay (the whole stack at once, warm front / cool
// back) — produced by hardware/pcb/pcba/render-board.ts straight from the
// fabrication Gerbers, so the lines have the real widths the board is made with.
//
// The material workspace loads this viewer when the reader selects PCB.
import PanZoom from "/pan-zoom.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { makeResetButton, makeMinimap, makeChromeFit } from "./pan-zoom-extras.js";
import { installPadPicker, clearPadPicker, clearPadSelection, makePadPickToggle, revealClearance, revealComponent, revealTraceRoute } from "./pcb-pick.js";

// Every board has these three; inner planes (inner1, inner2, …) are per-board,
// discovered by the server (walk.js) and slotted between Top and Bottom.
const FIXED_LABEL = { top: "Top", bottom: "Bottom", overlay: "Overlay", topmask: "Top Mask", bottommask: "Bottom Mask" };

// The view key for an inner-plane path (".../mini.inner2.svg" -> "inner2"), or
// null if the path isn't an inner view.
function innerKey(path) {
  const m = /\.inner(\d+)\.svg$/.exec(path || "");
  return m ? "inner" + m[1] : null;
}
// Human label for a view key: the fixed ones verbatim, "inner2" -> "Inner 2".
function viewLabel(view) {
  if (FIXED_LABEL[view]) return FIXED_LABEL[view];
  const m = /^inner(\d+)$/.exec(view);
  return m ? "Inner " + m[1] : view;
}
// The ordered {view, path} list a board offers, in physical stack order:
// Top (front) → inner planes front-to-back → Bottom (back) → Overlay (composite),
// then the solder-mask views (exposed-copper map per face) as adjuncts at the end.
// board.inners is already stack-ordered by the server; the mask views are present
// only when the board rendered them (older renders just omit them).
function orderedViews(board) {
  const list = [{ view: "top", path: board.top }];
  for (const p of board.inners || []) {
    const key = innerKey(p);
    if (key) list.push({ view: key, path: p });
  }
  list.push({ view: "bottom", path: board.bottom });
  list.push({ view: "overlay", path: board.overlay });
  if (board.topmask) list.push({ view: "topmask", path: board.topmask });
  if (board.bottommask) list.push({ view: "bottommask", path: board.bottommask });
  return list;
}

// What the board floats under beyond the chrome every 2D surface carries: the
// view toggle across the top, the dimensions chip, the inspector's readout, and
// the inspection toggle down the side. The same list the pad
// picker treats as chrome rather than board (pcb-pick.js CHROME_SEL).
const PCB_CHROME = [
  ".pcb-view-toggle", ".pcb-dims", ".pcb-wrapper > .edge-panel",
  ".pcb-wrapper > .pad-pick-toggle",
];

function pcbTransformKey(source) { return `pcb-transform:${source}`; }
function pcbViewKey(source) { return `pcb-view:${source}`; }

function pcbSaveTransform(source, t) {
  try { localStorage.setItem(pcbTransformKey(source), JSON.stringify(t)); } catch {}
}
function pcbLoadTransform(source) {
  try {
    const raw = localStorage.getItem(pcbTransformKey(source));
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (typeof s.scale !== "number") return null;
    return s;
  } catch { return null; }
}
function pcbSaveView(source, view) {
  try { localStorage.setItem(pcbViewKey(source), view); } catch {}
}
function pcbLoadView(source, validViews) {
  try {
    const v = localStorage.getItem(pcbViewKey(source));
    return validViews.includes(v) ? v : null;
  } catch { return null; }
}

// Parse an SVG string into a live SVGSVGElement. PanZoom reads an SVG's natural
// size from its viewBox (here in Gerber units, e.g. 150050), and fits/zooms by
// CSS-transforming the element — so the element's rendered px size must MATCH
// the viewBox units, or fit math (natural ÷ rendered) is off by the unit ratio.
// We therefore set width/height to the viewBox numbers. That makes the element
// nominally ~150000px, so .pcb-svg is positioned absolutely (viewer.css) and
// clipped by the overflow-hidden wrapper until PanZoom's fit scales it down —
// otherwise the unscaled element would blow out the page on first paint.
// Namespace SVG IDs so an inline board can't bind to another element's mask.
let svgIdSeq = 0;
function uniquifySvgIds(svgText) {
  const ids = new Set();
  for (const m of svgText.matchAll(/\bid="([^"]+)"/g)) ids.add(m[1]);
  if (!ids.size) return svgText;
  const tok = "__pcb" + (++svgIdSeq);
  let out = svgText;
  for (const id of ids) {
    const esc = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    out = out
      .replace(new RegExp(`id="${esc}"`, "g"), `id="${id}${tok}"`)
      .replace(new RegExp(`url\\(#${esc}\\)`, "g"), `url(#${id}${tok})`)
      .replace(new RegExp(`((?:xlink:)?href)="#${esc}"`, "g"), `$1="#${id}${tok}"`);
  }
  return out;
}

function parseSvgString(svgText) {
  svgText = uniquifySvgIds(svgText);
  const doc = new DOMParser().parseFromString(svgText, "image/svg+xml");
  const svgEl = doc.querySelector("svg");
  if (!svgEl) throw new Error("Board view has no <svg> element");
  const adopted = document.importNode(svgEl, true);
  const vb = adopted.viewBox?.baseVal;
  if (vb && vb.width && vb.height) {
    adopted.setAttribute("width", vb.width);
    adopted.setAttribute("height", vb.height);
  }
  adopted.style.display = "block";
  adopted.style.maxWidth = "none";
  adopted.style.maxHeight = "none";
  adopted.classList.add("pcb-svg");
  return adopted;
}

function contentUrl(path) { return `/api/pcb-content/${path}`; }
function picksUrl(path) { return `/api/pcb-picks/${path}`; }

// Fetch a board's pad-picker data (pads + identity), or null when the board
// has no picks sidecar / the fetch fails — the picker then just doesn't arm.
async function fetchPicks(board, signal) {
  if (!board || !board.picks) return null;
  try {
    const r = await fetch(picksUrl(board.picks), { signal });
    return r.ok ? await r.json() : null;
  } catch { return null; }
}

// Fetch a board's view SVGs — Top/Bottom/Overlay plus any inner planes — keyed
// by view name ({ top, bottom, overlay, inner1, … }). Returns null if any of the
// three fixed views fail; an inner plane that fails to load is simply omitted,
// so its toggle button never appears rather than blocking the whole board.
async function fetchViews(board, signal) {
  try {
    const entries = orderedViews(board);
    const texts = await Promise.all(
      entries.map((e) => fetch(contentUrl(e.path), { signal }).then(r => r.ok ? r.text() : null, () => null)),
    );
    const views = {};
    entries.forEach((e, i) => { if (texts[i] != null) views[e.view] = texts[i]; });
    if (!views.top || !views.bottom || !views.overlay) return null;
    return views;
  } catch { return null; }
}

// Board outer dimensions readout. Authoritative source is the board element's
// width/height, carried in picks.json (pick-data.ts); when a board has no picks
// sidecar we fall back to the mounted SVG's viewBox (Gerber units ÷ unitsPerMm),
// which is the rendered extent (a hair larger than the cut outline). Returns a
// "134 × 100 mm" string, or null if neither source is available.
function fmtMm(n) {
  return (Math.round(n * 10) / 10).toString();
}
function boardDimsText(picks, wrapper) {
  const s = picks && picks.size;
  if (s && s.width && s.height) return `${fmtMm(s.width)} × ${fmtMm(s.height)} mm`;
  const svg = wrapper && wrapper.querySelector("svg.pcb-svg");
  const vb = svg && svg.viewBox && svg.viewBox.baseVal;
  const per = (picks && picks.unitsPerMm) || 1000;
  if (vb && vb.width && vb.height) return `${fmtMm(vb.width / per)} × ${fmtMm(vb.height / per)} mm`;
  return null;
}
// Via tally for the dimensions chip. Vias live in picks.json (pick-data.ts);
// without a picks sidecar there is no via data, so this returns null and the
// chip shows dimensions alone. Returns a "42 vias" string (singular "1 via").
function viaCountText(picks) {
  const vias = picks && picks.vias;
  if (!Array.isArray(vias)) return null;
  return `${vias.length} via${vias.length === 1 ? "" : "s"}`;
}
// Clearance floor for the chip — the tightest cross-net copper gap (clearance.ts).
// Returns a "0.11 mm floor" string, or null when a board has no clearance sidecar.
function clearanceText(picks) {
  const f = picks && picks.clearance && picks.clearance.floor;
  if (typeof f !== "number") return null;
  return `${f.toFixed(3)} mm floor`;
}
// Manual-routing conversion for the chip — the authored-connection counts and the score (scorecard.ts).
// The headline of the effort to take the board off the autorouter onto deliberate hand copper.
function manualText(picks) {
  const sc = picks && picks.scorecard;
  if (!sc || typeof sc.score !== "number") return null;
  return `${sc.pcbPath} pcbPath · ${sc.pcbComb} pcbComb · ${sc.score}% score`;
}

// Create or update the bottom-centre dimensions chip in `wrapper`. The chip carries the
// glanceable readout (dims · vias · floor) plus a clickable checks badge — green when the
// board is clean, amber with a count when clearance.ts found genuine overlap/DRC errors —
// that opens the details modal.
function updateDimsChip(wrapper, picks) {
  if (!wrapper) return;
  closeChecksModal(wrapper);
  const text = [boardDimsText(picks, wrapper), viaCountText(picks), clearanceText(picks), manualText(picks)].filter(Boolean).join(" · ");
  const errors = (picks && Array.isArray(picks.errors)) ? picks.errors : null;
  const warns = advisoryCount(picks);
  let el = wrapper.querySelector(".pcb-dims");
  if (!text && !errors && !warns) { if (el) el.remove(); return; }
  if (!el) {
    el = document.createElement("div");
    el.className = "pcb-dims";
    wrapper.appendChild(el);
  }
  el.textContent = "";
  if (text) el.appendChild(Object.assign(document.createElement("span"), { className: "pcb-dims-text", textContent: text }));
  if (errors || warns) {
    // Three states, worst wins: red for hard DRC errors (incl. floating pads), amber for the
    // soft advisories (decoupling / ampacity / sourcing), green when both are clean.
    // `has-issues` tracks DRC errors ONLY, so it stays the manufacturability signal.
    const nErr = errors ? errors.length : 0;
    const badge = document.createElement("button");
    badge.type = "button";
    badge.className = "pcb-checks" + (nErr ? " has-issues" : warns ? " has-warns" : "");
    badge.textContent = nErr ? `⚠ ${nErr} issue${nErr === 1 ? "" : "s"}`
      : warns ? `⚠ ${warns} advisor${warns === 1 ? "y" : "ies"}`
      : "✓ clean";
    badge.title = "Clearance · DRC · decoupling · ampacity · fab";
    badge.addEventListener("click", (e) => { e.stopPropagation(); openChecksModal(wrapper, picks); });
    el.appendChild(badge);
  }
}

// --- Board-checks modal ---
// One panel opened from the chip's checks badge: the clearance floor with its tightest
// cross-net pairs, then the genuine overlap/DRC errors (or a clean note). Text-only via
// textContent — error strings are raw circuit-json messages.
function closeChecksModal(wrapper) {
  const m = wrapper && wrapper.querySelector(".pcb-checks-modal");
  if (m) m.remove();
}
function makeRow(cls, left, right) {
  const row = document.createElement("div");
  row.className = cls;
  row.appendChild(Object.assign(document.createElement("span"), { className: "k", textContent: left }));
  if (right != null) row.appendChild(Object.assign(document.createElement("span"), { className: "v", textContent: right }));
  return row;
}
function checkHead(text) {
  return Object.assign(document.createElement("div"), { className: "pcb-checks-h", textContent: text });
}
// A checks row that, given a `reveal` action, closes the modal and jumps the board to the
// thing it names (pan/zoom + select in the inspector). `reveal` null → a plain static row
// (nothing placed to jump to). Shared by every jumpable section: clearance, footprint,
// decoupling, ampacity.
function makeActionRow(cls, left, right, wrapper, reveal) {
  const row = makeRow(cls, left, right);
  if (!reveal) return row;
  row.classList.add("clickable");
  row.title = "Show on board";
  row.addEventListener("click", (e) => {
    e.stopPropagation();
    closeChecksModal(wrapper);
    reveal();
  });
  return row;
}
// A clearance-pair row: names where it pinches (the witness coordinate) and, when the pair
// carries its ends (clearance.ts), jumps to that pinch. Pairs without `ends` (an older
// sidecar) render static.
function makeClearanceRow(p, wrapper) {
  const ends = Array.isArray(p.ends) ? p.ends : null;
  const row = makeActionRow("pcb-checks-row", `${p.a} ↔ ${p.b}`, `${p.gap.toFixed(3)} mm`, wrapper, ends ? () => revealClearance(ends) : null);
  if (ends) {
    const mx = ends.reduce((s, e) => s + e.x, 0) / ends.length;
    const my = ends.reduce((s, e) => s + e.y, 0) / ends.length;
    row.querySelector(".k").appendChild(Object.assign(document.createElement("span"), {
      className: "pcb-checks-at", textContent: `  ${mx.toFixed(2)}, ${my.toFixed(2)} mm`,
    }));
  }
  return row;
}
// Count the advisory (amber) flags across every soft check — decoupling drift + missing
// decouplers (both in capAudit.flagged), thin current traces, unsourced parts.
// Separate from picks.errors, which are the hard (red) DRC failures.
function advisoryCount(picks) {
  if (!picks) return 0;
  let n = 0;
  if (picks.capAudit) n += picks.capAudit.flagged || 0;
  if (picks.ampacity) n += picks.ampacity.flagged || 0;
  if (picks.fab && Array.isArray(picks.fab.unsourced)) n += picks.fab.unsourced.length;
  return n;
}
// Append `rows` (ready row elements) to `card`, showing the first `limit` and tucking the rest
// behind a "Show N more" toggle. Keeps a long report glanceable — the worst few show, the tail
// expands on demand. Callers sort so anything that must stay visible (flagged rows) is up top
// and pass a `limit` that covers it.
function addCollapsibleRows(card, rows, limit) {
  const shown = Math.min(Math.max(limit, 0), rows.length);
  for (let i = 0; i < shown; i++) card.appendChild(rows[i]);
  const rest = rows.slice(shown);
  if (!rest.length) return;
  const more = document.createElement("div");
  more.className = "pcb-checks-more";
  more.hidden = true;
  for (const r of rest) more.appendChild(r);
  card.appendChild(more);
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "pcb-checks-toggle";
  const sync = () => { toggle.textContent = more.hidden ? `Show ${rest.length} more ▾` : "Show less ▴"; };
  sync();
  toggle.addEventListener("click", (e) => { e.stopPropagation(); more.hidden = !more.hidden; sync(); });
  card.appendChild(toggle);
}
// The requirements scorecard (scorecard.ts) at the top of the panel: the board's rules as
// pass/fail, the same verdict the build prints in the terminal. Gates (must hold to fab) lead
// with ✓/✗; the manual-routing goals show the conversion score and its backlog (auto/deferred
// connections) tucked behind a toggle. One result, from the same geometry both audiences read.
function appendScorecard(card, picks) {
  const sc = picks && picks.scorecard;
  if (!sc || !Array.isArray(sc.checks)) return;
  const mark = { pass: "✓", fail: "✗", warn: "•" };
  const gates = sc.checks.filter((c) => c.kind === "gate");
  const goals = sc.checks.filter((c) => c.kind === "goal");
  const passed = gates.filter((c) => c.status === "pass").length;
  card.appendChild(checkHead(`Requirements — gates ${passed}/${gates.length}${sc.gatesPass ? "" : " ✗ not fab-ready"} · ${sc.score}% score`));
  for (const c of gates) {
    card.appendChild(makeRow("pcb-checks-row" + (c.status === "pass" ? "" : " issue"), `${mark[c.status]} ${c.label}`, c.value));
    // Detail on a gate is either its offending items (when failing) or an advisory such as the
    // sub-Nominal body pairs (when passing); show it collapsibly either way.
    const drows = (c.detail || []).map((d) => makeRow("pcb-checks-row", `— ${d}`, null));
    if (drows.length) addCollapsibleRows(card, drows, 0);
  }
  for (const c of goals) {
    card.appendChild(makeRow("pcb-checks-row", `${mark[c.status]} ${c.label}`, c.value));
    const rows = (c.detail || []).map((d) => makeRow("pcb-checks-row", `— ${d}`, null));
    if (rows.length) addCollapsibleRows(card, rows, 0);
  }
}
function openChecksModal(wrapper, picks) {
  closeChecksModal(wrapper);
  const clearance = (picks && picks.clearance) || {};
  const errors = (picks && Array.isArray(picks.errors)) ? picks.errors : [];

  const modal = document.createElement("div");
  modal.className = "pcb-checks-modal";
  modal.addEventListener("click", () => closeChecksModal(wrapper));
  // The modal overlays the board but lives INSIDE the PanZoom container, so pointer and
  // wheel events over it otherwise bubble to PanZoom — the wheel zooms the board behind
  // it, and (because PanZoom takes pointer capture on pointerdown) a captured pointer
  // never delivers its click to a row's <div>, so the rows can't be clicked. Swallow
  // those events at the overlay: the card scrolls natively and rows get their clicks.
  // `click` is left to bubble so a backdrop click still closes.
  for (const ev of ["pointerdown", "pointermove", "pointerup", "wheel"]) {
    modal.addEventListener(ev, (e) => e.stopPropagation());
  }
  const card = document.createElement("div");
  card.className = "pcb-checks-card";
  card.addEventListener("click", (e) => e.stopPropagation());

  const head = document.createElement("div");
  head.className = "pcb-checks-head";
  head.appendChild(Object.assign(document.createElement("span"), { textContent: "Board checks" }));
  const x = Object.assign(document.createElement("button"), { type: "button", className: "pcb-checks-x", textContent: "✕" });
  x.addEventListener("click", () => closeChecksModal(wrapper));
  head.appendChild(x);
  card.appendChild(head);

  // The requirements scorecard leads the panel — the board's verdict before the detail sections.
  appendScorecard(card, picks);

  // Clearance floor + tightest pairs — collapsed to the tightest few (the floor is row 1).
  if (typeof clearance.floor === "number") {
    card.appendChild(checkHead(`Clearance floor — ${clearance.floor.toFixed(3)} mm`));
    const rows = (clearance.tight || []).map((p) => makeClearanceRow(p, wrapper));
    addCollapsibleRows(card, rows, 3);
  }

  // Footprint (component-body) clearance floor + tightest body pairs (footprint-audit.ts) — the
  // body-to-body sibling of the copper floor above, catching parts whose plastic/courtyard fouls a
  // neighbour even when the copper clears. Informational (a true overlap rides in Issues below).
  const foot = (picks && picks.footprints) || null;
  if (foot && typeof foot.floor === "number") {
    card.appendChild(checkHead(`Footprint clearance floor — ${foot.floor.toFixed(3)} mm`));
    const rows = (foot.tight || []).map((p) => makeActionRow("pcb-checks-row", `${p.a} ↔ ${p.b}`, `${p.gap.toFixed(3)} mm`, wrapper, () => revealComponent(p.a)));
    addCollapsibleRows(card, rows, 3);
  }

  // Hard DRC errors (clearance.ts) — floating pads, pour shorts, blind vias, courtyard overlaps…
  // These drive the red badge, so they sit near the top: a failing board leads with what's wrong.
  card.appendChild(checkHead(errors.length ? `Issues (${errors.length})` : "Issues"));
  if (!errors.length) card.appendChild(Object.assign(document.createElement("div"), { className: "pcb-checks-clean", textContent: "No overlap, floating-pad, or DRC errors." }));
  else for (const er of errors) card.appendChild(makeRow("pcb-checks-row issue", er.text, er.kind));

  // Decoupling (cap-audit.ts): each declared cap's pad gap to its target vs its per-job budget,
  // plus any chip missing a decoupler. Coverage gaps (amber) show first; placement rows collapse.
  const audit = (picks && picks.capAudit) || null;
  if (audit && Array.isArray(audit.rows) && audit.rows.length) {
    card.appendChild(checkHead(audit.flagged ? `Decoupling — ${audit.flagged} to review` : `Decoupling (${audit.rows.length})`));
    for (const m of (audit.missing || [])) card.appendChild(makeActionRow("pcb-checks-row warn", `${m.part} · ${m.pin}`, "no decoupler declared", wrapper, () => revealComponent(m.part, m.pin)));
    const rows = audit.rows.map((r) => {
      const left = r.role ? `${r.cap} → ${r.near} · ${r.role}` : `${r.cap} → ${r.near}`;
      const right = r.gap == null ? (r.note || "not placed") : `${r.gap.toFixed(2)} / ${r.budget} mm`;
      // gap null = a part isn't placed, so there's nothing on the board to jump to.
      return makeActionRow("pcb-checks-row" + (r.over ? " warn" : ""), left, right, wrapper, r.gap == null ? null : () => revealComponent(r.cap));
    });
    addCollapsibleRows(card, rows, Math.max(3, audit.rows.filter((r) => r.over).length));
  }

  // Ampacity (ampacity-audit.ts): declared current-carrying traces vs the width they want.
  // Each row jumps to (and selects) the trace it names.
  const amp = (picks && picks.ampacity) || null;
  if (amp && Array.isArray(amp.rows) && amp.rows.length) {
    card.appendChild(checkHead(amp.flagged ? `Ampacity — ${amp.flagged} thin` : `Ampacity (${amp.rows.length})`));
    const rows = amp.rows.map((r) => makeActionRow("pcb-checks-row" + (r.over ? " warn" : ""), `${r.label} · ${r.role}`, `${r.width.toFixed(2)} / ${r.minWidth} mm`, wrapper, () => revealTraceRoute(r.label)));
    addCollapsibleRows(card, rows, Math.max(3, amp.flagged));
  }

  // Fab readout (pick-data.ts): BOM sourcing + the tightest drill/annular the fab must hit.
  const fab = (picks && picks.fab) || null;
  if (fab) {
    card.appendChild(checkHead("Fab"));
    const ps = fab.partsSourced || { sourced: 0, total: 0 };
    const unsourced = Array.isArray(fab.unsourced) ? fab.unsourced : [];
    card.appendChild(makeRow("pcb-checks-row" + (unsourced.length ? " warn" : ""), "Parts sourced", `${ps.sourced} / ${ps.total}`));
    if (unsourced.length) card.appendChild(makeRow("pcb-checks-row warn", "Unsourced", unsourced.join(", ")));
    if (fab.layers != null) card.appendChild(makeRow("pcb-checks-row", "Layers", String(fab.layers)));
    if (fab.minDrillMm != null) card.appendChild(makeRow("pcb-checks-row", "Min drill", `${fab.minDrillMm.toFixed(2)} mm`));
    if (fab.minAnnularMm != null) card.appendChild(makeRow("pcb-checks-row", "Min annular", `${fab.minAnnularMm.toFixed(2)} mm`));
  }

  modal.appendChild(card);
  wrapper.appendChild(modal);
}

function makeViewToggle(views, onSelect) {
  const wrap = document.createElement("div");
  wrap.className = "pcb-view-toggle";
  wrap.setAttribute("role", "group");
  wrap.setAttribute("aria-label", "PCB layers");
  for (const view of views) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tool-seg-btn pcb-view-btn";
    btn.dataset.view = view;
    btn.textContent = viewLabel(view);
    btn.addEventListener("click", event => { event.stopPropagation(); onSelect(view); });
    wrap.append(btn);
  }
  return wrap;
}

let styles;
function loadStyles() {
  if (!styles) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/css/pcb.css";
    styles = new Promise((resolve, reject) => {
      link.onload = resolve;
      link.onerror = () => {
        link.remove();
        styles = null;
        reject(new Error("PCB styles unavailable"));
      };
      document.head.append(link);
    });
  }
  return styles;
}

async function loadBoard(source, signal) {
  const response = await fetch("/api/pcb", { signal, cache: "no-cache" });
  if (!response.ok) throw new Error("Board list unavailable");
  const board = (await response.json()).find(entry => entry.source === source);
  if (!board) throw new Error("Board unavailable");
  const [views, picks] = await Promise.all([fetchViews(board, signal), fetchPicks(board, signal)]);
  if (!views) throw new Error("Board layers unavailable");
  const layers = orderedViews(board).map(entry => entry.view).filter(view => views[view]);
  return { views, picks, layers };
}

export async function mountPcbView(wrapper, source, signal) {
  let board, activeView, toggle, svg, panZoom, minimap, chrome;
  let generation = 0;

  function installPicker() {
    const { picks } = board;
    installPadPicker(svg, picks ? {
      pads: picks.pads, vias: picks.vias, traces: picks.traces, source, wrapper, panZoom,
    } : null);
  }

  function syncToggle() {
    for (const btn of toggle.querySelectorAll("button")) {
      const active = btn.dataset.view === activeView;
      btn.classList.toggle("active", active);
      btn.setAttribute("aria-pressed", String(active));
    }
  }

  function releaseLayer() {
    panZoom?.destroy();
    minimap?.destroy();
    chrome?.destroy();
  }

  function mountLayer(view) {
    const next = parseSvgString(board.views[view]);
    const previous = panZoom?.getTransform();
    releaseLayer();
    svg?.remove();
    svg = next;
    wrapper.prepend(svg);
    chrome = makeChromeFit(wrapper, PCB_CHROME);
    minimap = makeMinimap(svg, wrapper, chrome.obstacles);
    panZoom = PanZoom.wrap(svg, {
      container: wrapper,
      initialFit: false,
      // The board's viewBox uses Gerber units. Its fit scale is below PanZoom's default floor.
      minScale: 0.0001,
      fitObstacles: chrome.obstacles,
      onTransformChange: transform => pcbSaveTransform(source, transform),
      onTransformLive: transform => minimap.update(transform),
    });
    wrapper.querySelector(".pan-zoom-reset")?.remove();
    wrapper.append(minimap.el, makeResetButton(panZoom, {
      transformKey: pcbTransformKey(source),
      refit: chrome.refit,
    }));
    chrome.attach(panZoom, minimap);
    updateDimsChip(wrapper, board.picks);
    chrome.open(previous || pcbLoadTransform(source));
    activeView = view;
    pcbSaveView(source, view);
    syncToggle();
    installPicker();
  }

  function selectLayer(view) {
    if (view !== activeView) mountLayer(view);
  }

  function render(next) {
    const previous = board;
    board = next;
    if (!toggle || previous.layers.join() !== next.layers.join()) {
      const newToggle = makeViewToggle(next.layers, selectLayer);
      if (toggle) toggle.replaceWith(newToggle);
      else wrapper.append(newToggle);
      toggle = newToggle;
    }
    const inspect = wrapper.querySelector(".pad-pick-toggle");
    if (next.picks?.pads?.length) {
      if (!inspect) wrapper.append(makePadPickToggle());
    } else inspect?.remove();

    if (previous) {
      clearPadSelection();
      closeChecksModal(wrapper);
    }
    const view = next.views[activeView] ? activeView : pcbLoadView(source, next.layers) || "overlay";
    if (view !== activeView || next.views[view] !== previous?.views[view]) mountLayer(view);
    else { syncToggle(); installPicker(); updateDimsChip(wrapper, next.picks); }
  }

  signal.addEventListener("abort", () => {
    releaseLayer();
    if (board) clearPadPicker();
  }, { once: true });

  const [, initial] = await Promise.all([loadStyles(), loadBoard(source, signal)]);
  if (signal.aborted) return;
  render(initial);

  async function refresh() {
    const requested = ++generation;
    try {
      const next = await loadBoard(source, signal);
      if (!signal.aborted && requested === generation) render(next);
    } catch (error) {
      if (!signal.aborted) console.warn("Refresh PCB view:", error.message);
    }
  }
  window.addEventListener(HSM_EVENTS.FILES_CHANGED, event => {
    if (event.detail?.files?.includes(source)) refresh();
  }, { signal });
  window.addEventListener(HSM_EVENTS.DEPLOY, refresh, { signal });
}
