# travel-04-return-seat: swing away, come back to a kinematic seat

**Picture it.** The gun in its shell is fixed to a plate with three steel balls underneath. The plate rests on a block with three V-grooves, held down by magnets and gravity, and hinges up at the back like a lid. Lift it and the nozzle rises out of the recess so a tube can be swapped or the head can leave at the end of a weld; lower it and the balls drop into the grooves and the gun is exactly where it was. Adjusting is something done occasionally to the seat's shims; returning is done every time.

Scene: `scenes/travel-04-return-seat`. Calculations: `calc/05-shuttle-clearance.mjs`, `calc/07-lift-and-slide.mjs`.

## The proposal

Split the motion into two kinds. **Return** motions (every swap, and the lift-off if the sequence has one) are given to a hinge and a kinematic seat, so the position at the work is defined by the seat's contacts, not by a motor's count. **Adjust** motions (per batch, per tube) are done by shims or stages elsewhere. The end-of-weld motion is exactly a return motion **if** the head must leave the puddle: the coordinator's shared context says the operator lifts the head straight away and the retract cycle breaks the wire in air. That sentence cites `46-the-per-weld-sequence.html`, but guide 46 and `weld-rotation-rig.md` say only to release the trigger, then the pedal, and to snip a stuck wire; use's exchange found the words *lift* and *retract* in neither. **[unknown, Derek's practice]**; everything below that depends on a lift-off is conditional on it.

Kinematic (Maxwell) couplings are the textbook way to get repeatable location: three balls in three grooves make six point contacts for six degrees of freedom. Precision-ground couplings repeat to a fraction of a micron in the literature; **[unchecked]** for printed grooves and steel balls, which will be far worse, and this study assumes no number (`sourcing/travel.md`, non-Amazon notes).

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** seated: the balls in the grooves (weight plus magnet preload) into a block on a post; swinging: the hinge ear only.
- **Establishes position:** three balls in three grooves and nothing else.
- **Free / restrained / driven:** a forked hinge that only guides (free except two constraints) while swinging; fully restrained by the seat when down; the swing is driven by a small motor or gas strut or a hand.

## What software could command, observe, what stays manual

- **Commands:** the swing (up/down). The seat is passive.
- **Observes:** each ball-to-groove contact as an electrical switch (three lines): seated or not per contact; the dot against the seam after returning, if a camera sees it.
- **Manual:** cleaning the seat; lifting and sliding the tube; shimming the seat once per batch.
- **Unresolved:** how the 5 m umbilical and the wire conduit ride the swing; magnet preload against cable pull.

## What was tried to break it

**1. The seat is an amplifier.** *Conflict:* a speck raising one ball by d tilts the plate by d over 1.5 R (R = ball circle radius); the dot is about 210-230 mm from the seat in the scene. 50 micron on a 30 mm circle is 1.1 mrad, 0.24 mm at the dot; 60 mm halves it (scene sliders). *Assumption:* the seat is at the grip, far from the dot. *Change:* place the seat close to the dot, spread the balls, clean it, and sense the contacts. A nonconductive speck shows as an open contact; a conductive one does not (no detection). *Leaves:* only a camera on the dot sees a conductive speck.

**2. The hinge fights the seat.** *Conflict:* a pin hinge plus a three-ball seat constrains the plate about eleven ways for a six-freedom body; hinge play or friction pushes the seat off its balls. *Assumption:* the hinge is a pin. *Change:* a forked hinge with a slot that only guides (drawn as the slot in the scene). *Leaves:* a slotted hinge is loose when swung; the arm needs a stop and a way to be held open.

**3. The swing is not enough on its own.** *Conflict:* with the gun seated the tube lifts about 55 mm before its rim meets the barrel; lifting the tube 12 mm and sliding it out needs the gun raised about 13 mm (illustrative pose), lifting it straight out needs about 144 mm (`calc/07`). A 12 degree swing about a hinge 262 mm away raises the nozzle about 54 mm (measured in the scene: 54.5 mm up and 1.4 mm along the tangent; an earlier version said 45): enough for lift-and-slide, not for lifting the tube out. *Assumption:* 12 mm is the lift needed to leave the nest; the nest's real guide height is **[unknown]** (pilot 4.5 mm **[repo]**). *Change:* combine with the lift-and-slide swap; or shuttle the work instead (`travel-01`). *Leaves:* the sliding path must be free of the rotator's towers (motor tower on -x, ground tower on +y in the kit's layout).

**4. The cables ride the swing.** *Conflict:* the gun is on the moving side and the fibre may not twist and needs 350 mm radius while emitting **[manual]**. *Assumption:* the umbilical hangs from the gun. *Change:* none in this scene. *Leaves:* open; `travel-08-cable-travel` (a balancer/gallows that follows the swing) is the candidate.

**Wave 3 entries, from use's exchange ("Also noticed").** **The lid is a lift, and a motor has to carry the gun's weight torque (use).** *Conflict:* the lid needs no plunge axis and no post, but a motor that lifts it supplies the gun's weight torque (1.2 kg at 230 mm is 2.7 N.m, illustrative) plus the magnets' preload; use-02's plunge along the barrel needs only the preload and a float. *Assumption behind it:* the swing motor is small. *What the change alters:* recorded; my scene's hinge line about x lifts the nozzle straight up with no radial motion: measured at a 12 degree swing, 54.5 mm up and 1.4 mm along the tangent (my text said about 45 mm; corrected in the scene and above). *What it leaves uncertain:* the cable on the swing (open in both).

**The end-of-weld lift-off is conditional (use).** *Conflict:* I had cited the head's lift-away as [repo] `46-the-per-weld-sequence.html`. *Assumption behind it:* the shared context's sentence was in the guide. *What the change alters:* the text now says the lift is unconfirmed (guide 46: release the trigger, then the pedal); everything here that depends on a lift-off is conditional on it. *What it leaves uncertain:* how Derek ends a bead.

## Branches and combinations

- **Seat between the holder and the rotator base** (so the gun returns relative to the *rotator*, not the bench): a seat that is part of the rotator's registration. Not drawn.
- **With `travel-01`:** T1 uses a shuttle with a hard stop where this uses a swing with a seat: both are return motions; the stack trims after either.
- **With `travel-02`:** the seat makes the hand stage repeatable, shrinking the medium stage's job.
- **With hand-setting only:** a seat plus a shim set can be the whole holder, with no motor, if a person swings the lid (`travel-09`/`travel-10` observation variants apply).

## Unresolved problems and questions for Derek

- Magnet size against gun mass and cable pull: weigh the gun; measure the pull at the grip.
- The nest's real lift-to-clear height; whether the ground shoe and wire feed tolerate a tube sliding out along +x.
- Whether there is an end-of-weld lift-off at all, and if so whether it is straight up or along the beam, and how far.
- Question: how does he lift the head today, and how far does it travel before the wire breaks?

## Assumptions

- Gun pose and geometry: kit proxy, **illustrative**; seat position, 30 mm ball circle, hinge line, 12 mm lift: **illustrative**. Nest pilot 4.5 mm, recess 6.35 mm: **[repo]**. Three-point tilt rule: **[derived]**. Debris values made up.

## Sourcing pointers

`sourcing/travel.md`: 8 mm G10 steel balls (9), N52 countersunk cup magnets (10), spring balancer (13), drawer slide for a linear return (7).

## Scene id

`travel-04-return-seat`

## Wave 2

The seat idea returns as the trunnion dock of `travel-14b-crown-cartridge` (two pins in two V-notches, an axial stop, a pitch stop; the gun lifts straight out at the end of the bead, if the sequence has that lift) and, with no wire at the gun (`travel-16-radial-plane`), the lift-off is no longer constrained by the wire break-off.
