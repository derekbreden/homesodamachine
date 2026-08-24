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
//   hue     what is in the pipe from this beat on — `water`, `soda`, `co2`,
//           `refrigerant`, `flavor`. Carried forward like `isolate`, so the
//           tour changes colour once, where the water becomes soda.
//   vertigo the field of view this beat and the ones after it are seen through.
//           The move into it changes lens and distance together so the SUBJECT
//           holds its size while the machine around it swells — the grammar for
//           "this is inside that", which an arc can only imply. 45 is the
//           page's own lens.
//   bare    the beat drops its own words partway through, so what is left on
//           screen at the end is the machine and the line and nothing else.
//   solid   ms the machine is drawn SOLID at the top of the tour before it
//           dissolves to the x-ray view. Only the opening beat reads it.
//   flow    ms per body of a bright crest travelling the beat's own list, over
//           and over, in the order it names them. Direction, on tubes that have
//           no centreline to run dashes along.
//   quiet   0..1, how far the machine BEHIND the lights is turned down for this
//           beat. The subject gets louder by everything else getting quieter,
//           which costs nothing and composes with every other tier. Carried by
//           the beat, not sticky — a beat with no `quiet` is a full-brightness
//           machine.
//   ignite  ms per body. The beat's bodies come on ONE AT A TIME, in the order
//           it names them, instead of arriving together. On a beat about a whole
//           run that order is the order the water takes, so the run draws itself.
//   overview  this beat is the whole run at once. It lights everything and is
//           not counted as ground covered, so the trail behind the tour still
//           means the legs it has actually walked.
//
// THE TRANSITION IS NOT AUTHORED. Between two beats that are not neighbours the
// player computes the third pose that holds BOTH subjects — the one the camera
// swings out to at the halfway mark — and passes through it. `flight.js` says
// how.

// HOW A HELD BEAT MOVES WHILE IT IS HELD. Every beat drifting the same way at
// the same rate is what makes a long walkthrough feel like a screensaver — the
// motion stops carrying information and becomes wallpaper. Each chapter takes
// one of these, so the picture is alive and the aliveness is not identical
// eleven times over.
//
//   ORBIT   swing round it, the ordinary case
//   RISE    swing and climb — for a thing read from above
//   FALL    swing and settle — for a thing read from below
//   PUSH    barely turn, and close in — for a thing worth staring at
//   BACK    turn the other way and ease off — the beat after a close one
const ORBIT = { az: 3.2, el: 0.5, dolly: -0.015 };
const RISE  = { az: 2.4, el: 2.2, dolly: -0.02 };
const FALL  = { az: 2.6, el: -2.0, dolly: -0.012 };
const PUSH  = { az: 1.2, el: 0.3, dolly: -0.045 };
const BACK  = { az: -3.0, el: 0.8, dolly: 0.012 };

