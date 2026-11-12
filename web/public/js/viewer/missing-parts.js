// The missing-parts notice: what the machine on the canvas is meant to have and does not.
//
// The machine's published facts list every run the plumbing needs and whether the machine as
// built completes it. When a run is not complete — a tube that was never routed, a fitting that
// is not there — this says so over the model, where it cannot be missed, naming each absent
// tube and fitting, and each row lights the two bodies the run would join. A machine with
// nothing missing shows nothing. The site works it out from the published facts
// (/api/step-missing, contracts/missing-parts.js).

import { factsPathFor, bodyOf, sceneBodies, lacks } from "/contracts/missing-parts.js";
import { scenePartNames, highlightParts } from "./part-highlight.js";

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

// Remove the notice — used before a re-mount (live reload, another model) and by teardown.
export function removeMissing(wrapper) {
  if (!wrapper) return;
  const notice = wrapper.querySelector(".missing-notice");
  if (notice) notice.remove();
}

function buildNotice(wrapper, missing) {
  const notice = el("div", "missing-notice");
  notice.setAttribute("role", "alert");
  // Orbit and zoom gestures on the notice stay on the notice.
  for (const ev of ["pointerdown", "pointermove", "pointerup", "wheel"]) {
    notice.addEventListener(ev, (e) => e.stopPropagation());
  }
  notice.appendChild(el("div", "missing-h",
    missing.length === 1
      ? "Missing from this machine: 1 connection"
      : `Missing from this machine: ${missing.length} connections`));
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
    notice.appendChild(row);
  }
  wrapper.appendChild(notice);
}

// Ask what `file`'s facts say is missing and mount the notice on `wrapper`. A model with no
// facts, or with nothing missing, gets no notice.
export async function mountMissing(wrapper, file) {
  let missing = [];
  try {
    const r = await fetch("/api/step-missing/" + factsPathFor(file));
    if (r.ok) missing = (await r.json()).missing;
  } catch {
    missing = [];
  }
  // The viewer may have closed, or moved to another model, while this asked.
  if (!wrapper.isConnected) return;
  removeMissing(wrapper);
  if (!Array.isArray(missing) || !missing.length) return;
  buildNotice(wrapper, missing);
}
