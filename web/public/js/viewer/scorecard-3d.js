// The 3D viewer's scorecard bar + drill-down modal — the enclosure's requirements verdict,
// mirroring the PCB board-checks UI (public/js/viewer/pcb.js) for the STEP viewer. Reads the
// <model>.scorecard.json sidecar (contracts/scorecard-sidecar.js) written by the build's
// _scorecard.py, and draws a thin bottom bar plus a modal that drills each gate/goal into its
// detail rows. The sidecar's port inventory goes to port-markers.js, which draws each connector
// on the model. One verdict, two surfaces: the same data the terminal prints.

import { scorecardPathFor, isScorecard, FOCUS_IDS, focusAxes, failingBends, bendPinned,
         unmountedComponents, sizeText } from "/contracts/scorecard-sidecar.js";
import { scenePartNames, highlightParts, clearHighlight } from "./part-highlight.js";
import { showPorts, clearPorts, makePortToggle } from "./port-markers.js";
import { showShapeBoxes, clearShapeBoxes, makeShapeBoxToggle } from "./shape-boxes.js";

const MARK = { pass: "✓", fail: "✗", warn: "•" };

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

function row(cls, left, right) {
  const r = el("div", cls);
  r.appendChild(el("span", "sc-k", left));
  if (right != null) r.appendChild(el("span", "sc-v", right));
  return r;
}

// Detail rows tucked behind a "Show N more" toggle so a long list (every unplaced part,
// every tight pair) doesn't flood the card. limit=0 hides them all until asked.
function addCollapsible(card, rows, limit = 0) {
  for (const r of rows.slice(0, limit)) card.appendChild(r);
  const hidden = rows.slice(limit);
  if (!hidden.length) return;
  const wrap = el("div", "sc-more");
  wrap.style.display = "none";
  for (const r of hidden) wrap.appendChild(r);
  const toggle = el("button", "sc-toggle", `Show ${hidden.length} more ▾`);
  toggle.type = "button";
  let open = false;
  toggle.addEventListener("click", () => {
    open = !open;
    wrap.style.display = open ? "" : "none";
    toggle.textContent = open ? "Show less ▴" : `Show ${hidden.length} more ▾`;
  });
  card.appendChild(toggle);
  card.appendChild(wrap);
}

// A row that names solids in the scene: click it to close the modal and highlight them. The one
// gesture every itemized row on this card shares — a failing bend's two end bodies, an unmounted
// component, a clearance pair.
function linkRow(cls, left, right, refs, wrapper, title) {
  const r = row(cls + (refs.length ? " clickable" : ""), left, right);
  if (refs.length) {
    r.title = title || "Show " + refs.join(" + ") + " on the model";
    r.addEventListener("click", (e) => {
      e.stopPropagation();
      closeModal(wrapper);
      highlightParts(refs);
    });
  }
  return r;
}

function appendCheck(card, c, gray, wrapper, partNames, showDetail = true) {
  const statusCls = c.status === "fail" ? " issue" : c.status === "warn" ? " warn" : "";
  card.appendChild(row("sc-row" + statusCls + (gray ? " gray" : ""), `${MARK[c.status]} ${c.label}`, c.value));
  if (!showDetail) return;
  // A detail row that names solids in the scene becomes clickable — it closes the modal and
  // highlights them on the model (part-highlight.js). A clearance pair names two, a clash names
  // the two bodies that share volume, an unrouted segment names its two ends.
  const drows = (c.detail || []).map((d) => {
    const refs = [...partNames].filter((n) => d.includes(n));
    const r = row("sc-row sub" + (gray ? " gray" : "") + (refs.length ? " clickable" : ""), `— ${d}`, null);
    if (refs.length) {
      r.title = "Show " + refs.join(" + ") + " on the model";
      r.addEventListener("click", (e) => {
        e.stopPropagation();
        closeModal(wrapper);
        highlightParts(refs);
      });
    }
    return r;
  });
  addCollapsible(card, drows, 0);
}

