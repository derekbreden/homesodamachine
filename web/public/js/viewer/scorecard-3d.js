// The 3D viewer's scorecard bar + drill-down modal — the enclosure's requirements verdict,
// mirroring the PCB board-checks UI (public/js/viewer/pcb.js) for the STEP viewer. Reads the
// <model>.scorecard.json sidecar (contracts/scorecard-sidecar.js) written by the build's
// scorecard.py, and draws a thin bottom bar plus a modal that drills each gate/goal into its
// detail rows. One verdict, two surfaces: the same data the terminal prints.

import { scorecardPathFor, isScorecard } from "/contracts/scorecard-sidecar.js";
import { scenePartNames, highlightParts, clearHighlight } from "./part-highlight.js";

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

function appendCheck(card, c, gray, wrapper, partNames) {
  const statusCls = c.status === "fail" ? " issue" : c.status === "warn" ? " warn" : "";
  card.appendChild(row("sc-row" + statusCls + (gray ? " gray" : ""), `${MARK[c.status]} ${c.label}`, c.value));
  // A detail row that names solids in the scene becomes clickable — it closes the modal and
  // highlights those parts on the model (part-highlight.js). A clearance pair names two.
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

function closeModal(wrapper) {
  const m = wrapper.querySelector(".sc-modal");
  if (m) m.remove();
}

function openModal(wrapper, sc) {
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
  head.appendChild(el("span", null, "Enclosure checks"));
  const x = el("button", "sc-x", "✕");
  x.type = "button";
  x.addEventListener("click", () => closeModal(wrapper));
  head.appendChild(x);
  card.appendChild(head);

  const gates = sc.checks.filter((c) => c.kind === "gate");
  const goals = sc.checks.filter((c) => c.kind === "goal");
  const passed = gates.filter((c) => c.status === "pass").length;
  const partNames = scenePartNames(); // solids in the scene → which rows are clickable

  card.appendChild(el("div", "sc-h",
    `Gates — ${passed}/${gates.length} pass` + (sc.gatesPass ? "" : " · not build-ready")));
  for (const c of gates) appendCheck(card, c, false, wrapper, partNames);

  const focus = goals.filter((c) => c.active);
  const deferred = goals.filter((c) => !c.active);
  card.appendChild(el("div", "sc-h", `Goal — focus: placed ${sc.placed}% · located ${sc.located}% · shaped ${sc.shaped}%`));
  for (const c of focus) appendCheck(card, c, false, wrapper, partNames);
  if (deferred.length) {
    card.appendChild(el("div", "sc-h", `Deferred — routed ${sc.routed}% · held ${sc.held}%`));
    for (const c of deferred) appendCheck(card, c, true, wrapper, partNames);
  }

  modal.appendChild(card);
  wrapper.appendChild(modal);
}

function gateCounts(sc) {
  const gates = sc.checks.filter((c) => c.kind === "gate");
  return { pass: gates.filter((c) => c.status === "pass").length, total: gates.length,
           fail: gates.filter((c) => c.status !== "pass").length };
}

function buildBar(wrapper, sc) {
  removeScorecard(wrapper);
  const g = gateCounts(sc);
  const bar = el("div", "sc-bar");
  bar.appendChild(el("span", "sc-bar-text",
    `gates ${g.pass}/${g.total} · placed ${sc.placed}% · located ${sc.located}% · shaped ${sc.shaped}%`));
  const badge = el("button", "sc-badge" + (g.fail ? " has-issues" : ""),
    g.fail ? `✗ ${g.fail} gate${g.fail === 1 ? "" : "s"}` : "✓ checks");
  badge.type = "button";
  badge.addEventListener("click", (e) => { e.stopPropagation(); openModal(wrapper, sc); });
  bar.appendChild(badge);
  wrapper.appendChild(bar);
}

// Remove the bar + any open modal — used before a re-mount (live reload) and by teardown.
export function removeScorecard(wrapper) {
  if (!wrapper) return;
  const b = wrapper.querySelector(".sc-bar");
  if (b) b.remove();
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
  buildBar(wrapper, sc);
}
