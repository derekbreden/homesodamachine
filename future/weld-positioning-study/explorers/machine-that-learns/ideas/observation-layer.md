# Observation layer — the part every arrangement shares

## Picture it

**The joint camera.** The ELP 16 MP camera already owned sits on the free +Y
side of the dot, inboard, ~85 mm up and ~120 mm away. It sits behind a red
filter and a sacrificial window, and looks into the recess at ~69° to the beam.

**Wider views.** A wide station camera watches the whole station. PTZ cameras,
registered by printed tags, are added in wave 3.

**Position readouts:**
- step counts;
- a printed index ring;
- AS5600 encoders;
- closed-loop boards;
- a stylus on the tube's OD.

**Control and firing.** One Klipper board and one host run the motors and
cameras. A person fires the laser through a Bowden pedal; software never does.

Sketches: [`../sketches/observation-plan.svg`](../sketches/observation-plan.svg),
[`../sketches/observation-camera-view.svg`](../sketches/observation-camera-view.svg).

**Major unresolved:**
- Whether the idle red beam sweeps with the wobble.
- Whether the triangulated cap height is good on brushed 316L.
- A dry-run mode for the rotator: a firmware and procedure decision.

---

Not an arrangement by itself: the cameras, readouts and software loop that turn
any of the carriers in this directory (the nest, the still gun, the RCM carriage,
the hexapod) into a station that learns. It is written once here so the
arrangement files can point at it.

Sketches: [`../sketches/observation-plan.svg`](../sketches/observation-plan.svg),
[`../sketches/observation-camera-view.svg`](../sketches/observation-camera-view.svg).
Numbers: [`../calc/arrangement_numbers.py`](../calc/arrangement_numbers.py).

## The joint camera

**Where it goes.** The gun occupies the (−X, −Y, +Z) side of the dot at the
opening pose. The free side is +Y. A camera at about (−45, +70, +85) mm from the
dot, aimed at the dot, is roughly the gun's mirror image across the radial
plane. Checked in `calc`: its line of sight stays inside the bore circle for
every height below 68 mm above the dot, so the 6.35 mm lip does not hide the
corner. It sees the cap face at ~45° and the wall obliquely (~68° from the
wall's normal); moving it further inward (−X) trades cap view for wall view.
That is a setting to try, not a design value.

**What it can resolve** (ELP-USB16MP01-KAF68 already on hand: IMX298,
4656 × 3496, 68° diagonal; implied focal length 4.83 mm):

| Distance | Field | Per pixel |
|---:|---:|---:|
| 60 mm | 65 × 49 mm | 14 µm |
| 100 mm | 108 × 81 mm | 23 µm |
| 150 mm | 162 × 122 mm | 35 µm |

At 100–120 mm a cropped 20 × 15 mm window around the corner is ~900 × 650
pixels. The tiny lens will not deliver per-pixel sharpness; assume 2–3 pixels
of real resolution, so ~50–70 µm for an edge, with centroiding of a bright dot
repeatable to perhaps 10–20 µm. Depth of field at f/2-ish and 100 mm is a few
millimetres — enough for the wall and cap together. These are estimates from
the sensor geometry, not measurements.

**The reference beam is structured light.** The camera sits ~69° off the beam,
so moving the gun 0.1 mm along its beam slides the dot's image ~3 px at 100 mm
(`calc`, section 2). Standoff is therefore measurable from the same image as
dot position — the gun's own aiming beam plus one camera is a triangulation
rangefinder. On the flat cap face the geometry is clean; on the corner the dot
splits across two surfaces and the split itself is the measurement.

**The wobble line.** If the reference beam is swept by the wobble motor while
idle (common on handheld heads; **unknown for the X1 Pro — question for
Derek**), a camera exposure longer than 1/80 s sees a red line, not a dot. Its
orientation is the wobble axis (an Unknown in shared-context), its length
tracks the sweep at the surface, and the fraction of it lying on the wall vs
the cap is a direct geometric proxy for the wall/cap split Derek rolls the gun
to get. That is exactly the quantity the grip-axis roll exists for, measured
instead of judged.

**What it reports per frame** (see the camera-view sketch): (a) dot/line centre
to the fitted corner line; (b) wall/cap share of the swept line; (c) line
length and angle; (d) standoff by triangulation; (e) wire tip to the leading
end of the line; (f) tack positions, which give the table angle.

**Light and filter.** A Tiffen Red 25 (long-pass ~600 nm, $16.95 Prime) in a
printed hood plus the camera's own IR-cut filter make a crude red band-pass:
the reference dot stands out, room light drops. For corner-edge detection,
switch a white LED ring on for alternate frames. A spare D18 × 2 mm protective
lens from the Hgnova 15-pack already bought for the gun makes a sacrificial
spatter window in the hood.

**Weld frames.** This camera is for dry runs and for post-weld photographs of
the bead with the laser off. Watching the puddle needs a shade filter and
probably another camera; later, and not required for anything below. Keep the
camera out of the specular reflection path of the 1080 nm beam off the cap
(assumption: the IR-cut filter and the offset position are enough for a
sensor at 120 mm — not established).

## The station camera

A second wide UVC camera (another ELP, $72.99 Prime) looking at the whole
station: gun, cables, tube, the rotator's turntable, the operator's hands. It
logs context, reads the gun's status/process LEDs (so the log knows whether
the laser was armed), sees cable swing and stuck-wire events, and reads a
**printed index ring** on the turntable rim (coded marks every 5°): an absolute
table angle that survives the DM542T releasing the motor 10 s after a stop and
the table being turned by hand. Step counting stays the fine angle; the ring
re-zeroes it.

