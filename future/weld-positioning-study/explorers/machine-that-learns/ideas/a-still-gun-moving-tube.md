# A — Still gun, moving tube: every software motion is on the work side

## Picture it

**Frame.** One 2040/4040 extrusion frame on the bench carries two things: a
fixed portal over the station, and a stack under the tube.

**The portal — nothing on it moves.** It holds:
- the gun in its scanned shell, on a kinematic seat under a printed pose block;
- the joint camera;
- a swivel saddle for the umbilical and wire conduit.

**The stack under the tube — this is what moves.**
- The existing rotator, unchanged (θ).
- A radial X ball-screw stage under it. This is the first new motor: it finds
  the corner, follows runout, and retracts ~50 mm to change tubes.
- A Z bed under that, lifted by three belt-linked screws: standoff and face
  runout.

**What carries and what locates.** Angles are set by pose blocks, or by a
work-side tilt branch. Gravity carries the stack down onto its screws; the
gun's loads never change. "Fixed" is the extrusion frame, so the wooden bench
is out of the loop. The dot sits ~400 mm above the bench.

Sketches: [`../sketches/a-still-gun-side.svg`](../sketches/a-still-gun-side.svg),
[`../sketches/a-still-gun-front.svg`](../sketches/a-still-gun-front.svg).

**Major unresolved:**
- The tube's thermal growth during a weld is invisible to dry runs. The stylus
  or post-weld bead photos can capture it.
- A 6–7 kg stack on a printer-style Z bed: any rock is 5.6 mm per degree at the
  dot.
- The raised working height (~1.1 m on a 28 in bench).
- The rotator's firmware needs a dry-run mode.

---

Sketches: [`../sketches/a-still-gun-side.svg`](../sketches/a-still-gun-side.svg),
[`../sketches/a-still-gun-front.svg`](../sketches/a-still-gun-front.svg).
Numbers: [`../calc/arrangement_numbers.py`](../calc/arrangement_numbers.py),
[`../calc/tube_change_clearance.py`](../calc/tube_change_clearance.py).
Grows out of [`d-watch-first-seat.md`](d-watch-first-seat.md); cameras and
control in [`observation-layer.md`](observation-layer.md).

## The idea

The three things with the worst motion constraints — the fiber (35 cm bend
radius while emitting, no twist), the wire (its straightness sets where the tip
points), and the camera that measures the dot — never move. The gun sits in its
scanned shell on a kinematic seat under a printed pose block on a fixed portal.
Everything software moves is **under the tube**: the existing rotator (θ),
unchanged, rides on a radial X stage, which rides on a Z bed. The station is one
2040/4040 extrusion frame carrying both the portal and the tube stack, so the
wooden bench top is no longer in the loop between gun and tube.

Motion is added in the order the learning needs it:

1. **θ** — exists. Needs a software-driven mode for dry runs (see observation layer).
2. **X, radial** — the first new motor. Finds the corner, follows runout, sweeps
   the dot across the joint for experiments, and retracts the tube for a change.
3. **Z** — second. Standoff/defocus experiments and face-runout following.
4. **Work-angle tilt** — third, as a branch (below). Until then, angles are pose
   blocks.

Plan angle never needs a joint here or anywhere: turning the gun about the
vertical line through the dot is *exactly* a sideways translation of the gun by
2R·sin(ψ/2), because the joint is a circle (checked numerically in `calc`,
section 1: −15° equals a 16.1 mm move with a 2.1 mm radial correction, identical
for every point of the gun). A fixed gun's plan angle is chosen once by where
its pose block puts it along Y; a 0.1 mm Y error is a 0.09° plan-angle error.

## Geometry (proposal)

- Frame: 2040 ladder on the bench; portal of 4040 posts at y ≈ +210 and −330 mm
  from the dot, crossbar ~270 mm above the dot, carrying the pose block, the
  joint camera, and the umbilical's swivel saddle on the rear post.
- Tube stack: Z bed (~15 mm plate on three belt-linked T8 screws, the way
  printer beds are lifted) → double-rail SFU1605 stage (ZBX150 class, 100 mm
  stroke, ~65 mm tall assumed) → 10 mm adapter plate → the rotator on its own
  24 mm feet (keeping the lower-port purge path it was designed with) → tube.
