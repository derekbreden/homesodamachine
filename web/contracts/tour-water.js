// Timed captions, camera poses and reveal states for the machine tour.
// `dwell` is the entire beat in milliseconds, including its opening motion.
// `parts` highlights real assembly bodies; `focus` sets a wider camera frame.
// `reveal` is the exploded position of the enclosure, cold core and carbonator.

const CLOSED = { enclosure: 0, coldCore: 0, carbonator: 0 };
const SCREWS = { enclosure: 0.36, coldCore: 0, carbonator: 0 };
const OPEN = { enclosure: 1, coldCore: 0, carbonator: 0 };
const CORE = { enclosure: 1, coldCore: 1, carbonator: 0 };
const CUTAWAY = { enclosure: 1, coldCore: 1, carbonator: 1 };

const CORE_FRAME = [
  "cold-core/carbonator-tube", "cold-core/reservoir-a", "cold-core/reservoir-b",
];
const PUMPS = ["pump-a-head", "pump-a-motor", "pump-b-head", "pump-b-motor"];

export const TOUR = {
  id: "machine",
  title: "Inside the home soda machine",
  subtitle: "From tap water to cold soda, in under two minutes",
  model: "manifold-layout/enclosure-assembly.step",
  paths: [],

  steps: [
    {
      chapter: "Open the machine", title: "Soda, on tap",
      body: "This is the under-counter appliance: it chills water, adds carbonation, and sends two flavors to a faucet.",
      label: "Home soda machine",
      parts: [], focus: ["*"], reveal: CLOSED,
      dir: [0.9, -1, 0.48], pad: 1.2, dwell: 6500,
      drift: { az: 3, el: 0.5, dolly: -0.025 },
    },
    {
      chapter: "Open the machine", title: "First, the screws",
      body: "The side screws turn out and float clear, releasing the four enclosure quadrants.",
      label: "Enclosure screws",
      parts: [], focus: ["*"], reveal: SCREWS,
      dir: [0.9, -1, 0.48], pad: 1.28, dwell: 5000,
      drift: { az: 1.5, el: 0, dolly: 0 },
    },
    {
      chapter: "Open the machine", title: "Make room to see",
      body: "The enclosure quadrants slide away. The working parts stay in place, so we can follow how they fit together.",
      label: "Four enclosure quadrants",
      parts: [], focus: ["*"], reveal: OPEN,
      dir: [0.9, -1, 0.48], pad: 1.8, dwell: 7000,
      drift: { az: 2, el: 0.5, dolly: -0.015 },
    },
    {
      chapter: "Bring in the water", title: "Start at the house supply",
      body: "Tap water enters at the rear. A beverage backflow preventer stops reverse flow toward the house supply.",
      label: "Water inlet and backflow preventer",
      parts: ["bulkhead-water", "asse1022-assembly", "tube-water-2"],
      focus: ["asse1022-assembly", "water-split", "bulkhead-water"],
      reveal: OPEN, hue: "water",
      dir: [-1, 0.85, 0.65], pad: 1.85, dwell: 7500,
      drift: { az: 3, el: 0.5, dolly: -0.02 },
    },
    {
      chapter: "Bring in the water", title: "Push against the pressure",
      body: "The diaphragm pump pushes water into the carbonator against the CO₂ pressure already inside. A fill valve opens for refills.",
      label: "Diaphragm pump",
      parts: ["seaflo-pump", "vk-solenoid", "tube-water-5"],
      focus: ["seaflo-pump", "vk-solenoid", "discharge-chain"],
      reveal: OPEN, hue: "water",
      dir: [-0.9, -0.65, 0.6], pad: 1.55, dwell: 8000,
      drift: { az: 3, el: 0.5, dolly: -0.03 },
    },
    {
      chapter: "Keep it cold", title: "A small refrigeration system",
      body: "Below the pumps, a compressor circulates refrigerant. The condenser and fan release the heat through the sides of the enclosure.",
      label: "Compressor, condenser and fan",
      parts: ["compressor", "condenser+fan", "tube-refrig-1"],
      reveal: OPEN, hue: "refrigerant",
      dir: [0.9, -1, 0.4], pad: 1.55, dwell: 8000,
      drift: { az: 4, el: 0.5, dolly: -0.02 },
    },
    {
      chapter: "Keep it cold", title: "The cold core",
      body: "Behind them, the cold core holds the carbonator and both flavor reservoirs. Foam insulation surrounds this chilled center of the machine.",
      label: "Insulated cold core",
      parts: ["cold-core/foam-shell", "cold-core/foam-cap-top"],
      focus: CORE_FRAME, reveal: OPEN, hue: "refrigerant",
      dir: [-0.95, 0.65, 0.4], pad: 1.7, dwell: 7500,
      drift: { az: 2.5, el: 0.5, dolly: -0.02 },
    },
    {
      chapter: "Keep it cold", title: "Follow the cold inward",
      body: "Lift the outer layers away. A copper evaporator coil wraps the carbonator, pulling heat from the water and holding it near freezing.",
      label: "Copper evaporator coil",
      parts: ["cold-core/evap-coil", "cold-core/evap-tail-inlet", "cold-core/evap-tail-outlet"],
      focus: CORE_FRAME, reveal: CORE, hue: "refrigerant",
      dir: [-0.85, -0.75, 0.4], pad: 1.55, dwell: 8000,
      drift: { az: 3, el: 0.5, dolly: -0.02 },
    },
    {
      chapter: "Make the bubbles", title: "Cold water meets CO₂",
      body: "Inside the coil is the stainless steel carbonator. CO₂ arrives from a cylinder beside the appliance and enters through its bottom cap.",
      label: "Carbonator and CO₂ inlet",
      parts: ["cold-core/carbonator-tube", "cold-core/line-co2-in", "cold-core/carbonator-elbow-co2-in"],
      focus: CORE_FRAME, reveal: CORE, hue: "co2",
      dir: [-0.85, -0.75, 0.3], pad: 1.5, dwell: 8000,
      drift: { az: 3, el: 0.5, dolly: -0.025 },
    },
    {
      chapter: "Make the bubbles", title: "A look inside the carbonator",
      body: "This cutaway exposes the sparge stone. It spreads CO₂ into small bubbles beneath the water, where the gas dissolves under pressure.",
      label: "Sparge stone · carbonator cutaway",
      parts: ["cold-core/sparge-stone", "cold-core/sparge-silicone-stub", "cold-core/sparge-barb"],
      focus: ["cold-core/endcap-bottom", "cold-core/float-rod-carb"],
      reveal: CUTAWAY, hue: "co2",
      dir: [-1, 0.02, 0.2], pad: 1.65, dwell: 8000,
      drift: { az: 3, el: 1, dolly: -0.015 },
    },
    {
      chapter: "Add the flavor", title: "Two flavors, already chilled",
      body: "The two flavor reservoirs nest beside the carbonator. Each holds concentrate and has its own line to a peristaltic pump.",
      label: "Two flavor reservoirs",
      parts: ["cold-core/reservoir-a", "cold-core/reservoir-b"],
      focus: CORE_FRAME, reveal: CORE, hue: "flavor",
      dir: [0.9, -0.8, 0.42], pad: 1.6, dwell: 7500,
      drift: { az: 3, el: 0.5, dolly: -0.015 },
    },
    {
      chapter: "Add the flavor", title: "Ready for the first drop",
      body: "Each peristaltic pump meters one flavor. The flavor lines stay primed and valve-locked between pours, ready when the faucet opens.",
      label: "Two peristaltic pumps",
      parts: PUMPS,
      focus: [...PUMPS, "valve-v-e", "valve-v-i"],
      reveal: CORE, hue: "flavor",
      dir: [0.9, -1, 0.5], pad: 1.6, dwell: 7500,
      drift: { az: 2, el: 0.5, dolly: -0.025 },
    },
    {
      chapter: "Pour a glass", title: "The pour starts the flavor",
      body: "Carbonated water passes through a flow sensor on its way to the faucet. Its pulses tell the machine to run the selected flavor pump.",
      label: "Carbonated-water flow sensor",
      parts: ["tube-carb-1", "digiten-flow", "tube-carb-2"],
      focus: ["digiten-flow", "bulkhead-carb"],
      reveal: CORE, hue: "soda",
      dir: [-0.85, 0.95, 0.5], pad: 2.2, dwell: 8000,
      drift: { az: 2.5, el: 0.5, dolly: -0.02 },
    },
    {
      chapter: "Pour a glass", title: "Together in the glass",
      body: "One tube carries carbonated water; two carry the flavors. The selected concentrate meets the water only in your glass.",
      label: "Soda and two flavor outlets",
      parts: ["bulkhead-carb", "bulkhead-flavor-a", "bulkhead-flavor-b"],
      reveal: CORE, hue: "soda",
      dir: [-0.8, 1, 0.45], pad: 2.1, dwell: 8000,
      drift: { az: 2, el: 0.5, dolly: 0.01 },
    },
    {
      chapter: "Pour a glass", title: "One machine, under the counter",
      body: "The layers return, the enclosure closes, and the screws seat. Water, cold, carbonation and flavor: ready for the next glass.",
      label: "Home soda machine",
      parts: [], focus: ["*"], reveal: CLOSED,
      dir: [0.9, -1, 0.48], pad: 1.2, dwell: 7000, motion: 6000,
      drift: { az: 2, el: 0.5, dolly: -0.025 },
    },
  ],
};
