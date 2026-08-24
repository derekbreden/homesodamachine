// THE WATER PATH, AS A TOUR. One journey, told in place, on the models the rest
// of the site already draws: cold tap water in at the rear wall, pumped to
// 100 psi into the carbonator, back out the wall beside it as soda water.
//
// ONE CLAIM, ONE HIGHLIGHT. That is the whole rule this file is written to.
// A beat says ONE thing and lights exactly the bodies that thing is about — so
// if the drip pan is mentioned, the drip pan is a beat, lit on its own, and
// nothing else is lit while it is being said. A beat that names four parts in
// three sentences is four beats.
//
// A CHAPTER IS ONE SHOT AND THEN A FEW HELD BEATS. Flying for every sentence
// would be seasickness; `hold: true` says the beat's subject is already framed,
// so the camera keeps drifting where it is while the light and the words cross
// over. The move that opens a chapter is the one that travels.
//
// THIS FILE IS THE CONTENT AND NOTHING ELSE. `public/js/tour/` plays it and
// knows nothing about water. Changing the walkthrough is changing this file.
//
// A STEP NAMES SOLIDS, NOT COORDINATES. `parts` are body names as the STEP
// carries them — the same names enclosure-assembly.facts.json lists and
// viewer/step.js stamps onto each mesh — and the camera is derived from where
// those bodies actually are when the model loads. So a beat keeps framing its
// subject after the subject moves. A name the loaded model does not carry is
// struck through on its own chip and named in the console, because this tree
// renames its bodies and a stale name would otherwise read as a bad angle.
//
//   chapter the group this beat belongs to. The rail draws one cluster per
//           chapter, so thirty ticks read as nine things.
//   parts   the bodies this beat is about: lit, and framed
//   focus   what to frame, when that is not the same as what to light.
//           `["*"]` is the whole model — what an establishing beat wants.
//   hold    this beat is the shot before it. No move: the light crosses over
//           where the camera already stands, and `dir`/`pad` are not read.
//   dir     where the camera stands, from the subject, in the machine's own
//           axes: +X right, −Y front (the user's side), +Z up — the ViewCube's
//           convention. Length is ignored.
//   pad     how much bigger than the subject the frame is. 1.0 is tight.
//   dwell   ms held. Omitted, it is read off the narration.
//   drift   the slow move made WHILE held, so the picture is never still:
//           degrees of azimuth and elevation, and a dolly as a fraction of the
//           distance (negative pushes in).
//   enter   ms of travel INTO this beat. Omitted, it is read off how far the
//           camera has to go.
//   isolate the sub-assembly this beat and the ones after it show ALONE. Every
//           body outside it goes out of the view, in place — no reload, no
//           second model. `null` puts the machine back. It carries forward
//           until another beat states one, the way a chapter does.
//   overview  this beat is the whole run at once. It lights everything and is
//           not counted as ground covered, so the trail behind the tour still
//           means the legs it has actually walked.
//
// THE TRANSITION IS NOT AUTHORED. Between two beats that are not neighbours the
// player computes the third pose that holds BOTH subjects — the one the camera
// swings out to at the halfway mark — and passes through it. `flight.js` says
// how.

const HOLD_DRIFT = { az: 3, el: 0.5, dolly: -0.015 };

