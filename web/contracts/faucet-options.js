// Printable faucet styles, in the same assembly coordinate frame. Paths are
// relative to hardware/, as in /api/steps and component-sources.js.
import { PETGF_BLACK } from "./material-finishes.js";
import { stepLocation } from "./step-locations.js";

const SHARED_TIP = "printed-parts/faucet/faucet-shell/faucet-shell-tip.step";
const SHARED_LEVER = "printed-parts/faucet/lever-replica/lever-replica.step";

export const FAUCET_STYLES = [
  {
    id: "sculpted", label: "Sculpted",
    description: "Smooth curves and softly blended transitions",
    assembly: "faucet-layout/faucet-assembly.step",
    parts: {
      lever: SHARED_LEVER,
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
      lever: SHARED_LEVER,
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

// The continuous black 4 mm flavor tubes keep their stock color in either finish.
const FINISH_BODIES = new Set([
  "shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate",
  "above_counter_gasket", "lever", "soda_faucet_tube",
]);


export function faucetStyleFor(file) {
  return FAUCET_STYLES.find((style) => style.assembly === file) || null;
}

export function faucetSourceFile(name, owner) {
  owner = stepLocation(owner).file;
  return faucetStyleFor(owner)?.parts[name] || null;
}

export function hasFaucetFinish(file) {
  const location = stepLocation(file);
  file = location.file;
  if (location.component && faucetStyleFor(file)) return FINISH_BODIES.has(location.component);
  return !!faucetStyleFor(file) || FAUCET_STYLES.some((style) =>
    Object.entries(style.parts).some(([name, path]) => FINISH_BODIES.has(name) && path === file));
}

export function isFaucetFinishBody(file, name) {
  file = stepLocation(file).file;
  if (faucetStyleFor(file)) return FINISH_BODIES.has(name);
  return hasFaucetFinish(file);
}

export function showsInFaucetFinish(file, name, finishId) {
  return true;
}
