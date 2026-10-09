# travel-01-tube-travels: the tube travels, the gun stays

**Picture it.** The gun sits in a printed shell on a rigid post with a few hand-set joints that are locked before the weld. It never moves, so the umbilical and the wire conduit hang still from a fixed hanger. Under the weld rotator is a small stack of stages: a long shuttle that slides the whole rotator out under the gun to a hard stop, then Z, X (radial) and Y (tangent). Everything that differs from one tube to the next is done to the tube, not to the gun.

Scene: `scenes/travel-01-tube-travels`. Calculations: `calc/02-work-side-translation.mjs`, `calc/03-abbe-and-stack.mjs`, `calc/05-shuttle-clearance.mjs`, `calc/06-holder-and-flexure-stiffness.mjs`.

## The proposal

Split the pose by *what varies*. Between tubes what varies is translation: seat depth, tube length, how the tube sits in the nest. What does not vary is the process pose of the gun (beam angle, standoff, wire approach), which is qualified once. So the per-tube trim is assigned to the work (a stack under the rotator), and the process pose is assigned to a locked holder.

Two geometric facts make a small stack enough. **[derived]**

1. The seam is a circle, so the position along the tangent is redundant (the rotator turns the seam through it). Sliding the tube along the tangent by s changes the radial position by s^2/2r only (0.008 mm at 1 mm).
2. What sliding along the tangent does change is the plan angle between the gun and the seam normal: 0.93 degree per mm (1/r with r = 61.85 mm). So the "vertical-axis" rotation of the orientation scene can be produced by a linear stage with a built-in reduction: 1 micron of stage is 0.0009 degree. Moving Y and X together (dx = r(1 - cos psi), dy = r sin psi) turns the plan angle and keeps the dot exactly on the seam. XY under the rotator therefore supplies exactly the two non-redundant horizontal freedoms (radial error and plan angle); Z supplies the third.

Roll about the grip axis and pitch about the hole axis are not touched by any stage: they are set by hand on the holder and locked. The head's standoff is the manual's graduated tube.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the holder post to the bench carries gun, shell and (through the hanger) the cables. The stack carries the rotator and tube (about 2 kg finished vessel **[repo]**, rotator mass **[unknown]**).
- **Establishes position:** the holder is hand-set once for a neighbourhood and locked; per-tube position is *nulled* by the stack against what is seen. The shuttle's hard stop gives a repeatable work position; it is not designed.
- **Free in setup, restrained in the weld:** the holder joints (free while setting, locked in operation). **Driven:** shuttle, Z, X, Y and the rotator. **Free:** the along-seam position (redundant).

## What software could command, observe, what stays manual

- **Commands:** X, Y, Z, shuttle in/out, rotator speed and turning (existing controller); coupling of X to Y so the dot stays on the seam.
- **Observes:** the dot against the seam when a camera can see it (outside and overhead cameras are drawn; line of sight is drawn geometry, not optics); stage positions from step counts (open loop) or from scales in the hand branch. The plan angle is dead-reckoned from the Y command: **no sensor is drawn for it**.
- **Manual or unresolved:** hand-setting and locking the holder; nozzle extension; retracting the wire before a shuttle; loading and unloading the tube; the hard stop; whether anything measures holder drift during the weld.

## What was tried to break it

Round 1 (baseline) is the scene as drawn. Rounds 2 and 3 are the breaks.

**1. The swap.** *Conflict:* in the kit's opening pose the nozzle tip is 5.0 mm above the rim and 55 mm from the axis, inside the bore, with the barrel crossing the bore's opening plane. With the gun seated the tube can be lifted only about 55 mm before its rim meets the barrel, so it cannot be lifted out; lifting 12 mm and sliding it out sideways collides once the far wall sweeps past the nozzle (`calc/07`). *Assumption behind it:* the kit's 16 mm nozzle clearance, 60 degree pitch and 44.6 degree beam are illustrative. *Change:* instead of moving the gun, shuttle the whole rotator out under the fixed gun with no lift. A horizontal shuttle clears only while 16 cos(beta) > 6.35 mm, i.e. beta < 66.6 degrees from vertical (the tip stays above the rim plane; `calc/05`), and only with the wire retracted (the wire crosses the rim plane inside the bore). Drop the gun 6 mm by hand in the scene and the red badge appears. *Leaves uncertain:* the real nozzle extension (the manual's graduated tube) and the real pose; the wire retract; the hard stop. The alternative is to move the gun: about 13 mm of raise clears a 12 mm lift and a slide-out, about 144 mm is needed to lift the tube straight out (`calc/07`, illustrative pose): see travel-04.

