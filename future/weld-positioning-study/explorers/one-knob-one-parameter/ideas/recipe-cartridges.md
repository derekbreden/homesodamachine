# Recipe cartridges: the gun's angles as printed parts on kinematic seats

**Picture it.**
- **Shell.** The gun sits in its full-length shell, which carries three 1/4 in
  steel balls: under the barrel near the body front, at the grip base, and under
  the housing back.
- **Pose block.** The balls sit in three vees on the top of a printed pose
  block. The block's three lower balls sit in dowel-pin vees on a stand plate
  outboard on the −Y side, clear of the tube, on posts to the baseplate.
- **What it fixes.** The block is generated from the recipe's hole and roll
  angles. It is the setting, and cannot drift.
- **Knobs that remain.** The dot's place (X, Z) and yaw (Y) are knobs at the
  work, set per tube with the dot camera; standoff is a micrometer on the shell.
- **Carrying and locating.** The block carries the gun's weight into the stand,
  and the six ball-vee contacts locate it. A spring clamp holds it seated.
- **Moving it.** Lifting the shell off its seats frees the gun for hand work or
  loading. Putting it back returns the pose to microns.
- **Fixed** is the stand's baseplate.
- **Branch S** (after borrowed-ecosystems): steel angle blocks under a hinged
  plate set the angle, and printing only locates.

Sketches: `../sketches/recipe-cartridge-pose.svg` (at the opening pose
45/30/−15), `../sketches/recipe-cartridge.svg` (schematic of seats and the
shelf of blocks).

**Major unresolved problems.**
- Print accuracy and creep of PET-GF blocks under point loads.
- Routing the cable through a block whose shape changes per pose.
- One print per step makes sweeps slow.
- In branch S, the hinge must pivot on the dot.

Sketch: `../sketches/recipe-cartridge.svg`. Shares the isocentre vocabulary
and the couch from `isocentric-couch-and-gantry.md`.

## The idea

A knob can drift, be bumped, be misread, or be set from the wrong side. A
printed part cannot. So the gun-side angles (hole and roll) are not knobs at
all. Each recipe is a **pose block**: a rigid printed part generated from the
two angles by the same pose math as the scene, which sits on three steel
balls in three V-seats on the stand. The gun's full-length shell sits on the
block's upper seats in the same way, on three balls of its own.

- "Change one parameter" = regenerate the block with one number changed and
  print it. The script guarantees the model changed only that number. Its
  file name and commit are the record.
- "Return to baseline" = put block R0 back. A kinematic coupling re-seats to
  microns, steel on steel, and nothing on the block can have moved since last
  week.
- The dot's place (couch X, Z with the camera), the couch φ and the standoff
  micrometer stay as knobs. Those are the settings that must be re-trimmed per
  tube anyway.
- The shelf of blocks is the experiment plan: R0 baseline, R1 roll 40, R2 roll
  50, R3 "work +3°, travel held" (the three-knob combination from the
  weld-angle table, embodied in one part).

A second person cannot mis-set the gun side. They seat block R0, dial three
couch numbers, and compare the camera image with the reference.

## The two interfaces

- **Stand → block:** three V-seats, each a pair of 6 mm ground dowel pins
  pressed into the stand plate, grooves pointing at the centre (a Maxwell
  three-groove coupling). Three 1/4 in G25 balls are bonded into the block's
  underside. A single spring clamp gives a constant, light preload
  (tens of N), so the block is held rather than forced.
- **Block → shell:** the same pattern upward. The three balls are on the
  shell, spread along the gun's length. The shell also carries what the roll
  body carries in the couch version: standoff rail, wire stage, trigger lever
  and Bowden stop, and the umbilical clamp.

The shell's balls are what make the gun **removable**. Lift the shell off the
block, and the gun is free for hand work or to clear the tube for loading. Put
it back and it returns to the same pose. Loading therefore needs no retract
mechanism at all: lift the gun off, hang it on a hook, drawer the tube out.

## Trying to break it

