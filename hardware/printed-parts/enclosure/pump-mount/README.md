# Pump mount

The printed saddle that holds one Kamoer KPHM400 peristaltic pump in Zone C, and
lets a hand take it out from above with the funnel lifted. Two of them per
appliance — `pump-mount-a` under P-A, `pump-mount-b` under P-B. Zone framing:
[`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md).
The pump itself: [`/hardware/reference/kamoer-kphm400/`](/hardware/reference/kamoer-kphm400/).

## Why it is a socket and not a bracket

The pump's own mounting interface is four M3 screws through its stamped bracket,
driven parallel to the motor axis — a good joint and the wrong one here. The
silicone tube in the head is the wear part, so the pump is a service item, and
`../../zone-c/README.md` promises the user lifts the funnel and reaches it. Four
screws behind a 62 mm head, reached down a 148 mm hole, is not that.

So the pump is held the way its shape already allows: its head is a square
prism, and a square socket takes the rotor's torque reaction in wall shear across
the head's own width — no clamping force, no friction, nothing to walk against.
Retention is then a small job, and it is the only job left for a spring.

## Shape

A static part in its own frame — origin **on the pump's motor axis, in the plane
of its mounting-bracket face**; +X toward the head, +Y world back, +Z up. The
pump row lies depth-along-X in one pose, so the enclosure assembly places each
mount by a pure translation (`_contents.PUMP_MOUNT_A_POS` /
`PUMP_MOUNT_B_POS`). Front to back:

- **Head socket.** A [62.61 mm](MOUNT_SEAT) square seat with a side wall up each
  side to the pump's own axis plane — half the head's height of wall to shear the
  torque against, and no more, because that height is exactly the lift a swap
  costs: the pump is free of the mount [31.30 mm](MOUNT_LIFT) up, and every
  millimetre of wall is a millimetre it must travel up a column that ends at the
  ceiling. The head slips in on [0.35 mm](MOUNT_FIT) a side. An end wall at the
  head's front face and a low rib at its rear face close the axis to
  [1.2 mm](MOUNT_FLOAT) of float; the rib sits in the seat's corner, outside the
  boss behind the bracket face that no drawing pins.
- **Spread latch.** Each side wall carries on up past the shelf as a tongue — the
  shelf is its root, so the wall below it is the fixed end — and ends in a ledge
  that returns **flat** over the head's top face. Flat is the point: a lift loads
  that ledge in shear instead of camming the tongue open, so the pump cannot rise
  while the tongues are relaxed and the hold does not depend on a friction angle.
  Driving the head down past both 45° lead-ins takes [14 N](MOUNT_INSERT) and
  spreads each tongue [1.15 mm](MOUNT_SPREAD) at [0.43%](MOUNT_STRAIN) peak strain;
  releasing it takes [2.5 N](MOUNT_RELEASE) at one tab. Each tab hangs **inboard**
  of its tongue on a short arm, over the head's top face, because that is the one
  place a finger reaches both of them — P-B's whole −Y flank stands south of the
  top-wall opening, so nothing on the outside of a wall is reachable there. Two
  fingertips down the [47 mm](MOUNT_LANE) lane between the tabs, pushed apart,
  free both ledges at once.
- **Motor saddle.** An open half-round under the Ø[35.73 mm](MOUNT_SADDLE)
  barrel, in the band of bare cylinder the reference mock and the datasheet part
  agree on. No snap: it is the pump's second support, carrying the motor's
  cantilever off the socket, and an open cradle never has to be released.
- **Feet.** Two webs off the spine plate to the enclosure's front wall, each with a
  flange up its inner face and two M3 clearance holes — [4](MOUNT_SCREWS) screws per
  mount, driving from *inside* the cabinet into heat-set inserts the front wall
  carries, so no fastener breaks the front face the display and the spout share.
  The feet straddle the pump's mass, one under the head and one under the saddle.
  This joint is factory, not service: **tool-free is a property of the pump↔mount
  interface only.**

## The two mounts differ in two numbers

Both are the same part built at different values, and both differences are
consequences of where the row's two poses sit under the top-wall opening
(x 119.5…268, y 19…166 — `enclosure._hopper_hole`):

| | `pump-mount-a` | `pump-mount-b` |
|---|---|---|
| foot reach to the front wall | 64.00 mm | 53.51 mm |
| latch station on the head's top face | front band | rear band |

P-A's motor end runs 107.9 mm west of the opening, so only the FRONT band of its
head's top face lies under it; P-B's head front face runs 3.4 mm east of the
opening, so only the REAR band of its own does. The station is wherever a finger
can reach.

## What the opening reaches

Measured on the placed solids (`hardware/scripts/probe.py`), with the funnel
lifted and both 1/4" lines pulled off the collets:

- **Every release tab of both mounts is inside the opening**, with 14–16 mm of
  clear air over its top. The pump's own outlet-elbow free legs sweep the lane
  between the tabs at z ≈ 270–285, so the fingertips come in beside a leg rather
  than straight down onto the tab.
- **P-B lifts out of the mount and through the opening**, after a jog: 3.4 mm of
  its head front face and 4.4 mm of its −Y flank stand under the top wall, so the
  motion is up [31.30 mm](MOUNT_LIFT) clear of the socket, ~5 mm west-and-north,
  then out.
- **P-A does not leave the box.** 107.9 mm of its length lies under solid top
  wall west of the opening, and the 6.0 mm nose gap to P-B is the only room east.
  Its latch releases and re-seats by hand from above and the pump lifts free of
  the socket in place; taking it out of the cabinet needs the front-top piece off.
  Closing that gap is a pump-row placement question, not a mount question — the
  row would have to stand the two pumps motor-up side by side inside the opening,
  which fits it (2 × 62.61 mm of head in the opening's 148.5 mm of X, 62.61 in its
  147 mm of Y, 127 mm of pump in the 137.7 mm from the seat plane to the ceiling)
  and re-solves every routed flavor segment.

## Print

Build direction along +X, head end down, standing on the socket's end wall. The
layer planes are then the YZ planes, so a latch tongue — beam axis along +Z,
deflection along ±Y — bends entirely within a layer instead of across the layer
bond, which is the one loading an FDM snap must not take. Every wall, web and
flange stands vertical in that orientation; the stop rib, the latch ledges and
the saddle's lead-in are the only overhangs, each under 5 mm.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-mount/pump_mount.py`
→ `pump-mount-a.step`, `pump-mount-b.step`. Seated in the enclosure view by
[`../enclosure-assembly/enclosure_assembly.py`](/hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-mount/pump_mount.py`