## Readouts that are not cameras

- Table angle: step count from whoever generates the steps, plus the index ring.
- Hand-set angles and micrometers: AS5600 magnetic encoders ($7.99/2, Prime)
  on any knob shaft or hinge, 0.09° per count on that shaft — so a manual
  setting still lands in the log.
- Closed-loop NEMA 17 boards (MKS SERVO42D) on motorised axes: their encoder
  reports position whether the move came from a command or from a hand on the
  knob (the second half **unverified**; see B).
- Trigger state: a microswitch on the shell's trigger lever (see Safety).

## Control stack

One Klipper board (BIGTREETECH Octopus Pro, 8 stepper sockets, $64.99 Prime)
on a small Linux host, exposing Moonraker's HTTP/websocket API. An AI agent then
drives the station the way it would drive a 3D printer: G-code moves, homing,
macros, and camera frames from the same host. The rotator's DM542T takes
step/dir, so the same board can generate its steps; a common trick in rotary
engraving is to drive the rotary axis as the extruder so it moves in
coordinated `G1 X… E…` moves (my recollection of the ecosystem, not verified
here). For runout following, tight synchronisation is not even needed: the
radial follow speed is 10–30 µm/s (`calc`, section 3), so a host loop updating
X from the table angle at 10 Hz is ample.

This changes one thing about the rotator as it stands: today "the pedal is the
whole of the control" and nothing takes the table from the operator. A learning
station needs a mode in which software turns the table. The proposal keeps the
pedal as a deadman for any motion while the laser is armed and lets software
move the table only in dry-run mode with the laser disabled — a firmware and
procedure question for later, recorded here, not a change made.

## Safety boundary

Software never fires the laser. The gun's light switch (trigger) is pressed by
a purely mechanical path the human operates: a second foot pedal pulling a
Bowden cable (bicycle brake cable) to a lever printed into the shell. A
microswitch on that lever only reports. Dry runs use the 0.3 mW reference beam
alone. Whether the X1 Pro exposes an external enable (the RS232/DB25 reading
is an earlier agent's, not re-verified) does not change this boundary.
Unknown: trigger force; what the process switch does.

## What the machine can learn without welding

1. **Corner finding.** Sweep X; the dot's image path kinks where it passes from
   cap to wall. Fit the corner per table angle.
2. **Runout map per tube.** Corner position and standoff at 72 table angles →
   r(θ), z(θ). First harmonic = eccentricity/tilt, second = ovality. The
   procedure's limits (≤0.25 mm radial TIR, ≤0.30 mm face TIR) become measured
   curves for each tube and each reseat.
3. **Compensation check.** Play X(θ), Z(θ) back during a dry revolution at weld
   speed; the residual dot-to-corner error is the number that matters.
4. **Reseat statistics.** Lift and reseat the same tube N times; lift and reseat
   the gun on its kinematic seat N times. Distributions, not impressions.
5. **Wire aim.** With the feeder jogged (by hand, or later by a relay across its
   jog button — a proposal needing Derek's look at the feeder), the tip's
   landing point relative to the dot, and its scatter as the wire's cast varies.
6. **Station drift.** Hold everything still overnight and watch the dot against
   the tube: creep of printed parts, temperature, cable settling.
7. **Cable sensitivity.** Move the umbilical by a known amount; watch the dot.
8. **Angle sweeps** (on carriers that can actuate angles): the swept line's
   wall/cap share against roll and tilt.

What it cannot learn dry: melt behaviour, lip distortion, penetration. Those
need coupons and welds, fired by the human; the station contributes identical
setups, full logs, and post-weld bead photographs, which is what makes a
one-variable-at-a-time campaign interpretable. Offset between the red beam and
the 1080 nm spot: one low-power mark on a scrap coupon, fired by the human,
photographed against the red dot, calibrates it.

## Open questions for Derek

- Does the reference beam sweep with the wobble when not firing?
- Trigger force and travel; what the process switch does.
- Mass and CoM of the gun; stiffness/weight of the umbilical near the grip.
- Does the wire feeder have a jog/inch button?

---

## Wave 3 additions

**PTZ cameras (Derek's automated-setup vision).**
- **Why.** Optical zoom lets a camera see the corner finely from ~1 m, out of
  the spatter. Estimate, assuming a 1/2.8 in sensor and ~88 mm focal length at
  full zoom: 10 µm/px at 0.6 m, 16 at 1 m, 24 at 1.5 m. The same camera can
  re-aim between the dot, the wire tip and the whole station.
- **Representative part.** FoMaKo 4K PTZ, 20× optical, $449 Prime, "100+
  bought in past month" (sourcing file).
- **Limit.** PTZ pointing is not metrology-grade. Printed fiducial tags on a
  fixed surface near the joint (a collar or portal) let every frame be
  registered, so a pan or zoom change does not move the measurement's
  reference.
- **Unknowns.** Minimum focus distance at full zoom; the control protocol
  (VISCA/UVC).

**Weld-time sensing.** The red dot is invisible during the weld. Two things
still see during it:
- fiducials on the shell, under narrowband LED light and a filter (gun pose);
- the D-s stylus on the tube's OD at the dot's angle (the wall's radial
  position, including thermal growth).

**Preload and a closed loop need each other** (carry-and-locate and I agree).
A camera loop makes a cheap mechanism accurate only if each drive's load keeps
one sign, so play becomes an offset rather than hysteresis. Balancer bias, gas
springs, gravity or tension provide that.

**A soft carrier cannot be servoed into a holder** (`calc/exchange/servoed_float.py`).
It can be servoed into a placer and a drift canceller. The hold during the weld
stays mechanical.
