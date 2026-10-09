# B. Gun stays, work travels — the tube carries every state change

Sketch: `../sketches/drawer-lift.svg`. Path check: `../calc/drawer_path.py`.

> **Pose note (wave 3).** Numbers in the wave-1 text below were computed at scene hole **dial 65** (my proxy passed the dial straight into `posePoint`; the scene subtracts 35). Derek's opening pose is dial 30. The corrected numbers and the repaired branches are in the *Wave 3* sections at the end; dial-65 values are kept where they describe that reachable orientation.

## Picture it (as it now stands: branch B-r, true opening pose)

The gun is fixed for the whole session. Its shell hangs from a portal (post and
beam) on a common subplate, through a recipe block. Its umbilical, wire conduit
and a camera never move.

- **What moves: the work.** The rotator bolts, through its four clamp holes, to a
  carriage. The carriage rides on three hardened balls, 20 mm below weld height,
  out along +X to a load position with open sky above the nest.
- **Seating.** Pushed back in, the balls climb 60 mm ramps and drop into three vees
  on a plate carried by a cross-slide. The cross-slide holds radial position and
  yaw per recipe, gib-locked. The vees, not the guides, locate.
- **Per-tube height.** Three screws between the carriage and the rotator, set with
  the carriage seated against a rim flag on the portal.
- **The plate.** Held at its recess by the stand-hung plate head: a spindle on the
  tube axis catching two plugs in the plate's ports, with three stationary pads at
  45° / 150° / 255° pulled against the plate face. That lets the eight tacks be
  fixture pulses.
- **Fixed to.** The subplate carrying the portal, the ramps and the cross-slide.

Sketches: `../sketches/drawer-lift.svg` (true pose, side view) and
`../sketches/x2-plate-hung-from-P.svg` (the plate head, true pose).

## Major unresolved problems

1. **The plate head.** Its spring force, and its fight with the turntable's face
   wobble between tacks.
2. **Footprint and operator side.** About 600 × 350 mm, loaded from +X, behind the
   station.
3. **The purge hose and cables** riding the carriage.
4. **Tube-length spread** (unmeasured) and the per-tube X trim.

## The physical idea

Everything hard to move repeatably — the gun, its 5 m umbilical with a 350 mm
emitting bend radius, the wire conduit, the aim, the camera — is set up once per
session (or once per recipe) and never moves. Everything that has to move anyway —
the tube, which must be loaded, indicated, capped and inverted — moves on a
carriage.

- A portal (extrusion post + beam, or a printed-node frame) on a common subplate
  holds the fine-aim stage and the gun shell over the weld station.
- The rotator bolts through its four Ø10 bench-clamp holes to a carriage plate. The
  carriage runs out ~250 mm to a **load position** with open sky above the nest,
  and back in to the **weld position**.
- The carriage travels **20 mm low**. In the last 60 mm of travel three hardened
  balls under the carriage climb three ramps and drop into three vee seats (Kelvin /
  Maxwell). The seats, not the slides, define the weld position. Pull-out reverses
  it: the tube drops away from the wire before it moves sideways.

## The geometry that decides the direction

The wire tip rests at the inside corner, *outside* any horizontal path of the rim
unless the tube comes in from the right side:

- For a straight approach at angle φ from +X, the wire tip is inside the bore only
  during the last 123.6·cos φ mm of travel. Along ±Y (tangent) it is never inside:
  the tube cannot arrive sideways along the tangent.
- `drawer_path.py` moves the tube relative to the fixed proxy gun: an approach
  moving −X (the tube arrives **from the weld-station side**) within about ±20°
  clears everything with as little as 10 mm drop and any ramp from 30 to 100 mm;
  I propose 20 mm drop for stickout and runout margin. Steeper approach angles put
  the wire's last millimetres against the wall.
- Consequence for layout: the load position is on the +X side, behind the station.
  The operator loads from +X; the gun's grip and umbilical are on the far side.

## Operating it, phase by phase

| Phase | What moves | Notes |
|---|---|---|
| Open session | Aim set or verified with a reference tube; stickout trimmed with the carriage out (gun stands free) | Aim persists for every tube that follows |
| Load, indicate, plate, shoe, float | Carriage out | Full access from above; indicator base on the NEMA as now |
| Tacks | Carriage in; fixture tacks at indexed angles | Needs the stationary swivel hanger (kit K1-H2) — see B1 |
| Aim | Push in until it drops into the seats | Dry run is a *verification*, not a setup |
| Weld | Nothing but the table | Trigger via kit K2 |
| Stuck wire | Nothing | Snip first; never pull the carriage with a stuck wire |
| Gun away | Carriage out (the gun never moves) | Re-trim stickout here with the gun free-standing |
| Invert | Carriage out | Purge hose to the lower port rides with the carriage |

The work lead stays on the copper shoe (it rides with the rotator). The motor,
driver cable and pedal lead need a service loop for 250 mm of travel.

## What this buys

- **Constant cable loads.** The umbilical's unknown weight and spring-back become a
  fixed preload that never changes between tubes. The largest unknown force in
  the problem is removed rather than resisted.
