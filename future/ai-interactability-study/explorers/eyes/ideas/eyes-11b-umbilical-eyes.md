# eyes-11b Umbilical's own eyes (branch of eyes-11)

No scene. Origin: swarm (eyes framing), branch. Maturity: sketch.

**Picture it.** A painted stripe runs along the fibre umbilical, with a bead every 200 mm. A camera high on the wall looks at the whole hanging length. Software fits a curve through the beads, reads the smallest bend radius, and reads the twist from how the stripe spirals. If the fibre would bend tighter than the manual allows, or begin to twist, it says so, and limits whatever is moving the gun.

## The proposal

The fibre is a fragile part with two rules from the manual: minimum bend radius 24 cm stored and 35 cm while emitting, and **twisting is strictly forbidden** (**[manual]** p.20). Whatever moves the gun (a person today; an arm, a boom or a trim stage in other ideas) can violate either without knowing. Watch the umbilical itself: a visible stripe for twist, beads or a printed grid for curvature. The stripe is straight when there is no twist; a helix means twist, with pitch giving the amount.

## What carries loads, what establishes position, what is free or restrained

The umbilical hangs from the grip base to a hook (a fixed point in other scenes) and is otherwise free; its weight and stiffness are **[unknown]**. The observer is a fixed camera; the stripe is paint or tape.

## What software could command, observe, and what stays manual

- **Observe:** bend radius along the length (from bead positions), twist along the length (from the stripe), whether the cable is inside the allowed envelope. **Command:** a stop or slow-down on whatever moves the gun; a lamp. **Manual:** painting the stripe, hanging the cable, untwisting.

## What was tried to break it

1. **Bend radius from a few beads.** The scenes' cable badge (`WK.cableBadge`) does this on a drawn curve; on a real one, beads 200 mm apart resolve a radius near 240 mm only coarsely (a 350 mm arc has a sagitta of about 14 mm over a 200 mm chord: measurable to a millimetre with a camera at 1 to 2 m). Assumption: the fibre lies in a plane roughly facing the camera. What breaks: an arc curving toward the camera is invisible.
2. **Twist in a sheathed cable that is round.** A stripe shows twist of the sheath, not necessarily of the fibre inside. Uncertain.
3. **The wire feed.** The external wire feed and gas tube run beside the umbilical near the grip base (**[Derek]**); they cross the stripe and may cause the fibre to pull. Not modelled.
4. **Prevention beats detection.** A curved saddle guide or a ball-swivel hook that keeps the radius above 35 cm removes the need to look. This is a mechanical idea for the support explorers; the eye is the fallback.

5. **For the gun what matters is the pull, and the cable's shape between two known endpoints already says most of it** *(from freedom's exchange, section 4)*. Conflict: eyes-11b reads twist and bend radius against the manual's rules; from the force side there is a second job, and a limit on it. A cable that is elastic and lies in a plane has a shape fixed by its two ends (the gun's exit pose and the hook), its weight and EI, so the force it puts on the grip is computable from the endpoints without seeing the cable; the camera adds information only where the endpoints do not decide the shape: hysteresis (armoured or jacketed cable slips in its own layers, so the pull at a pose depends on how it got there), twist, and a loop that has been pulled into a kink. And 0.4 to 4 N of the pull at the grip is the fibre's own recoil at the emitting radius (EI/R²: 0.9 to 8.7 N at 240 mm, 47 % of that at 350 mm). Assumption behind it: mine, that bend radius and twist are the quantities that matter (they are, for the fibre); theirs, that for the gun what matters is the pull. What the change alters: the camera is worth its place for what the force-from-pose model misses, and for safety; **calibrate once** with a spring scale at the exit at five poses (a $9.99 10 N Newton meter is on Prime, `sourcing/freedom.md`), fit a pose-to-force table, and let the beads flag a shape that is off the table. That gives the pull-change input of `freedom-13-map-and-step` without a load cell. **Prevention beats detection**: route the fibre to the largest practical radius and let something else carry its weight (travel-08's balancer, borrowed-11's festoon whose track can keep 350 mm); doubling the radius cuts the pull to a quarter. What it leaves uncertain: EI, weight per metre and hysteresis of the actual fibre and of the wire conduit and gas tube beside it (all [unknown]); whether the conduit's stiffer, stickier pull swamps the fibre's; a stripe shows the sheath's twist, not the fibre's.
6. **Is "1 mm of shape" real?** *(freedom's question, section 4; `calc/umbilical-gauge.mjs`)* In the image plane, yes, and better: a camera at 1.5 m with a 60° lens on 3840 px is 0.45 mm per pixel, so a bead's centroid is found to about 0.14 mm at 0.3 px, and a fit through four beads with the hook fixed and the gun's exit pose known to about 0.07 mm (illustrative; bead-to-centreline offsets and lens distortion would raise it toward 0.5 to 1 mm in practice). Against 0.3 to 56 mN per mm of shape (3 EI/L³ for EI 0.05 to 0.5 and L 0.3 to 0.8 m: freedom's range, reproduced), that resolves 0.04 to 25 mN: one to two orders below the 0.5 to 2 N of pull change that matters. So the gauge is not camera-limited. It is limited by **depth** (one camera sees one plane; a fibre that bends toward or away from it is invisible), by **hysteresis** (the table above), and by the exit pose (1 mm of exit error is 1 mm of shape). What it leaves uncertain: all of the fibre's mechanics.

## Branches and combinations

Sibling of `eyes-11-what-each-eye-sees` (a coordinate outside the six). Would use a fixed camera from `eyes-02-where-can-an-eye-stand` that already exists for other reasons.

## Unresolved problems, questions for Derek

Wave 3: pull the umbilical along and across its exit at the working pose with a spring scale at three poses: how many newtons? (freedom-15's number, and the one every scene here has as a slider.) How the umbilical hangs in the current hand-held use; whether Derek has seen a stripe or marker on it; how much twist it takes in practice.

## Assumptions

Fibre rules **[manual]** p.20. Everything else illustrative.

## Sourcing pointers

None (tape, paint, an existing camera).

## Scene

None.

