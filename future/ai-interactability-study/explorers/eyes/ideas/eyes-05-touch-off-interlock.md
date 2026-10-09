# eyes-05 Touch-off through the interlock

No scene yet. Origin: swarm (eyes framing). Maturity: sketch. Wave 3: its scene is `scenes/freedom-12-touch-trigger` (freedom's branch, `branchOf` this idea); the revised stylus is below.

**Picture it.** Before the bead, with the laser off, the gun is lowered toward the rim until a small metal stylus on the shell (or the copper nozzle itself) kisses the tube. A circuit closes, a light comes on, the axis stops. Three touches on the rim and one on the plate face tell the software where the gun is relative to the tube, the way a machinist finds an edge.

## The proposal

Use the tube's grounded conductivity as a touch sensor. The laser already refuses to fire unless a circuit through the workpiece is complete: the rotator's copper shoe wipes the tube and the work clip goes to it (**[repo]** weld-rotation-rig.md; **[manual]** p.19: "only when a complete circuit is formed between the clip and the welding gun can the laser be emitted"; the alarm "Unconducted" on p.32 names poor "contact between the welding torch and workpiece"). If the gun end of that circuit is the nozzle, the interlock is a free touch probe whose state the software might read from the laser unit's ready LED, its HMI or an unpublished port. If it is not, a 3 V continuity loop through an insulated stylus on the shell does the same job and can be read by the rotator's existing ESP32.

A touch-off routine: approach the rim from above at three azimuths, register the rim plane and the axis; touch the plate face through the bore side to register the seam height; touch the wall to register radius. Each touch is a **direct** measurement of a position at a point, at the cost of contact.

## What carries loads, what establishes position, what is free or restrained

The stylus contacts the tube with a spring-limited force; the gun's support must stop cleanly on contact (a tiny overrun on a printed shell is fine; a driven axis is not). Position: the tube's rim and plate are the reference, read at discrete points.

## What software could command, observe, and what stays manual

- **Command:** the approach axis (a slow move toward contact), retreat on contact. **Observe:** contact / no contact at each step; the axis position at contact. **Manual/unresolved:** fitting the stylus; deciding the rim points; the gun-end connection of the laser's interlock circuit.

## What was tried to break it

1. **The circuit at the gun end is unknown.** The manual says "between the clip and the welding gun". If the nozzle must touch the work to complete it, the reference pose (nozzle 16 mm off the seam) could not weld; so it probably does not. Assumption: the nozzle or wire can be the probe. What it leaves: **[unknown]**, needs Derek.
2. **A rotating tube.** Touching while the tube turns drags the stylus and breaks the tack. Assumption: touch-off is a dry, stopped operation; the rotator's deadman means the tube is stopped when the software probes.
3. **Rim as a proxy for the seam.** The seam is 6.35 mm below the rim (nominally; recess varies tube to tube, **[unknown]** by how much). Touching the rim gives a height and axis estimate, not the corner. The corner needs a touch on the plate face or a section (eyes-07). What this changes: touch-off registers the tube; it does not find the dot.
4. **Contact at the corner.** A ball stylus in the corner sits at a definite offset from it (ball radius); a wire stylus would too. But the interlock cannot say wall from plate: both are one conductor. Two stylus tips, or a force direction, would be needed. Left standing.
5. **Damage and burrs.** Touching a 0.065 in wall rim with a hard stylus can score it; the rim is not a weld surface but the slip fit lives there. Uncertain.

6. **A touch reports the support unless the driven axis is the stiffest element on that axis** *(from freedom's exchange, section 2)*. Conflict: the touch reports the position of whatever the approach axis is, and every soft element between that axis's encoder and the stylus gives way by trigger force divided by its stiffness: at 0.2 N a ring-and-bungee axis (0.15 N/mm) reads 1.3 mm short, a friction arm (10 mm per 2 N of pre-sliding) 1.0 mm, a rigid-grip arm 0.1 mm, the nose stage of the seat 3 µm. Assumption behind it: mine, that the touch axis is a stage and the stylus rigid; theirs, that what a touch measures depends on what stands between the encoder and the tip and on the force at trigger, which the stylus design sets. What the change alters: the rule is *read the position downstream of the softness* (a scale on the gun side of every soft element, or approach through the stiffest axis); a hand-held encoded arm (borrowed-03) reads joint angles downstream of its balance spring, so the spring's softness does not enter, only the joints' play and the arm's own flex. What it leaves uncertain: whether a printed seat repeats to hundredths (freedom's illustrative 0.005 mm for steel, 0.03 mm for printed), and whether a steel ball at 0.2 N marks the inside of a 316L bore (a question for Derek).
7. **One conductor, an unknown gun-end circuit, and a possible fight with the laser's own loop** *(entries 1 and 4 above, and freedom's section 2, points 1 and 2)*. Conflict: wall and plate close the same circuit, so the contact cannot say which surface it found; and a second loop on the same tube may upset the work-contact check. Assumption behind it: that the tube's conductivity is the sensor. What the change alters: the stylus is a **touch trigger on three contacts** (steel balls in printed sockets, three switches, one preload spring; the Renishaw pattern in miniature): a sideways push opens the contact nearest the push first (six patterns, direction to 60°), an axial push opens all three, so wall is told from plate by which contacts open, and the stylus's own circuit depends on neither the tube nor the laser's loop. Trigger force is the design: with a 6 mm contact circle, a 25 mm stylus and 1.5 N of preload, 0.18 to 0.36 N sideways and 1.5 N axial (0.06 to 0.12 N and 0.5 N at a lighter preload). It registers its tip, not the dot: the tip-to-dot vector is a calibration (entry 8). This is `freedom-12-touch-trigger`, which also shows overtravel (after the trigger the tip tilts against the spring alone, so 1 µm of overrun adds 0.5 mN) and that a stylus held at trigger force can lean on a turning tube (a sliding steel ball at μ 0.3 drags 0.054 N). What it leaves uncertain: whether the stylus fits beside the nozzle 8 mm from the wall.
8. **What does a touch add if the sweep of eyes-06 already finds the corner?** *(freedom's question, section 2)* My answer: the sweep finds the corner in actuator units where the *dot* is on it, by light; the touch finds the corner where the *stylus tip* is on it, by contact, with a different set of failure modes (no glare, no fume, no calibrated camera; but path stiffness and seat repeatability). The two together give the one number neither gives alone, the **tip-to-dot vector** (a sweep with the dot on the corner, then a wall touch and a plate touch at the same station): a constant per stylus mounting, checked again after a knock or spatter. After that the touch registers a tube's corner in the dark, quickly, without a camera; the eye at the dot and the touch are independent routes whose disagreement is a bias check for the eye (eyes-07 does the same with a phantom, off the real tube). Wall only, or plate too? The wall touch gives the radial position; the plate touch gives the seat depth of this tube, which is unknown per tube and which eyes-16 reads optically; both give the corner. The plate touch at the lighter 0.5 N preload keeps the head's vibration motor (0.05 N for a 5 g stylus at 1 g) from false-triggering it. What it leaves uncertain: the plate touch's 1.5 N (or 0.5 N) against a thin plate.
9. **In a hand's hand** *(wave 3, from the new direction)*: a touch trigger is also a cue with no estimate behind it. A stylus that beeps or lights a lamp when it touches the wall tells a hand that the nozzle is at the wall, without light and without a model; which contact opened says from which side. `eyes-19-touch-cue` sketches it.

## Branches and combinations

`freedom-12-touch-trigger` (the three-contact stylus; combines `freedom-07-floating-on-work` and `datum-07-touch-off`); `eyes-19-touch-cue` (the hand-held cue). Discrete cousin of `eyes-04-proximity-skin` (proximity without contact). Registers the tube for `eyes-03-marker-cube` (frame from the rim) and for the section camera stand of `eyes-07`. A continuously riding stylus on the rim would measure runout (a digital indicator on the OD replaces the Neoteck by hand): an automated version of the acceptance check in weld-rotation-rig.md; not developed.

## Unresolved problems, questions for Derek

Wave 3: does a steel ball at a fraction of a newton mark the inside of a 316L bore? Fit and preload of the stylus in an 8 mm canyon.

What the gun-end of the work-contact circuit is; whether the laser's ready LED or a port shows the circuit state with the laser disabled; whether a low-voltage second loop on the same tube upsets the laser's own contact check. **Question for Derek:** with the laser powered but the trigger not pulled, does the yellow "Ready" light (or the HMI) change when the nozzle touches the tube?

## Assumptions

Circuit facts **[manual]** pp.15, 19, 32; **[repo]** shoe. Everything about reading its state is unknown.

## Sourcing pointers

None needed (a stylus and a continuity input on the existing ESP32). Digital indicator with data output not sourced this wave.

## Scene

None of mine. `scenes/freedom-12-touch-trigger` draws the three-contact stylus, the reading error by way of holding the gun, and the fast-then-slow touch sequence.
