# workspace-as-structure — summary entries

View: the workspace — tables, openings, plates, shelves, the cart, the rotator's
own mounting — is the first positioning stage. It builds the nominal pose into
structure, carries the loads, and decides which motions are easy.

All geometry uses the scene's gun proxy at the true opening pose (grip 45°, hole
dial 30° = parameter −5, vertical −15°) via `geom.py`. The proxy is an
illustrative shape, not a scan. Prices were observed 2026-09-28 in Derek's
Chrome; Amazon entries are Prime-confirmed. Details:
`../../sourcing/workspace-as-structure.md`.

## 1. Table opening + countertop gantry *(Derek's example, developed as he described it)*

`ideas/table-opening-gantry.md` · `sketches/table-opening-gantry.svg`

**Layout.** The rotator hangs under a Ø150–160 hole in a VEVOR bench, on a shelf
carried by four posts. Four belt-linked Tr8×2 screws lift it and a lock clamps
it. The rim is flush with the top, and the box's front is open.

**Where the gun sits.** The gun body is over solid table on the −Y side, 70–200 mm
up. Only the barrel crosses the mouth; the nozzle is ~5 mm above the rim.

**The gantry.** It runs beside the hole, not over it: MGN12 Y rails either side,
an X beam 20–40 mm above the top, and the printed shell resting in a named pose
saddle on the X carriage.

**What each motion does.**
- X sets the dot across the seam.
- Y is the plan angle, 0.93° per mm (the tangent slide).
- Z is the shelf.
- The two rolls live in the saddle.
- "Fixed" is fixed to the bench top.

**Payoff.** A tube change is a ~70 mm shelf drop and a slide out the open face; the
gun and cables never move. The mouth is at countertop height, the snip and the
view are from above, and purge rises straight up.

**Breaks and repairs.**
- The loop runs through the 30 mm wood top: ~0.1–0.5 mm under a lean (estimate).
  Repair: the collar (entry 3).
- The crank repeats the nest, not the corner (work-as-datum). Tube cut tolerance is
  ±3.2 mm, and 1 mm high puts the dot 0.64 mm onto the plate. Repair: T-W1
  (entry 2).
- A stuck wire pulls along Y. Repair: a breakaway detent.
- Branch kept: the edge-of-bench variant Derek raised.

**Parts.** MGN12H 400 mm rail, $24.99, next day, a standard profile from 7+ Prime
sellers. Tr8×2 screws, $11.99 for two, same day, 466 ratings.

**Unresolved:** bench crossbars; gun mass and cable force [unmeasured]; discrete
angles.

## 2. Branch T-W1: the collar centre *(work-as-datum's repair, adopted)*

In `ideas/table-opening-gantry.md` (wave 3) ·
`../work-as-datum/sketches/xw-collar-centre-and-lid.svg`

**How it works.**
- Two 316 hex nipples go finger-tight in the plate's tapped ports; a seat bar
  carries a countersink at their midpoint.
- An arm from the collar's +Y edge carries a spring plunger down the axis (LM12
  bushing, 1/2 in ball, dial). At the true pose every gun surface is ≥ 38.8 mm from
  that axis.
- Per tube: crank until the ball seats and the dial reads zero, then lock.

**What it absorbs.** Tube length, radial runout and loose-tube seating leave the
pose. Face tilt stays, as one indicator reading per tube.

**Additions here.**
- Let the plunger rotate with the seat.
- Motorise crank-to-zero with a NEMA 17 and a 0.01 mm RS232 dial ($23.99, 101
  ratings).
- Their sprung shelf (W1b) is recorded, not preferred.

**Unresolved:** nipples in the ports at weld time (Derek); how the plate is held
before tacking; the port-to-edge eccentricity (their estimate, ±0.19 mm RSS).

## 3. Drop-in collar *(a repair of Derek's table)*

`ideas/drop-in-collar.md` · `sketches/drop-in-collar.svg`

**The part.** One laser-cut plate (1/2 in MIC-6 or steel) with every hole cut in
one datum, resting on three pads in an oversized bench hole, like a sink. The gun
support goes above it.