// A run of checks behind one toggle, each keeping its own detail toggle inside.
//
// WHAT HOLDS IS A COUNT, NOT A LIST. A card opens on the decisions it is asking for, and a
// check that passes is not one of them — seventy of them ahead of the four that are is the
// card asking the reader to do the filtering it was built to do.
function addCollapsedChecks(card, checks, label, wrapper, partNames, gray = false) {
  if (!checks.length) return;
  const wrap = el("div", "sc-more");
  wrap.style.display = "none";
  for (const c of checks) appendCheck(wrap, c, gray, wrapper, partNames);
  const toggle = el("button", "sc-toggle", `${label} ▾`);
  toggle.type = "button";
  let open = false;
  toggle.addEventListener("click", () => {
    open = !open;
    wrap.style.display = open ? "" : "none";
    toggle.textContent = open ? `${label} ▴` : `${label} ▾`;
  });
  card.appendChild(toggle);
  card.appendChild(wrap);
}

function closeModal(wrapper) {
  const m = wrapper.querySelector(".sc-modal");
  if (m) m.remove();
}

// ── Size ────────────────────────────────────────────────────────────────────────────────────
// How big the thing on the canvas is, in the units both readers use: the printed box, and the
// whole assembly around it. Above the focus panels, because it is what the rest is measured in.
function appendSize(card, sc) {
  const rows = Array.isArray(sc.size) ? sc.size : [];
  if (!rows.length) return;
  card.appendChild(el("div", "sc-h", "Size — width × depth × height"));
  for (const s of rows) {
    const r = row("sc-row size", s.id, sizeText(s));
    r.title = s.label;
    card.appendChild(r);
  }
}

// ── The focus panels ────────────────────────────────────────────────────────────────────────
// The two axes the work is on get the top of the card and a panel each, itemized down to the
// thing a fix acts on: a run's two end bodies, a component's missing joint. Every other axis is
// a line. Both panels read the sidecar's uncapped tables (`bends`, `mounts`).

// Every failing run, worst first, each row clicking through to the two bodies its ends stand on.
function bendPanel(sc, wrapper, partNames) {
  return failingBends(sc).map((b) => {
    const ends = [b.frm, b.to].map((a) => String(a).split(".")[0]);
    const refs = ends.filter((n) => partNames.has(n));
    const pinned = bendPinned(b);
    return linkRow(
      "sc-row sub issue",
      `— ${b.id} ${ends[0]} → ${ends[1]}` + (pinned ? "  · move a body" : "  · raise the radius"),
      `${b.atSpec}/${b.bends} · R${b.radius.toFixed(1)} of R${b.minBend}`,
      refs, wrapper,
      pinned
        ? `Pinned by its placement — reach R${b.reach == null ? "∞" : b.reach.toFixed(1)}. `
          + `Show ${refs.join(" + ")} on the model`
        : `Its legs seat R${b.reach == null ? "∞" : b.reach.toFixed(1)} — raise bend=. `
          + `Show ${refs.join(" + ")} on the model`);
  });
}

// Every component with no printed feature fastening it — one row per joint still to design,
// clicking through to the body that needs it.
function mountPanel(sc, wrapper, partNames) {
  return unmountedComponents(sc).map((m) =>
    linkRow("sc-row sub warn", `— ${m.component}`,
            m.held && m.held !== "none" ? `${m.held} — not printed in` : "nothing holds it",
            partNames.has(m.component) ? [m.component] : [], wrapper));
}

const FOCUS_PANEL = { "bend-radius": bendPanel, mounted: mountPanel };

