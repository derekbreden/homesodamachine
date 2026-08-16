// The 3D viewer's checks badge + drill-down modal — the enclosure's requirements verdict,
// mirroring the PCB board-checks UI (public/js/viewer/pcb.js) for the STEP viewer. Reads the
// <model>.scorecard.json sidecar (contracts/scorecard-sidecar.js) written by the build's
// _scorecard.py, and draws a badge at the bottom of the canvas that opens a modal drilling each
// gate/goal into its detail rows. One verdict, two surfaces: the same data the terminal prints.

import { scorecardPathFor, isScorecard, sizeText } from "/contracts/scorecard-sidecar.js";
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
// whole assembly around it. At the top of the card, because it is what the rest is measured in.
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

  // How big it is, then every gate: the ones that are red, and a count for the rest.
  appendSize(card, sc);

  const holds = (c) => c.status === "pass";
  const red = gates.filter((c) => !holds(c));

  card.appendChild(el("div", "sc-h",
    `Gates — ${passed}/${gates.length} pass` + (sc.gatesPass ? "" : " · not build-ready")));
  for (const c of red) appendCheck(card, c, false, wrapper, partNames);
  addCollapsedChecks(card, gates.filter(holds), `${passed} holding`, wrapper, partNames);

  const active = goals.filter((c) => c.active);
  const deferred = goals.filter((c) => !c.active);
  const open = active.filter((c) => !holds(c));
  const met = active.filter(holds);
  if (open.length || met.length) {
    card.appendChild(el("div", "sc-h", "Goal"));
    for (const c of open) appendCheck(card, c, false, wrapper, partNames);
    addCollapsedChecks(card, met, `${met.length} met`, wrapper, partNames);
  }
  if (deferred.length) {
    card.appendChild(el("div", "sc-h", `Deferred — placed ${sc.placed}% · located ${sc.located}% · `
      + `routed ${sc.routed}%`));
    addCollapsedChecks(card, deferred, `${deferred.length} not asked for yet`,
                       wrapper, partNames, true);
  }

  modal.appendChild(card);
  wrapper.appendChild(modal);
}

// Watches the mounted badge's height for the phone layout; one at a time, since
// one wrapper carries one badge.
let badgeSize = null;

// The verdict in one word, and the count when it is a bad one. Everything behind it —
// each gate, each goal's score, the sizes — is a click away in the modal.
function buildBadge(wrapper, sc, title) {
  removeScorecard(wrapper);
  const fail = sc.checks.filter((c) => c.kind === "gate" && c.status !== "pass").length;
  const badge = el("button", "sc-badge" + (fail ? " has-issues" : ""),
    fail ? `✗ ${fail} gate${fail === 1 ? "" : "s"}` : "✓ checks");
  badge.type = "button";
  badge.addEventListener("click", (e) => { e.stopPropagation(); openModal(wrapper, sc, title); });
  wrapper.appendChild(badge);
  // How much room the badge takes at the bottom of the wrapper, published for the
  // phone layout to stand the rail and Reset view on top of (viewer.css).
  //
  // Measured here and again on every resize. The first reading is taken inline
  // because offsetHeight forces the layout it reads, which holds in a tab that
  // is not being painted — a ResizeObserver in that tab does not run until the
  // tab is looked at, and the rail would stand over the badge until then.
  const publish = () => {
    wrapper.style.setProperty("--sc-badge-lift", `${Math.ceil(badge.offsetHeight) + 8}px`);
  };
  publish();
  badgeSize = new ResizeObserver(publish);
  badgeSize.observe(badge);
}

// Remove the badge and any open modal — used before a re-mount (live reload) and by teardown.
export function removeScorecard(wrapper) {
  if (!wrapper) return;
  if (badgeSize) { try { badgeSize.disconnect(); } catch {} badgeSize = null; }
  wrapper.style.removeProperty("--sc-badge-lift");
  const b = wrapper.querySelector(".sc-badge");
  if (b) b.remove();
  closeModal(wrapper);
}

// Fetch the sidecar for `file` and mount the badge on `wrapper`. No sidecar (404 / malformed) =
// no badge, silently — most STEP models don't carry a scorecard.
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
  if (!wrapper.isConnected) return;
  // Whatever the last model left on screen goes, card or no card.
  removeScorecard(wrapper);
  if (!sc || !isScorecard(sc)) return;
  buildBadge(wrapper, sc, file.split("/").pop().replace(/\.step$/, ""));
}