**The shelf posts.** Four 1 in aluminium tube posts carry the shelf below,
~2,900 N/mm sideways (calc). Tr8 screws used as posts would give only ~70 N/mm.

**What it changes.**
- The loop never touches wood.
- A lean tilts gun and tube together.
- A steel collar gives the indicator's magnetic base a seat beside the mouth, best
  aimed at the plate face near the corner.

**Parts.** SendCutSend MIC-6 at 0.25/0.375/0.5 in, ±0.005 in, 2–4 days production
(price not observed). 1 × 1 × 48 in aluminium tube, $29.99, 100+/month.

**Unresolved:** cutting the bench; the frame under the opening.

## 4. Countertop sled *(from Derek's "gun tip at countertop height")*

`ideas/countertop-sled.md` · `sketches/countertop-sled.svg`

**The mount.** The shell stands on three ball feet on a rim-height plate, with
fence buttons along Y, a rear stop and a spring: a 3-2-1 kinematic mount.
- The plane carries the weight and sets height and both tilts; the fence and stop
  only locate.
- The gun lifts off and returns to the same pose, and the spring doubles as a free
  stuck-wire fuse.

**Branches.**
- A pusher gantry that carries no weight.
- Six stationary actuators at the contacts.
- "The rotator grows a deck": legs on the rotator's own base, no bench cutting.

**Breaks and repairs.**
- Friction (1.7–3.3 N unpreloaded) against cable tug; repair: preload and
  anchoring.
- Stick-slip.
- Dirt under the feet.
- Printed legs creeping.

**Parts.**
- Dasqua Grade A granite plate 400 × 250 × 70 mm, $142.54, 30 ratings (weak).
- 1/2 in G25 balls, $9.45, 946 ratings.
- Mitutoyo 150-801 micrometer head, $100.

**Unresolved:** umbilical force; spatter; discrete angles.

## 5. Fixed gun, moving shelf *(mirror of Derek's gantry; six explorers reached this family)*

`ideas/fixed-gun-moving-shelf.md` · `sketches/fixed-gun-moving-shelf.svg`

**Layout.** A pose saddle on a rigid bridge holds the gun still. A cross-slide
under the rotator gives X across the seam and Y as the plan angle; the shelf gives
Z. Runout is followed by moving the rotator ±0.125 mm at 0.02 Hz.

**Parts.** VEVOR cast-iron table, $135.90, 50+/month. MYSWEETY 6350, $95.99, 1,068
ratings.

**Breaks.**
- Dovetail backlash.
- Angles are fixed per saddle.
- It conflicts with T-W1 over X, so the correction moves to the plunger arm.

## 6. Lidded mouth *(seed → work-as-datum's L1 family)*

`ideas/lidded-mouth.md` · `sketches/lidded-mouth.svg`,
`../work-as-datum/sketches/xw-collar-centre-and-lid.svg`

**The seed and its branches.**
- **Seed:** a stationary lid carrying gun, camera and gas ports.
- **L1 (work-as-datum):** the lid rides the plate on the port seat and ball
  transfers, 3 mm above the rim, notched for barrel and wire, and parks on the
  collar when the shelf drops.
- **L1a (work-as-datum):** a nose ring on the lid, leaving 0.12 of any work motion
  at the dot.
- **L1h:** the ring load (6–8 N) lands ~40 mm outside the lid's support triangle
  and tips it; a ~30 N hold-down through the centre pin fixes that.
- **L1p:** split-mount rollers instead of a ring on the copper nozzle.

**Unresolved:** heat and spatter; interlock contact through the ring; gun centre
of mass.

## 7. Cart station *(beyond Derek's examples)*

`ideas/cart-station.md` · `sketches/cart-station.svg` · `cable_path.py`

**Layout on the Weldpro cart.**
- A module plate (rotator, gun support, feeder) on three hard feet on the upper
  tray.
- The X1 Pro on the bottom tray, with the middle tray removed.
- Argon at the rear, with purge straight up.
- A rear mast saddle giving the umbilical one R 375 bend.
- ~3 m of spare fiber stored as an S of opposite turns.

