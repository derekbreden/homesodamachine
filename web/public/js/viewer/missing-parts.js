// The mark above Reset view: what is so of the model on the canvas, in one small round mark.
//
// On the machine, whose published facts list every run the plumbing needs and the wires the
// build left out as not routed: a green check when every run is complete and no wire is left
// out, a red x when not — a tube or a wire that is not routed, a fitting that is not there. A
// click opens the list behind it: each of those with what is so of it and the error the build
// gave, and a click on one lights the two bodies it would join. Under those, the list names the
// machine's printed parts that the fitted record has no row for, each a way to that part; they
// do not turn the mark red. The site works it out from the published facts
// (/api/step-missing, contracts/missing-parts.js) and the fitted record (contracts/fitted.js).
//
// On a printed part of its own: a green check when the fitted record has a row for it, a quiet
// dash when it is not fitted yet. A click shows the day, what Derek said and what he tried.
//
// The mark covers no other control and moves none. A model with neither gets no mark.

import { factsPathFor, bodyOf, sceneBodies, said } from "/contracts/missing-parts.js";
import { fittedState, notFitted } from "/contracts/fitted.js";
import { materialForFile, materialIndex, explodeBom } from "/contracts/materials.js";
import { state } from "./state.js";
import { scenePartNames, highlightParts } from "./part-highlight.js";

const SVG = "http://www.w3.org/2000/svg";
const CHECK = "M3.5 8.5l3 3 6-7";
const CROSS = "M4.5 4.5l7 7M11.5 4.5l-7 7";
const DASH = "M4.5 8h7";

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

// The machine mark's one sentence: what it says on hover, to a screen reader and at the head of
// its list.
function verdict(missing) {
  if (!missing.length) return "Nothing is missing from this machine";
  return missing.length === 1
    ? "Missing from this machine: 1 connection"
    : `Missing from this machine: ${missing.length} connections`;
}

// The part mark's one sentence.
const standing = (fit) => fit.fitted ? `Fitted · ${fit.rows[0].date}` : "Not fitted yet";

// Remove the mark and its list — used before a re-mount (live reload, another model) and by
// teardown.
export function removeMissing(wrapper) {
  if (!wrapper) return;
  for (const node of wrapper.querySelectorAll(".missing-mark, .missing-list")) node.remove();
}

// The printed parts of the model `file`'s own material, and those of them the fitted record has
// no row for.
function waitingForFit(file) {
  const catalog = state.materialCatalog;
  const owner = catalog?.fitted && materialForFile(catalog, file);
  if (!owner) return { printed: 0, waiting: [] };
  const ids = explodeBom(catalog, owner.id, { finish: state.faucetFinish }).map((row) => row.material.id);
  const printed = new Set(catalog.fitted.printed);
  const index = materialIndex(catalog);
  return {
    printed: new Set(ids.filter((id) => printed.has(id))).size,
    waiting: notFitted(catalog.fitted, ids).map((id) => index.get(id)),
  };
}

// What the fitted record says of the model `file`'s own material, where it is a printed part or
// has a row.
function fitOf(file) {
  const catalog = state.materialCatalog;
  const owner = catalog?.fitted && materialForFile(catalog, file);
  return owner ? fittedState(catalog.fitted, owner.id) : null;
}

// The machine's list: what is missing, then the printed parts not fitted yet.
function machineList(missing, file) {
  const list = el("div", "missing-list" + (missing.length ? " has-missing" : ""));
  list.setAttribute("aria-label", "What is missing from this machine");
  list.appendChild(el("div", "missing-h", verdict(missing)));
  if (!missing.length) {
    list.appendChild(el("div", "missing-note", "Every plumbing connection is complete and no wire is left out."));
  }
  for (const run of missing) {
    const row = el("button", "missing-row", said(run));
    if (run.why) row.appendChild(el("span", "missing-why", run.why));
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
  const { printed, waiting } = waitingForFit(file);
  if (waiting.length) {
    list.appendChild(el("div", "missing-h fitted-h", `Not fitted yet: ${waiting.length} of ${printed} printed parts`));
    for (const material of waiting) {
      const row = el("button", "missing-row fitted-row", material.description);
      row.type = "button";
      row.title = "Open this part";
      row.addEventListener("click", async (e) => {
        e.stopPropagation();
        const { openMaterial } = await import("./material-nav.js");
        openMaterial(material.id);
      });
      list.appendChild(row);
    }
  }
  return list;
}

// A printed part's list: the day, his words and what he tried, for each time on record.
function partList(fit) {
  const list = el("div", "missing-list" + (fit.fitted ? "" : " not-yet"));
  list.setAttribute("aria-label", "Whether this part is fitted");
  list.appendChild(el("div", "missing-h" + (fit.fitted ? "" : " fitted-h"), standing(fit)));
  for (const row of fit.rows) {
    list.appendChild(el("blockquote", "missing-said", `“${row.said}”`));
    list.appendChild(el("div", "missing-note", [row.date, row.tried].filter(Boolean).join(" · ")));
  }
  if (!fit.fitted) list.appendChild(el("div", "missing-note", "No try of this print is on record."));
  return list;
}

// One mark on `wrapper`: its look, its sentence and the list a click opens.
function buildMark(wrapper, { look, glyph, sentence, list }) {
  const mark = el("button", "missing-mark" + (look ? " " + look : ""));
  mark.type = "button";
  mark.title = sentence;
  mark.setAttribute("aria-label", sentence);
  mark.setAttribute("aria-expanded", "false");
  mark.appendChild(icon(glyph));
  keepGestures(mark);
  mark.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = wrapper.querySelector(".missing-list");
    if (open) {
      open.remove();
      mark.setAttribute("aria-expanded", "false");
      return;
    }
    const shown = list();
    shown.setAttribute("role", "dialog");
    keepGestures(shown);
    wrapper.appendChild(shown);
    mark.setAttribute("aria-expanded", "true");
  });
  wrapper.appendChild(mark);
}

// Ask what `file`'s facts say is missing and mount the mark on `wrapper`: the machine's where
// the model has facts, else a printed part's fit. A model with neither gets no mark.
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
  if (Array.isArray(missing)) {
    buildMark(wrapper, {
      look: missing.length ? "has-missing" : "",
      glyph: missing.length ? CROSS : CHECK,
      sentence: verdict(missing),
      list: () => machineList(missing, file),
    });
    return;
  }
  const fit = fitOf(file);
  if (!fit) return;
  buildMark(wrapper, {
    look: fit.fitted ? "" : "not-yet",
    glyph: fit.fitted ? CHECK : DASH,
    sentence: standing(fit),
    list: () => partList(fit),
  });
}
