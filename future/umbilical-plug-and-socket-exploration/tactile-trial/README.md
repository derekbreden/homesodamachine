# Optional umbilical tactile trial

This trial answers whether the plug size, guidance, exposed grip, snap frame and actual
bundle transition feel worthwhile. It is prepared for **Mark1 (H2C), left 0.4 mm nozzle,
black PET-GF, +0.18 mm user trim**. Nothing has been sent to a printer.

Its plug is the 52 mm coupling article. The [guided boot trial](../guided-boot-trial/README.md)
provides the 98 mm blue boot and matching key for curved tube-feed, foam and fabric tests.
Use this plate's socket, wall coupon and counter ring as its mating fixtures; its plug
and key are separate articles.

| File | Contents |
| --- | --- |
| [Editable project](tactile-mark1-z018.3mf) | Six parts with reviewed placement and settings |
| [Native sliced archive](tactile-mark1-z018.gcode.3mf) | Estimated 3 h 59 min, 138.05 g at the saved filament density |
| [Print record](tactile-mark1-z018.print.json) | Source hashes, embedded mesh fidelity, geometry, settings and emitted toolpaths |

The socket and plug have **filled magnet pockets**. They need no SB443-IN magnets or pause,
and cannot receive those magnets later without replacement prints. The retainer, tube key
and 6 mm wall coupon use the saved coupling geometry in `umbilical.py`. The sixth part is a simple
50 mm outside-diameter ring with a 34.93 mm bore through 30 mm, representing the counter hole.
Printable meshes are in [parts/](parts/).

The native slice has zero supports and zero pause commands, four walls and 25% grid infill,
0.20 mm first layer and 0.24 mm normal layers. Textured-PEI G-code clears trim then emits
`G29.1 Z0.16`. The complete layer-bead envelope is at least **84.64 mm** inside the usable
bed boundary. These checks establish the prepared job; physical fit and roof quality await a print.

## Materials and scope

Use the printed parts, three approximately 300 mm 1/4-inch offcuts from existing stock,
soda-tube foam, braid, display cable, marker, ruler and removable tape. Use the already
ordered 4 mm tube when available; leaving that
lane empty limits the bundle observation. Existing pogo halves can be fitted to inspect
cable routing, but they are optional for the initial plastic fit. Keep this trial unpowered
and unpressurized.

The full magnetic engagement/removal force, missing 4 mm union, four-line seating, sealing,
electrical operation and life are outside this trial. A pleasant loose plug fit alone is not
functional acceptance.

## Bench procedure and decisions

1. Inspect the receiver roofs, cup, tube bores and snap leaves. Remove loose strings and
   ordinary bed brim; do not force a fused opening or cracked leaf. Mark TOP on both halves
   with a pen so orientation is obvious during the initial trial.
2. Support the wall coupon by hand or against a bench fixture with its opening unobstructed.
   Push the socket into it from the flange side. The flange should sit against its stepped
   ledge and both leaves should catch, without a crack or an unseated edge. Rock it gently
   as it would be handled; report visible looseness or a leaf that releases. This answers
   whether the proposed local receiver and snap are practical.
3. Slide the bare plug into the socket while holding the coupon. Try several natural
   approaches. Assess whether it guides itself, binds, needs careful visual aiming, and
   leaves enough grip to withdraw: only 18 mm of its 52 mm body remains outside the 34 mm
   cup when seated. With no magnet bars, this does not reproduce final holding force.
4. Feed the real tubes through the plug, preserving their identities. For a tube-guidance
   trial without unions, use the drawn 25.8 mm quarter-inch and 22.8 mm drain projections.
   These are mockup dimensions, not sealing specifications. Fit the key from the drain
   side using hand pressure and mark the tubes at the rear face. Stop if the key requires
   abusive force, visibly crushes a tube or scores it. Insert the tube-bearing plug and
   verify that the correct orientation guides the stubs while an inverted plug stops
   before seating. Do not force the wrong orientation.
5. First bring the soda foam against the plug's rear face and gather the smaller tubes
   and display cable into the braid. Deliberately compress the foam as the intended boot
   would. Temporarily hold the braid with removable tape for handling; this attachment is
   not the finished strain relief. Try passing the complete plug and bundle through the
   counter ring. Comfortable hand passage with foam compression is useful evidence.
   Identify any tube flattening, cable pinch, displaced tube mark, difficult catch or
   persistent foam damage. Do not peel off insulation or remove the key to make it pass.
6. If direct packing is awkward, compare the [alternative compact packing](../assessment/bundle-study.png):
   leave approximately 65 mm behind the plug before the foam starts, keep soda straight,
   and gather both flavors along one side of the foam with the drain between them.
   Route the cable without pulling its connector tails. Compare counter-ring passage,
   neck feel and grip with the direct compressed arrangement. Favor the simplest arrangement
   that passes comfortably while preserving tube shape and positions. The ring represents
   a 30 mm counter; actual thickness and edge condition can differ.
7. Repeat ordinary handling and inspect the rear-face tube marks. Any moved projection,
   visible tube damage, an awkward grip or a transition requiring individual-line adjustment
   is a reason to revise or stop this concept before buying its missing hardware.

Optional existing 1/4-inch unions can give a partial dry feel only when fitted with the actual
retainer and its two M3 screws/inserts. The quarter-inch nominal full-stop projection is
26.3 mm; follow the real union's insertion depth rather than treating the mockup projection
as seated. Machine-side tubes must remain free to accommodate union movement. This partial
exercise does not establish all-four-line force, release or a pressure-ready assembly.

No measurement tool purchase is needed. A short description or photo of what catches,
binds or moves is enough to choose the next design step. These acceptance observations
come directly from guided connection, preserved tube position and the existing counter hole;
they are not endurance or load-capacity criteria.

## Preparation

```sh
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/assessment/prepare_tactile_trial.py
```

The script writes and slices the job, checks this trial's emitted settings and bead envelope,
and never launches a printer. Read the [engineering assessment](../assessment/README.md)
before interpreting the result as a reason to fund further connector development.
