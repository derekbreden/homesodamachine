# A2 — The arm carries, a dock locates (toolchanger coupling)

## Picture it

**The dock.** The shell carries three steel balls. A receiver with three vees,
3D-printer-toolchanger style, sits on a fine XYZ stage on a bench post (or on a
plate shared with the rotator), held shut by magnets or a latch.

**Carrying.** A soft carrier floats the gun's weight: a monitor arm on a CG
hook, a balancer, or E's film arm. Derek guides the shell onto the vees through
printed funnels.

**Locating.** The dock locates all six freedoms against the bench. The tube is
located separately by the rotator's nest, so runout is not followed. The dock is
a *motion to a stop*; the XYZ stage under the receiver holds the per-tube knobs,
set by camera. The gun lifts off for hand tacking and returns to the same pose.

It **grew from Derek's monitor-arm example** and belongs to the "soft carrier +
seat" family (sequence-of-use's lid and session, carry-and-locate's
float-and-dock, one-knob-one-parameter's cartridges).

**Sketch:** `../sketches/a2-arm-into-dock.svg` (true opening pose).

**Major unresolved problems.**
- The hand-to-dock transition with an umbilical attached (see my wave-4 note on
  sequence-of-use).
- Runout is left in.
- Post placement against the motor and ground towers.

Sketch: `../sketches/a2-arm-into-dock.svg`. Sibling of A1; grew from A0.
Developed less far than A1 and B.

## The physical idea

3D-printer toolchangers (and optics kinematic mounts) solve "put a heavy head
down in exactly the same place every time" with three balls sitting in three
V-grooves, held by magnets or a latch. The shell carries the ball plate; a
receiver with the grooves sits on a bench-fixed post with a fine XYZ stage (or
on the B nodal head). The monitor arm or a balancer floats the weight; Derek
guides the shell onto the receiver, printed chamfers funnel it in, and it seats.

- Carries: arm/balancer (weight); dock (only the preload and disturbances).
- Locates: the three ball–groove contacts, six constraints, no redundancy.
- Fixed to: the bench, through the post. The tube is located separately by the
  rotator nest, so runout and reseating are *not* followed (unlike A1).
- Driven: by hand onto the dock; fine XYZ on the receiver by screws.

## Why it is different from A1 and B

- The gun comes off and goes back to the same pose: hand-tack, inspect, clean
  the protective lens, then return to within microns (kinematic couplings of
  this kind repeat to a few µm; with printed grooves and steel balls, tens of µm
  is a safer assumption).
- The locator never touches the hot tube.

## Breaking it

- **Lever arm.** Balls ~80 mm apart, dock ~150–250 mm from the dot. A 5 µm
  seating difference is ~60 µrad, i.e. ~12 µm at 200 mm. Fine.
- **Preload vs. disturbance.** The magnets must hold against the moment of an
  umbilical tug about the nearest ball pair. With the umbilical grounded to its
  own saddle, the residual is small; three 90 lb-class pot magnets would be
  overkill in force, but an unseat alarm (a contact through two balls) is cheap.
- **Arm fights the dock.** Same answer as A1: hang the shell from the arm on a
  soft spring at the CG, not the VESA plate.
- **Stuck wire.** The dock holds; the wire pulls. Either the magnets let go at a
  set force (a breakaway, as on robot torch mounts) or the wire bends. Pedal
  release is the first response.
- **Runout not followed.** The dot sees the tube's ≤0.25 mm radial / ≤0.30 mm
  face TIR. If the process window turns out tighter, pair with A1-S.

## Open questions

- Where the receiver post stands relative to the ground tower and motor tower.
- Whether the dock should *be* the B head's output, which makes A2 the
  "quick-release between hand and machine" rather than a separate station.

---

## Wave 3 note

one-knob-one-parameter: the dock repeats the gun against the *post* to microns,
but the corner moves per tube by up to millimetres (tube length ±3.2 mm, cap
recess, seating). So the dock is a **motion to a stop**, and the XYZ stage under
the receiver holds the real knobs, re-set per tube by the camera. Agreed; the
chain post → XYZ → receiver already has that order. Their recipe cartridges are
this dock with the angles in the block. The toolchanger hardware — magnets,
printed funnels, an unseat alarm through two balls — transfers to their shell
interface. E (`e-film-grip-carrier.md`) is a better carrier for this dock than a
monitor arm: its gimbal passes no moment, so the dock is never fought.