// The FOCUS block: the header counts, then each focus check with its own panel of rows.
//
// AN AXIS AT SPEC ITEMIZES NOTHING. Its panel exists to name the thing a fix acts on, and an
// axis with nothing to fix has no such thing — what stands under a passing check is the note
// explaining how it is graded, which is reading for whoever is changing the gate and noise for
// everyone else. It stays behind the toggle with the rest of the detail.
function appendFocus(card, sc, wrapper, partNames) {
  const axes = focusAxes(sc);
  const byId = Object.fromEntries(sc.checks.map((c) => [c.id, c]));
  const present = FOCUS_IDS.filter((id) => byId[id]);
  if (!present.length) return present;

  const h = el("div", "sc-h focus");
  h.appendChild(el("span", null, "Focus"));
  axes.forEach((a, i) => {
    if (i) h.appendChild(el("span", "sc-sep", "·"));
    h.appendChild(el("span", "sc-focus-n" + (a.status === "fail" ? " issue" : a.status === "warn" ? " warn" : ""),
                     `${a.done}/${a.total} ${a.label}`));
  });
  card.appendChild(h);

  for (const id of present) {
    const c = byId[id];
    if (c.status === "pass") {
      appendCheck(card, c, false, wrapper, partNames);   // line + its detail behind the toggle
      continue;
    }
    appendCheck(card, c, false, wrapper, partNames, false);
    // The panel's rows come off the sidecar's table. A sidecar carrying the check but not its
    // table falls back to the check's own detail, so the axis still itemizes.
    const panel = FOCUS_PANEL[id];
    const rows = panel ? panel(sc, wrapper, partNames) : [];
    addCollapsible(card, rows.length ? rows
      : (c.detail || []).map((d) => row("sc-row sub", `— ${d}`)), 6);
  }
  return present;
}

function openModal(wrapper, sc, title) {
  closeModal(wrapper);
  clearHighlight(); // reopening the checks restores the full model
  const modal = el("div", "sc-modal");
  modal.addEventListener("click", () => closeModal(wrapper)); // backdrop closes
  // Don't leak orbit/zoom gestures to the TrackballControls on the canvas behind the modal.
  for (const ev of ["pointerdown", "pointermove", "pointerup", "wheel"]) {
    modal.addEventListener(ev, (e) => e.stopPropagation());
  }
  const card = el("div", "sc-card");
  card.addEventListener("click", (e) => e.stopPropagation());

  const head = el("div", "sc-head");
  head.appendChild(el("span", null, `${title} checks`));
  const x = el("button", "sc-x", "✕");
  x.type = "button";
  x.addEventListener("click", () => closeModal(wrapper));
  head.appendChild(x);
  card.appendChild(head);

  const gates = sc.checks.filter((c) => c.kind === "gate");
  const goals = sc.checks.filter((c) => c.kind === "goal");
  const passed = gates.filter((c) => c.status === "pass").length;
  const partNames = scenePartNames(); // solids in the scene → which rows are clickable

  // How big it is, then the two focus axes itemized. Below, each keeps its line in the block it
  // belongs to; its rows are above.
  appendSize(card, sc);
  const promoted = appendFocus(card, sc, wrapper, partNames);
  const shown = (c) => !promoted.includes(c.id);

  // A promoted check already has its line and its panel at the top of the card. Its block below
  // counts it and does not draw it again.
  const holds = (c) => c.status === "pass";
  const red = gates.filter((c) => !holds(c) && shown(c));

  card.appendChild(el("div", "sc-h",
    `Gates — ${passed}/${gates.length} pass` + (sc.gatesPass ? "" : " · not build-ready")));
  for (const c of red) appendCheck(card, c, false, wrapper, partNames);
  addCollapsedChecks(card, gates.filter((c) => holds(c) && shown(c)), `${passed} holding`,
                     wrapper, partNames);

  const active = goals.filter((c) => c.active);
  const deferred = goals.filter((c) => !c.active);
  const open = active.filter((c) => !holds(c) && shown(c));
  const met = active.filter((c) => holds(c) && shown(c));
  if (open.length || met.length) {
    card.appendChild(el("div", "sc-h", "Goal"));
    for (const c of open) appendCheck(card, c, false, wrapper, partNames);
    addCollapsedChecks(card, met, `${met.length} met`, wrapper, partNames);
  }
  if (deferred.length) {
    card.appendChild(el("div", "sc-h", `Deferred — placed ${sc.placed}% · located ${sc.located}% · `
      + `shaped ${sc.shaped}% · routed ${sc.routed}% · held ${sc.held}%`));
    addCollapsedChecks(card, deferred, `${deferred.length} not asked for yet`,
                       wrapper, partNames, true);
  }

  modal.appendChild(card);
  wrapper.appendChild(modal);
}

