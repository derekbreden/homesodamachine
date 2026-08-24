// THE WATER PATH, AS A TOUR. One journey, told in place, on the models the rest
// of the site already draws: cold tap water in at the rear wall, pumped to
// 100 psi into the carbonator, back out the wall beside it as soda water.
//
// THIS FILE IS THE CONTENT AND NOTHING ELSE. Every camera angle, every part
// named, every word said, and every beat's length is here; `public/js/tour/`
// is the machine that plays it and knows nothing about water. Changing the
// walkthrough is changing this file, and a push of this file alone is a
// deploy of the new walkthrough.
//
// A STEP NAMES SOLIDS, NOT COORDINATES. `parts` are body names as the STEP
// carries them — the same names hardware/manifold-layout/enclosure-assembly.facts.json
// lists and viewer/step.js stamps onto each mesh — and the camera is derived
// from where those bodies actually are when the model loads. So a step keeps
// framing its subject after the subject moves, and a run that gets longer is
// still in shot. What a step states about the camera is a DIRECTION to look
// from and how much room to leave, never a position.
//
//   parts   the bodies this step is about: lit, and framed
//   focus   what to frame, when that is not the same as what to light
//   dir     where the camera stands, from the subject, in the machine's own
//           axes: +X right, −Y front (the user's side), +Z up — the ViewCube's
//           convention. Length is ignored.
//   pad     how much bigger than the subject the frame is. 1.0 is tight.
//   dwell   ms held on the step. Omitted, it is read off the narration.
//   drift   the slow move made WHILE held, so the picture is never still:
//           degrees of azimuth and elevation, and a dolly as a fraction of
//           the distance (negative pushes in).
//   enter   ms of travel INTO this step. Omitted, it is read off how far the
//           camera has to go.
//   model   the STEP this step is shown on, when that is not the one before.
//   overview  this beat is the whole run at once. It lights everything and is
//           not counted as ground covered, so the trail behind the tour still
//           means the legs it has actually walked.
//
// THE TRANSITION IS NOT AUTHORED. Between two steps the player computes the
// third pose that holds BOTH subjects — the one the camera swings out to at
// the halfway mark — and passes through it. `flight.js` says how.

