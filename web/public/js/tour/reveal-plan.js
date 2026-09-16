export const REVEAL_STATES = Object.freeze({
  closed: Object.freeze({ enclosure: 0, coldCore: 0, carbonator: 0 }),
  screws: Object.freeze({ enclosure: 0.36, coldCore: 0, carbonator: 0 }),
  open: Object.freeze({ enclosure: 1, coldCore: 0, carbonator: 0 }),
  core: Object.freeze({ enclosure: 1, coldCore: 1, carbonator: 0 }),
  carbonator: Object.freeze({ enclosure: 1, coldCore: 1, carbonator: 1 }),
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
const CARBONATOR_WALL = new Set([
  "carbonator-tube", "evap-coil", "evap-tail-inlet", "evap-tail-outlet",
  "reed-bridge", "reed-carb-1", "reed-carb-2",
  "probe-carbonator-ds18b20", "probe-coil-ds18s20",
]);

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

  const c = clamp(state.coldCore || 0);
  if (name === "foam-cap-lid-top") return [0, 0, 225 * phase(c, 0, 0.66)];
  if (name === "foam-cap-top") return [0, 0, 160 * phase(c, 0.10, 0.76)];
  if (name === "foam-cap-lid-bottom") return [0, 0, -410 * phase(c, 0, 0.72)];
  if (name === "foam-cap-bottom") return [0, 0, -360 * phase(c, 0.10, 0.82)];
  if (name === "foam-shell") return [0, 0, -300 * phase(c, 0.25, 1)];

  if (CARBONATOR_WALL.has(name)) {
    const v = ease(state.carbonator || 0);
    return [0, 230 * v, 35 * v];
  }
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
