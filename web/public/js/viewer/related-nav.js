// The Related group in the CAD rail — the way out of a part to the models the
// walk cannot reach.
//
// The component picker offers what an assembly HOLDS; this offers what stands
// beside it. A funnel's mold is not carried by any assembly, so opening the
// enclosure and clicking down through it arrives everywhere except the two
// halves that cast the part you are looking at. The rule for what counts is
// contracts/related-steps.js; this file is only the chips it draws.
//
// Taking one is a drill: the model you came from goes on the trail, so the
// breadcrumb and the browser's Back both walk back through it.
//
// Mounted on open (cad-detail.js) and again on every move (step-nav.js), the
// same as the scorecard — the rail itself is built once and outlives both.

import { state } from "./state.js";
import { relatedSteps, KIND_CAPTIONS, label } from "/contracts/related-steps.js";
import { makeToolGroup } from "./tool-rail.js";
import { drillTo } from "./step-nav.js";

const GROUP_CLASS = "tool-group-related";

function removeRelated(wrapper) {
  for (const el of wrapper.querySelectorAll("." + GROUP_CLASS)) el.remove();
}

function chip(rel) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tool-chip related-chip";
  btn.title = rel.file;
  const text = document.createElement("span");
  text.className = "tool-label";
  text.textContent = label(rel.file);
  btn.appendChild(text);
  btn.addEventListener("click", () => drillTo(rel.file));
  return btn;
}

/**
 * Draw the models related to `file` into the rail this wrapper holds, replacing
 * whatever the last model left there. A model with nothing beside it leaves the
 * rail carrying no Related group at all.
 *
 * `trail` is the walk above this model; those are already one Back away and are
 * not offered a second time.
 */
export function mountRelated(wrapper, file, trail = []) {
  if (!wrapper) return;
  // On open this runs while the wrapper is still being assembled, before it is
  // in the page.
  const rail = wrapper.querySelector(".tool-rail");
  if (!rail) return;
  removeRelated(wrapper);

  const related = relatedSteps(file, state.allFiles || [], trail);
  if (!related.length) return;

  // One captioned group per kind, in the order the contract sorts them.
  for (const kind of ["beside", "from", "of"]) {
    const run = related.filter((r) => r.kind === kind);
    if (!run.length) continue;
    const row = document.createElement("div");
    row.className = "tool-chips";
    for (const rel of run) row.appendChild(chip(rel));
    const group = makeToolGroup(KIND_CAPTIONS[kind], row);
    group.classList.add(GROUP_CLASS);
    rail.appendChild(group);
  }
}
