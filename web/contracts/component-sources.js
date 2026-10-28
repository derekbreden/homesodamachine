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
// `coil-v-c` is the coil half of the Beduan solenoid).
//
// THE COLD CORE IS NOT REACHED THROUGH A NAME HERE. The enclosure carries the core's
// own bodies — the shell and its caps, the carbonator, the coil, both reservoirs,
// every fitting and the lines among them — so each is picked where it stands and
// offers the file it was modelled in, the same as any other component. `foam-assembly`
// is still the name the port table, the scorecard rows and the plumbing runs speak,
// but it is the envelope the machine measures against and not a body it exports.
//
// Catalog identities resolve their canonical standalone representations first.
// A body built only in its assembly has no separate source file here; the viewer
// opens that named geometry through a component view of the owner.
//
// Paths are root-relative to `hardware/`, the same form `/api/steps` returns.
// web/tests/component-sources.test.js holds every path to a file that exists.

import { leafOf } from "./body-path.js";
import { faucetSourceFile } from "./faucet-options.js";
import { materialForComponent } from "./materials.js";
import { stepLocation } from "./step-locations.js";

export const ALIASES = {
  "bulkhead-carb": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-flavor-a": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-flavor-b": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-water": "reference/jg-bulkhead-union/jg-bulkhead-union.step",
  "bulkhead-drain": "reference/neofit-drain-bulkhead/neofit-drain-bulkhead.step",
  "c14-inlet": "reference/iec-c14-inlet/iec-c14-inlet.step",
  "carbonator-tube": "cut-parts/carbonation/carbonator-tube/carbonator-tube.step",
  "co2-inlet": "reference/neofit-bulkhead/neofit-bulkhead.step",
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
  "collar_drain": "printed-parts/faucet/tube-collar/tube-collar-drain.step",
  "collar_drain_word": "printed-parts/faucet/tube-collar/tube-collar-drain.step",
  "collar_flavor_a": "printed-parts/faucet/tube-collar/tube-collar-flavor-a.step",
  "collar_flavor_a_word": "printed-parts/faucet/tube-collar/tube-collar-flavor-a.step",
  "collar_flavor_b": "printed-parts/faucet/tube-collar/tube-collar-flavor-b.step",
  "collar_flavor_b_word": "printed-parts/faucet/tube-collar/tube-collar-flavor-b.step",
  "collet-water-in": "reference/jg-pp010822e/jg-pp010822e.step",
  "digiten-flow": "reference/digiten-flow-sensor/digiten-flow-sensor.step",
  "discharge-chain": "reference/neofit-achv44-check/neofit-achv44-check.step",
  "display": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "endcap-bottom": "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step",
  "endcap-top": "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step",
  "faucet_display": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "faucet_display_screen": "reference/waveshare-43b-display/waveshare-43b-display.step",
  "flow-regulator": "reference/yzmsz-water-regulator/geometry/yzmsz-water-regulator.step",
  "gas-check": "reference/neofit-achv44-check/neofit-achv44-check.step",
  "gas-regulator": "reference/compact-inline-candidates/geometry/candidate-regulator.step",
  "ground-stack": "reference/ground-ring-stack/ground-ring-stack.step",
  // Two files carry the `funnel` stem — the part, and the mould's casting of it.
  "funnel": "printed-parts/zone-c/funnel/funnel.step",
  "funnel-drain-union": "reference/jg-pp0308e-elbow/jg-pp0308e-elbow.step",
  "above_counter_gasket": "printed-parts/faucet/above-counter-gasket/above-counter-gasket.step",
  "above_counter_plate": "printed-parts/faucet/above-counter-plate/above-counter-plate.step",
  "mq6-sensor": "reference/mq6-gas-sensor/mq6-gas-sensor.step",
  "nameplate": "printed-parts/enclosure/nameplate/nameplate-001.step",
  "nameplate-ink": "printed-parts/enclosure/nameplate/nameplate-001.step",
  "pcba": "printed-parts/electronics/pcba-tray/pcba-board.step",
  "bulkhead-ring-carb": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-carb.step",
  "bulkhead-ring-carb-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-carb.step",
  "bulkhead-ring-drain": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-drain.step",
  "bulkhead-ring-drain-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-drain.step",
  "bulkhead-ring-co2": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-co2.step",
  "bulkhead-ring-co2-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-co2.step",
  "bulkhead-ring-flavor-a": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-a.step",
  "bulkhead-ring-flavor-a-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-a.step",
  "bulkhead-ring-flavor-b": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-b.step",
  "bulkhead-ring-flavor-b-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-flavor-b.step",
  "bulkhead-ring-water": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-water.step",
  "bulkhead-ring-water-word": "printed-parts/enclosure/bulkhead-ring/bulkhead-ring-water.step",
  "psu": "reference/meanwell-irm90/meanwell-irm90.step",
  // Both elbows on the G Ganen's barbs are the one printed part.
  "pump-inlet-tpu": "printed-parts/diaphragm-pump-sleeve/diaphragm-pump-sleeve.step",
  "pump-outlet-tpu": "printed-parts/diaphragm-pump-sleeve/diaphragm-pump-sleeve.step",
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
  "shell_base": "printed-parts/faucet/faucet-shell/faucet-shell-base.step",
  "shell_tip": "printed-parts/faucet/faucet-shell/faucet-shell-tip.step",
  "tee-y-a": "reference/tee-connector/tee-connector.step",
  "tee-y-b": "reference/tee-connector/tee-connector.step",
  "tee-y-c": "reference/tee-connector/tee-connector.step",
  "tee-y-d": "reference/tee-connector/tee-connector.step",
  "tee-y-f": "reference/tee-connector/tee-connector.step",
  "tee-y-g": "reference/tee-connector/tee-connector.step",
  "thermal-fuse": "reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step",
  "tpu_o_ring": "printed-parts/faucet/tpu-o-ring/tpu-o-ring.step",
  "umbilical-organizer": "printed-parts/faucet/umbilical-organizer/umbilical-organizer.step",
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
  "westbrass": "reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step",
  "vk-solenoid": "reference/beduan-solenoid/beduan-solenoid.step",
  "wago-g": "reference/wago-221/wago-221-413.step",
  "wago-gnd": "reference/wago-221/wago-221-413.step",
  "wago-h": "reference/wago-221/wago-221-413.step",
  "wago-mana": "reference/wago-221/wago-221-420.step",
  "wago-manb": "reference/wago-221/wago-221-415.step",
  "wago-n": "reference/wago-221/wago-221-413.step",
  "wago-reeds-b": "reference/wago-221/wago-221-413.step",
  "wago-sensors": "reference/wago-221/wago-221-413.step",
  "wago-v12": "reference/wago-221/wago-221-413.step",
};