function gateCounts(sc) {
  const gates = sc.checks.filter((c) => c.kind === "gate");
  return { pass: gates.filter((c) => c.status === "pass").length, total: gates.length,
           fail: gates.filter((c) => c.status !== "pass").length };
}

function buildBar(wrapper, sc, title) {
  removeScorecard(wrapper);
  const g = gateCounts(sc);
  const bar = el("div", "sc-bar");
  // The bar says the two focus axes as counted things; the badge beside it carries the gate
  // verdict. An edition whose scorecard has neither axis falls back to its percentages.
  const axes = focusAxes(sc);
  if (axes.length) {
    axes.forEach((a, i) => {
      if (i) bar.appendChild(el("span", "sc-bar-text sc-sep", "·"));
      bar.appendChild(el("span", "sc-bar-text sc-focus-n"
        + (a.status === "fail" ? " issue" : a.status === "warn" ? " warn" : ""),
        `${a.done}/${a.total} ${a.label}`));
    });
  } else {
    bar.appendChild(el("span", "sc-bar-text",
      `gates ${g.pass}/${g.total} · placed ${sc.placed}% · located ${sc.located}% · shaped ${sc.shaped}%`));
  }
  const badge = el("button", "sc-badge" + (g.fail ? " has-issues" : ""),
    g.fail ? `✗ ${g.fail} gate${g.fail === 1 ? "" : "s"}` : "✓ checks");
  badge.type = "button";
  badge.addEventListener("click", (e) => { e.stopPropagation(); openModal(wrapper, sc, title); });
  bar.appendChild(badge);
  wrapper.appendChild(bar);
}

// Remove the bar, the port toggle, and any open modal — used before a re-mount (live reload) and
// by teardown. The markers themselves belong to the model, and go with it (clearPorts).
export function removeScorecard(wrapper) {
  if (!wrapper) return;
  const b = wrapper.querySelector(".sc-bar");
  if (b) b.remove();
  for (const sel of [".port-toggle", ".shape-box-toggle"]) {
    const t = wrapper.querySelector(sel);
    if (t) t.remove();
  }
  closeModal(wrapper);
}

// Fetch the sidecar for `file` and mount the bar on `wrapper`. No sidecar (404 / malformed) =
// no bar, silently — most STEP models don't carry a scorecard.
export async function mountScorecard(wrapper, file) {
  let sc = null;
  try {
    const r = await fetch("/api/step-scorecard/" + scorecardPathFor(file));
    if (r.ok) sc = await r.json();
  } catch {
    sc = null;
  }
  // The modal may have closed (or reloaded to another model) while we fetched — bail if the
  // wrapper is no longer in the document.
  if (!sc || !isScorecard(sc) || !wrapper.isConnected) return;
  // The card is titled by the model it belongs to — more than one assembly writes one now.
  buildBar(wrapper, sc, file.split("/").pop().replace(/\.step$/, ""));
  const ports = Array.isArray(sc.ports) ? sc.ports : [];
  if (ports.length) wrapper.appendChild(makePortToggle(showPorts(ports, file)));
  else clearPorts();
  const shapes = Array.isArray(sc.shapes) ? sc.shapes : [];
  if (shapes.length) wrapper.appendChild(makeShapeBoxToggle(showShapeBoxes(shapes, file)));
  else clearShapeBoxes();
}
