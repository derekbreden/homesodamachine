export const REVEAL_DEFAULTS = Object.freeze({
  enclosure: 0, park: 0, coreIsolation: 0, coreCaps: 0, coreShell: 0, coreSpread: 0,
  coldCore: 0, carbonator: 0,
});
const stage = (values) => Object.freeze({ ...REVEAL_DEFAULTS, ...values });
export const REVEAL_STATES = Object.freeze({
  closed: stage({}),
  screws: stage({ enclosure: 0.36 }),
  open: stage({ enclosure: 1 }),
  isolated: stage({ enclosure: 1, coreIsolation: 1 }),
  caps: stage({ enclosure: 1, coreIsolation: 1, coreCaps: 1 }),
  core: stage({ enclosure: 1, coreIsolation: 1, coreCaps: 1, coreShell: 1 }),
  spread: stage({ enclosure: 1, coreIsolation: 1, coreCaps: 1, coreShell: 1, coreSpread: 1 }),
  carbonator: stage({ enclosure: 1, coreIsolation: 1, coreCaps: 1, coreShell: 1, coreSpread: 1 }),
});

// enclosure-assembly.facts.json box.y_bosses; enclosure.py _y_boss and _boss_x.
export const ENCLOSURE_FASTENERS = Object.freeze({
  exteriorX: 107.5,
  axisY: 204.65,
  levels: Object.freeze([48.9, 152.1, 334.05]),
  headSeatDepth: 4,
  headDiameter: 5.5,
  headHeight: 3,
  shankDiameter: 3,
  shankLength: 10,
});

export const clamp = (n) => Math.min(1, Math.max(0, Number.isFinite(n) ? n : 0));
export const ease = (n) => { const t = clamp(n); return t * t * (3 - 2 * t); };
const phase = (n, start, end) => ease((n - start) / (end - start));

const FRONT_TOP = new Set(["enclosure-front-top", "display", "display-cover", "display-gasket", "pump-jack"]);
const BACK_TOP = new Set(["enclosure-back-top", "nameplate", "nameplate-ink"]);
const FUNNEL = new Set(["funnel", "funnel-drain-clamp", "funnel-drain-stub", "funnel-drain-union"]);
const COIL = new Set(["evap-coil", "evap-tail-inlet", "evap-tail-outlet", "probe-coil-ds18s20"]);
const CARBONATOR = new Set([
  "carbonator-tube", "endcap-top", "endcap-bottom", "float-rod-carb", "float-carb",
  "reed-bridge", "reed-carb-1", "reed-carb-2", "probe-carbonator-ds18b20",
  "sparge-barb", "sparge-silicone-stub", "sparge-stone",
  "collet-co2-in", "collet-carb-water-out", "collet-water-in", "prv-sv125", "prv-shroud",
  "line-water-in", "line-carb-water-out", "line-co2-in", "line-prv-vent",
]);

/** Every fitting, probe, float and fluid line travels with the body it serves. */
export function corePartGroup(name) {
  name = name.replace(/^cold-core\//, "");
  if (name.startsWith("foam-cap-")) return "caps";
  if (name === "foam-shell" || name.startsWith("copper-plug-")) return "shell";
  if (COIL.has(name)) return "coil";
  if (CARBONATOR.has(name) || name.startsWith("carbonator-elbow-") || name.startsWith("sparge-stone-")) return "carbonator";
  for (const side of ["a", "b"]) {
    if (name === `reservoir-${side}` || name.startsWith(`reservoir-${side}-`)
        || name === `bulkhead-reservoir-${side}` || name === `bulkhead-seal-${side}`
        || name === `vent-membrane-${side}` || name === `float-rod-${side}`
        || name === `float-${side}` || name.startsWith(`reed-${side}-`)
        || name === `line-reservoir-${side}` || name.startsWith(`line-reservoir-${side}-`)) {
      return `reservoir-${side}`;
    }
  }
  return null;
}

export function revealOpacity(name, state = {}) {
  const group = corePartGroup(name);
  if (group === "caps" || group === "shell") return 1 - 0.88 * ease(state.coreSpread || state.carbonator || 0);
  return name.startsWith("cold-core/") || group ? 1 : 1 - ease(state.coreIsolation || 0);
}

/** Model-local millimetres. The open state is an exploded illustration. */
export function revealMotion(name, state = {}) {
  name = name.replace(/^cold-core\//, "");
  const q = phase(state.enclosure || 0, 0.38, 1);
  const park = ease(state.park || 0) * q;
  const clear = phase(state.enclosure || 0, 0.38, 0.64);
  const spread = phase(state.enclosure || 0, 0.62, 1);
  if (FUNNEL.has(name)) return [0, -45 * q, 190 * phase(state.enclosure || 0, 0.36, 0.68) + 500 * park];
  if (FRONT_TOP.has(name)) return [0, -205 * q - 30 * clear - 1200 * park, 135 * spread];
  if (name === "enclosure-front-bottom") return [0, -215 * q - 30 * clear - 1200 * park, -95 * spread];
  if (BACK_TOP.has(name) || name.startsWith("bulkhead-ring-")) {
    return [0, 270 * q + 30 * clear + 1200 * park, 125 * spread];
  }
  if (name === "enclosure-back-bottom") return [0, 270 * q + 30 * clear + 1200 * park, -100 * spread];

  const caps = clamp(state.coreCaps || phase(state.coldCore || 0, 0, 0.45));
  const shell = clamp(state.coreShell || phase(state.coldCore || 0, 0.45, 1));
  const inner = ease(state.coreSpread || state.carbonator || 0);
  const coreGroup = corePartGroup(name);
  if (coreGroup === "caps") {
    const bottom = name.endsWith("bottom");
    const lid = name.includes("-lid-");
    const lift = (bottom ? -150 : 120) * phase(caps, 0, 0.68);
    const lidGap = (bottom ? -22 : 22) * phase(caps, 0, 0.36);
    return [195 * phase(caps, 0.38, 1), 0, lift + (lid ? lidGap : 0)];
  }
  if (coreGroup === "shell") {
    // The print lowers off the contents, slides aside, then rises beside them.
    return [0, 330 * phase(shell, 0.4, 0.82),
      -230 * phase(shell, 0, 0.4) + 170 * phase(shell, 0.82, 1)];
  }
  if (coreGroup === "coil") return [0, 0, 140 * inner];
  if (coreGroup === "carbonator") return [0, 0, -80 * inner];
  if (coreGroup === "reservoir-a") return [0, 65 * inner, 0];
  if (coreGroup === "reservoir-b") return [0, -65 * inner, 0];
  return [0, 0, 0];
}

/** Turns and outward travel of one M3 seam screw, before the quadrants move. */
export function fastenerMotion(progress, index = 0) {
  const p = clamp(progress);
  const delay = (index % 3) * 0.012;
  const turn = phase(p, delay, 0.23 + delay);
  const float = phase(p, 0.22 + delay, 0.36);
  const park = phase(p, 0.38, 1);
  return { turns: 6 * turn, distance: 12 * turn + 50 * float + 80 * park };
}