**2. Moving the work does not move the lever problem away.** *Conflict:* the seam stands 232 mm above the rotator feet **[derived from repo numbers]**; a layer's tilt error becomes a sideways error at the dot: 0.05 degree = 0.20 mm, 0.3 degree (a scissor jack, illustrative) = 1.2 mm at the rotator feet, more if the layer sits lower. That is the same size as gun-side joint slop at 200-280 mm lever. *Assumption:* the stage tilt values are illustrative. *Change:* only the *change* of tilt over the travel actually used matters, so the fine layers should be short-travel; the long shuttle relies on its hard stop, not its straightness, and the residual at the stop is trimmed by X and Z. Stack order: long axes at the bottom with hard stops, fine axes on top. *Leaves uncertain:* the return repeatability at the stop.

**3. Y alone.** *Conflict:* a tangent move by 10 mm leaves 0.8 mm radial error. *Change:* software couples X to Y (a toggle in the scene); the correction is r - sqrt(r^2 - y^2), known exactly. *Leaves:* nothing observes the plan angle itself.

**4. The holder is not rigid enough.** *Conflict:* the umbilical pulls on a locked holder. Force is **[unknown]**. Per newton, a 12 mm steel rod 300 mm long moves the dot 44 microns, a 20 mm steel rod 6 microns, 12 mm aluminium 128 microns; a friction joint that creeps 0.02 degree at 250 mm lever is 0.09 mm (`calc/06`). *Assumption:* the force acts at the tip and the gun is rigid. *Change:* the holder is a short, fat, bolted structure, not a ball head; the hanger takes the cable weight so the pull is only the cable's stiffness. *Leaves:* measure the gun mass and the umbilical pull (Derek).

**5. What the stack cannot do.** It does not change roll or pitch, so a tube whose plate is not square to its axis (face runout) needs a Z follow (see travel-02) rather than a tilt.

**Wave 3 entries, from use's exchange (`exchange/use--on--travel-w2.md` section 1) and answered in `exchange/travel--reply-to-use-w3.md`.**

**6. Z's range is bigger than the swap margin (use).** *Conflict:* in the kit's proxy pose the nozzle tip is 5.0 mm above the rim plane and the barrel behind it is nearer the rim ring than the tip; 8 mm of the 12 mm of fine Z are shuttle-safe, a weld that ends with the axis trimmed high crashes on the next swap, and nothing in the drawing stopped it. *Assumption behind it:* Z exists only to trim. The +-6 mm was sized for tube length and plate-seat spread (both unmeasured), never for the swap; the swap's clearance silently assumed Z stayed low. *What the change alters:* a drop tier (30 to 60 mm, hard stops) under the fine tier; to swap, drop, then shuttle, and the tier's bottom-stop switch enables the shuttle: an interlock by construction, not a rule computed from Z and the plate depth, which nothing measures. With a 40 mm drop and Z at +6 the rim clears the barrel by 39 mm (`calc/12-drop-tier-seat.mjs`). Adopted as a combination, `travel-19-drop-tier-on-a-seat` (combines this idea and `use-13-work-states`; both originals stay). *What it leaves uncertain:* the nozzle margin is the kit's proxy; one more axis to build.