**What it gives.** The cable force becomes a constant, measured once. The conduit
is short and fixed. The mouth is at ~985 mm with no bench cut, and the station
moves as one piece. "Fixed" is fixed to the module.

**Rule found.** Park the gun by rotating about an axis through the cable exit,
perpendicular to the cable's bending plane.

**Breaks and repairs.**
- **Tipping:** ~180 N·m restoring against a 200 N lean at 1 m. Repair: outriggers
  or a dock.
- **Space:** the tray is 531 × 330 mm.
- **Heat** (revised with machine-that-learns): ~0.8 kW while firing for about a
  minute per closure, reading "2500 W" as maximum draw. Adopted their H1:
  common-mode layout, thermistors, a camera-fitted drift model.

**Branches.**
- **M (machine-that-learns):** an X stage under the rotator. Additions here:
  - a ~5° nose-up park about the cable exit, lifting the nozzle ~22 mm, before its
    ~50 mm retract;
  - M excludes a gun support that rides the plate.
- The cart docked to a bench.
- The mast as a travelling overhead anchor for other explorers' balancers.

**Open disagreement.** machine-that-learns holds that the first gun-side motor
ruins the constant cable shape. The view here: a cable force that is a repeatable
function of pose is still usable, and only hysteresis on the saddle would ruin
it. Approaching one pose from both sides with the camera would settle it.

**Parts.** Weldpro cart, $179.99, 50+/month, 317 ratings. X1 Pro 470 × 205 × 335 mm,
21 kg (vendor).

**Unresolved:** tray heights; the unit's air path, idle draw and umbilical exit;
storing fiber without twist.

## 8. Split-mount station *(combination)*

`ideas/split-mount-station.md` · `sketches/split-mount-station.svg` · `split_mount.py`

**Sources.**
- work-as-datum: port seat, compass, L1 park, puck.
- machine-that-learns: E's motor order, observation layer, dry-run rule.
- carry-and-locate: the open C-ring roll.
- one-knob-one-parameter: tilts on the gun, work vertical.
- This explorer: collar and sled.

**The rule: each contact of a 3-2-1 mount goes to the side that should own its
freedom.**
- A hub pin on the port seat sets x and y.
- Two stainless rollers on the plate, on a line through the dot, set height.
- A collar foot under the grip sets rotation about that line.
- A fence sets azimuth.

**Why the tilt is exact.** The dot lies on the roller line, so a lead screw
lifting the foot tilts the gun about the dot: 4.9 mm per degree, 0.87 mm along the
seam at 10°, no arc.

**Hold-down and the rest.**
- RC62 magnets on a 430 disc (38 N each at contact on thick steel, per K&J; Derek
  owns 30) hold it down with zero net force on the tube.
