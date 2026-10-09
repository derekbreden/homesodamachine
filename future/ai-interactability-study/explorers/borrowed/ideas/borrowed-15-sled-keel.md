# borrowed-15-sled-keel: gravity as a spring you choose, a damper, and where the cable is anchored

Origin: combination (branch of freedom-08-gravity-tilt, combining freedom-02 and freedom-14; also answering the ledger of freedom-15), drawn in wave 2 from `exchange/borrowed--on--freedom-w2.md` (sections 3 and 4). Maturity: developed. Scene: `scenes/borrowed-15-sled-keel/index.html`.

## Picture it

A side view of the gun hanging from a gimbal, the way a camera hangs on a stabiliser sled: a post rises to an arm above, a small grey block on the pivot is a rotary damper, a brass keel hangs below on a post, and a cable pulls off the tail along a line whose distance from the pivot is drawn as a dashed lever. Press the replay and the gun swings after a step of pull; the trace on the right is the dot's distance from the seam in millimetres, with a red band for the tolerance. With no keel and no damper it rings for the whole ten seconds. Move the cable's lever to zero and the trace goes flat.

## The proposal

A camera stabiliser sled (Steadicam-style, FLYCAM, Glidecam) is freedom-08's plumb bob in a product: a three-axis ball-bearing gimbal in the handle above the load, a fine-tune stage that shifts the camera so the total centre of mass hangs under the gimbal, and a **bottom weight** on a post that sets how stiff gravity is. freedom-08 has a pivot above the centre of mass (spring K = M g l, 0.42 N.m/rad at the housing top) and one trim mass, so its stiffness and its equilibrium are both set by the pivot's position. The sled decouples them: the balance knobs set the equilibrium, the keel sets the spring. Two more parts complete it: a **damper** (a video fluid head is a rotary viscous damper with stepped drag) and the point where the **cable** is anchored.

The scene is one rotation of a rigid body: I th'' = -S g sin(th) - c th' + tau_step - m_s g x, with S = M l_c + m_k d_k (kg.m), a step of torque tau = dF x e + dC at t = 0.5 s (a change of pull dF at lever e from the pivot plus a couple dC at the exit), an optional trim loop, and the dot moving by (pivot-to-dot) x th.

## What carries the loads, establishes position, is free, restrained or driven

- Carried: the whole payload (gun, shell, keel) by the gimbal pivot, which an arm or balancer holds; the carrier sees 1.8 kg at the defaults.
- Position of the dot: pivot position plus (pivot-to-dot) x orientation; orientation from gravity and the trim.
- Free: the vertical-axis turn (no gravity spring); the pivot's small friction.
- Restrained: pitch and roll, by a gravity spring the keel chooses; damped by the fluid damper.
- Driven: the trim mass on its screw (optional loop, slow); everything else is passive.

## Software: command, observe, manual

- Command: the trim mass position.
- Observe: tilt from an IMU (eyes-11; pitch and roll from gravity); the trim mass by step count; the step of pull by a load cell in the carrier line (freedom-13).
- Manual: choosing the pivot, keel and damper; routing the fibre to the pivot; setting the trim before the bead.

## What was tried to break it

