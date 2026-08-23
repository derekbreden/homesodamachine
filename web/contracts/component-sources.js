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
// A COMPONENT MAY BE A WHOLE ASSEMBLY, and then the file is that assembly and the
// drill-down goes on from there. `foam-assembly` is the machine's one handle on
// the cold core — the name its port table, its scorecard rows and its plumbing
// runs all speak — and `cold-core-layout/cold-core-assembly.step` is that same
// body one frame in, foam and all, with the vessel, the coil, both reservoirs,
// every fitting and the lines among them standing in it. Opening it is how they
// are reached; contracts/parts-tree.js seats the two the same way.
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
  "collar_carb": "printed-parts/faucet/tube-collar/tube-collar-carb.step",
  "collar_carb_word": "printed-parts/faucet/tube-collar/tube-collar-carb.step",
  "collar_flavor_a": "printed-parts/faucet/tube-collar/tube-collar-flavor-a.step",
  "collar_flavor_a_word": "printed-parts/faucet/tube-collar/tube-collar-flavor-a.step",
  "collar_flavor_b": "printed-parts/faucet/tube-collar/tube-collar-flavor-b.step",
  "collar_flavor_b_word": "printed-parts/faucet/tube-collar/tube-collar-flavor-b.step",
  "collet-carb-water-out": "reference/jg-pp010822e/jg-pp010822e.step",
  "collet-co2-in": "reference/jg-pp010822e/jg-pp010822e.step",
  "collet-water-in": "reference/jg-pp010822e/jg-pp010822e.step",
  "digiten-flow": "reference/digiten-flow-sensor/digiten-flow-sensor.step",
  "discharge-chain": "reference/seaflo-discharge-chain/seaflo-discharge-chain.step",
  "display": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "enclosure-ceiling-panel": "printed-parts/enclosure/ceiling-panel/ceiling-panel.step",
  "endcap-bottom": "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step",
  "endcap-top": "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step",
  "faucet_display": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "faucet_display_screen": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "flow-regulator": "reference/neofit-flow-control/neofit-flow-control.step",
  "foam-assembly": "cold-core-layout/cold-core-assembly.step",
  "gasher-co2": "reference/gasher-check-valve/gasher-check-valve.step",
  "ground-stack": "reference/ground-ring-stack/ground-ring-stack.step",
  "hopper-drain-clamp": "reference/worm-clamp/worm-clamp.step",
  "hopper-drain-union": "reference/jg-pp0408w/jg-pp0408w.step",
  "moisture-plate": "reference/shutao-moisture-plate/shutao-moisture-plate.step",
  "mounting_gasket": "printed-parts/faucet/above-counter-gasket/above-counter-gasket.step",
  "mounting_plate": "printed-parts/faucet/above-counter-plate/above-counter-plate.step",
  "mq6-sensor": "reference/mq6-gas-sensor/mq6-gas-sensor.step",
  "nameplate": "printed-parts/enclosure/nameplate/nameplate-001.step",
  "nameplate-ink": "printed-parts/enclosure/nameplate/nameplate-001.step",
  "pcba": "printed-parts/electronics/pcba-tray/pcba-board.step",
  "port-ring-carb": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-carb.step",
  "port-ring-carb-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-carb.step",
  "port-ring-co2": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-co2.step",
  "port-ring-co2-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-co2.step",
  "port-ring-flavor-a": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-a.step",
  "port-ring-flavor-a-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-a.step",
  "port-ring-flavor-b": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-b.step",
  "port-ring-flavor-b-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-b.step",
  "port-ring-water": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-water.step",
  "port-ring-water-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-water.step",
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
  "shell_bottom": "printed-parts/faucet/faucet-shell/faucet-shell-bottom.step",
  "shell_middle": "printed-parts/faucet/faucet-shell/faucet-shell-middle.step",
  "shell_top": "printed-parts/faucet/faucet-shell/faucet-shell-top.step",
  "suction-chain": "reference/seaflo-suction-chain/seaflo-suction-chain.step",
  "tee-y-a": "reference/tee-connector/tee-connector.step",
  "tee-y-b": "reference/tee-connector/tee-connector.step",
  "tee-y-c": "reference/tee-connector/tee-connector.step",
  "tee-y-d": "reference/tee-connector/tee-connector.step",
  "tee-y-f": "reference/tee-connector/tee-connector.step",
  "tee-y-g": "reference/tee-connector/tee-connector.step",
  "thermal-fuse": "reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step",
  "tpu_o_ring": "printed-parts/faucet/tpu-o-ring/tpu-o-ring.step",
  "tube-collar-co2-word": "printed-parts/faucet/tube-collar/tube-collar-co2.step",
  "tube-collar-water-word": "printed-parts/faucet/tube-collar/tube-collar-water.step",
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
  "valve_body": "reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step",
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
