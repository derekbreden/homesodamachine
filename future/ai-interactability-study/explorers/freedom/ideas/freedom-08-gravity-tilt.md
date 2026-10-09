# freedom-08: gravity as the tilt actuator (weight-shift orientation)

Scene: `scenes/freedom-08-gravity-tilt` (rough: a side view of the hanging gun with the cable pull and trim mass). Origin: swarm original (from the freedom framing; touches the two-loop hinge of freedom-01). Depth: sketch with numbers (`calc/25-gravity-tilt.cjs`); parameters **illustrative**.

## Picture it

The gun hangs from a pivot high on its shell, like a plumb bob. Gravity pulls its centre of mass under the pivot, so pitch and roll set themselves. A small mass on a screw inside the shell slides a few millimetres and the gun leans a fraction of a degree. There is no actuator at the tail, so nothing at the tail fights the cable.

## The proposal

Use gravity as the restoring force for two of the three rotations. Hang the shell from a low-friction pivot (a ball seat or a small gimbal) placed above the gun's centre of mass at the working pose; pitch and roll then equal the direction at which the COM is directly beneath the pivot. A trim mass moved by a lead screw shifts the COM by m_s × d / M: 100 g moved 7.5 mm shifts a 1.2 kg gun's COM by 0.63 mm, which is 1.0° of tilt about a housing-top pivot (0.5° about a collar pivot). Yaw about the vertical through the pivot has no restoring torque: it needs a motor or a lock. The pivot is moved by the XYZ axes.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: the pivot carries all of it.
- **Position of the dot**: pivot position plus (pivot-to-dot) × orientation; the lever is 125 to 269 mm depending on the pivot (2.2 to 4.7 mm per degree).
- **Orientation**: pitch and roll from gravity and the trim mass; yaw from a motor.
- **Free**: yaw, until driven; the pivot's small friction.
- **Restrained**: pitch and roll, by a weak gravity spring; the cable and the trigger push against it.

## What software could command, observe, and what stays manual

- **Command**: the trim mass position (a stepper on a screw), yaw, the pivot's XYZ.
- **Observe**: tilt from an IMU or by the dot; the trim mass position by step count.
- **Manual or unresolved**: picking the pivot so the working pose is an equilibrium; the cable route.

## What was tried to break it

**Entry 1. Gravity is a weak spring, and the umbilical is a strong one.**
- Conflict: restoring stiffness is M g ℓ with ℓ the pivot-to-COM distance: 0.42 N·m/rad (0.0074 N·m/deg) about the housing top, 0.84 about the barrel collar, 0.91 about the housing back. A 2 N pull at the cable exit, 145 mm from a housing-top pivot, is 0.29 N·m: the gun would lean about 39° (small-angle). To hold 0.1° the cable torque must be under 0.74 N·mm, 0.25% of that pull.
- Assumption: the umbilical's torque on the gun can be ignored.
- Change: route the cable so it exerts almost no torque about the pivot (the cable leaves along the line through the pivot, the tail supported separately), or add feedback: an IMU reads the tilt and the trim mass corrects it (the mass shift is fine enough: 1° per 100 g × 7.5 mm).
- Leaves uncertain: the real umbilical torque (unknown).

**Entry 2. The working pose is not a natural hanging pose.**
- Conflict: in freedom-01 the hinge line's natural roll is 131° away from the working roll. A pivot chosen so the working pose *is* the hanging pose puts the pivot above the COM at that pose, which forces its position on the shell (and the trim mass offsets the rest).
- Assumption: any pivot works.
- Change: trim mass as the pose adjust; the pivot chosen as the one point that makes the working pose a plumb pose.
- Leaves uncertain: whether that point is reachable on a printed shell with clear cable routing.

