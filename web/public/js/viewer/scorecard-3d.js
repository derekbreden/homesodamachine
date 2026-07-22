// The 3D viewer's scorecard bar + drill-down modal — the enclosure's requirements verdict,
// mirroring the PCB board-checks UI (public/js/viewer/pcb.js) for the STEP viewer. Reads the
// <model>.scorecard.json sidecar (contracts/scorecard-sidecar.js) written by the build's
// scorecard.py, and draws a thin bottom bar plus a modal that drills each gate/goal into its
// detail rows. The sidecar's port inventory goes to port-markers.js, which draws each connector
// on the model. One verdict, two surfaces: the same data the terminal prints.

import { scorecardPathFor, isScorecard } from "/contracts/scorecard-sidecar.js";
import { scenePartNames, highlightParts, clearHighlight } from "./part-highlight.js";
import { showPorts, clearPorts, makePortToggle } from "./port-markers.js";
import { showShapeBoxes, clearShapeBoxes, makeShapeBoxToggle } from "./shape-boxes.js";
import { isXrayEnabled, setXrayEnabled } from "./xray.js";

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

// The overlap-solid the editor baked for a pack-closes row ("a ∩ b: v mm³"), if it's in the scene.
// The name mirrors enclosure_assembly.py: `clash__a__b` (ASCII — the ∩ label doesn't survive a STEP
// round-trip). Null for any row without one (a clearance/routing row, or a non-editor build).
function clashSolidFor(detail, partNames) {
  const head = detail.split(":")[0];
  if (!head.includes(" ∩ ")) return null;
  const [a, b] = head.split(" ∩ ").map((s) => s.trim());
  const name = `clash__${a}__${b}`;
  return partNames.has(name) ? name : null;
}

// Flip x-ray on (via the toggle so its label refreshes too) so the parts ghost and a highlighted
// overlap volume nested inside them actually reads. No-op if already on.
function enableXray() {
  if (isXrayEnabled()) return;
  const btn = document.querySelector(".xray-toggle");
  if (btn) btn.click();
  else setXrayEnabled(true);
}

function appendCheck(card, c, gray, wrapper, partNames) {
  const statusCls = c.status === "fail" ? " issue" : c.status === "warn" ? " warn" : "";
  card.appendChild(row("sc-row" + statusCls + (gray ? " gray" : ""), `${MARK[c.status]} ${c.label}`, c.value));
  // A detail row that names solids in the scene becomes clickable — it closes the modal and
  // highlights them on the model (part-highlight.js). A clearance pair names two. A pack clash also
  // carries a baked overlap solid: prefer it — x-ray on + highlight the exact overlapping region,
  // rather than the two whole parts.
  const drows = (c.detail || []).map((d) => {
    const clash = clashSolidFor(d, partNames);
    const refs = clash ? [clash] : [...partNames].filter((n) => d.includes(n));
    const r = row("sc-row sub" + (gray ? " gray" : "") + (refs.length ? " clickable" : ""), `— ${d}`, null);
    if (refs.length) {
      r.title = clash ? "X-ray to the overlap on the model" : "Show " + refs.join(" + ") + " on the model";
      r.addEventListener("click", (e) => {
        e.stopPropagation();
        closeModal(wrapper);
        if (clash) enableXray();
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
  buildBar(wrapper, sc);
  const ports = Array.isArray(sc.ports) ? sc.ports : [];
  if (ports.length) wrapper.appendChild(makePortToggle(showPorts(ports, file)));
  else clearPorts();
  const shapes = Array.isArray(sc.shapes) ? sc.shapes : [];
  if (shapes.length) wrapper.appendChild(makeShapeBoxToggle(showShapeBoxes(shapes, file)));
  else clearShapeBoxes();
}