- The dot rises from 232 mm to about 400 mm above the bench. On a VEVOR bench at
  its 28 in minimum that puts the dot ~1.1 m above the floor, a standing working
  height. At 39.5 in it would be ~1.4 m — too high to load comfortably.
- Rotator orientation: motor tower toward +Y (away from the gun), ground tower
  under the gun side (it is 91 mm tall; the lowest gun part near the tube is the
  nozzle, 11 mm above the dot).

Moving mass, estimated: rotator ~3.5 kg (PET-GF base and turntable, NEMA 23,
towers), tube 1.40/2.01 kg, adapter ~1 kg: 6–7 kg. The listed ZBX150 carries
120 kg horizontally; the single-rail SFU1605 stage 30 kg.

## How it is used

- **Tube change:** Z down 10 mm (the rim is only ~5 mm below the nozzle tip),
  then X toward −X. After ~50 mm the whole gun proxy is outside the tube's plan
  footprint (`tube_change_clearance.py`: closest gun point 67.7 mm from the tube
  axis at 50 mm, vs the 63.5 mm OD), so the tube lifts straight out. Load the
  next, press "return": the stage comes back and the camera re-finds the corner
  before anything else happens.
- **Dry run:** software turns the table with the laser disabled, scans X across
  the corner at a few angles, builds the runout map, then replays X(θ) and Z(θ)
  for a verification lap. Hours of this across tubes need nobody present.
- **Weld:** pedal (deadman) + trigger (hand, or the Bowden pedal) as today. While
  the pedal turns the table, X and Z follow the stored map. Release trigger,
  then pedal; following stops with the table.
- **Stuck wire:** nothing may move — moving the tube would bend or drag the wire.
  Software holds all axes after a pedal release until the operator confirms the
  snip (a button). The gun, being fixed, is already where the procedure wants it.
- **Second closure:** same; the 2.01 kg vessel with the float inside rides the
  same stack. The purge hose leaves sideways under the rotator base within the
  24 mm foot clearance, as it must today, and needs slack for the X travel.
- **Second person:** loads tubes and presses pedals. The pose is the pose block;
  the dot placement is the machine's.

## What I tried to break

**Runout following with one axis.** Eccentricity of the tube about the table
axis moves the corner at the dot radially (X) and along the tangent (Y). The Y
part only slides the joint along itself, so X alone cancels eccentricity. Face
runout or a tilted tube adds a once-per-rev vertical motion at the dot (±0.15 mm
at the procedure limit) — that needs Z. The follow speeds are tiny (10–30 µm/s
peak at 5–15 mm/s travel), so even a host loop at 10 Hz reading the table angle
is enough; no tight coordination is needed.

**Thermal growth during the weld is invisible to a dry run.** 316L at
~16 µm/m·K: a 100 K rise in the tube near the joint grows its radius by ~0.1 mm
(rough estimate) — comparable to the runout being cancelled. The dry-run map
cannot know it. **Repair options, none established:** learn it from welds
(photograph the bead after each weld and fit its offset from the corner against
θ, then fold that into the next map); or watch the corner ahead of the puddle
during the weld with a shade-filtered camera or a 650 nm stripe (seam tracking).
The first needs no new hardware.

**Moving the rotator moves its cables.** The NEMA 23 cable, pedal lead, work
lead (heavy) clamped on the copper shoe, and purge hose all ride with the stack
through ~60 mm of X. A slack loop or small drag chain; the heavy work lead needs
its own strain relief to the frame so its weight does not load the stage
sideways. Not a precision problem at µm/s.

**Stiffness of the fixed gun.** The only moving thing near the gun is the tube;
the gun's loads are constant (its weight, the umbilical's static pull at the
saddle). Constant loads give constant deflection — calibrated away once. The
remaining risk is **creep** of the printed pose block under that constant
moment; the overnight drift experiment measures it; the repair is an aluminium
drop with a thin printed angle wedge.

