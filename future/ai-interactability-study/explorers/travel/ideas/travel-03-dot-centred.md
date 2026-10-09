# travel-03-dot-centred: orientation about the dot

**Picture it.** The gun's shell rides on printed arcs whose centre is the laser dot, so pitching it or turning it in plan swings the barrel and the grip through space while the dot stays where it was. Or the same arcs sit under the rotator and tilt the tube and its rotator about the dot while the gun does not move. Set a pivot at the grip base instead and one degree of pitch throws the dot 4.9 mm across the recess.

Scene: `scenes/travel-03-dot-centred`. Calculations: `calc/01-pose-and-levers.mjs`.

## The proposal

Assign the three orientation freedoms (pitch about the radial hole axis, plan angle about the vertical, beam roll about the dot-to-grip line) to stages whose axes pass through the dot. Then orientation commands cannot displace the dot, position stages never inherit lever errors, and software sees two decoupled interfaces: XYZ for the seam, angles for the aim.

- **Lever arms in the kit's illustrative pose** (`calc/01`): pivot at the grip base 279 mm from the dot (4.87 mm per degree), grip top 190 mm, barrel middle 93 mm (1.62 mm per degree), nozzle tip 16 mm. **[derived from illustrative geometry]**
- **Beam roll is free for any pivot on the dot-to-grip line.** The grip-axis roll rotates about a line through both the dot and the grip base, so a hinge at the grip base, or anywhere on that line, costs nothing at the dot. Only pitch and plan angle need dot-centred hardware. **[derived]**
- **Plan angle has a second route:** shift the *work* along the tangent (`travel-01`), a linear stage with a 1/r reduction (0.93 degree per mm).
- **Two forms.** Gun side: arcs (printed tracks, rack or friction wheel drive) around the dot with the shell on a carriage. Work side: the rotator and tube tilt about a line through the dot on two arc tracks under the base.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** gun side: arcs held by struts to a room post carry the shell; work side: two arc tracks carry the rotator and tube (ball race sees a side load of sin(angle) of the weight).
- **Establishes position:** the arcs' centre being the dot. That centre is a physical thing set by hand and by the arcs' accuracy.
- **Free / restrained / driven:** each arc restrains everything except rotation about its axis; one motor per arc drives it. The other rotations are locked or on their own arcs.

## What software could command, observe, what stays manual

- **Commands:** one angle per axis (angular step chosen; the scene default 0.05 degree); optionally an XYZ compensation when the pivot is not the dot (scene: Compensate).
- **Observes:** the angle from the step count; the dot against the seam from a camera (the corner inset is exact scene geometry, not a sensor reading). **Calibration by the AI:** command a rotation and watch the dot walk; the walk is the arcs' centre error times the angle, and can be fed forward as an XYZ table. This turns "the arcs must be centred exactly" into "the arcs must be centred well enough that the remaining walk is within the XYZ stage's range".
- **Manual / unresolved:** placing the arcs so their centre is at the dot; where the dot really is relative to the melt (**[unknown]**); wire retract; hand-set neighbourhood.

## What was tried to break it

**1. A pivot at the dot cannot be a hinge.** *Conflict:* the dot is inside the recess, 6.35 mm below the rim, against a 1.65 mm wall: there is nothing to hang a pin on. *Assumption:* the pivot must be a physical hinge line. *Change:* arcs whose centre is a point in space (the scene draws the shell's own arc about the dot). *Leaves:* the arcs must clear the tube rim, the wire feed and the operator's hands; arcs around the tube top restrict access. Whether an arc of the radius the scene draws (100-250 mm, set by where the shell lug sits) clears all of them is not checked.

**2. The umbilical and wire follow the gun's grip.** *Conflict:* rotating about the dot moves the grip base along an arc of radius 279 mm: +-10 degrees is +-48 mm. The fibre may not twist and has a 350 mm minimum bend radius while emitting **[manual]**. *Change:* the work-side form leaves the gun and its cables where they are. *Leaves:* the work-side form loads the rotator's printed ball race with sin(angle) of the weight (about 17 percent at 10 degrees), which is not designed and may or may not be tolerated; the rim must still clear the nozzle (badge).

**3. A hinge at the grip is not the same as a pivot at the dot.** *Conflict:* an arm with wrist joints at the grip couples pitch and plan angle into dot travel (4.9 mm per degree at 279 mm). *Change:* compensate with XYZ, which trades the angle resolution for the XYZ step: a 0.05 degree motor step (0.24 mm at the dot) needs XYZ steps of 0.02 mm or less to be back to about 0.01 mm, a second set of axes and a Jacobian that depends on the pose. The scene shows this with the Compensate toggle and the step slider. *Leaves:* two coordinated stage sets versus arcs that need one.

**3b. The free axis costs the cable.** *Conflict:* beam roll costs nothing at the dot for a pivot on the dot-to-grip line, but that line is also the line from the dot to the cable exit **[repo]**; if the umbilical leaves along it, rolling the gun twists the fibre about its own axis and twisting is strictly forbidden **[manual]** p. 20 (scene badge). *Assumption:* the cable leaves along the roll axis: **[unknown]**. *Change:* a long free hang that untwists (`travel-08-cable-travel`), or roll stays on a hand-set hinge, or the work-side form (the cable does not move). *Leaves:* the exit direction.

**4. Where is the centre, really?** *Conflict:* the dot is a 0.3 mW red reference beam **[manual]**; how closely it sits on the melt is **[unknown]**, and the manual's "red light alignment" screen may move only the pilot. *Change:* none from this idea: it inherits the dot's accuracy.

## Branches and combinations

- **travel-03b work-side cradle** is the "who turns" branch in the scene (gun fixed, tube and rotator on arcs).
- **With `travel-01`:** the stack gives position, arcs give orientation; the two stage sets are independent because arcs do not move the dot.
- **With `travel-05-lever-map`:** the lever map is the calculator for any pivot that is not the dot.
- **Serial arm (Derek's monitor arm) as a reading of this idea:** an arm's wrist pivots away from the dot, so the joint slop times its lever lands at the dot: three joints of 0.1 degree at 600, 350 and 200 mm levers are about 1.9 mm worst case (scene travel-05). The arm can carry and roughly place the gun; it cannot locate the dot.

## Unresolved problems and questions for Derek

- How much orientation range is needed. +-12 degrees is illustrative; the reference scene's slider limits are not requirements.
- Arc drive: rack, friction wheel, or a cable-driven arc; backlash; printing an arc of radius 200-250 mm in PET-GF on a Bambu bed.
- Whether roll can be left to a hand-set hinge: it costs nothing at the dot for a pivot on the line.
- Question: which of the three orientation freedoms does he actually expect to change between welds, and by how much?

## Assumptions

- Gun geometry and pose: kit proxy, **illustrative**. Ideal rotations, no hinge play, arc flex or cable force.
- Beam roll axis = the line from the dot to the grip base: **[repo]** (`hardware/assembly/weld-position.md`). Cable radii: **[manual]** p. 20.

## Sourcing pointers

`sourcing/travel.md`: planetary gearbox for a stepper (14); printed arcs need only the printer.

## Scene id

`travel-03-dot-centred`