1. **freedom-08 as drawn rings.** With no keel (K 0.42 N.m/rad, inertia 0.0106 kg.m^2, both illustrative) the period is 0.99 s and the bearing damping ratio 0.03. A 1 N step at a 145 mm lever leans the gun about 20 deg (69 mm at the dot, small-angle) and the first swing goes to 137 mm. The trim mass (100 g, +-30 mm) supplies 0.029 N.m, which cancels 0.2 N of change in pull at that lever. Assumption: gravity's stiffness is fixed by where the pivot is. Left standing: the numbers are for a gun of unknown mass and centre of mass.
2. **A keel divides the lean by four, not by a hundred.** 0.6 kg on a 200 mm post takes K to 1.60 N.m/rad, the lean per newton from 69 to 18 mm, the payload to 1.8 kg, the trim 3.8 times finer (0.035 deg per mm of 100 g instead of 0.133) and its range 3.8 times smaller (+-1.05 deg). To hold 0.15 mm per newton the cable's line of action has to pass within 0.31 mm of the pivot (no keel) or 1.2 mm (this keel).
3. **A damper turns ringing into settling.** Critical damping for the defaults is 0.47 N.m.s/rad; the trace settles when the damper is at or above it. A video fluid head's damping is set in steps and is on no listing; a spring scale on the handle at a known speed measures it. The dot-space damping of 0.47 N.m.s/rad at a 202 mm lever is 0.0115 N.s/mm.
4. **The anchor.** Put the cable's collar on the gimbal axis (a hollow ball through which the fibre passes straight) and the force has no lever: the lean per newton goes to zero. What is left is the couple a fibre clamped at the exit applies when it leaves already bent: at most EI/R (0.14 N.m for the placeholder EI 0.05 N.m^2 at 350 mm), zero if it leaves straight. 0.05 N.m of couple alone moves the dot 6.3 mm, 0.2 N.m moves it 25 mm. A slack service loop from the exit to the collar adds a spring EI/l_loop (0.33 to 3.3 N.m/rad for a 150 mm loop and EI 0.05 to 0.5): the same order as the keel's spring, with a rest shape that can be chosen.
5. **The trim loop is a trim.** It cancels a change of pull of 0.2 N at 145 mm; the pendulum, the damper and the anchor point do the rest.

## Branches and combinations

- With freedom-02: the keel is a mass that fills a monitor arm's 2 kg payload floor (1.2 + 0.6 = 1.8 kg) and the carrier is that arm.
- With freedom-14: the fluid head is the adjustable damper; c_lin = c_rot / L^2 converts it to a dot-space number.
- With freedom-01 round 4: the two-loop hinge is a gimbal axis; a keel defines an equilibrium at the working roll (option (c) of that round) with a spring, where a counterweight only nulls the torque.
- With freedom-15: the anchor at the pivot is the ledger's exit-axis rule applied to the pivot; the couple is its missing column.
- With borrowed-13: a hexapod's software pivot removes the need for a gravity spring at all, at the price of six actuators.

## Unresolved problems and questions that need Derek

- Gun mass and centre of mass; drop time of the gun hung from a thread through each candidate pivot (a stopwatch; the period gives K/I); the tilt of the gun hung from the pivot with the fibre attached (the cable's torque, force and couple together).
- A fluid head's drag: the Newton meter on the handle at a steady pace, smallest and largest step.
- Whether a printed shell and the gun can sit on a bought sled (FLYCAM HD-3000, $178, up to 3.5 kg); a first test of period and trim needs no purchase beyond a thread.

## Assumptions

- Illustrative: gun and shell 1.2 kg, COM 36 mm below the pivot, gun's own inertia 0.0075 x mass, keel 0.6 kg on a 200 mm post, pivot 202 mm from the dot, cable lever 145 mm, step 1 N, tolerance +-0.15 mm, bead 8 mm/s [repo], trim 100 g on +-30 mm at 5 mm/s. One rotation, sin(th) gravity, viscous damping, no friction, no coupling to the other rotations. The dot shift is (pivot-to-dot) x angle.
- Product facts: FLYCAM HD-3000 (3-axis ball-bearing gimbal, micro-balance knobs, up to 3.5 kg, $178, 362 ratings) and fluid heads (V504 $56.99, 5 kg; SIRUI VA-5 $99) from Prime listings observed 2026-09-29. Drop-time practice (2 to 3 s) from search results on operator documentation: unchecked.

## Sourcing pointers

sourcing/borrowed.md wave 2: FLYCAM HD-3000, fluid heads, the Tigon balancer as the carrier.

## Scene

`borrowed-15-sled-keel`
