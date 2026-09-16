// Timed captions, camera poses and reveal states for the machine tour.
// `dwell` includes the opening motion. `motions` times individual reveal channels.
// `focus` frames the subject; `context` keeps its neighboring bodies in the shot.

const CLOSED = {
  enclosure: 0, park: 0, coldCore: 0, carbonator: 0,
  coreIsolation: 0, coreCaps: 0, coreShell: 0, coreSpread: 0,
};
const SCREWS = { ...CLOSED, enclosure: 0.36 };
const OPEN = { ...CLOSED, enclosure: 1 };
const WORKING = { ...OPEN, park: 1 };
const ISOLATED = { ...WORKING, coreIsolation: 1 };
const UNCAPPED = { ...ISOLATED, coreCaps: 1 };
const UNSHELLED = { ...UNCAPPED, coreShell: 1 };
const SPREAD = { ...UNSHELLED, coreSpread: 1 };

const COIL = ["cold-core/evap-coil", "cold-core/evap-tail-inlet", "cold-core/evap-tail-outlet"];
const CARBONATOR = ["cold-core/carbonator-tube", "cold-core/endcap-top", "cold-core/endcap-bottom"];
const RESERVOIRS = ["cold-core/reservoir-a", "cold-core/reservoir-b"];
const CORE_FRAME = [...CARBONATOR, "cold-core/evap-coil", ...RESERVOIRS];
const CORE_COVERS = [
  "cold-core/foam-shell", "cold-core/foam-cap-top", "cold-core/foam-cap-bottom",
  "cold-core/foam-cap-lid-top", "cold-core/foam-cap-lid-bottom",
];
const CORE_WIDE = [...CORE_FRAME, ...CORE_COVERS];
const CORE_SUBJECTS = [
  { id: "coil", text: "Copper coil", parts: ["cold-core/evap-coil"] },
  { id: "carbonator", text: "Carbonator", parts: ["cold-core/carbonator-tube"] },
  { id: "flavor-a", text: "Flavor A", parts: ["cold-core/reservoir-a"] },
  { id: "flavor-b", text: "Flavor B", parts: ["cold-core/reservoir-b"] },
];
const PUMPS = ["pump-a-head", "pump-a-motor", "pump-b-head", "pump-b-motor"];