1. **Print accuracy.** PET-GF shrinks anisotropically. After scale
   calibration, 0.1–0.3 mm over a 200 mm block is my **[estimate]**, which
   is 0.05–0.1° of angle and up to ~0.5 mm of beam miss at the isocentre.
   - *Why it is tolerable:* within one block nothing rotates, so a beam miss
     is only a translation of the dot. The couch X/Z trim absorbs it when the
     camera sets the dot place, which happens per tube anyway. The angle error
     is fixed, so it is measured once and written on the block: the Klein
     gauge on a steel pad on the shell reads elevation from gravity, and the
     camera reads the rest.
   - *What remains:* going from R0 to R1 changes the intended angle by 5° plus
     the *difference* of two print errors in the others (~0.1°). That is small
     against a 5° step, but the record should carry measured, not nominal,
     angles.
2. **Creep.** Balls bonded into PET-GF and a plastic block under a
   permanent clamp slowly relax, with humidity and heat as accelerants. The
   block is ~250 mm from the weld. *Repair:* a light, constant clamp force;
   balls bonded in epoxy seats rather than pressed; re-measure a block before
   a critical series. *Left:* no measured creep rate for PET-GF under this
   kind of point load.
3. **Sweep speed.** One print per step. With two H2Cs, perhaps 4–8 blocks a
   day for a ~200 × 120 × 120 mm part **[estimate]**.
   - For welded trials this may not be the bottleneck: each trial costs a tube
     and cap, and PT/hydro inspection.
   - For AI-run laser-dot sweeps it is the bottleneck. Blocks are the wrong
     tool for exploring and the right tool for freezing.
4. **"Just add tip/tilt screws to the block"** (an optics kinematic mount).
   Such a mount pivots about one of its seat balls, not the dot. At 200 mm from
   the dot, one degree of trim moves the dot about 3.5 mm. That brings back
   exactly the coupling the isocentre removes, so each "one-knob" trim becomes
   three adjustments. Rejected for the gun side; kept as the calibration
   mechanism for the couch table's position.
5. **Common-mode shift of the gun in its shell.** If the gun moves inside the
   shell, every block is off by the same amount. The camera sees it as a dot
   offset at the start of a session. The shell grips the gun's turned barrel
   sections as its datum, not the housing.
6. **The block is in the umbilical's way.** It sits under the shell, behind
   the grip base, where the umbilical and wire leave. The block's shape is
   generated per pose, so a cable channel is part of the generator: the
   cable leaves along the grip axis for 50 mm, then turns down.

## How it combines

- **With the couch-and-gantry station.** Blocks sit on the gantry's Z carriage
  in place of the hole table and roll bearing. That is the cheapest version
  of the station: two knobs fewer, a 4-inch table fewer, and no roll-bearing
  problem, since the captive cable never has to pass through a closed ring.
- **As the end state of exploration.** Knobs find the recipe, a block freezes
  it, and the camera confirms that block and knobs agree. The transfer to
  someone besides Derek is then a physical object plus a card of three couch
  numbers.
- **The shell's kinematic balls are worth having anyway.** Every arrangement
  benefits from a gun that can leave the station and come back to the same
  pose.

## Contribution and open problems

It makes the baseline a physical object that cannot drift, keeps the record
in git, and fits "I like printing things" exactly. Open: print accuracy and
creep of PET-GF blocks under point loads; cable routing through a
pose-dependent block; how many parameters are worth freezing versus leaving
as knobs.

## Wave-3 branch: steel sets the angle (after borrowed-ecosystems)

Their objection to the original: the printed block's own accuracy and creep
decide the angle. The machinist's answer to "an angle that cannot drift" is a
hardened angle gauge block, or a sine bar on gauge blocks.

**Branch S.** The cartridge becomes a printed carrier with steel seats, plus a
stack of hardened angle blocks under a hinged pose plate.
- Printing *locates*; steel *sets the angle*.
- Print error and creep move only position, which the couch X/Z trims per tube
  anyway.
- Bought examples: WEN 12-piece angle blocks, 1/4°–30°, $41.74; Accusize
  10-piece at ±30 arcsec, $42 (their sourcing).

**What it changes:**
- The angle record moves from a git commit to a list of blocks, e.g.
  "30° + 5° − 1/4°".
- Compound angles need two stacks at 90° (one per hinge), or the gravity sine
  arms of `isocentric-couch-and-gantry.md` R3.

**What it loses:** the one-generated-part-per-recipe elegance.

**Left uncertain:** a hinge that sits on an angle stack must pivot about an
axis through the dot, or the dot moves when the stack changes. That is the
same isocentre condition, now on the hinge. A printed hinge located by two
steel dowels on the dot's radial line (hole) or grip axis (roll) is the obvious
form, and it needs the walk test like everything else.