**7. The end of a bead has no owner (use).** *Conflict:* if the head must leave the puddle the gun cannot (it is locked), so the work must drop: 20 mm along the beam is 28.1 mm of Z (beam vertical component 0.712 in the kit's opening pose), 0.47 s at 60 mm/s while the tube turns (3.7 mm of seam at 8 mm/s); the fine range gives at most 8.5 mm along the beam. *Assumption behind it:* the sequence has a lift. That is the coordinator's shared-context sentence; guide 46 and `weld-rotation-rig.md` say only to release the trigger, then the pedal, and I had repeated the sentence as [repo] in `travel-04` (corrected there, in `travel-14b`, `travel-16`, `travel-07`'s scene and the notebook). *What the change alters:* the drop tier owns the escape, the escape slider starts at 0 (the sequence as written), and a fused wire stops the drop by the tier motor's current limit (unmeasured) and is a hold state. *What it leaves uncertain:* whether the head has to leave at all and how far (question for Derek); how a stepper tier behaves at a fused wire.

**8. A return axis's tilt is face runout (use).** *Conflict:* every landing tilts the stack by the stop's scatter over its span; at r = 61.85 mm a tilt d makes a once-per-turn vertical error r tan(d): 0.02 degree is 0.022 mm, 0.05 degree is 0.054 mm peak (0.11 mm peak to peak) against the 0.30 mm TIR window [repo]. The fine axes trim the position a tilt causes, not the tilt. *Assumption behind it:* a hard stop returns flat. *What the change alters (and the answer to use's question, what tilt I would accept):* 0.0185 degree, 0.02 mm peak, a tenth of the window. A three-ball top seat leaves ball scatter over ball circle: 10 micrometres over 150 mm is 0.0038 degree, 4 micrometres peak, five times inside; it does not depend on the guides' straightness (they only guide); a scissor lab jack at 0.3 degree would leave 0.32 mm. Drawn in `travel-19` (tilt exaggerated by a slider, the trace and readouts true). *What it leaves uncertain:* printed grooves and creep; the plate's sag under the rotator; each approach draws the balls again.

**9. Two approaches per closure, and a fused wire is a state (use).** *Conflict:* guide 46 tacks with the gun at the seam and checks the face with the dial at the weld circle: tube in, out, in, two landings, and the last trim has to come after the second; a wire fused in the bead ties the gun to the tube, so a shuttle or a drop before the cut drags it through the seam. *Assumption behind it:* one approach; nothing fuses. *What the change alters:* the order rule adopted (last trim after the last approach, the dry lap after that); `travel-19`'s Landing radio draws each landing's tilt; a fused-wire toggle raises a hold badge and every axis is inhibited until a hand has cut the wire and says so. *What it leaves uncertain:* one approach goes away only if the dial can stand opposite the gun; the cables on a shuttling, dropping body.

## Branches and combinations

- **travel-01b: monitor arm carries, stack locates.** The arm holds the gun (gas spring, hand-set, locked) and is not asked to locate; the stack does. This gives "a monitor arm is too flexible" a concrete arrangement: it carries and roughly places, and the vibration of the head's motor (manual p. 20) and the umbilical pull must be checked against its creep. Not yet a scene; the matrix row D1 + T1.
- **travel-19-drop-tier-on-a-seat (wave 3, combination with `use-13-work-states`):** the drop tier under the fine Z on a three-ball seat, its bottom-stop switch the shuttle interlock; both originals stay.
- **travel-01c: hand-crank branch (in the scene).** The same stack cranked by hand with scales; software reads and tells the person which wheel to turn: idea `travel-09-hand-moves-software-reads`.
- **travel-01d: table plate.** The gun's fitted shell sits in a pocket in a table plate above the stack (Derek's table example with the roles swapped: the table locates the gun, the stack under it moves the work). Candidate combination with `room`.
- **With travel-04:** the swing-away seat is the alternative to the shuttle for the swap and, if the sequence has one, the end-of-bead lift-off. **With travel-02:** the stack is the medium stage. **With travel-06:** the nest screws are the innermost stage.

## Unresolved problems and questions for Derek

- Hard stop and its repeatability; cable and hose management on a shuttling rotator (motor lead, pedal, ground shoe, purge hose).
- The rotator stands about 100 mm higher on the stack (illustrative); loading height, camera views and the laser hood are not considered.
- **Questions that need Derek's observation:** the gun's mass; the umbilical pull at the grip; the rotator's mass with a tube; how much the plate seat depth and tube length actually vary (a few indicator readings on five tubes); whether a 5 mm tip-above-rim clearance matches the real nozzle.
- **Wave 3, questions for Derek (from use's exchange):** how do you end a bead today, how far does the head go before the wire is free, and does it lift at all? Can the dial stand opposite the gun for the face-runout check (that removes one of the two approaches)? What do the rotator, its base and a tube weigh together (the tier and the stack carry it)?

## Assumptions

- Gun pose = the reference scene's opening pose, kit proxy geometry: **illustrative**. Stage ranges (shuttle 200 mm, Z +-6, X +-8, Y +-12 mm), stack thickness, hand-set error defaults: **illustrative**.
- r = 61.85 mm, recess 6.35 mm, nest pilot 4.5 mm, runout limits 0.25 / 0.30 mm TIR: **[repo]**. Seam height above feet 232 mm: **[derived]**. Plan angle per mm: **[derived]**.
- Gun mass, cable force, rotator mass, tube variation: **[unknown]**.

## Sourcing pointers

`sourcing/travel.md`: dovetail XY tables (entries 1, 2), CNC linear stage with stepper (3, 4), MGN12 rails (5), lab jack (6, capacity 25 kg), drawer slides (7), digital scales (11), T-slot (18).

## Scene id

`travel-01-tube-travels`

## Wave 2

The stack is the mover for `travel-15-touch-stack` (datum-07's touch-off with the work moving into a fixed stylus: a null measurement, no soft stage on the gun side) and the medium and follow stages assigned by fitted term in `travel-18-signature-parity`. datum-04's two-lead yaw estimate could be nulled by the Y stage (1.08 mm per degree of plan angle).