export const TOUR = {
  id: "machine",
  title: "Inside the soda machine",
  subtitle: "Water, cold, carbonation and flavor — a guided look inside",
  model: "manifold-layout/enclosure-assembly.step",
  paths: [],

  steps: [
    {
      id: "soda-on-tap", chapter: "Open the machine", title: "Soda, on tap",
      body: "The soda machine chills water, adds carbonation, and keeps two flavors ready at the faucet.",
      label: "Soda machine",
      parts: [], focus: ["*"], reveal: CLOSED,
      dir: [0.9, -1, 0.48], pad: 1.2, dwell: 6000,
      drift: { az: 3, el: 0.5, dolly: -0.025 },
    },
    {
      id: "release-screws", chapter: "Open the machine", title: "First, release the enclosure",
      body: "First, the side screws turn out, releasing the four enclosure quadrants.",
      label: "Enclosure screws",
      parts: [], focus: ["*"], reveal: SCREWS,
      dir: [0.9, -1, 0.48], pad: 1.28, dwell: 4500, motion: 3400,
      drift: { az: 1, el: 0, dolly: 0 },
    },
    {
      id: "open-enclosure", chapter: "Open the machine", title: "A machine built around its cold center",
      body: "Refrigeration at the front. Pumps and valves above. An insulated cold core filling the back.",
      label: "Four enclosure quadrants",
      parts: [], focus: ["*"], reveal: OPEN,
      dir: [0.9, -1, 0.48], pad: 1.8, dwell: 6000, motion: 4500,
      drift: { az: 2, el: 0.5, dolly: -0.015 },
    },
    {
      id: "water-inlet", chapter: "Bring in the water", title: "Water starts at the house supply",
      body: "Tap water enters at the rear. A beverage backflow preventer protects the house supply from reverse flow.",
      label: "Water inlet and backflow preventer",
      parts: ["bulkhead-water", "asse1022-assembly", "tube-water-2"],
      focus: ["asse1022-assembly", "water-split", "bulkhead-water"],
      reveal: WORKING, hue: "water", motions: { park: [0, 1500] },
      dir: [-1, 0.85, 0.65], pad: 1.85, dwell: 7000, enter: 2500,
      drift: { az: 3, el: 0.5, dolly: -0.02 },
    },
    {
      id: "water-pump", chapter: "Bring in the water", title: "Refill under pressure",
      body: "The diaphragm pump pushes water into the carbonator against the CO₂ pressure inside. A fill valve opens when more water is needed.",
      label: "Diaphragm pump and fill valve",
      parts: ["seaflo-pump", "vk-solenoid", "tube-water-5"],
      focus: ["seaflo-pump", "vk-solenoid", "discharge-chain"],
      reveal: WORKING, hue: "water",
      dir: [-0.9, -0.65, 0.6], pad: 1.55, dwell: 7000, enter: 2400,
      drift: { az: 3, el: 0.5, dolly: -0.03 },
    },
    {
      id: "refrigeration", chapter: "Keep it cold", title: "Move the heat out",
      body: "The compressor circulates refrigerant through the cold core. The condenser and fan carry that heat out through the enclosure's side grilles.",
      label: "Compressor, condenser and fan",
      parts: ["compressor", "condenser+fan", "tube-refrig-1"],
      reveal: WORKING, hue: "refrigerant",
      dir: [-0.9, -1, 0.4], pad: 1.55, dwell: 7000, enter: 2200,
      drift: { az: 4, el: 0.5, dolly: -0.02 },
    },
    {
      id: "cold-core", chapter: "Inside the cold core", title: "Stay with the cold core",
      body: "Inside this insulated block: the carbonator, its copper coil, and both flavor reservoirs. Everything else recedes.",
      label: "Insulated cold core",
      parts: ["cold-core/foam-shell"], focus: CORE_WIDE, context: CORE_WIDE,
      reveal: ISOLATED, hue: "refrigerant",
      dir: [-1, -0.45, 0.38], pad: 1.35, dwell: 6000, motion: 2800, enter: 3000,
      drift: { az: 2, el: 0.5, dolly: -0.025 },
    },
    {
      id: "core-caps", chapter: "Inside the cold core", title: "Insulated at both ends",
      body: "Foam-filled caps close both ends. Beneath them is a layered construction.",
      label: "Top and bottom foam caps",
      parts: ["cold-core/foam-cap-top", "cold-core/foam-cap-bottom"],
      focus: CORE_WIDE, context: CORE_WIDE, reveal: UNCAPPED, hue: "refrigerant",
      dir: [-1, -0.45, 0.38], pad: 1.25, dwell: 4500, motion: 3400, enter: 2400,
      drift: { az: 1, el: 0, dolly: 0 },
    },
    {
      id: "core-shell", chapter: "Inside the cold core", title: "Under the printed shell",
      body: "The printed foam shell holds the insulation. Beneath it, two reservoirs nest beside the coil-wrapped carbonator.",
      label: "Printed foam shell",
      parts: ["cold-core/foam-shell"], focus: CORE_WIDE, context: CORE_WIDE,
      reveal: UNSHELLED, hue: "refrigerant",
      dir: [-1, -0.4, 0.36], pad: 1.25, dwell: 5500, motion: 4300, enter: 2800,
      drift: { az: 1, el: 0.5, dolly: -0.02 },
    },
    {
      id: "core-spread", chapter: "Inside the cold core", title: "Four parts, one cold center",
      body: "Copper above, carbonator below, a flavor reservoir on either side. A little separation reveals how they fit.",
      label: "Copper · carbonator · two flavors",
      parts: CORE_FRAME, focus: CORE_FRAME, subjects: CORE_SUBJECTS,
      context: CORE_COVERS, contextWeight: 0.25,
      reveal: SPREAD, hue: "refrigerant", emphasis: 0.22,
      dir: [-1, -0.38, 0.32], pad: 1.25, dwell: 6000, motion: 4000, enter: 3000,
      drift: { az: 2, el: 0.5, dolly: -0.02 },
    },
    {
      id: "copper-coil", chapter: "Inside the cold core", title: "Copper takes heat from the water",
      body: "Refrigerant evaporates inside this copper coil. Bonded around the carbonator's steel wall, it pulls heat directly from the water inside.",
      label: "Copper evaporator coil",
      parts: COIL, focus: ["cold-core/evap-coil"], subjects: CORE_SUBJECTS,
      context: CORE_FRAME, contextWeight: 0.55,
      reveal: SPREAD, hue: "refrigerant", emphasis: 0.45,
      dir: [-1, -0.2, 0.45], pad: 1.35, dwell: 8000, enter: 3000,
      drift: { az: 3, el: 0.5, dolly: -0.025 },
    },
    {
      id: "carbonator", chapter: "Inside the cold core", title: "Cold water becomes carbonated water",
      body: "The stainless steel carbonator holds water under CO₂ pressure. Gas enters at the bottom; an internal sparge stone spreads it into small bubbles.",
      label: "Stainless steel carbonator",
      parts: [...CARBONATOR, "cold-core/carbonator-elbow-co2-in"],
      focus: CARBONATOR, context: CORE_FRAME, contextWeight: 0.55, subjects: CORE_SUBJECTS,
      reveal: SPREAD, hue: "co2",
      dir: [-1, 0.15, 0.22], pad: 1.35, dwell: 8000, enter: 3000,
      drift: { az: 3, el: 0.5, dolly: -0.02 },
    },
    {
      id: "flavor-reservoirs", chapter: "Inside the cold core", title: "Two flavors share the cold",
      body: "Each reservoir holds its own concentrate. Nestled beside the carbonator, both flavors pre-chill before separate pumps send them to the faucet.",
      label: "Two flavor reservoirs",
      parts: RESERVOIRS, focus: RESERVOIRS, subjects: CORE_SUBJECTS,
      context: CORE_FRAME, contextWeight: 0.6,
      reveal: SPREAD, hue: "flavor",
      dir: [-1, 0.55, 0.34], pad: 1.35, dwell: 8000, enter: 3000,
      drift: { az: 3, el: 0.5, dolly: -0.015 },
    },
    {
      id: "core-reassemble", chapter: "Inside the cold core", title: "Everything nests together",
      body: "The coil hugs the carbonator, the reservoirs return to their pockets, and the shell and caps surround them. One insulated core keeps water and flavor cold.",
      label: "Cold core",
      parts: [], focus: CORE_WIDE, context: CORE_WIDE, frameReveal: SPREAD,
      reveal: ISOLATED,
      motions: { coreSpread: [1800, 3900], coreShell: [4000, 6500], coreCaps: [6600, 8300] },
      dir: [-1, -0.35, 0.36], pad: 1.25, dwell: 9000, motion: 8300, enter: 2400,
      drift: { az: 1.5, el: 0, dolly: -0.08 },
    },
    {
      id: "core-in-machine", chapter: "From the core to the faucet", title: "Back in the machine",
      body: "The cold core fits at the back. Refrigeration works ahead of it; pumps and valves sit above.",
      label: "Cold core, refrigeration and pumps",
      parts: [], focus: [...CORE_COVERS, "compressor", "condenser+fan", ...PUMPS],
      reveal: WORKING,
      dir: [-1, -0.65, 0.45], pad: 1.4, dwell: 6000, motion: 3000, enter: 3200,
      drift: { az: 3, el: 0.5, dolly: -0.01 },
    },
    {
      id: "flavor-pumps", chapter: "From the core to the faucet", title: "Flavor, ready for the first drop",
      body: "Each peristaltic pump meters one flavor. The flavor lines stay primed and valve-locked between pours, ready when the faucet opens.",
      label: "Two peristaltic pumps",
      parts: PUMPS, focus: [...PUMPS, "valve-v-e", "valve-v-i"],
      reveal: WORKING, hue: "flavor",
      dir: [0.9, -1, 0.5], pad: 1.6, dwell: 8000, enter: 2800,
      drift: { az: 2, el: 0.5, dolly: -0.025 },
    },
    {
      id: "flow-sensor", chapter: "Pour a glass", title: "The pour starts the flavor",
      body: "Carbonated water passes through a flow sensor on its way to the faucet. Its pulses tell the machine to run the selected flavor pump.",
      label: "Carbonated-water flow sensor",
      parts: ["tube-carb-1", "digiten-flow", "tube-carb-2"],
      focus: ["digiten-flow", "bulkhead-carb"],
      reveal: WORKING, hue: "soda",
      dir: [-0.85, 0.95, 0.5], pad: 2.2, dwell: 8000, enter: 3000,
      drift: { az: 2.5, el: 0.5, dolly: -0.02 },
    },
    {
      id: "outlets", chapter: "Pour a glass", title: "Together in the glass",
      body: "One tube carries carbonated water; two carry the flavors. The selected concentrate meets the water only in your glass.",
      label: "Soda and two flavor outlets",
      parts: ["bulkhead-carb", "bulkhead-flavor-a", "bulkhead-flavor-b"],
      reveal: WORKING, hue: "soda",
      dir: [-0.8, 1, 0.45], pad: 2.1, dwell: 8000, enter: 2200,
      drift: { az: 2, el: 0.5, dolly: 0.01 },
    },
    {
      id: "ready-to-pour", chapter: "Pour a glass", title: "Ready for the next glass",
      body: "The enclosure closes around the working parts. Water, cold, carbonation and flavor — all under the counter, ready at the faucet.",
      label: "Home soda machine",
      parts: [], focus: ["*"], reveal: CLOSED,
      motions: { park: [0, 1800], enclosure: [1800, 6400] },
      dir: [0.9, -1, 0.48], pad: 1.2, dwell: 7500, motion: 6400, enter: 2600,
      drift: { az: 2, el: 0.5, dolly: -0.025 },
    },
  ],
};