- The roll uses the open C-ring.
- X/Y micro-slides carry the rollers and gun together.
- An inclinometer reads both rotations (WitMotion BWT901CL, $47.99, 89 ratings;
  0.05° is the seller's figure).

**Found along the way.**
- Rollers on the radius collide: 4 mm from the nozzle, and the nipples sweep
  r ≤ 27. A line 30° off the radius clears by 15–22 mm.
- Dot height = 1.61·P1 − 0.61·P2.

**Unresolved:** clearances need the scan; the tilt axis is a 30° mix of Derek's two
rolls; plan-angle trim only −4.6…+2.3°; spatter under a roller.

## 9. Paddle compass *(branch contributed to work-as-datum's endcap compass)*

`../../exchange/workspace-as-structure--on--work-as-datum.md` §1 ·
`sketches/paddle-compass.svg`

**The problem.** The compass's all-plate support triangle has a 17.5 mm inradius
while the grip is 233 mm out, so a 1.5 N force tips it.

**The branch.** Two plate contacts on a line through the dot, plus a room foot and
fence under the grip.
- The inradius becomes ~33 mm and the loads go to the room.
- Tube length becomes a 0.23° per mm roll.
- A 20–30 N hold-down keeps the near roller loaded.

**Correction (wave 4).** The radius rollers collide; entry 8 is the working form.

**Parts.** S695ZZ rollers, $8.79 (weak volume). GE8 bearing, $9.39 (thin stock,
standard size).

## 10. Cold-lap map, room-held replay *(branch contributed to lip-collar-track)*

Same exchange, §2 · `wave2_calcs.py` §3

**The problem.** A follower 25° ahead of the puddle leaves 43% of the runout error
(9% with a symmetric pair) and 85% of the ovality error (36% with a pair).

**The branch.**
- Map at the dot's azimuth on a cold lap: a lip pinch plus a plate-face skid, read
  by RS232 indicators.
- Replay by moving the work, with no contact during the weld.
- For thermal drift, use the live reading minus the map at the contact's azimuth.

**Unresolved:** a real-time table angle; whether 0.1–0.2 mm of thermal growth
matters.

## 11. Axis quill in the collar *(branch contributed to between-centres)*

Same exchange, §3 · `axis_clearance.py`

**Clearance.** The axis column is open for hole dials ≤ ~40: ≥ 38.8 mm at the
opening pose, ≥ ~21 mm across the neighbourhood. It closes at ≥ 50.

**The branch.** The tailstock becomes a vertical quill from a bridge on the collar's
+Y side. The collar is their sub-plate, and the quill scale is the per-tube height
gauge.

**The drill press.** The WEN 4208T quill (2 in stroke, depth stop) could serve if
transplanted, but the whole press can't straddle the rotator.

## 12. Branches contributed to machine-that-learns' E

`../../exchange/workspace-as-structure--on--machine-that-learns-w4.md`

- **Stuck wire in tension.** In the rig's direction the drag is bounded by the
  rotator's ~140 N before the wire's ~250–320 N (estimate). A belt Y (~60 N hold)
  slips silently, costing ~0.9° per mm. Repair: a 20–30 N detent with a Klipper
  endstop switch.
- **Umbilical.** A loose ring near the butt; the first hard clamp ≥ 700 mm away.
- **Stylus heat.** ~50–100 K peak (estimate), which is fine.
- **E-s.** Entry 8.

## Transferable pieces

- **Tangent slide = vertical-axis turn.** 0.93° per mm with dy²/2R radial error.
  It is also the retract and breakaway axis, and the direction of stuck-wire pull.
- **Contact-placement rule.** Put each contact on the side that owns its freedom.
  Two work contacts on a line through the dot give an exact tilt axis. Sled,
  paddle, split mount and compass are one family, and carry-and-locate's
  float-and-dock seats join it.
- **Cable-exit parking rule.** Rotate about an axis through the exit,
  perpendicular to the cable's plane; never load by rolling about the grip axis.
- **Cable force.** A cable force that depends only on pose is as good as a
  constant; test hysteresis on the saddle.
- **Guidance separate from lift,** and precision at the moment of locking.
- **Close the loop in one plate,** not the bench.
- **Geometry at the true pose.**
  - The body sits over a solid surface on −Y.
  - The nozzle is ~5 mm above the rim.
  - The grip base is 233 mm from the axis, ~133 mm above the rim.
  - The axis column is open for dials ≤ ~40.
  - 1 mm of corner height = 0.64 mm across and 0.75 mm along the seam.
- **Trigger force inside the shell;** per-tube height from the plate, not a crank
  number.
- **Stuck wire is tension in the rig's direction,** so give supports a reported
  tangent breakaway.
- **Follower lead transfer:** 2 sin(lead/2) for runout, 2 sin(lead) for ovality.
  Map cold, and use live contacts only for drift.

## Questions only Derek's observation can answer

1. Gun mass and centre of mass; umbilical and conduit force at the grip when moved
   ±5 mm; trigger force.
2. Where the umbilical and cooling air leave the X1; its idle draw; the feeder's
   size and conduit length; the cylinder size.
3. Weldpro tray heights; whether the middle tray comes out; the current layout.
4. The VEVOR top's crossbars. Cut a bench, use a collar on legs, or give the
   rotator a deck?
5. May 316 nipples sit in the ports while welding? How is the plate held before
   tacking?
6. Tube length spread and end squareness.
7. Does ~1 m countertop height suit him better than the chest-height joint?
8. When will a gun scan exist? Every clearance here is on the proxy.