export const TOUR = {
  id: "water",
  title: "The water path",
  subtitle: "Tap to soda, end to end",
  model: "manifold-layout/enclosure-assembly.step",

  // THE MAP, BY FLUID. Every body the run touches, faint, all tour long — so a
  // close-up is always read against the line it belongs to. Split where the
  // water becomes soda, because that is the machine's whole point and the
  // colour is the cheapest way to say it: blue in at the rear wall, teal back
  // out of it. `spotlight.js` HUES is the palette.
  paths: [
    { hue: "water", parts: [
      "tube-customer-water", "bulkhead-water", "bulkhead-ring-water", "tube-collar-water",
      "asse1022-assembly", "tube-water-2", "water-split", "tube-water-3",
      "vk-solenoid", "suction-chain", "tube-water-7", "seaflo-pump",
      "tube-water-6", "discharge-chain", "tube-water-5",
    ] },
    { hue: "soda", parts: [
      "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb", "bulkhead-ring-carb",
    ] },
  ],

  steps: [
    // ── The line ────────────────────────────────────────────────────────────
    { chapter: "The line", title: "Rear wall to rear wall",
      body: "Water enters at the back of the machine and leaves as soda by the same wall.",
      overview: true, focus: ["*"],
      parts: ["tube-customer-water", "bulkhead-water", "asse1022-assembly", "tube-water-2",
              "water-split", "tube-water-3", "vk-solenoid", "suction-chain", "tube-water-7",
              "seaflo-pump", "tube-water-6", "discharge-chain", "tube-water-5",
              "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb"],
      dir: [0.9, -1.0, 0.5], pad: 1.12, dwell: 11000, enter: 0,
      solid: 3200, ignite: 240, quiet: 0.45, flow: 150,
      drift: { az: 12, el: 2, dolly: -0.07 } },

    // ── The house connection ────────────────────────────────────────────────
    { chapter: "The house connection", title: "The customer's line",
      body: "Quarter-inch tubing, from the cold supply under the sink.",
      parts: ["tube-customer-water"],
      dir: [-0.45, 1.0, 0.38], pad: 1.9, drift: { az: 5, el: -1, dolly: -0.05 } },
    { chapter: "The house connection", title: "Push to connect",
      body: "It ends at a bulkhead union through the wall. No tools, no thread.",
      parts: ["bulkhead-water"], hold: true, drift: FALL },
    { chapter: "The house connection", title: "The wall wears a ring",
      body: "One at every crossing this wall carries.",
      parts: ["bulkhead-ring-water"], hold: true, drift: FALL },
    { chapter: "The house connection", title: "TAP",
      body: "The ring's word says which line this is.",
      parts: ["bulkhead-ring-water-word"], hold: true, drift: FALL },
    { chapter: "The house connection", title: "So does the tube",
      body: "A collar rides the line itself.",
      parts: ["tube-collar-water"], hold: true, drift: FALL },
    { chapter: "The house connection", title: "The same word again",
      body: "Lettered along the tube, so it reads down the line rather than across the face.",
      parts: ["tube-collar-water-word"], hold: true, drift: FALL },

    // ── Nothing goes back ───────────────────────────────────────────────────
    { chapter: "Nothing goes back", title: "The preventer",
      body: "Carbonic acid must never reach the house supply. This is what stops it.",
      parts: ["asse1022-assembly"],
      dir: [-1.0, 0.45, 0.4], pad: 1.7, drift: { az: 7, el: 1, dolly: -0.05 } },
    { chapter: "Nothing goes back", title: "Where it weeps",
      body: "If it ever fails, it vents to atmosphere — into this.",
      parts: ["asse-drip-pan"], hold: true, drift: ORBIT },
    { chapter: "Nothing goes back", title: "Watched, not just provided",
      body: "A moisture sensor lies in the pan.",
      parts: ["moisture-plate"], hold: true, drift: ORBIT },
    { chapter: "Nothing goes back", title: "Downstream of it",
      body: "From here the path is quarter-inch all the way to the pump's own barbs.",
      parts: ["tube-water-2"], hold: true, drift: ORBIT },

    // ── The split ───────────────────────────────────────────────────────────
    { chapter: "The split", title: "The supply divides",
      body: "A tee, low on the −X wall.",
      parts: ["water-split"],
      dir: [-0.9, -0.5, 0.55], pad: 2.0, drift: { az: 8, el: 2, dolly: -0.06 } },
    { chapter: "The split", title: "One leg goes to flavor",
      body: "This one feeds the manifold, and we leave it there.",
      parts: ["tube-fluid-1"], hold: true, drift: RISE },
    { chapter: "The split", title: "Throttled down",
      body: "A needle valve holds that side under ten psi.",
      parts: ["flow-regulator"], hold: true, drift: RISE },
    { chapter: "The split", title: "The other goes the long way",
      body: "The length of the machine corridor — 255 mm and eight corners.",
      parts: ["tube-water-3"],
      dir: [0.1, -0.7, 0.8], pad: 1.35, drift: { az: -9, el: -2, dolly: -0.05 } },
    { chapter: "The split", title: "The fill valve",
      body: "V-K, on the far wall. It decides whether the carbonator is filling.",
      parts: ["vk-solenoid"],
      dir: [0.95, -0.55, 0.4], pad: 1.9, drift: { az: 7, el: 2, dolly: -0.05 } },

    // ── The pump ────────────────────────────────────────────────────────────
    { chapter: "The pump", title: "Face to face",
      body: "The valve's outlet meets the suction chain's collet. No tube between them.",
      parts: ["suction-chain"],
      dir: [0.85, -0.75, 0.35], pad: 1.9, drift: { az: 8, el: 2, dolly: -0.06 } },
    { chapter: "The pump", title: "Over a molded barb",
      body: "A reinforced PVC stub. This pump has no port thread — a hose and a clamp is all it offers.",
      parts: ["tube-water-7"], hold: true, drift: PUSH },
    { chapter: "The pump", title: "The pump",
      body: "A SeaFlo 22-series diaphragm pump. 12 V, 1.3 GPM.",
      parts: ["seaflo-pump"],
      dir: [0.7, -0.85, 0.45], pad: 1.5, drift: { az: 11, el: 3, dolly: -0.07 } },
    { chapter: "The pump", title: "100 psi",
      body: "Its shutoff, and the whole trick: enough head to push water in against the CO2 already in the vessel.",
      parts: ["seaflo-pump"], hold: true, dwell: 5600, quiet: 0.4, drift: PUSH },
    { chapter: "The pump", title: "Out the other side",
      body: "The discharge is the same stub, the other way.",
      parts: ["tube-water-6"], hold: true, drift: PUSH },
    { chapter: "The pump", title: "One-way",
      body: "A check valve stands in the discharge chain. Nothing comes back at the pump.",
      parts: ["discharge-chain"], hold: true, drift: PUSH },
    { chapter: "The pump", title: "Into the cold",
      body: "It turns down out of the service bay and crosses the foam.",
      parts: ["tube-water-5"],
      dir: [-0.8, -0.7, 0.5], pad: 1.6, drift: { az: 7, el: -3, dolly: -0.1 } },

    // ── Inside the vessel ───────────────────────────────────────────────────
    { chapter: "Inside the vessel", title: "The carbonator",
      body: "A 316L stainless tube, standing upright inside the foam.",
      parts: ["cold-core/carbonator-tube"], isolate: "cold-core", vertigo: 68,
      dir: [0.85, -0.9, 0.3], pad: 1.7, dwell: 5000, drift: { az: 9, el: 2, dolly: -0.05 } },
    { chapter: "Inside the vessel", title: "The top cap",
      body: "Welded on. Water comes in here, and pressure leaves here.",
      parts: ["cold-core/endcap-top"], hold: true, drift: RISE },
    { chapter: "Inside the vessel", title: "The bottom cap",
      body: "Welded on. Gas comes in here, and soda leaves here.",
      parts: ["cold-core/endcap-bottom"], hold: true, drift: RISE },
    { chapter: "Inside the vessel", title: "Where the water lands",
      body: "An elbow on the top cap. This is where the 100 psi is spent.",
      parts: ["cold-core/carbonator-elbow-water-in"],
      dir: [0.6, -0.95, 0.5], pad: 2.2, drift: { az: 8, el: -2, dolly: -0.06 } },
    { chapter: "Inside the vessel", title: "Its collet",
      body: "Quarter-inch, push-fit, made up at the bench.",
      parts: ["cold-core/collet-water-in"], hold: true, drift: RISE },
    { chapter: "Inside the vessel", title: "And the line it takes",
      body: "Buried in the foam the moment it is poured.",
      parts: ["cold-core/line-water-in"], hold: true, drift: RISE },

    // ── Making it soda ──────────────────────────────────────────────────────
    { chapter: "Making it soda", title: "Gas comes in low",
      body: "Through the bottom cap, not the top.",
      parts: ["cold-core/carbonator-elbow-co2-in"],
      dir: [0.9, -0.7, 0.1], pad: 2.1, drift: { az: -8, el: 4, dolly: -0.06 } },
    { chapter: "Making it soda", title: "Made up first",
      body: "Its collet is the one joint the foam puts out of reach. Tug-test it before the pour.",
      parts: ["cold-core/collet-co2-in"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "Down the lane",
      body: "The line falls the shell's whole height to reach it.",
      parts: ["cold-core/line-co2-in"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "A barb inside",
      body: "The port feeds it from within the vessel.",
      parts: ["cold-core/sparge-barb"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "A silicone stub",
      body: "Short, and flexible enough to hang what comes next.",
      parts: ["cold-core/sparge-silicone-stub"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "The sparge stone",
      body: "Hanging in the water column, near the floor.",
      parts: ["cold-core/sparge-stone"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "Below the liquid",
      body: "Gas entering under the water dissolves the whole way up.",
      parts: ["cold-core/sparge-stone"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "The coil",
      body: "Copper, wound onto the vessel's outside.",
      parts: ["cold-core/evap-coil"],
      dir: [0.95, -0.6, 0.25], pad: 1.5, drift: { az: -11, el: 3, dolly: -0.05 } },
    { chapter: "Making it soda", title: "Held near freezing",
      body: "Cold water takes gas. Warm water gives it back.",
      parts: ["cold-core/evap-coil"], hold: true, dwell: 5000, drift: ORBIT },
    { chapter: "Making it soda", title: "The wall's temperature",
      body: "One probe reads the vessel itself.",
      parts: ["cold-core/probe-carbonator-ds18b20"], hold: true, drift: ORBIT },
    { chapter: "Making it soda", title: "And the coil's",
      body: "The other reads the coil, for the freeze cutout.",
      parts: ["cold-core/probe-coil-ds18s20"], hold: true, drift: ORBIT },

    // ── Knowing the level ───────────────────────────────────────────────────
    { chapter: "Knowing the level", title: "A magnet on the water",
      body: "A float rides inside, at whatever height the water is.",
      parts: ["cold-core/float-carb"],
      dir: [0.55, -1.0, 0.25], pad: 2.0, drift: { az: 8, el: 2, dolly: -0.05 } },
    { chapter: "Knowing the level", title: "On a rod",
      body: "A 316L rod running the vessel's full height.",
      parts: ["cold-core/float-rod-carb"], hold: true, drift: BACK },
    { chapter: "Knowing the level", title: "Seen through the wall",
      body: "Two reed switches outside catch the magnet, so nothing pierces the vessel.",
      parts: ["cold-core/reed-carb-1", "cold-core/reed-carb-2"], hold: true, drift: BACK },
    { chapter: "Knowing the level", title: "The last word on pressure",
      body: "A relief valve, on a port of its own in the top cap.",
      parts: ["cold-core/prv-sv125"],
      dir: [0.4, -1.0, 0.5], pad: 2.0, drift: { az: 9, el: 3, dolly: -0.05 } },
    { chapter: "Knowing the level", title: "Kept clear of the foam",
      body: "A printed cup holds the air cavity the valve needs to pop.",
      parts: ["cold-core/prv-shroud"], hold: true, drift: BACK },

    // ── Out of the bottom ───────────────────────────────────────────────────
    { chapter: "Out of the bottom", title: "Soda leaves here", hue: "soda",
      body: "At the floor of the vessel, where it is coldest and least disturbed.",
      parts: ["cold-core/carbonator-elbow-carb-water-out"],
      dir: [0.5, -0.95, 0.12], pad: 2.1, drift: { az: 7, el: 4, dolly: -0.05 } },
    { chapter: "Out of the bottom", title: "Into a collet",
      body: "The same quarter-inch push-fit as everywhere else on this path.",
      parts: ["cold-core/collet-carb-water-out"], hold: true, drift: FALL },
    { chapter: "Out of the bottom", title: "And up through the cap",
      body: "The line climbs out of the foam the way it came in.",
      parts: ["cold-core/line-carb-water-out"], hold: true, drift: FALL },

    // ── Up and out ──────────────────────────────────────────────────────────
    { chapter: "Up and out", title: "The climb",
      body: "Back in the cabinet, 279 mm up the corridor.",
      parts: ["tube-carb-1"], isolate: null, vertigo: 45,
      dir: [-0.7, -0.75, 0.4], pad: 1.7, drift: { az: 10, el: 2, dolly: -0.06 } },
    { chapter: "Up and out", title: "Every pour passes here",
      body: "A flow sensor, in the line and not beside it.",
      parts: ["digiten-flow"],
      dir: [-0.55, -0.5, 0.55], pad: 2.1, drift: { az: 8, el: 2, dolly: -0.06 } },
    { chapter: "Up and out", title: "What its pulses start",
      body: "They tell the machine a glass is filling, and start the flavor pumps.",
      parts: ["digiten-flow"], hold: true, drift: PUSH },
    { chapter: "Up and out", title: "Twenty-two millimetres",
      body: "All that is left between the sensor and the wall.",
      parts: ["tube-carb-2"], hold: true, drift: PUSH },
    { chapter: "Up and out", title: "Out",
      body: "Through a bulkhead one row above the deck.",
      parts: ["bulkhead-carb"], hold: true, drift: PUSH },
    { chapter: "Up and out", title: "Blue",
      body: "This ring matches the soda tube in the umbilical.",
      parts: ["bulkhead-ring-carb"], hold: true, drift: PUSH },
    { chapter: "Up and out", title: "SODA",
      body: "And its word, so there is no doubt which of the three this is.",
      parts: ["bulkhead-ring-carb-word"], hold: true, drift: PUSH },

    // ── The whole path ──────────────────────────────────────────────────────
    { chapter: "The whole path", title: "Two connections, one line",
      body: "Rear wall to rear wall, through a pump and a pressure vessel.",
      overview: true, focus: ["*"],
      parts: ["tube-customer-water", "bulkhead-water", "asse1022-assembly", "tube-water-2",
              "water-split", "tube-water-3", "vk-solenoid", "suction-chain", "tube-water-7",
              "seaflo-pump", "tube-water-6", "discharge-chain", "tube-water-5",
              "tube-carb-1", "digiten-flow", "tube-carb-2", "bulkhead-carb"],
      dir: [-0.95, -1.0, 0.45], pad: 1.15, dwell: 9000, ignite: 130, quiet: 0.4,
      flow: 120, bare: true, drift: { az: 20, el: 4, dolly: -0.04 }, enter: 4200 },
  ],
};
