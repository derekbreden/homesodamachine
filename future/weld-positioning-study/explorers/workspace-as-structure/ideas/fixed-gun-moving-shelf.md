# Gun as structure, work moves: a fixed pose saddle above, XY + Z under the rotator

## Picture it

- **The gun is structure.** Its shell is bolted in a pose saddle on a rigid
  bridge on the collar. Gun, wire conduit and umbilical never move.
- **The work moves.** Below the opening, a compound cross-slide sits between
  the four-post shelf and the rotator: a cast-iron VEVOR table, or a printed
  MGN12 stage.
  - X moves the tube across the seam.
  - Y moves it along the tangent, which is the plan angle (0.93° per mm).
  - The shelf gives Z.
  - Runout can be followed by moving the rotator in X.
- **"Fixed" is fixed to:** the collar (bridge and shelf posts).
- **The opening** is Ø200 to leave room for the travel.

**Sketch:** `../sketches/fixed-gun-moving-shelf.svg` (includes the
tangent-slide geometry).

**Major unresolved problems:**

- Angles are fixed per saddle.
- Dovetail backlash and gibs.
- It conflicts on X with the collar centre (T-W1).
- The space under the bench top.


Sketch: `../sketches/fixed-gun-moving-shelf.svg` (elevation, plus the
tangent-slide geometry).

## The idea, and what it changes in Derek's table branch

Same opening, same four-corner shelf underneath, same fitted shell — but the
gantry above is replaced by a rigid **bridge** bolted to the collar, holding the
shell in a pose saddle that does not move. All adjustment goes below the
opening: the shelf carries a **compound cross-slide** (X across the seam, Y
along the tangent) under the rotator, and the four synced screws give Z.

Derek's branch has "something above the hole that moves the gun in X and Y";
this is its mirror: the gun becomes part of the workspace and the workspace
moves the work. Kept as a branch beside the original, not as a replacement.

## Why moving the work suits the tangent pose

- **The gun's cables never move.** The umbilical (35 cm minimum bend while
  emitting, no twisting) and the wire conduit are clamped to the bridge right
  behind the grip and never flex during setup or welding. The wire's final
  approach, which Derek ties to the gun staying tangent, is fixed in space.
  What moves instead — the rotator's motor and pedal leads, the ground lead
  from the copper shoe, the purge hose — tolerates motion.
- **Y is the vertical-axis control.** Sliding the work dy along the tangent
  under a fixed gun lands the dot where the local tangent is rotated
  atan(dy/R) = 0.93°/mm from the gun's line; a dx = dy²/2R correction puts the
  dot back in the corner (see the sketch's right panel). So the cross-slide's
  two handwheels give across-seam position and the vertical-axis angle; the
  shelf gives height. The remaining two angles (grip roll, hole axis) are fixed
  by the saddle.
- **Runout compensation is natural.** If the tube's weld end runs 0.25 mm TIR,
  the corner wanders ±0.125 mm across the seam once per revolution (48.6 s at
  8 mm/s). Moving the whole rotator in X by the opposite amount cancels it at
  the dot — a 0.02 Hz sinusoid, slow enough for a stepper on the X handwheel
  driven from the console's degree count or a camera. The same applies to face
  runout through Z. A moving gun would have to do this while dragging its
  cables.

## One representative build

- **Cross-slide:** a cast-iron compound milling table (VEVOR 2-axis table,
  17.7 × 6.7 in, X travel 210 mm, Y 110 mm, trapezoidal screws with scales,
  $135.90, Prime, 50+ bought/month, observed 2026-09-28) or the lighter
  aluminium MYSWEETY 6350 (X 180, Y 50 mm, 3 mm per handwheel turn, $95.99,
  Prime, 1,068 ratings). The rotator bolts to the cross-slide table through
  its four Ø10 clamp holes (on an adapter plate for the 300 × 250 base).
  Printed alternative: two MGN12 rails at right angles with Tr8×2 screws and
  dial knobs.
- **Z:** the four-post shelf from `table-opening-gantry.md`, hanging lower by
  the slide's height (~70–100 mm).
- **Bridge + saddle:** aluminium square tube or steel, bolted to the collar
  (`drop-in-collar.md`). The saddle is the printed pose block; for a family of
  poses, the saddle is swapped.
- **Opening:** larger, by the travel: Ø200 for ±20 mm of X/Y with clearance.

## How it is used

- **Setup:** saddle on, gun in shell, cables clamped. Reference dot on; turn X
  and Y handwheels and the Z crank until the dot sits in the corner. Record the
  three dial numbers and the saddle name.
- **Tube change:** crank Z down ~70 mm, slide the tube out through the box's
  open face, reverse. The cross-slide stays where it is; the gun never moves.
- **Different pose angle:** swap saddle; the dot will be somewhere else; find it
  again with X/Y/Z (three handwheels, fast).

## Breaking it

1. **Mass on the moving stage.** Rotator + tube ~8–10 kg plus a cast-iron table
   ~15 kg on a hanging shelf: fine for four aluminium posts in tension/shear
   (~2,900 N/mm sideways for 1 in × 1/8 in tubes); the lead screws should only
   lift. Handwheel effort is small because the dovetails carry the load.
2. **Dovetail backlash and gib friction.** Typical hobby cross-slides have
   0.05–0.2 mm backlash. For setup: approach from one direction and lock the
   gibs. For live runout following: preload the slide with a spring or a weight
   on a cord so the screw always pushes one way.
3. **The saddle fixes two angles.** An angle sweep (grip roll, hole axis) isn't
   available without a new saddle or an arc guide on the bridge. This branch is
   good at position and heading, weak at angle experiments.
4. **Moving the rotator changes where the copper shoe, motor and hoses sit
   relative to the opening.** With ±20 mm travel, nothing gets near the edge of
   a Ø200 opening except the tube; the rotator's other parts are below the top.
5. **Heavier, larger, more permanent.** A cast-iron cross-slide under the table
   is not a quick build; the printed MGN version is.
6. **Metrology:** the rotation axis now moves relative to the collar. Indicate
   runout relative to the collar (bore lip from above) rather than relative to
   the rotator's motor — both are available.

## Contribution

- The gun, wire and umbilical never move once set: the cleanest cable
  situation of the arrangements here.
- The vertical-axis angle comes from a straight slide.
- Real-time runout following by moving the work is cheap and slow.

## Unresolved / rests on

- Angles fixed per saddle; combine with an arc guide (mechanism explorers) if
  angle sweeps matter.
- Backlash and gib behaviour of the specific cross-slide — unmeasured.
- Space under the VEVOR top for shelf + cross-slide + rotator (~340 mm below the
  top surface) [Derek to look].

---

## Wave 3 note (from work-as-datum's exchange)

**The conflict.** If work-as-datum's collar centre (T-W1) is fitted, the plate
centre is forced onto the collar's plunger axis. Moving the rotator in X to
follow runout then fights that centre. The two are alternatives on the same
axis.

**Choosing between them:**

- **W1 for the bulk:** length and runout, passively.
- **A slow X correction for the last ±0.1–0.2 mm** (the plate-edge vs
  port-pair residual the camera sees). It belongs on the plunger arm (a small
  X stage moving the centre, which moves the plate) or on the gun's X, not on
  the rotator.
- **Without W1:** live runout following by moving the work stays as developed
  above.
