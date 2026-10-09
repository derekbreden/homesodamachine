# workspace-as-structure on machine-that-learns — E, the motorised table station (wave 4)

My view: the workspace is the first positioning stage and carries the loads;
I wrote the manual table-opening branch and the collar that E stands on. E asks
what that branch becomes as the first stage of Derek's automated vision. The
answers below come from seeing where motors change what my manual version
relied on.

Supporting files (mine):
- `explorers/workspace-as-structure/split_mount.py`
- `explorers/workspace-as-structure/ideas/split-mount-station.md`
- `explorers/workspace-as-structure/sketches/split-mount-station.svg`

## What motorising improves over my manual branch (agreed, briefly)

- **Z first, with the height taken from the work (E-h1 camera, E-h2 plunger).**
  This answers work-as-datum's objection to my branch ("the crank repeats the
  nest, not the corner") and makes "tube change without touching the gun"
  true across tube lengths. LOAD/WELD as buttons is the manual crank made
  honest.
- **X/Y at countertop height.** It cuts the gravity moment on the nearest
  gun-side stage 3–5× compared with their B, and keeps drive loads one-signed.
  I had placed the beam there for reach; they found the load reason.
- **Fiducials on the collar and the three-camera split.** Collar tags register
  PTZ frames. The joint camera (fixed, ~69° off the beam) does the metrology;
  the front PTZ sees the wall, the +Y-end PTZ sees the dot and wire.

---

## 1. The stuck wire is in tension in the rig's direction, and a motorised Y slips silently

### The difficulty, in E's variant

E's Y is the gantry on its rails, belt-driven (GT2 in E's parts list). It is
also the plan-angle axis (0.93° per mm). E's stuck-wire line: "Axes hold; …
the wire yields at 3–5 N, long before any drive."

### The assumption behind it

A stuck wire loads the gun by bending the stick-out. That is true for the
first millimetres. The rig's procedure places the wire "on the arriving side of
the puddle" [Repo, weld-rotation-rig.md]. The wire comes from the gun's side
(−Y), so the surface at the dot moves **+Y, away from the gun**.

- **After the stick-out bends over:** the drag pulls the wire out along its own
  axis, in tension. The stick-out is ~10 mm, and 4–8 mm of travel passes
  between trigger release and pedal release at 8 mm/s.
- **The ceiling on that tension:** the rotator can pull ~140 N at the bead
  (digest; carry-and-locate's holding-torque bound). A 0.030 in ER316L wire
  holds roughly 250–320 N (UTS 550–700 MPa, estimate). The wire doesn't yield
  first; the drive does.

### What that does in E

- **The belt slips.** A NEMA 17 with a 20T GT2 pulley (pitch radius ~6.4 mm)
  holds ~0.4 N·m / 6.4 mm ≈ 60 N. A 60–140 N pull back-drives it: the gantry
  is dragged along +Y and the motor loses steps.
- **Nothing reports it.** The controller's Y count is now wrong by the drag
  distance. That error is a **plan-angle error of ~0.9° per mm**, which the
  next dry lap sees as "the recipe drifted".
- **Parts in the path take a jolt.** The shell's wire-guide bracket and the
  roll yoke carry the same pull.

### Repair: a deliberate, reported breakaway on Y

The manual branch had this: Y was the tangent, the insensitive direction, and
the natural fuse. Motorising should keep it.

- **Coupling:** the Y carriage connects to its belt clamp through a ball-and-
  spring detent (or two magnets kissing), which lets go at ~20–30 N. That is
  well above anything the weld itself puts on Y, and well below the belt's
  holding.
- **Switch:** the detent carries a microswitch wired as a Klipper endstop.
  Breakaway raises an event. The station halts the recipe and asks for the
  snip.
- **Re-home:** jog Y back until the detent re-seats. Klipper homes on the
  switch, so the count is right again before the next lap.
- **Cheaper partial alternative:** StallGuard on a TMC2209 for Y reports the
  slip. It doesn't limit the force on the wire guide.
- **What it leaves:** the X and roll drives also see part of the pull if the
  wire's line isn't exactly along Y (it is pitched down ~45° to the dot).
  Sized the same way, the detent's 20–30 N along Y caps the Y component. The
  vertical component loads the head, which is stiff.

---

## 2. The head at countertop height (E's own open problem 1) → branch E-s, "split mount"

### The difficulty, in E's variant

The tilt about the hole axis is an arc of R ≈ 200 mm centred on the radial
line through the dot, standing on the X carriage beside the gun body. The roll
is a yoke carrying carry-and-locate's open C-ring. E lists what the head must
clear: the table top (elevation ≥ 9° at R 200), the umbilical at 133 mm, the
wire path and the joint camera's sightline, "none of [which] can be closed
without the gun scan".

### The assumption behind it

A rotation about an axis through the dot has to be manufactured on the gun
side, by an arc or linkage whose geometry puts the centre there.

### The branch: make the remote centre from contact geometry instead

Details in `ideas/split-mount-station.md`.

**What rides the plate:** a paddle (my wave-2 branch of work-as-datum's
compass) with:
- a hub pin on the plate's port seat;
- two rollers on the plate face on **a line through the dot**;
- a room foot P3 on the collar under the grip, with a fence.

**The one room-set rotation is exact.** Lifting P3 turns the gun about the
roller line. The dot lies on that line, so it doesn't move: 0.87 mm along the
seam for 10°, from the 5 mm roller-centre height, and 0.08 mm in height.

**The tilt motor is a lead screw under the collar**, ~5 mm per degree, not an
arc on the carriage.

**Checked on the proxy (`split_mount.py`):** the line can't be the radius
itself.
- A roller holder at (36, 0) is 4.3 mm from the nozzle at the opening pose and
  collides at vertical −30°.
- On the other side are the rotating nipples, whose sweep reaches r 27.
- Tilted 30° toward +Y, away from the gun, with P1 34 mm and P2 90 mm from the
  dot, the P1 holder clears the gun by 15–22 mm across six poses.
- Dot height = 1.61 × P1 − 0.61 × P2.

This also corrects my wave-2 paddle, which put the rollers on the radius (I
had checked a point, not a holder).

**What changes in E:**

| E | E-s (split mount) |
|---|---|
| Tilt arc R 200 on the X carriage (open problem 1) | P3 lift under the collar; the dot stays on the tilt line by construction |
| Roll yoke with the open C-ring | Same, now the only gun-side rotation mechanism |
| X/Y gantry, 212 mm from the dot, low | Short X/Y micro-slides between the paddle and a carrier that holds the rollers and the gun; rollers ride with the gun, so the dot stays on the line |
| Per-tube height (E-h1/E-h2) and Z-follow of the face runout map | Not needed to keep the dot on the corner: the gun rides the plate. Shelf Z only brings the plate into range and does LOAD/WELD |
| X-follow from the stylus | Not needed for runout at the plate centre (the pin follows it). The stylus can still read ovality and heat, if wanted |
| Angles read by camera | Both rotations read by an inclinometer on the shell (the tube is vertical, so gravity is the right reference); the camera verifies the dot |

**What it costs:**

- **Per-closure work:** nipples and a seat bar every closure, and Derek's
  permission to have them in the ports at weld time.
- **Load on the work:** the paddle rides the plate with 20–40 N on the rollers.
  A hold-down magnet in the hub pulls on the seat, internal to the plate.
- **Plan-angle range:** only about −4.6° to +2.3° around a nominal built into
  the carrier. That is the range over which both rollers stay on clean plate,
  outside the nipples' sweep and inside the fillet toe. E's Y has tens of
  degrees.
- **Moving parts on the work:** small motors on the paddle.

**What E keeps unchanged:** its order of motorisation, the observation layer,
Klipper, the dry-run mode, the fiducials, and LOAD/WELD.

---

## 3. The umbilical's first clamp sits before the head, so roll twists a short span

- **Variant:** "Umbilical … clamped on the carriage (after X/Y, before the
  head)."
