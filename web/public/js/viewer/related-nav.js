// The Related group in the CAD rail — the way out of a part to the models the
// walk cannot reach.
//
// The component picker offers what an assembly HOLDS; this offers what stands
// beside it. A funnel's mold is not carried by any assembly, so opening the
// enclosure and clicking down through it arrives everywhere except the two
// halves that cast the part you are looking at. The rule for what counts is
// contracts/related-steps.js; this file presents those models in one compact
// disclosure with a scrollable list.
//
// Taking one is a drill: the model you came from goes on the trail, so the
// breadcrumb and the browser's Back both walk back through it.
//
// Mounted on open (cad-detail.js) and again on every move (step-nav.js), the
// same as the scorecard — the rail itself is built once and outlives both.

import { state } from "./state.js";
import { relatedSteps, KIND_CAPTIONS, label } from "/contracts/related-steps.js";
import { iconSvg } from "/contracts/icons.js";
import { drillTo } from "./step-nav.js";
import { faucetStyleFor } from "/contracts/faucet-options.js";

const GROUP_CLASS = "tool-group-related";

function removeRelated(wrapper) {
  for (const el of wrapper.querySelectorAll("." + GROUP_CLASS)) el.remove();
}

function chip(rel) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tool-chip related-chip";
  btn.title = `${KIND_CAPTIONS[rel.kind]}: ${rel.file}`;
  const text = document.createElement("span");
  text.className = "tool-label";
  text.textContent = label(rel.file);
  btn.appendChild(text);
  btn.addEventListener("click", () => {
    closeRelated(btn.closest(".cad-wrapper"));
    drillTo(rel.file);
  });
  return btn;
}

// Escape returns focus to the disclosure; a pointer outside it just dismisses
// the list and leaves that pointer free to operate the model or another tool.
export function closeRelated(wrapper, focus = false) {
  const group = wrapper?.querySelector(`.${GROUP_CLASS}[open]`);
  if (!group) return false;
  group.open = false;
  if (focus) group.querySelector("summary").focus();
  return true;
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

  const related = relatedSteps(file, state.allFiles || [], trail)
    .filter((rel) => !(faucetStyleFor(file) && faucetStyleFor(rel.file)));
  if (!related.length) return;

  const group = document.createElement("details");
  group.className = GROUP_CLASS;
  const summary = document.createElement("summary");
  summary.className = "tool-btn";
  summary.textContent = `Related (${related.length})`;
  summary.title = "Related models";
  summary.insertAdjacentHTML("beforeend", iconSvg("chevron", "tool-icon"));
  group.appendChild(summary);
  const list = document.createElement("div");
  list.className = "related-menu";
  for (const rel of related) list.appendChild(chip(rel));
  group.appendChild(list);
  rail.appendChild(group);
}