function stem(path) {
  return path.slice(path.lastIndexOf("/") + 1).replace(/\.step$/i, "");
}

// name -> path, or null when the assembly is the only place that body exists.
// `stepPaths` is state.allFiles: an alias still has to name a file that is
// really there, so a part deleted out from under the table reads as null
// rather than as a link to a 404.
// A BODY INSIDE A SUB-ASSEMBLY IS STILL THE BODY IT IS. The appliance stands the cold core's
// bodies under `cold-core/<name>`, which says what holds them and changes nothing about what
// each one was modelled in — so the name is asked for whole first, and then by its leaf.
export function sourceFileFor(name, stepPaths, owner = null, catalog = null, options = {}) {
  if (!name || !Array.isArray(stepPaths)) return null;
  owner = stepLocation(owner).file;
  const material = materialForComponent(catalog, owner, name, options);
  const representation = material?.models?.find(model => !model.context && (!model.type || model.type === "step") && stepPaths.includes(model.file));
  if (representation) return representation.file;
  for (const key of [name, leafOf(name)]) {
    const scoped = faucetSourceFile(key, owner);
    if (scoped) return stepPaths.includes(scoped) ? scoped : null;
    const alias = ALIASES[key];
    if (alias) return stepPaths.includes(alias) ? alias : null;
    const hit = stepPaths.find((p) => stem(p) === key);
    if (hit) return hit;
  }
  return null;
}