- **Difficulty:** the roll then turns the gun relative to that clamp. Per
  carry-and-locate, the butt's cable twists ~0.87× the roll, so ±15° of roll is
  ~±13° of twist. Put into the ~100–150 mm between clamp and butt, that is
  ~90–130°/m. The manual forbids twisting.
- **Assumption:** the clamp is only a strain relief.
- **Repair:**
  1. Let the first grip on the cable be carry-and-locate's open ring or a
     loose saddle, so the cable can turn inside it.
  2. Put the first hard clamp far from the butt: at the fixed saddle at the
     bench end, or at the cart's mast (my cart-station branch "cart docks to a
     bench"). The roll's twist then spreads over ≥ 700 mm of free span
     (≤ 20°/m).
  3. Keep the free span's shape repeatable with the cart dock, so the constant
     cable force the head sees is the same every session.

---

## 4. The stylus in the gap (checked, mostly fine)

- **Worry:** the stylus touches the OD at the dot's own azimuth ~9 mm below the
  joint, behind the fillet through a 1.65 mm wall. Is it in the heat?
- **Estimate:** Rosenthal thin-plate peak temperature, all heat in the wall
  (worst case: the plate sinks most of it), 100–200 W net at 8 mm/s, 9 mm from
  the heat line. That gives ~50–100 K above ambient. **Warm, not hot**
  [estimate].
- **What it reads:** the local thermal bulge (~0.05 mm on the radius), which
  the corner shares. Following it is right.
- **Two things enter that aren't the corner:**
  - the welded tube's longitudinal seam passing once per revolution;
  - wall-thickness variation (it reads the OD).

  Both repeat each revolution, so subtract them using the dry-lap map at the
  same azimuth. Keep live − map for weld-time drift.
- **Rotation direction:** if Derek flips cw/ccw between recipes, nothing about
  the stylus changes, since it sits at the dot's azimuth, not ahead of it.

---

## 5. A small layout note: the +Y side is everyone's

The gun owns azimuths about −10° to −120° (low: barrel at r 39–45, −17° to −61°,
z < 60; body high toward −90° to −110°). Everything else wants the free half:

- the joint camera (+Y, inboard, ~85 mm up, ~120 mm out);
- work-as-datum's W1 arm (+Y edge to the axis, 40–60 mm up);
- the +Y-end PTZ (inboard);
- the lid's notch edge;
- in E-s, the rollers (az +28° at r 37 and +110° at r 48, below 13 mm).

A one-page azimuth/height budget on the collar drawing avoids three parts
wanting the same line of sight. The rollers and W1 sit low; the camera looks
over them from 85 mm up.

---

## What E does that my manual branch lacked, and what transfers

- **Theirs → mine:** knob-first motorisation (a crank that stays as the manual
  knob); per-tube height from the work closing the Z loop; fiducials; the
  gravity-moment reason for a low gantry. My table branch should adopt Z-first
  as its default build order.
- **Mine → theirs:**
  - the Y breakaway (now reported);
  - clamp placement from the cable's point of view;
  - E-s, which removes the head's arc by letting two work contacts on a line
    through the dot define the tilt axis.