**The Z bed on three screws.** Printer beds lifted on three belt-linked screws
are stiff enough for printing, but this bed carries 6–7 kg ~320 mm below the dot,
and any rocking of the bed tilts the tube and moves the dot by 5.6 mm per degree
(`calc`, section 5). The screws need rails to take the moment (as printer beds
have); the camera can measure bed rock by pushing on the rotator. If Z is left
manual at first (three fine-thread feet set once), stage 2 needs only X.

**Heavy stack, small motions.** Everything moving is 6–7 kg to position to tens
of microns. Ball screws with 5 mm lead and 1/16 microstepping give 1.6 µm steps;
the listed ±0.03 mm repeatability is the stage's own claim. What matters is
repeatability relative to the corner, which the camera measures every lap.

## Branch A-tilt: work angle on the tube side

Keeping the gun still means angles must come from the tube if they are to be
software-controlled.

- **A-tilt-1, differential Z.** Three independently driven bed screws (printer
  "Z tilt" hardware) tilt the whole stack about a pivot ~320 mm below the dot:
  5.6 mm of dot displacement per degree, re-centred by X (and a small Z). With
  ~50 mm of X to spare, about ±5° of work-angle trim. Cheap, but the pivot is a
  number, not a bearing, and every tilt also tilts the puddle off downhand.
- **A-tilt-2, trunnion through the dot.** The whole stack sits in a cradle
  pivoting on two pillow blocks (UCP205, $20.25/pair Prime) whose axis is the
  tangent line through the dot, at the dot's height, outside the rotator's
  footprint (y ≈ −260 and +300). Tilting about that line changes the work angle
  and the dot stays on the corner mechanically, because every point on that line
  is fixed. Cradle ~12–15 kg with its centre of mass ~250 mm below the axis: a
  pendulum, restoring ~6 N·m at 10°, held by a worm (a NEMA 17 on a 40:1 worm
  gearbox gives ~16 N·m). The gun portal must straddle the cradle. The trunnion
  axis has to pass through the dot within the tolerance of interest — set once by
  observing that tilting the cradle does not move the red dot on the cap.

Both change gravity on the puddle by the tilt angle. Whether a few degrees off
downhand matters is itself an experiment this station can run.

## Parts

Printed: shell, seat, pose blocks, camera hood/mounts, index ring, adapter
details, cable saddle, cable-chain links. Bought (sourcing file): ZBX150-class
or SFU1605 stage, three NEMA 17 T8 screws or one motor + belt loop for the bed,
2040/4040 extrusion, Octopus Pro, closed-loop board for X, balls/pins/magnets,
second camera, red filter. Existing rotator unchanged.

## Contribution, open problems, assumptions

Contribution: the cable-and-wire problem disappears from the moving system; the
first new motor (X) already delivers corner-finding, runout following and
automated tube changes; the camera stays registered to the gun, so the dot is
always at the same pixel and only the corner moves in the image.

Open: thermal growth during the weld; whether a 6–7 kg stack on a printer-style
Z is rigid enough; the raised working height; that angles are either slow (pose
blocks) or come with tilting the puddle (A-tilt). The rotator firmware's
pedal-only control needs a dry-run mode (a later firmware/procedure decision).

Rests on: the scene proxy for the gun's shape and pose; estimated masses; listing
specifications for the stages.

---

## Wave 3 — notes from the exchanges

- **The work lead and purge hose ride the X stage** (carry-and-locate). Their
  weight side-loads the stage by a different amount at each X. Hang the work
  lead from above on a light spring balancer, the same way the umbilical is
  carried, so the stage sees only the constant part.
- **Per-tube height** (OnlineMetals' ±3.2 mm cut tolerance, raised by
  work-as-datum and workspace-as-structure). With the Z bed motorised, the
  camera measures the corner height on the first dry lap of each tube and Z
  moves to it. Alternatively, work-as-datum's centre plunger on the plate's
  port seat gives a mechanical reference for Z to drive against. E develops
  both.
- **Weld-time radial reference.** The D-s stylus from my exchange
  (`exchange/machine-that-learns--on--carry-and-locate.md` §3) stands on the
  portal, touches the tube's OD at the dot's angle, and drives X during the
  weld when the camera cannot see the dot.
- **Gravity keeps A's drives one-signed** (carry-and-locate agrees): the Z bed
  always carries the stack downward, and the gun's loads are constant.