- **Aim is a session state, not a per-tube action.** The dot dry run becomes a
  check that tube *n* matches tube *n − 1*, which is the repeatable-experiment loop
  Derek described. A fixed camera shares the gun's frame, so dot-track videos from
  different tubes are directly comparable (and suit an AI running dry runs).
- **Guarding.** The weld cell can be a fixed enclosure with a curtain over the
  carriage opening. A second person never has their head near the beam path while
  loading.

## Trying to break it

**B1 — tacking.** The gun cannot come to the tube at the load position, so tacks
happen at the weld station, with the plate held at depth while the table indexes.
A rim-bridge hanger collides with the fixed gun (the same conflict as A5).
*Repair:* the stationary swivel hanger H2 (kit K1), mounted on the portal on the −X
side, holding the plate through its ports on a bearing so the plate turns under it.
But the plate must also be held while the carriage travels in: *further repair:* a
plate carrier that screws into both ports, rests on the rim with fold-away feet
while at the load position, and is picked up by H2's swivel when the carriage seats;
then the feet fold clear of the rim. *Leaves:* a real mechanism to design;
depth set by the carrier's feet against the rim, transferred to H2.

**B2 — per-tube joint height.** The gun is fixed; a longer tube lifts the corner
into the wire. *Repair:* the fine stage's Z slide on the portal dialled to the
measured tube length before pushing in, or a wire touch-off after seating. *Leaves:*
unmeasured length spread.

**B3 — the wire tip meets the corner last.** On the ramp the corner rises
diagonally toward the tip (the relative path passes the rim level ~10 mm inboard of
the wall). A long stickout gets pushed up by the plate. *Repair:* as in A3 — tip set
~1 mm short, jog to touch after seating.

**B4 — mass on the ramp.** Rotator + tube is perhaps 5–7 kg (estimate: NEMA 23 ~1.1
kg, PET-GF parts, 1.4–2.0 kg rotating mass). Raising it 20 mm over 60 mm needs
~20–25 N of push plus friction; seating is by gravity, and a detent keeps it from
rolling out. Acceptable by hand. The PET-GF base is not a ball seat: the balls go in
a carriage plate (aluminium or thick printed with steel inserts) under the rotator.

**B5 — slide slop vs seats.** Drawer slides have millimetres of play, which is fine
because the seats locate. The slides must *release* the carriage vertically at the
end of travel (they cannot lift with it). *Repair:* the carriage rides on its three
balls directly on printed/aluminium tracks for the whole travel (no drawer slides),
or the slides carry a sub-frame that the carriage lifts off. The first is simpler.

**B6 — footprint.** Rotator 300 × 250 plus ~250 mm travel plus portal: roughly a
600 × 350 mm subplate. It fits a 48 or 72 in bench; it is a larger object than the
rotator alone.

**B7 — operator at the +X side.** The operator loads from behind the weld station
and watches the puddle from there or on a monitor. The gun's grip and umbilical go
away from them, which is good for guarding and bad for any hand intervention at the
gun (which B is designed not to need).

## Parts (representative)

- Three 1/2 in chrome balls (PGN G25, Prime), stainless dowel-pin vees.
- If slides are used for the travel: LONTAN 14 in 100 lb full-extension pair (Prime,
  $22.99 for 2 pairs) — only as a guide, with the lift handled as in B5.
- Extrusion / printed portal; the same fine stage and shell as A.

## Contribution, open problems, assumptions

Contribution: turns the umbilical and aim from per-tube variables into session
constants, and shows the only approach direction that works. Biggest open problem:
plate holding through travel and tacks (B1). Assumptions: proxy pose; masses;
tube-length spread small enough for one Z dial.

---

## Wave 3 — true opening pose (hole dial 30) and branch B-r

**Pose re-run** (`calc/drawer_path.py`, `calc/exchange_w2.py`):

- The approach result stands: the tube must travel along −X/+X within about ±20°,
  and drop ≥ 10 mm before the wire tip can clear the rim.
- The nozzle tip is 5.0 mm above the rim (8.8 mm at dial 65).
- **Retracting the wire instead of dropping** now needs **14 mm** of feeder
  retract, not 8 mm: the wire rises at 38° from the tip, not 71°.

**Branch B-r (who-moves-what's allocation):**

- The three vee seats sit on a plate carried by their cross-slide. Radial and yaw
  are set per recipe and gib-locked; the ramps and seats return the carriage to them
  on every load. This supplies what my B lacked, since it had no X or yaw setting.
- Per-tube height is taken on three screws between the carriage and the rotator, so
  the ramps never change.
- **Sequence note:** set that height with the carriage seated, against the rim flag
  on the portal's plate head (exchange file, "plate hung from P"). Setting it at the
  load position has no station reference.

**B1 (plate and tacks) is repaired** by the stand-hung plate head from my wave-2
exchange file. At the true pose its pads move to 45° / 150° / 255° with the frame at
rim + 15 mm (38.8 mm centre-line clearance to the barrel; `calc/head_w3.py`). The
wave-2 layout collides with the barrel at dial 30.
