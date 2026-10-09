# room-10: sit-stand desk frame as a lift (portal, or elevator dock)

**Origin:** swarm (room framing; ordinary furniture at volume as a coarse Z stage). **Scene:** none yet. **Depth:** sketch, with one design error found in thinking it through.

## Picture it

A dual-motor sit-stand desk frame, the kind that sells by the thousand: two telescoping columns on feet, a cross member, a controller with memory presets. Two uses were tried on paper.

**A. Portal.** The frame straddles the rotator; its top carries a small gun carriage. The columns raise the whole gun structure. Rejected as first drawn: the columns lift far more than needed (the joint is at one height for every tube), and they stand a metre apart, so a small skew between the two legs (a millimetre or two is normal for these frames; not stated on the listing) becomes a tilt of the beam.

**B. Elevator dock.** The rotator sits on the desk's top, which acts as a lift table. Down: the tube is loaded, seated and indicated at waist height. Up: it rises through a hole (as in room-01) or into a fixed cell (room-05) and stops against a hard stop that sets the height. It is room-05's drawer turned vertical.

## The proposal (B)

Buy the loading ergonomics and the coarse Z as one ordinary, high-volume, motorised part. The controller's memory presets are commandable heights out of the box; some frames have a serial or Bluetooth interface (unchecked). The hard stop (not the frame's encoder) sets the weld height.

## What carries, what establishes position, what is free

Carries: the desk frame carries the rotator (rated 220 lb on the listing). Position: the hard stop above and the dock balls at the top. Free: nothing at the top. Driven: the two columns. Escape at the end of a bead: the frame lowers the tube (at 25 to 38 mm/s typical, unchecked: about 1 s for 30 mm).

## Software

Command: preset heights (needs a controller interface: unchecked). Observe: the frame's own height count, and a dock-seated switch. Manual: loading, indicating.

## Tried to break it

1. **Rising toward the nozzle.** *Assumption:* Z up is always safe. *Finding:* from room-01's clearance readout, the plate meets the nozzle about 11 mm above nominal; a lift with a hard stop that is 10 mm too high crashes. The stop must be set from the gun's pose, not from the frame's encoder. *Leaves:* the last few millimetres need a slower, damped approach.
2. **Leg skew.** Two columns driven by two motors drift apart by an unstated amount. *Change:* the dock's balls bring the top to the same plane every time; skew matters only between stops. *Leaves:* the dock must grab a platform 1 to 2 mm off in height and tilt.
3. **Speed.** 25 to 38 mm/s (typical of these frames, unchecked) is slow as an escape motion; fine as a loading motion.

## Branches and combinations

`room-05-drawer-cell` (the drawer version), `room-09-move-only-shelf` (a shelf with a linear actuator instead of a whole desk frame: much smaller).

## Unresolved, questions for Derek

The frame's real travel range, repeatability and interface. Whether the office-desk noise, stroke and speed are acceptable in the shop.

## Assumptions

Listing figures (sourcing 9): dual motor, 220 lb, 3 memory presets, fits tops to 77 x 43 in; 4.7 stars, 1,209 ratings, 200+ bought last month. Speeds and skew: **[unknown]**.

## Sourcing pointers

`sourcing/room.md` entry 9.

## Scene

None yet.
