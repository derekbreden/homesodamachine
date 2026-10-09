# sequence-of-use on borrowed-ecosystems (wave 4): E, film-grip carrier

Their idea: `explorers/borrowed-ecosystems/ideas/e-film-grip-carrier.md`. A
Steadicam-type iso-elastic arm on a stainless C-stand carries the gun through a
printed yoke gimbal at the centre of mass. The umbilical and conduit ride a saddle
on the stand's boom. The arm only carries; the A1-S tube rider (or A2's dock)
locates.

I walked it through a whole session. Numbers are in
`explorers/sequence-of-use/calc/w4_calcs.py`, at the true opening pose (hole dial
30), on my proxy. The sketch is
`explorers/sequence-of-use/sketches/w4-film-grip-session.svg`.

## What E does that my arrangements lack

- **A carrier with no horizontal return and no moments.** My monitor-arm session
  (idea E, "carry, park, dock") has friction swivels and a gas spring whose force
  shifts with height. Their arm is the better carrier for my HAND state. I adopt it
  as a branch of mine.
- **Carrier and cable support on one mobile stand.** Rolling the stand away moves
  the saddle with the gun, so the gun-to-saddle span keeps one shape in PARK as well
  as at the dock. That is my umbilical rule (session kit K6) in its best form.
- **Published payload windows,** and a named failure mode (bounce), which is benign
  on a static station.

## Difficulty 1 — the gimbal's attitude during transitions is set by the umbilical, not by pendulosity

*Variant:* E with the A1-S rider, the CG 2–5 mm below the trunnions, and the saddle
0.3–0.5 m back on −Y.

*Assumption:* "the lifted gun hangs near its working attitude". Their restoring
torque is 0.9–2 N·mm per degree, and they call it "too small to matter once the
rider holds the pose". That holds *on* the rider. The question is the moments when
the rider is *not* holding: lift-off, park, carry, set-down.

*Numbers* (`w4_calcs.py` §1): the cable exit is 129 mm from the CG (proxy). A
slack span pulling 1–5 N at the exit gives 130–640 N·mm about the CG.

| CG below pivots | Restoring per degree | 1 N cable pull tips it | 5 N cable pull tips it |
|---|---|---|---|
| 2 mm | 0.86 N·mm/° | over (flips) | over |
| 5 mm | 2.1 N·mm/° | over | over |
| 20 mm | 8.6 N·mm/° | 15° | over |
| 60 mm | 26 N·mm/° | 5° | 26° |
| 100 mm | 43 N·mm/° | 3° | 15° |

With the design's 2–5 mm, the lifted gun takes whatever attitude the cable's
catenary gives it.

*Where that bites in the session:*

- **Set-down.** The rider's V-wheels and OD wheels capture only a few mm and a few
  degrees. The wire tip is the gun's lowest point, and it reaches the lip first.
- **Lift-off.** Once the rider is off, the gun swings nozzle-first.
- **Park.** The gimbal sits in the docking cup, but the gun still swings in it.

In hand welding (E-H) none of this matters, because the hand holds the gun.

*Repair — carry pins (branch E-s).*

- **Pins:** two spring index plungers (M8 pull-ring type, Prime) in the yoke lock
  the gimbal's two non-vertical axes at the recipe attitude. The vertical (heading)
  bearing stays free, so the hand still aims the heading, and the rider's OD pair
  captures it.
- **When they are in:** the pins go IN whenever the gun is off the tube, and come
  OUT only after the rider has landed and its Z is at the weld stop.
- **What that changes:** carried with pins in, the gun is a rigid body at the recipe
  attitude, so set-down becomes a translation plus a heading.
- **Recipe changes:** the plunger holes are in a printed indexing ring clamped on
  each trunnion, so a recipe change is a new ring — the same idea as the printed
  recipe blocks.
- **Pulling a pin while seated:** the pull runs along the pin's own axis, through
  the pivots, so it puts no torque on the seated gun.
