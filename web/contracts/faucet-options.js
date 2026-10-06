// Printable faucet styles, in the same assembly coordinate frame. Paths are
// relative to hardware/, as in /api/steps and component-sources.js.
import { PETGF_BLACK } from "./material-finishes.js";

const SHARED_TIP = "printed-parts/faucet/faucet-shell/faucet-shell-tip.step";

export const FAUCET_STYLES = [
  {
    id: "sculpted", label: "Sculpted",
    description: "Smooth curves and softly blended transitions",
    assembly: "faucet-layout/faucet-assembly.step",
    parts: {
      shell_base: "printed-parts/faucet/faucet-shell/faucet-shell-base.step",
      shell_tip: SHARED_TIP,
      "faucet-display-cover-seated": "printed-parts/faucet/faucet-display-cover/faucet-display-cover.step",
      above_counter_plate: "printed-parts/faucet/above-counter-plate/above-counter-plate.step",
      above_counter_gasket: "printed-parts/faucet/above-counter-gasket/above-counter-gasket.step",
    },
  },
  {
    id: "industrial", label: "Industrial",
    description: "Simple cylinders and crisp pronounced shoulders",
    assembly: "faucet-layout/faucet-industrial-assembly.step",
    parts: {
      shell_base: "printed-parts/faucet/industrial/industrial-shell-base.step",
      shell_tip: SHARED_TIP,
      "faucet-display-cover-seated": "printed-parts/faucet/industrial/industrial-display-cover.step",
      above_counter_plate: "printed-parts/faucet/industrial/industrial-above-counter-plate.step",
      above_counter_gasket: "printed-parts/faucet/industrial/industrial-above-counter-gasket.step",
    },
  },
];

// Linear RGB; both finishes have a matte, nonmetallic surface.
export const FAUCET_FINISHES = [
  { id: "black", label: "Black", ...PETGF_BLACK },
  { id: "white", label: "White", rgb: [0.8713671192, 0.8713671192, 0.8559926082], roughness: 0.85, metalness: 0 },
];

// The flavor pair's runs through the faucet take the finish; their black runs in the umbilical
// do not.
const FINISH_BODIES = new Set([
  "shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate",
  "above_counter_gasket", "lever", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x",
]);

// A White faucet joins each white flavor tube to its black run with a John Guest union inside the
// braid; a Black faucet's flavor tube is one black length, and the assembly carries the piece of it
// that runs where a union would stand as a bridge. Each finish shows its own and not the other's.
const FINISH_ONLY = new Map([
  ["flavor_union_pos_x", "white"], ["flavor_union_neg_x", "white"],
  ["flavor_tube_bridge_pos_x", "black"], ["flavor_tube_bridge_neg_x", "black"],
]);

export function faucetStyleFor(file) {
  return FAUCET_STYLES.find((style) => style.assembly === file) || null;
}

export function faucetSourceFile(name, owner) {
  return faucetStyleFor(owner)?.parts[name] || null;
}

export function hasFaucetFinish(file) {
  return !!faucetStyleFor(file) || FAUCET_STYLES.some((style) =>
    Object.entries(style.parts).some(([name, path]) => FINISH_BODIES.has(name) && path === file));
}

export function isFaucetFinishBody(file, name) {
  if (faucetStyleFor(file)) return FINISH_BODIES.has(name);
  return hasFaucetFinish(file);
}

export function showsInFaucetFinish(file, name, finishId) {
  const only = faucetStyleFor(file) ? FINISH_ONLY.get(name) : null;
  return !only || only === finishId;
}