export const TOUR = {
  id: "water",
  title: "The water path",
  subtitle: "Tap to soda, end to end",
  model: "manifold-layout/enclosure-assembly.step",

  // Everything the water touches, lit faintly for the whole tour so the leg on
  // screen is always read against the line it belongs to.
  path: [
    "tube-customer-water", "bulkhead-water", "bulkhead-ring-water", "tube-collar-water",
    "asse1022-assembly", "tube-water-2", "water-split", "tube-water-3",
    "vk-solenoid", "suction-chain", "tube-water-7", "seaflo-pump",
    "tube-water-6", "discharge-chain", "tube-water-5",
    "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb", "bulkhead-ring-carb",
  ],

  steps: [
    // ── The line ────────────────────────────────────────────────────────────
    {
      chapter: "The line",
      title: "Rear wall to rear wall",
      body: "Water comes in at the back of the machine and leaves as soda by the "
          + "same wall. Everything between is one line.",
      overview: true,
      parts: ["tube-customer-water", "bulkhead-water", "asse1022-assembly",
              "tube-water-2", "water-split", "tube-water-3", "vk-solenoid",
              "suction-chain", "tube-water-7", "seaflo-pump", "tube-water-6",
              "discharge-chain", "tube-water-5",
              "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb"],
      focus: ["*"],
      dir: [0.9, -1.0, 0.5],
      pad: 1.12,
      dwell: 6500,
      drift: { az: 9, el: 2, dolly: -0.06 },
      enter: 0,
    },

    // ── The house connection ────────────────────────────────────────────────
    {
      chapter: "The house connection",
      title: "The customer's line",
      body: "Quarter-inch LLDPE, from the cold supply under the sink.",
      parts: ["tube-customer-water"],
      dir: [-0.45, 1.0, 0.38],
      pad: 2.4,
      drift: { az: 5, el: -1, dolly: -0.05 },
    },
    {
      chapter: "The house connection",
      title: "It pushes in",
      body: "A bulkhead union through the wall. The customer plugs it in at "
          + "install time — no tools, no thread, nothing the factory closes.",
      parts: ["bulkhead-water"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "The house connection",
      title: "The wall says which",
      body: "Every crossing wears a ring, and the ring carries the word. This one "
          + "says TAP.",
      parts: ["bulkhead-ring-water", "bulkhead-ring-water-word"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "The house connection",
      title: "So does the line",
      body: "A collar on the tube carries the same word, so what is marked is the "
          + "line and not only the wall.",
      parts: ["tube-collar-water", "tube-collar-water-word"],
      hold: true,
      drift: HOLD_DRIFT,
    },

    // ── Nothing goes back ───────────────────────────────────────────────────
    {
      chapter: "Nothing goes back",
      title: "The preventer",
      body: "First thing inboard of the wall. Carbonic acid must never reach the "
          + "house supply.",
      parts: ["asse1022-assembly"],
      dir: [-1.0, 0.45, 0.4],
      pad: 1.7,
      drift: { az: 7, el: 1, dolly: -0.05 },
    },
    {
      chapter: "Nothing goes back",
      title: "Where it weeps",
      body: "If it ever fails it vents to atmosphere, and this is what it vents "
          + "into.",
      parts: ["asse-drip-pan"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Nothing goes back",
      title: "And who is watching",
      body: "A moisture sensor lies in the pan. The telltale is watched, not just "
          + "provided.",
      parts: ["moisture-plate"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Nothing goes back",
      title: "Downstream of it",
      body: "From the preventer's outlet the path is quarter-inch the whole way to "
          + "the pump's own barbs.",
      parts: ["tube-water-2"],
      hold: true,
      drift: HOLD_DRIFT,
    },

    // ── The split ───────────────────────────────────────────────────────────
    {
      chapter: "The split",
      title: "One line becomes two",
      body: "A tee. One leg feeds the flavor manifold; the other fills the "
          + "carbonator.",
      parts: ["water-split"],
      dir: [-0.9, -0.5, 0.55],
      pad: 2.2,
      drift: { az: 8, el: 2, dolly: -0.06 },
    },
    {
      chapter: "The split",
      title: "The flavor leg, throttled",
      body: "A needle valve holds that side under ten psi, and we leave it there.",
      parts: ["tube-fluid-1", "flow-regulator"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "The split",
      title: "The long way round",
      body: "The fill leg runs the length of the machine corridor — 255 mm and "
          + "eight corners — to the far wall.",
      parts: ["tube-water-3"],
      dir: [0.1, -0.7, 0.8],
      pad: 1.35,
      drift: { az: -9, el: -2, dolly: -0.05 },
    },
    {
      chapter: "The split",
      title: "The fill valve",
      body: "It ends at V-K, which is what decides whether the carbonator is "
          + "filling.",
      parts: ["vk-solenoid"],
      dir: [0.95, -0.55, 0.4],
      pad: 2.0,
      drift: { az: 7, el: 2, dolly: -0.05 },
    },

    // ── The pump ────────────────────────────────────────────────────────────
    {
      chapter: "The pump",
      title: "Face to face",
      body: "The valve's outlet meets the suction chain's collet directly — no "
          + "tube between them.",
      parts: ["suction-chain"],
      dir: [0.85, -0.75, 0.35],
      pad: 2.0,
      drift: { az: 8, el: 2, dolly: -0.06 },
    },
    {
      chapter: "The pump",
      title: "Onto the barb",
      body: "A reinforced PVC stub over a molded barb. This pump has no port "
          + "thread — a hose and a clamp is the only connection it offers.",
      parts: ["tube-water-7"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "The pump",
      title: "100 psi",
      body: "A SeaFlo 22-series diaphragm pump: 12 V, 1.3 GPM, shutting off at "
          + "100 psi. Enough head to push water in against the CO2 already "
          + "standing in the vessel.",
      parts: ["seaflo-pump"],
      dir: [0.7, -0.85, 0.45],
      pad: 1.55,
      dwell: 6200,
      drift: { az: 11, el: 3, dolly: -0.07 },
    },
    {
      chapter: "The pump",
      title: "And out the other side",
      body: "The discharge is the same stub the other way.",
      parts: ["tube-water-6"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "The pump",
      title: "One-way",
      body: "A check valve stands in the discharge chain, so what is downstream "
          + "never comes back at the pump.",
      parts: ["discharge-chain"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "The pump",
      title: "Into the cold",
      body: "From there it turns down out of the service bay and crosses the foam.",
      parts: ["tube-water-5"],
      dir: [-0.8, -0.7, 0.5],
      pad: 1.6,
      drift: { az: 7, el: -3, dolly: -0.1 },
    },

    // ── Inside the vessel ───────────────────────────────────────────────────
    {
      chapter: "Inside the vessel",
      title: "The carbonator",
      isolate: "cold-core",
      body: "A 316L stainless tube, standing upright inside the foam.",
      parts: ["cold-core/carbonator-tube"],
      dir: [0.85, -0.9, 0.3],
      pad: 1.7,
      dwell: 5200,
      drift: { az: 9, el: 2, dolly: -0.05 },
    },
    {
      chapter: "Inside the vessel",
      title: "Closed at both ends",
      body: "Welded end caps, with four NPT ports between them.",
      parts: ["cold-core/endcap-top", "cold-core/endcap-bottom"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Inside the vessel",
      title: "Where the water lands",
      body: "The top plate's own elbow. This is where the 100 psi is spent.",
      parts: ["cold-core/carbonator-elbow-water-in", "cold-core/collet-water-in", "cold-core/line-water-in"],
      dir: [0.6, -0.95, 0.45],
      pad: 2.3,
      drift: { az: 8, el: -2, dolly: -0.06 },
    },

    // ── Making it soda ──────────────────────────────────────────────────────
    {
      chapter: "Making it soda",
      title: "Gas comes in low",
      body: "CO2 enters through the bottom plate, not the top.",
      parts: ["cold-core/carbonator-elbow-co2-in", "cold-core/collet-co2-in", "cold-core/line-co2-in"],
      dir: [0.9, -0.7, 0.1],
      pad: 2.2,
      drift: { az: -8, el: 4, dolly: -0.06 },
    },
    {
      chapter: "Making it soda",
      title: "Onto a stub",
      body: "Inside the vessel it turns onto a barb and a short silicone stub.",
      parts: ["cold-core/sparge-barb", "cold-core/sparge-silicone-stub"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Making it soda",
      title: "The sparge stone",
      body: "Hanging in the water column. The gas enters below the liquid and "
          + "dissolves on the way up.",
      parts: ["cold-core/sparge-stone"],
      hold: true,
      dwell: 5200,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Making it soda",
      title: "The coil",
      body: "Wound on the outside and holding the water near freezing. Cold water "
          + "takes gas; warm water gives it back.",
      parts: ["cold-core/evap-coil"],
      dir: [0.95, -0.6, 0.25],
      pad: 1.5,
      dwell: 5600,
      drift: { az: -11, el: 3, dolly: -0.05 },
    },
    {
      chapter: "Making it soda",
      title: "Two temperatures",
      body: "One probe on the vessel wall, one on the coil. The compressor cycles "
          + "against them, with a freeze cutout.",
      parts: ["cold-core/probe-carbonator-ds18b20", "cold-core/probe-coil-ds18s20"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Making it soda",
      title: "A magnet on the water",
      body: "A float rides a rod inside, at whatever level the water is.",
      parts: ["cold-core/float-carb", "cold-core/float-rod-carb"],
      dir: [0.55, -1.0, 0.2],
      pad: 2.1,
      drift: { az: 8, el: 2, dolly: -0.05 },
    },
    {
      chapter: "Making it soda",
      title: "Read through the wall",
      body: "Reed switches outside see it. The level is known without piercing the "
          + "vessel anywhere.",
      parts: ["cold-core/reed-carb-1", "cold-core/reed-carb-2"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Making it soda",
      title: "The last word on pressure",
      body: "A relief valve on the top plate, on a port of its own.",
      parts: ["cold-core/prv-sv125", "cold-core/prv-shroud"],
      dir: [0.4, -1.0, 0.5],
      pad: 2.1,
      drift: { az: 9, el: 3, dolly: -0.05 },
    },
    {
      chapter: "Making it soda",
      title: "Out of the bottom",
      body: "Carbonated water leaves from the floor of the vessel, where it is "
          + "coldest and least disturbed.",
      parts: ["cold-core/carbonator-elbow-carb-water-out", "cold-core/collet-carb-water-out",
              "cold-core/line-carb-water-out"],
      dir: [0.5, -0.95, 0.12],
      pad: 2.2,
      drift: { az: 7, el: 4, dolly: -0.05 },
    },

    // ── Up and out ──────────────────────────────────────────────────────────
    {
      chapter: "Up and out",
      title: "The climb",
      isolate: null,
      body: "Back in the cabinet, 279 mm up the corridor.",
      parts: ["tube-carb-1"],
      dir: [-0.7, -0.75, 0.4],
      pad: 1.7,
      drift: { az: 10, el: 2, dolly: -0.06 },
    },
    {
      chapter: "Up and out",
      title: "The pour, detected",
      body: "A flow sensor. Its pulse train is what tells the machine a glass is "
          + "being filled, and what starts the flavor pumps.",
      parts: ["digiten-flow"],
      dir: [-0.55, -0.5, 0.55],
      pad: 2.2,
      drift: { az: 8, el: 2, dolly: -0.06 },
    },
    {
      chapter: "Up and out",
      title: "Twenty-two millimetres",
      body: "That is all that is left between the sensor and the wall.",
      parts: ["tube-carb-2"],
      hold: true,
      drift: HOLD_DRIFT,
    },
    {
      chapter: "Up and out",
      title: "The ring that says SODA",
      body: "Out through the bulkhead one row above the deck, into the umbilical, "
          + "and up through the countertop to the faucet.",
      parts: ["bulkhead-carb", "bulkhead-ring-carb", "bulkhead-ring-carb-word"],
      dir: [-0.4, 1.0, 0.28],
      pad: 2.2,
      dwell: 5600,
      drift: { az: -6, el: -2, dolly: -0.07 },
    },

    // ── The whole path ──────────────────────────────────────────────────────
    {
      chapter: "The whole path",
      title: "Two connections, one line",
      body: "Rear wall to rear wall, through a pump and a pressure vessel.",
      overview: true,
      parts: ["tube-customer-water", "bulkhead-water", "asse1022-assembly",
              "tube-water-2", "water-split", "tube-water-3", "vk-solenoid",
              "suction-chain", "tube-water-7", "seaflo-pump", "tube-water-6",
              "discharge-chain", "tube-water-5",
              "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb"],
      focus: ["*"],
      dir: [-0.95, -1.0, 0.45],
      pad: 1.15,
      dwell: 8000,
      drift: { az: 20, el: 4, dolly: -0.04 },
      enter: 4200,
    },
  ],
};
