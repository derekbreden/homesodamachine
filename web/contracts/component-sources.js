// Which file a component in an assembly was modelled in — the map the 3D
// viewer's drill-down walks (web/public/js/viewer/step-nav.js).
//
// A component is one named solid of an assembly STEP: `enclosure-front-bottom`
// inside `manifold-layout/enclosure-assembly.step`. Most carry the stem of the
// file they were modelled in, so the name resolves against the `/api/steps`
// list on its own. ALIASES carries the rest.
//
// What a component maps to is THE FILE ITS GEOMETRY IS MODELLED IN, which is
// not always a file holding that component alone. Several seats of one part
// share one file (four bulkheads off one union, ten lever nuts off three
// WAGOs), and a component that is one solid of a larger purchased part maps to
// that part (`pump-a-motor` is one of three solids in the Kamoer's STEP;
// `coil-v-a` is the coil half of the Beduan solenoid).
//
// A name in neither is a body the assembly builds itself and keeps: the routed
// `tube-*`, `turn-*` and `step-*` runs, the cold core's vessel primitives and
// its `line-*` runs, the condenser block. Those resolve to null, which is what
// leaves the drill-down offer off a solid there is nowhere to go from.
//
// Paths are root-relative to `hardware/`, the same form `/api/steps` returns.
// web/tests/component-sources.test.js holds every path to a file that exists.

export const ALIASES = {
  "bulkhead-carb": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-flavor-a": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-flavor-b": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-water": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "c14-inlet": "reference/iec-c14-inlet/iec-c14-inlet.step",
  "co2-inlet": "reference/neofit-bulkhead/neofit-bulkhead.step",
  "coil-v-a": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-b": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-c": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-d": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-e": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-f": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-g": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-h": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-i": "reference/beduan-solenoid/beduan-solenoid.step",
  "coil-v-j": "reference/beduan-solenoid/beduan-solenoid.step",
  "collet-carb-water-out": "reference/jg-pp010822e/jg-pp010822e.step",
  "collet-co2-in": "reference/jg-pp010822e/jg-pp010822e.step",
  "collet-water-in": "reference/jg-pp010822e/jg-pp010822e.step",
  "digiten-flow": "reference/digiten-flow-sensor/digiten-flow-sensor.step",
  "discharge-chain": "reference/seaflo-discharge-chain/seaflo-discharge-chain.step",
  "display": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "flow-regulator": "reference/neofit-flow-control/neofit-flow-control.step",
  "gasher-co2": "reference/gasher-check-valve/gasher-check-valve.step",
  "ground-stack": "reference/ground-ring-stack/ground-ring-stack.step",
  "hopper-drain-clamp": "reference/worm-clamp/worm-clamp.step",
  "hopper-drain-union": "reference/jg-pp0408w/jg-pp0408w.step",
  "moisture-plate": "reference/shutao-moisture-plate/shutao-moisture-plate.step",
  "mq6-sensor": "reference/mq6-gas-sensor/mq6-gas-sensor.step",
  "pcba": "printed-parts/electronics/pcba-tray/pcba-board.step",
  "port-ring-carb": "printed-parts/enclosure/port-ring/port-ring-carb.step",
  "port-ring-carb-word": "printed-parts/enclosure/port-ring/port-ring-carb.step",
  "port-ring-co2": "printed-parts/enclosure/port-ring/port-ring-co2.step",
  "port-ring-co2-word": "printed-parts/enclosure/port-ring/port-ring-co2.step",
  "port-ring-flavor-a": "printed-parts/enclosure/port-ring/port-ring-flavor-a.step",
  "port-ring-flavor-a-word": "printed-parts/enclosure/port-ring/port-ring-flavor-a.step",
  "port-ring-flavor-b": "printed-parts/enclosure/port-ring/port-ring-flavor-b.step",
  "port-ring-flavor-b-word": "printed-parts/enclosure/port-ring/port-ring-flavor-b.step",
  "port-ring-water": "printed-parts/enclosure/port-ring/port-ring-water.step",
  "port-ring-water-word": "printed-parts/enclosure/port-ring/port-ring-water.step",
  "psu": "reference/meanwell-irm90/meanwell-irm90.step",
  "pump-a-boss": "reference/kamoer-kphm400/kamoer-kphm400.step",
  "pump-a-head": "reference/kamoer-kphm400/kamoer-kphm400.step",
  "pump-a-motor": "reference/kamoer-kphm400/kamoer-kphm400.step",
  "pump-b-boss": "reference/kamoer-kphm400/kamoer-kphm400.step",
  "pump-b-head": "reference/kamoer-kphm400/kamoer-kphm400.step",
  "pump-b-motor": "reference/kamoer-kphm400/kamoer-kphm400.step",
  "relay-1": "reference/teyleten-relay/teyleten-relay.step",
  "relay-2": "reference/teyleten-relay/teyleten-relay.step",
  "reservoir-a": "printed-parts/cold-core/reservoir/reservoir-right.step",
  "reservoir-a-cap": "printed-parts/cold-core/reservoir/reservoir-cap-right.step",
  "reservoir-b": "printed-parts/cold-core/reservoir/reservoir-left.step",
  "reservoir-b-cap": "printed-parts/cold-core/reservoir/reservoir-cap-left.step",
  "seaflo-pump": "reference/seaflo-22-pump/seaflo-22-pump.step",
  "suction-chain": "reference/seaflo-suction-chain/seaflo-suction-chain.step",
  "tee-y-a": "reference/tee-connector/tee-connector.step",
  "tee-y-b": "reference/tee-connector/tee-connector.step",
  "tee-y-c": "reference/tee-connector/tee-connector.step",
  "tee-y-d": "reference/tee-connector/tee-connector.step",
  "tee-y-f": "reference/tee-connector/tee-connector.step",
  "tee-y-g": "reference/tee-connector/tee-connector.step",
  "thermal-fuse": "reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step",
  "valve-v-a": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-b": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-c": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-d": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-e": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-f": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-g": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-h": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-i": "reference/beduan-solenoid/beduan-solenoid.step",
  "valve-v-j": "reference/beduan-solenoid/beduan-solenoid.step",
  "vk-solenoid": "reference/beduan-solenoid/beduan-solenoid.step",
  "wago-g": "reference/wago-221/wago-221-413.step",
  "wago-gnd": "reference/wago-221/wago-221-413.step",
  "wago-h": "reference/wago-221/wago-221-413.step",
  "wago-mana": "reference/wago-221/wago-221-420.step",
  "wago-manb": "reference/wago-221/wago-221-415.step",
  "wago-n": "reference/wago-221/wago-221-413.step",
  "wago-reeds-a": "reference/wago-221/wago-221-415.step",
  "wago-reeds-b": "reference/wago-221/wago-221-420.step",
  "wago-sensors": "reference/wago-221/wago-221-415.step",
  "wago-v12": "reference/wago-221/wago-221-413.step",
  "wr1110": "reference/wr1110-regulator/wr1110-regulator.step",
};

function stem(path) {
  return path.slice(path.lastIndexOf("/") + 1).replace(/\.step$/i, "");
}

// name -> path, or null when the assembly is the only place that body exists.
// `stepPaths` is state.allFiles: an alias still has to name a file that is
// really there, so a part deleted out from under the table reads as null
// rather than as a link to a 404.
export function sourceFileFor(name, stepPaths) {
  if (!name || !Array.isArray(stepPaths)) return null;
  const alias = ALIASES[name];
  if (alias) return stepPaths.includes(alias) ? alias : null;
  return stepPaths.find((p) => stem(p) === name) || null;
}