**Entry 3. Yaw is free.**
- Conflict: no restoring torque about the vertical through the pivot: any push spins it.
- Change: a yaw motor with a stiff hold, or a bungee pair (freedom-01b's yaw bungee).

**Entry 4 (wave 3, from borrowed's exchange, section 3). Time: the pendulum rings. Decision: revised (scene readouts and a damper slider).**
- Conflict: the scene shows a static tilt. With the gun's inertia about the pivot at 0.0106 kg·m² (illustrative) and the gravity spring above, the period is 0.99 s and the bearing alone damps to a ratio of about 0.03: a 1 N step of pull at bead start leans the gun and the first swing goes to twice the lean, and it rings for the whole bead. Critical damping for these masses is 0.13 N·m·s/rad. To hold 0.15 mm for a 1 N step with gravity as the only spring the cable's line of action would have to pass within 0.31 mm of the pivot (borrowed's figure at K 0.42, pivot 202 mm from the dot). The trim mass (100 g, ±30 mm) supplies 0.029 N·m: it cancels 0.2 N of change in pull at 145 mm, a fifth of the step.
- Assumption: gravity's stiffness and the trim are the whole story; time does not matter.
- Change: the scene now reads the period and the damping ratio, and for a 1 N step across the cable's lever the static lean and the first swing at the dot (in the default: 15.9 degrees and 107 mm with the bearing alone); a rotary damper slider brings the ratio toward 1. The trim mass is the slow, fine part.
- Leaves uncertain: the real inertia and friction of a gimbal; stick at small angles is not in the model.

**Entry 5 (wave 3, from borrowed's exchange, section 3). The sled: a keel, a damper, an anchor. Decision: adopted as a combination (`freedom-17-hung-on-the-line`, combines this idea and `borrowed-15-sled-keel`; both originals stay).**
- Conflict: a stabiliser sled has two knobs where this idea has one: the balance (the trim) and a bottom weight that sets how stiff gravity is without moving the equilibrium. 0.6 kg on a 200 mm post takes K from 0.42 to 1.6 N·m/rad, cuts the lean per newton from 69 to 18 mm, makes the trim 3.8 times finer and its range 3.8 times smaller; a fluid head is a damper; the cable anchored on the pivot has no lever, and what is left is the couple. The bought part is a FLYCAM HD-3000 (3-axis ball-bearing gimbal, up to 3.5 kg, $178).
- Assumption: gravity's stiffness is whatever the pivot choice gives.
- Change: `borrowed-15` draws it; the scene here takes the cable's anchor and couple as sliders and `freedom-17` puts the pivot on the fibre's line in the kit's geometry.
- Leaves uncertain: one axis only; the vertical-axis turn has no gravity spring at all (entry 3); room below the pivot for the keel.

**Entry 6 (wave 3, from borrowed's exchange, section 3, the question). Would you place the pivot on the fibre's line? Decision: answered, drawn in `freedom-17-hung-on-the-line`, and left standing.**
- Conflict: with the pivot on the line the axial part of the cable's force has no lever and a keel and trim do the rest. In the kit's geometry the line is not where the centre of mass is (74 mm above a pivot at 150 mm from the dot, 49 at 200, 9 at the grip base), the keel must hang 42 to 190 mm to one side to balance, and the cable's release point is far from the pivot (about 440 mm of lever for the S-boot of freedom-16): a step of 0.03 N is 13 N·mm, which against 0.45 N·m/rad is 6 mm at the dot. To hold 0.1 mm the spring must be about 26 N·m/rad.
- Assumption: removing the force's lever removes the cable from the aim.
- Change: yes to the pivot on the line for the axial part; no to gravity as the whole holder for any route that lets go far from the pivot. A fairlead (the fibre through a hollow ball at the pivot, so no lever and no couple) is possible only beyond the grip base, 279 mm out; the alternative is the tail bridle of freedom-01b for rotation, with gravity as a trim.
- Leaves uncertain: the real centre of mass and inertia; a statics run of the seat with its ball on the line (the setup did not converge in this session).

## Branches and combinations

- With freedom-01: the two-loop hinge is a special case where gravity acts on the roll about the line between the loops.
- With freedom-01b: the seat at the nose is an inverted pivot (COM above the seat); this idea puts the pivot above the COM instead.
- With freedom-05: the IMU-plus-trim feedback is a slow servo like the runout table.

## Unresolved problems, and questions that need Derek's observation

- Gun COM: hang it from a thread at two points and mark the vertical lines (also needed by every other idea).
- Umbilical torque about a candidate pivot: hang the gun from a thread at the pivot point and see how far the cable tilts it. With the fibre attached and laid the way it will lie, the tilt from plumb gives the cable's torque force and couple together; two hangs with the fibre laid differently separate them (borrowed's question, freedom-15 entry 5).
- Drop time: hang the gun from a thread through the housing top, the collar and the housing back in turn, nudge it, count ten swings and time them. The period gives K/I for each candidate pivot with nothing bought (borrowed-15).

## Assumptions

- Mass 1.2 kg, COM (0, −18, 178) local: **illustrative** (**[unknown]**). Pivot candidates: housing top (0, 17, 185.5), collar (0, 0, 109), housing back (0, 0, 253) in the kit proxy frame: **illustrative**. Umbilical pull 2 N at the grip base: **illustrative**.

## Sourcing pointers

`sourcing/freedom.md`: AS5600 (tilt encoder), 608 bearings and 1 inch balls (pivot stock), mini linear rail (trim-mass screw). An IMU was not searched.

## Scene

`freedom-08-gravity-tilt` (rough).