export const TOUR = {
  id: "water",
  title: "The water path",
  subtitle: "Tap to soda, end to end",
  model: "manifold-layout/enclosure-assembly.step",

  // WHERE A SECOND MODEL STANDS IN THE FIRST ONE'S FRAME. The cold core is
  // drawn in its own frame and seated in the machine at a quarter turn
  // (enclosure_assembly.py FOAM_YAW), so a swap that did not turn it would
  // land the core across the cabinet. `anchor` is the body in the incoming
  // model that answers to `into` in the outgoing one; matching those two
  // boxes after the turn is what puts the core back where the foam block
  // stood, and the camera never has to move for the swap.
  frames: {
    "cold-core-layout/cold-core-assembly.step": {
      yawDeg: 90,
      anchor: ["foam-shell", "foam-cap-top", "foam-cap-bottom",
               "foam-cap-lid-top", "foam-cap-lid-bottom"],
      into: "foam-assembly",
      // The seat, for the case where the enclosure is not on screen to be
      // asked — a link straight into a cold-core beat, which is the ordinary
      // way to come back to one while the words are still being written. The
      // live body wins whenever the enclosure has been loaded, so this is a
      // cold start's answer rather than a second source of truth. It is
      // `foam-assembly` in manifold-layout/enclosure-assembly.facts.json.
      intoBox: [-90.5, 178.0, 0.0, 90.5, 461.0, 305.6],
    },
  },

  // Everything the water touches, lit faintly for the whole tour so the leg
  // on screen is always read against the line it belongs to.
  path: [
    "tube-customer-water", "bulkhead-water", "port-ring-water", "tube-collar-water",
    "asse1022-assembly", "tube-water-2", "water-split", "tube-water-3",
    "vk-solenoid", "suction-chain", "tube-water-7", "seaflo-pump",
    "tube-water-6", "discharge-chain", "tube-water-5",
    "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb", "port-ring-carb",
  ],

  steps: [
    {
      id: "map",
      title: "One line, back to back",
      body: "Cold tap water enters the rear wall, crosses the machine to a pump, "
          + "goes into the carbonator under pressure, and leaves by the wall it "
          + "came in by. Everything between is one continuous line.",
      parts: ["tube-customer-water", "bulkhead-water", "asse1022-assembly",
              "tube-water-2", "water-split", "tube-water-3", "vk-solenoid",
              "suction-chain", "tube-water-7", "seaflo-pump", "tube-water-6",
              "discharge-chain", "tube-water-5",
              "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb"],
      overview: true,
      focus: ["*"],
      dir: [0.9, -1.0, 0.5],
      pad: 1.12,
      dwell: 7000,
      drift: { az: 9, el: 2, dolly: -0.06 },
      enter: 0,
    },
    {
      id: "inlet",
      title: "The house connection",
      body: "A quarter-inch line pushes into the bulkhead union on the +Y wall of "
          + "back-top. House pressure, house temperature — the only water "
          + "connection the appliance makes.",
      parts: ["tube-customer-water", "bulkhead-water", "port-ring-water",
              "tube-collar-water", "port-ring-water-word"],
      dir: [-0.45, 1.0, 0.42],
      pad: 1.85,
      drift: { az: 6, el: -2, dolly: -0.07 },
    },
    {
      id: "backflow",
      title: "Nothing goes back",
      body: "Carbonic acid must never reach the house supply. The ASSE 1022 "
          + "preventer stands first inside the wall, and weeps to a sensed drip "
          + "pan if it ever fails.",
      parts: ["asse1022-assembly", "asse-drip-pan", "moisture-plate", "tube-water-2"],
      dir: [-1.0, 0.5, 0.45],
      pad: 1.9,
      drift: { az: 8, el: 1, dolly: -0.05 },
    },
    {
      id: "split",
      title: "The split, and the long run",
      body: "The supply divides. One leg throttles down to the flavor manifold; "
          + "the other runs the length of the machine corridor — 255 mm and eight "
          + "corners — to the fill solenoid on the far wall.",
      parts: ["water-split", "tube-water-3", "vk-solenoid"],
      dir: [0.1, -0.75, 0.8],
      pad: 1.5,
      drift: { az: -10, el: -3, dolly: -0.05 },
    },
    {
      id: "pump",
      title: "100 psi",
      body: "A SeaFlo 22-series diaphragm pump, 12 V and 1.3 GPM, shuts off at "
          + "100 psi. That is the whole trick: enough head to push water in "
          + "against the CO2 already standing in the vessel.",
      parts: ["seaflo-pump", "suction-chain", "tube-water-7", "tube-water-6",
              "discharge-chain"],
      dir: [0.75, -0.85, 0.5],
      pad: 1.6,
      dwell: 7000,
      drift: { az: 12, el: 3, dolly: -0.08 },
    },
    {
      id: "into-core",
      title: "Into the cold",
      body: "The discharge turns down out of the service bay and crosses the "
          + "foam into the carbonator's top plate.",
      parts: ["discharge-chain", "tube-water-5", "foam-assembly"],
      dir: [-0.85, -0.7, 0.5],
      pad: 1.7,
      drift: { az: 7, el: -4, dolly: -0.12 },
    },
    {
      id: "vessel",
      title: "Inside the vessel",
      model: "cold-core-layout/cold-core-assembly.step",
      body: "A 316L stainless tube between two welded end caps, standing upright. "
          + "Water arrives through the top plate's own elbow.",
      parts: ["carbonator-tube", "endcap-top", "endcap-bottom",
              "carbonator-elbow-water-in", "collet-water-in", "line-water-in"],
      dir: [0.85, -0.9, 0.35],
      pad: 1.75,
      dwell: 6500,
      drift: { az: 10, el: 2, dolly: -0.06 },
    },
    {
      id: "carbonate",
      title: "Gas going up, water coming down",
      body: "CO2 enters low through a sparge stone and rises as fine bubbles. "
          + "The coil wound on the outside holds the water near freezing — cold "
          + "water takes gas, warm water gives it back.",
      parts: ["sparge-stone", "sparge-barb", "sparge-silicone-stub",
              "carbonator-elbow-co2-in", "evap-coil"],
      dir: [0.95, -0.55, 0.12],
      pad: 1.7,
      dwell: 7000,
      drift: { az: -12, el: 6, dolly: -0.05 },
    },
    {
      id: "leaves-vessel",
      title: "Out of the bottom",
      body: "Carbonated water leaves from the bottom, where it is coldest and "
          + "least disturbed. A relief valve on the top plate guards the rest.",
      parts: ["carbonator-elbow-carb-water-out", "collet-carb-water-out",
              "line-carb-water-out", "endcap-bottom", "prv-sv125", "prv-shroud"],
      dir: [0.5, -1.0, 0.18],
      pad: 2.0,
      drift: { az: 9, el: 5, dolly: -0.05 },
    },
    {
      id: "flow-sensor",
      title: "The pour, detected",
      model: "manifold-layout/enclosure-assembly.step",
      body: "Back in the cabinet, the line climbs 279 mm to the flow sensor. Its "
          + "pulse train is what tells the machine a glass is being filled, and "
          + "what starts the flavor pumps.",
      parts: ["tube-carb-1", "digiten-flow"],
      dir: [-0.7, -0.75, 0.4],
      pad: 1.9,
      drift: { az: 11, el: 2, dolly: -0.06 },
    },
    {
      id: "outlet",
      title: "Out the wall it came in by",
      body: "Through the blue-ringed bulkhead one row above the deck, into the "
          + "umbilical, and up through the countertop to the faucet.",
      parts: ["tube-carb-2", "bulkhead-carb", "port-ring-carb", "port-ring-carb-word"],
      dir: [-0.4, 1.0, 0.3],
      pad: 2.5,
      drift: { az: -7, el: -2, dolly: -0.08 },
    },
    {
      id: "whole",
      title: "The whole path",
      body: "Rear wall to rear wall, through a pump and a pressure vessel. "
          + "Two connections to the world, and one line between them.",
      parts: ["tube-customer-water", "bulkhead-water", "asse1022-assembly",
              "tube-water-2", "water-split", "tube-water-3", "vk-solenoid",
              "suction-chain", "tube-water-7", "seaflo-pump", "tube-water-6",
              "discharge-chain", "tube-water-5",
              "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb"],
      overview: true,
      focus: ["*"],
      dir: [-0.95, -1.0, 0.45],
      pad: 1.15,
      dwell: 9000,
      drift: { az: 22, el: 4, dolly: -0.04 },
      enter: 4200,
    },
  ],
};
