// Printable faucet styles, in the same assembly coordinate frame. Paths are
// relative to hardware/, as in /api/steps and component-sources.js.
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
  { id: "black", label: "Black", rgb: [0.0331047666, 0.0331047666, 0.0363064840], roughness: 0.85, metalness: 0 },
  { id: "white", label: "White", rgb: [0.8713671192, 0.8713671192, 0.8559926082], roughness: 0.85, metalness: 0 },
];

const FINISH_BODIES = new Set([
  "shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate",
  "above_counter_gasket", "lever", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x",
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