- *Leaves:* pin clearance (±0.3° of attitude play, well inside the rider's capture)
  and the order of operations. The pins' coloured rings make the state visible.

*Branch E-p (no pins):* raise the pendulosity to 60–100 mm. The gun then hangs
nearly plumb (3–5° under a 1 N pull), and on the rider it passes 26–43 N·mm per
degree of misalignment. With contacts 60–100 mm apart that is ~0.3–0.7 N of contact
change, against 5–10 N of preload: acceptable. It does not survive a 5 N cable
pull (15–26°), and it gives up the design's moment-free property. It is kept as the
lighter option, and it combines with the pins.

## Difficulty 2 — landing the rider and putting the wire in the corner are one event

*Variant:* "Swing the gun over the tube and set the rider down … one hand and
slow", on a 1–2 Hz undamped spring.

*Assumption:* the rider arrives at its weld pose. The rider holds the gun at the
weld pose, so the wire tip reaches the corner at the same instant the wheels touch
the rim. A hop then lands the wire on the plate or the lip, and a 1 mm-long stickout
bends it.

*Repair — two hard stops on the rider's Z (branch E-z).* The A1-G knob set already
has a Z along the barrel line (their lift-off note uses it). Give it two stops,
worked by a cam lever:

- **LAND:** the gun sits ~10 mm back along the barrel, with the wire tip clear of
  the rim.
- **WELD:** the recipe stop.

The session order becomes:

1. Pins in, Z at LAND.
2. Set down. The bounce now only hops wheels on cold rim and OD; their damper
   settles it.
3. Z to WELD.
4. Pins out.
5. Jog the wire to touch, then run the dry lap.

Lift-off is the reverse. Z to LAND first moves the tip up and inward along the
barrel, which is the wire-escape rule. Then pins in, then lift.

A stop instead of a screw count also makes the Z a recipe *position* a second
person cannot mis-set.

## Difficulty 3 — tacks, with a rider on the rim

*Variant:* the rider's rim V-wheels sit at ±60° on the rim edge. The plate needs
holding at its 6.35 mm recess, and the eight tacks need the table indexed between
them.

*Assumption:* E is silent on phases 3–6. A rim-bridge hanger — the obvious way to
hold the plate — has feet on the rim, and they run into the ±60° wheels as the
table indexes. E-H hand tacking avoids that only if the rider comes off the shell.

*Repair:* the stand-hung plate head from my wave-2/3 exchange with who-moves-what.

- **Geometry:** pads inside the tube at 45° / 150° / 255°, r = 40 mm, frame 15 mm
  above the rim, arm over the −X rim. The rider occupies ±30…±75° around the station,
  outside the OD, so the two never meet.
- **Tacks:** with the rider seated and pins out, tacks become eight short trigger
  pulses at indexed table angles, as repeatable as the bead.
- **If hand tacks are preferred:** make the rider detachable from the shell stage
  (a small kinematic plate). E-H then tacks with a rim bridge, and the rider goes on
  afterwards.

## Difficulty 4 — stuck wire with a gun that yields

*Variant:* "the tube drags wire, gun and rider along the rim … the tether's
breakaway opens the pedal line".

This is gentler on the gun than a latched dock (mine), and I take the pedal-loop
contact. It is a series contact in the pedal's `COM`–`NO` loop — a rotation stop,
not a laser command, so it is consistent with the rig's rules; still, it is a rig
change and Derek's call.

The sequence has to follow it:

- The gun ends up tens of mm round the rim, with the wire kinked between the nozzle
  and the bead.
- Snip.
- Slide the rider back along the rim to the station (it rolls) and re-seat the
  tether.
- Re-trim the stickout: feed past the kink and cut at a stickout gauge. Put that
  gauge in the docking cup on the stand, with a nozzle cap, so PARK always ends
  with a known stickout.

## The session, as repaired

| Phase | Pins | Rider Z | Who locates | Wire tip |
|---|---|---|---|---|
| Park (cup) | IN | LAND | cup | in the cup's gauge |
| Lift out, carry | IN | LAND | the hand (heading only) | clear |
| Set down | IN | LAND | rider wheels | ~10 mm back |
| Z to WELD | IN | WELD | rider | 1 mm short |
| Pins out | OUT | WELD | rider | jog to touch |
| Tacks (plate head), dry run, weld | OUT | WELD | rider | in the corner / feeding |
| Stuck wire | OUT | WELD | rider + tether | snip |
| Lift-off | IN after Z to LAND | LAND | the hand | leaves up and inward |
| Park, roll the stand away | IN | LAND | cup | re-trim |

**Second person:** the pins' coloured rings and the Z lever show the state. The
recipe is the arm-tension count, the indexing-ring ID and the WELD-stop ID. Floor
marks place the stand.

## What transfers back to me

- Their carrier replaces my monitor arm in my idea E as branch **E-f**. It fixes my
  E4 (creep, friction band) outright.
- My E1 repair (a friction brake on the bail) becomes **carry pins**: a discrete
  attitude, not a friction setting.
- Their rider in place of my dock gives a carry-pins + rider + plate-head station:
  no per-tube height dial at all, because the rider references the rim.

## Left open

- The real umbilical pull at the exit, which decides whether E-p alone is enough.
- The yoke's clearance for plunger rings on the real scan.
- Whether a cam-lever Z with two stops fits inside A1-G's knob stack.
