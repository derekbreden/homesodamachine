// The CAD viewer's world-axis rulers. The shared factory owns the geometry,
// labels and listeners; this wrapper keeps the existing viewer exports and
// per-browser preference.

import { scene, camera, controls, renderer } from "./scene.js";
import { makeToolChip } from "./tool-rail.js";
import { createAxisRulers } from "./axis-rulers.js";

const rulers = createAxisRulers({ scene, camera, controls, renderer, storageKey: "step-rulers" });

export const updateRulers = rulers.update;
export const setRulersEnabled = rulers.setEnabled;
export const areRulersEnabled = rulers.isEnabled;

export function makeRulerToggle() {
  return makeToolChip({
    className: "ruler-toggle",
    label: "Rulers",
    icon: "rulers",
    title: "Three labelled world axes through the orbit target, ticked in mm",
    read: areRulersEnabled,
    write: setRulersEnabled,
  });
}
