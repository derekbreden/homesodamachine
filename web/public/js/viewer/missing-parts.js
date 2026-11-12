// The missing-parts mark: whether the machine on the canvas has everything it is meant to have.
//
// The machine's published facts list every run the plumbing needs and whether the machine as
// built completes it. This puts one small mark above Reset view: a green check when every run
// is complete, a red x when one is not — a tube that was never routed, a fitting that is not
// there. The mark covers no other control and moves none. A click on it opens the list behind
// it: each incomplete run with the tubes and fittings it lacks, and a click on a run lights the
// two bodies it would join. A model with no facts gets no mark. The site works it out from the
// published facts (/api/step-missing, contracts/missing-parts.js).

import { factsPathFor, bodyOf, sceneBodies, lacks } from "/contracts/missing-parts.js";
import { scenePartNames, highlightParts } from "./part-highlight.js";

const SVG = "http://www.w3.org/2000/svg";
const CHECK = "M3.5 8.5l3 3 6-7";
const CROSS = "M4.5 4.5l7 7M11.5 4.5l-7 7";

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

function icon(d) {
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("viewBox", "0 0 16 16");
  svg.setAttribute("aria-hidden", "true");
  const path = document.createElementNS(SVG, "path");
  path.setAttribute("d", d);
  svg.appendChild(path);
  return svg;
}

// Orbit and zoom gestures that start on the mark or its list stay there.
function keepGestures(node) {
  for (const ev of ["pointerdown", "pointermove", "pointerup", "wheel"]) {
    node.addEventListener(ev, (e) => e.stopPropagation());
  }
}

// The mark's one sentence: what it says on hover, to a screen reader and at the head of its list.
function verdict(missing) {
  if (!missing.length) return "Nothing is missing from this machine";
  return missing.length === 1
    ? "Missing from this machine: 1 connection"
    : `Missing from this machine: ${missing.length} connections`;
}

// Remove the mark and its list — used before a re-mount (live reload, another model) and by
// teardown.
export function removeMissing(wrapper) {
  if (!wrapper) return;
  for (const node of wrapper.querySelectorAll(".missing-mark, .missing-list")) node.remove();
}

function closeList(wrapper, mark) {
  const list = wrapper.querySelector(".missing-list");
  if (list) list.remove();
  mark.setAttribute("aria-expanded", "false");
}

function openList(wrapper, mark, missing) {
  const list = el("div", "missing-list" + (missing.length ? " has-missing" : ""));
  list.setAttribute("role", "dialog");
  list.setAttribute("aria-label", "What is missing from this machine");
  keepGestures(list);
  list.appendChild(el("div", "missing-h", verdict(missing)));
  if (!missing.length) {
    list.appendChild(el("div", "missing-note", "Every connection the plumbing lists is complete."));
  }
  for (const run of missing) {
    const row = el("button", "missing-row", `${run.id} — ${run.from} to ${run.to}: ${lacks(run)}`);
    row.type = "button";
    row.title = "Show the two ends on the model";
    row.addEventListener("click", (e) => {
      e.stopPropagation();
      // Resolved on the click, when the scene is certain to be loaded.
      const names = scenePartNames();
      const ends = [run.from, run.to].flatMap((port) => sceneBodies(bodyOf(port), names));
      if (ends.length) highlightParts(ends, { owner: "missing" });
    });
    list.appendChild(row);
  }
  wrapper.appendChild(list);
  mark.setAttribute("aria-expanded", "true");
}

function buildMark(wrapper, missing) {
  const mark = el("button", "missing-mark" + (missing.length ? " has-missing" : ""));
  mark.type = "button";
  mark.title = verdict(missing);
  mark.setAttribute("aria-label", verdict(missing));
  mark.setAttribute("aria-expanded", "false");
  mark.appendChild(icon(missing.length ? CROSS : CHECK));
  keepGestures(mark);
  mark.addEventListener("click", (e) => {
    e.stopPropagation();
    if (wrapper.querySelector(".missing-list")) closeList(wrapper, mark);
    else openList(wrapper, mark, missing);
  });
  wrapper.appendChild(mark);
}

// Ask what `file`'s facts say is missing and mount the mark on `wrapper`. A model with no facts
// gets no mark.
export async function mountMissing(wrapper, file) {
  let missing = null;
  try {
    const r = await fetch("/api/step-missing/" + factsPathFor(file));
    if (r.ok) missing = (await r.json()).missing;
  } catch {
    missing = null;
  }
  // The viewer may have closed, or moved to another model, while this asked.
  if (!wrapper.isConnected) return;
  removeMissing(wrapper);
  if (!Array.isArray(missing)) return;
  buildMark(wrapper, missing);
}
