# room-01b: edge, notch and slot (neighbours of the table opening)

**Origin:** branch of `room-01-table-opening`; the edge is Derek's own question ("we might as well just do all this on the edge of the table instead of a hole"). **Scene:** the table-form radio in `scenes/room-01-table-opening` draws hole, notch and edge; the slot is described here only. **Depth:** developed.

## Picture it

Three ways to open the same pit. An **edge**: the table simply ends where the tube's tangent is, and the tube stands beside it. A **notch**: a U-shaped cut in the table's edge, open to the side away from the gun. A **slot**: a long narrow cut, like a router table's, along which the rotator (with the tube standing through) can run from a loading end to the weld end.

## Proposal and what carries

- **Edge.** Table region only behind the tube. Shelf and box hang off the table's underside and are cantilevered past the edge; the bridge is one-sided, on a single X rail behind the tube. Loading is from the free side, so no lifting through a hole.
- **Notch.** Table remains on both sides of the notch (the gantry can have rails both sides). The notch is 160 mm wide, so the tube can stay seated on the rotator: **indicate and seat the tube at a bench, then slide the rotator in sideways under the table**. That turns the notch into a pallet slot.
- **Slot.** A carriage under the table carries the rotator along the slot; the rim is flush with the table throughout, the gun (retracted) waits at one end. The carriage must drop the tube by 20 to 30 mm as it leaves the weld end, because the nozzle sits 5 mm above the rim and the wall would otherwise slide under it.

## Software and manual

Same commands and observations as room-01. The slot adds a carriage axis and an end-of-travel switch. Manual: indicating the tube (edge and notch: at the bench; slot: at the loading end), tacking.

## Tried to break

1. **Edge: the cantilever.** *Assumption:* a rotator of a few kilograms hanging 200 mm off the table edge is fine. *Finding:* about 10 N·m at the table's edge for 5 kg (rotator mass **[unknown]**; rotating mass with tube is 1.40 to 2.01 kg **[repo]**). *Leaves:* real stiffness of the wooden top and the box; a metal edge bracket is the first repair.
2. **Notch: the gantry rails.** A rail along X at the +Y side would cross over the notch. *Change:* rails only where the table is; the bridge is at x about 100, beside the notch (as drawn).
3. **Slot: the nozzle.** *Change:* the carriage drops as it moves; same trick as the dock ramp in room-05. *Leaves:* slot width against dust and spatter; carriage stiffness at the end stop.
4. **All three: the fibre still needs the table behind the gun (room-01 finding 3).** The edge variant has less table behind the gun if the free side faces it; put the free side away from the cable.

## Branches and combinations

The slot with a dock at the weld end is `room-05-drawer-cell` without the cabinet; the notch with off-line indicating is the drawer's first-step version.

## Unresolved, questions for Derek

Would sideways sliding of a seated tube disturb its seat? (The rotator's ID pilot has 0.20 mm radial clearance [repo]; the answer may need a hold-down.) How much of the bench can be cut?

## Assumptions

Notch and slot dimensions: **[illustrative]**. Cantilever moment: **[derived]** with rotator mass **[unknown]**.

## Sourcing pointers

`sourcing/room.md` entries 4 (drawer slides, as a slot carriage), 10 (MGN12H).

## Scene

`scenes/room-01-table-opening` (hole / notch / edge radio).

## Wave 2

- The slot with two rotators on one carriage is `room-12-one-axis-head` in its *two on a carriage* mode (a branch of `use-07`): the fibre never moves and the head only plunges 20 mm.
