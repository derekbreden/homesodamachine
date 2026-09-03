# Cap-weld rotation rig

This bench fixture stands the 5-inch 316L carbonator tube vertically and turns
it under the operator-held XLaserlab X1 Pro head while either end-cap closure
is welded. The tube end in the fixture may be bare or already closed; the
replaceable nest registers on both its ID and OD without reaching an installed
end plate.

The fixture is the tooling for steps 3 and 5 of
[`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md). It rotates the
work only; it does not carry the welding head. The foot pedal never commands
the laser.

## The built system

| Element | Current part |
|---|---|
| Motion | STEPPERONLINE 23HS30-2804S NEMA 23, 2.8 A/phase, with DM542T driver |
| Power | BTF-LIGHTING 24 V, 4 A Class 2 adapter and its included female barrel-to-wire connector |
| Logic power | Acquired universal 5 V, 3 A adapter using its Micro-USB tip |
| Deadman | HimaPro 50122 cast-aluminum SPDT pedal, wired as a low-voltage `COM`–`NO` contact |
| Reduction | Purchased 20T × 15 mm HTD-5M pulley, purchased 550-5M-15 belt, integral printed 90T pulley |
| Controller | Acquired ESP32-DevKitC-32E and ULN2803A module |
| Indicating | Ordered Neoteck 0.0005-inch test indicator and magnetic base |
| Structure | PET-GF base and four riser feet, rail motor tower, sliding motor carriage and pads, turntable with a screwed-on upper race ring and spool, tube nest, bearing cage and continuity arm |
| Rotary bearing | 36 acquired 10 mm PP balls on a 165 mm pitch circle |
| Work contact | Stationary 6 × 25 × 50 mm shoe made by one 25 mm crosscut from the acquired nominal 1/4 × 2 inch C110 bar; no copper drilling |

The order records and ownership status are in
[`purchases.md`](/hardware/ledger/purchases.md). Printable geometry, individual
STEP files, assembly STEP and print instructions are in
[`fixtures/weld-rotator/`](/hardware/printed-parts/fixtures/weld-rotator/README.md).
The dedicated controller is
[`src_weld_rotator/`](/firmware/src_weld_rotator/README.md).

## Joint and speed

The end plate is an ID-fit plug recessed [6.35 mm](RECESS). Its outer face and
the tube bore make a circular corner fillet:

| Quantity | Value |
|---|---:|
| Weld-circle diameter | [123.70 mm](BEAD_D) |
| One revolution at the bead | [388.61 mm](BEAD_C) |
| Rotating mass, first / second closure | [1.40 kg](MASS_FIRST) / [2.01 kg](MASS_SECOND) |
| Allowed bead travel | [5 mm/s](SPEED_MIN)–[15 mm/s](SPEED_MAX) |
| Corresponding table range | [0.772–2.316 rpm](RPM_WINDOW) |

Travel speed is the recipe setting; table rpm follows from `v = ωr` at the
tube ID. The current 12 mm/s wire-feed setting is shown only to make deposited
area visible during process iteration:

| Travel | Table rpm | 360° | 380° | Step pulses/s | Calculated triangular fillet leg at [12 mm/s](WIRE_FEED) wire |
|---:|---:|---:|---:|---:|---:|
| 5 mm/s | [0.772](RPM_5) | [77.7](REV_5) s | [82.0](LAP_5) s | [185.3](PULSE_5) | [1.48](LEG_5) mm |
| 6 mm/s | [0.926](RPM_6) | [64.8](REV_6) s | [68.4](LAP_6) s | [222.3](PULSE_6) | [1.35](LEG_6) mm |
| **8 mm/s** | **[1.235](RPM_8)** | **[48.6](REV_8) s** | **[51.3](LAP_8) s** | **[296.4](PULSE_8)** | **[1.17](LEG_8) mm** |
| 10 mm/s | [1.544](RPM_10) | [38.9](REV_10) s | [41.0](LAP_10) s | [370.6](PULSE_10) | [1.05](LEG_10) mm |
| 12 mm/s | [1.853](RPM_12) | [32.4](REV_12) s | [34.2](LAP_12) s | [444.7](PULSE_12) | [0.96](LEG_12) mm |
| 15 mm/s | [2.316](RPM_15) | [25.9](REV_15) s | [27.3](LAP_15) s | [555.8](PULSE_15) | [0.85](LEG_15) mm |

The 5–15 mm/s bounds keep the calculated wire-only triangular leg between
0.85 and 1.48 mm and keep a full revolution between 25.9 and 77.7 seconds.
The drive has more speed available, but the controller clamps commands to this
process-development window; changing speed outside it requires an explicit
firmware and procedure review.

Start at **[8 mm/s](SPEED_NOM)**. It is centered inside the useful window, runs
the table at [1.235 rpm](RPM_NOM), and completes a 360° + [20°](OVERLAP_DEG)
lap in [51.3 s](LAP_NOM). Keep laser power, wobble, wire feed, standoff and
shielding fixed while changing one variable. Use 1 mm/s speed increments after
the first 316L coupon; record PT, section and hydro results beside the exact
stored setpoint. This is the commissioning window for iteration, not a
qualified weld schedule; coupon evidence sets the production value.

At 3,200 pulses per motor revolution and a [4.5:1](RATIO) reduction, the table
has [14,400](TABLE_PULSES) pulses/revolution. One pulse is
[0.025°](TABLE_STEP_DEG), or [0.027 mm](TABLE_STEP_MM) at the bead. The default
380° lap is exactly [15,200](LAP_PULSES) pulses, independent of elapsed-time
error. The motor turns only [5.558 rpm](MOTOR_RPM_NOM) at the nominal recipe.

## Mechanical fixture

The stationary base is one 300 × 250 × 12 mm PET-GF print. Four 10 mm bench
holes make clamping part of setup, and the rotary race and motor-tower inserts
share the same uninterrupted printed datum. Four printed feet hold the base
[24 mm](BASE_CLEARANCE) above the bench. A concentric [90 mm](SERVICE_BORE)
passage through the nest, turntable, retainer, and base exposes both recessed
ports in an already-welded lower end plate, so the second closure has a real
purge inlet and outlet rather than trapping the connections against the bench.

The 36-ball, 165 mm diameter race carries the vessel load near the tube wall
rather than through a flexible center spindle. Both grooves are printed as top
faces: the lower one in the base, the upper one in a separate race ring that
is screwed groove-down to the turntable's flat underside. A spool enters the
base from below and screws up into the turntable; its flange rim sits inside a
126 × 6 mm base recess with a 1 mm axial running gap to the base shoulder, so
it catches lift without carrying running load.

The turntable carries an integral 90T HTD-5M pulley. With the purchased 20T
pulley and 550 mm belt, nominal shaft center distance is
[125.1 mm](BELT_CENTER). The purchased pulley is 20 mm long on the motor's
21 mm shaft. Its motor-side flange is gauged 0.25 mm off the front face of the
motor's 1.6 mm-long Ø38.1 pilot, placing its 16 mm land from 33.5 to 49.5 mm
above the base bottom and centered in the printed tooth zone. The outer flange
stands 0.85 mm beyond the nominal shaft end, so the shaft tip is not an axial
datum. The motor hangs face-down in a printed carriage whose 2 mm skin
registers the face pilot and clears the complete land envelope by 1.85 mm; two
side pads clamp the 57.3 mm frame, and four slotted M3 screws into the tower's
rail tops supply 8 mm of outward tension adjustment. The tower is two rails
and a rear wall that stay outside the belt's swept path across that whole
travel. Two M5 × 12 countersunk screws pass through 10.2 mm 90-degree recesses
in the carriage arms and engage the rear pair of the motor's tapped flange
holes; the front pair stays open because the belt's swept path crosses it at
full tension.
Small-pulley wrap is [127.1°](SMALL_WRAP), or
[7.1](SMALL_WRAP_TEETH) engaged teeth. Print and check the 12-tooth belt coupon
against the delivered belt before printing the complete turntable.

The direct belt train is backdrivable. Releasing the pedal removes step motion,
and a wire catch can yield through the motor rather than pulling against a
self-locking gearbox.

## Tube datum and runout

The replaceable 150 mm nest uses three surfaces:

- a 123.30 mm × 4.5 mm ID pilot, giving 0.20 mm nominal radial clearance;
- a 127.80 mm OD guide, giving 0.40 mm nominal radial clearance;
- three direct-contact M3 adjusters at 120°, installed through radial heat-set
  inserts in the outer collar.

The pilot is shorter than the 6.35 mm end-cap recess. A welded plate therefore
clears it, while a bare tube still supplies the same ID datum. The loose guides
load the part repeatably without forcing a thin, slightly oval tube round; the
three screws supply the final indicator adjustment through continuous radial
passages to the tube OD. Their stations are staggered between the nest-retainer
wells, with the ID pilot backing the tube at each contact.

Three M3 × 10 screws retain the nest to the turntable. Each is installed from
above through a straight Ø6.2 mm well in the nest's ID pilot and seats in a
recess in the 10 mm base. The underside register socket preserves 3.2 mm of
straight engagement, then its annular cavity closes through opposed 45-degree
roofs instead of a broad unsupported ceiling.

With the tube seated, seat the indicator's magnetic base on the exposed
stationary steel lamination face of the NEMA 23, lock both arm joints, and
shake-test it. PET-GF and the 316L tube are not magnetic-base datums. Indicate
the OD as close to the working end as the head clearance permits. Acceptance
is:

- radial runout at the weld end **≤ 0.25 mm TIR**;
- end-cap face runout at the weld circle **≤ 0.30 mm TIR**.

A part outside either limit is not corrected with more screw force. Verify that
the lower rim is seated, then square the tube end or correct the end-cap seat.
The adjusters touch lightly; they do not deform the 0.065-inch wall.

## Continuous work contact

The laser's work lead clamps to the exposed 38 mm top of the stationary C110
shoe. The PET-GF ground arm places its face 1.0 mm inside the nominal tube
surface, so its 5 mm in-plane leaf stays loaded against the tube through
runout. The shoe is one 25 mm crosscut from the acquired
[YTKavq 1/4 × 2 × 12 inch C110 bar](https://www.amazon.com/dp/B0DR2PX6TT),
stood with the stock's 2-inch width vertical. A printed shelf carries its cut
edge and one M3 side clamp grips it through a heat-set insert in the arm; the
copper has no drilled or tapped feature. The bar's delivered thickness window
leaves 0.75–1.50 mm of preload when the tube seats the shoe against the fork's
back wall. The PP balls and printed races are not part of the electrical path,
and no cable turns with the vessel.

Scuff the tube contact stripe and copper immediately before use. With the laser
disabled, meter shoe-to-tube continuity through two dry revolutions. Any blink
fails setup. This contact exists for the welder's conductance interlock; it is
not a protective-earth connection.

## Driver, pedal and wiring

Set the DM542T logic selector to **5 V** and use two acquired ULN2803A channels
as open-collector sinks:

| Connection | Destination |
|---|---|
| ESP32 GPIO25 → ULN IN1; ULN OUT1 | DM542T `PUL-` |
| ESP32 GPIO26 → ULN IN2; ULN OUT2 | DM542T `DIR-` |
| ESP32 `VIN/5V` | DM542T `PUL+` and `DIR+` |
| ESP32 GND | ULN GND and pedal `COM` |
| ESP32 GPIO27 with internal pull-up | pedal `NO` |
| ESP32 3V3 through acquired 4.7 kΩ resistor | ESP32 GPIO27 |
| acquired 5 V adapter, Micro-USB tip | ESP32 Micro-USB power input |
| motor black / green | DM542T `A+` / `A-` |
| motor red / blue | DM542T `B+` / `B-` |
| included female barrel connector + / − | DM542T `VDC` / `GND` |

Leave ULN `COM` and DM542T `ENA+`/`ENA-` unconnected. The acquired 5 V adapter
powers the ESP32 and 5 V signal loops. The 24 V adapter powers only the
optically isolated driver power stage; never connect 24 V to the ESP32.

For flashing and setup, plug the DevKitC's own Micro-USB into the host. Its
onboard CP2102 carries the upload, the automatic bootloader reset and the
115200 baud console, and it powers the board while connected. Store the
settings, then move the Micro-USB to the acquired 5 V adapter's tip for bench
use. The onboard bridge drives `RX0/TX0` whenever the board is USB-powered, so
no external TTL adapter is connected to those pins.

The driver settings are 3.76 A peak, 50% standstill current and 3,200
pulses/revolution:

| Switch | SW1 | SW2 | SW3 | SW4 | SW5 | SW6 | SW7 | SW8 |
|---|---|---|---|---|---|---|---|---|
| Position | ON | OFF | OFF | OFF | ON | ON | OFF | ON |

The pedal is a dry contact on 3.3 V, not a motor-power switch. Twist its `COM`
and `NO` conductors together; the external 4.7 kΩ pull-up gives the long bench
lead a firm released state in the welder's electrical environment. Opening the
contact always stops new pulses. The controller also refuses motion at boot
until it has observed the pedal released.

## Stored controls

Connect the ESP32 USB serial console at 115200 baud. Commands are accepted only
while stopped and persist in NVS:

```text
status
speed 8.0
overlap 20
mode lap
mode jog
direction cw
direction ccw
dirinvert on
defaults
```

`lap` is the weld mode: press and hold for the counted 380° move. Release early
and motion aborts. When the count completes, motion stops even if the pedal is
still down and cannot restart until the pedal is released. `jog` follows the
pedal for indicating, belt run-in and positioning. `speed 5` through `speed 15`
changes the process window without a pulley, gearbox or printed-part change.

During dry commissioning, mark the table and verify `direction cw` from above.
If it moves counterclockwise, issue `dirinvert on` once. Wire lead/trail
orientation is set only after this direction convention is true.

## Build and commissioning gates

1. Generate the fixture and print the pulley coupon. The delivered belt must
   fully seat across all 12 grooves without riding the flanges.
2. Print the base, four riser feet, and rotating parts; install heat-set
   inserts, the race ring, sorted balls, the spool, motor tower, carriage,
   motor pads, pulley and belt per the fixture README. Prove a 25.4 mm service
   envelope at both end-cap port positions through the raised base before
   loading a tube.
3. With no tube, run ten jog revolutions in each direction. The belt must stay
   between both flanges, the race must not bind, and the spool flange must
   remain unloaded.
4. Install the tube and indicate it to the radial/face limits above.
5. Install the copper contact. Meter two complete jog revolutions without one
   continuity dropout.
6. Time one dry revolution at 5, 8 and 15 mm/s: targets are 77.7, 48.6 and
   25.9 s. Each must be within ±1%; a stall, skipped tooth or audible step loss
   fails the drive.
7. Hold the pedal at boot; the table must remain still. Release, press to jog,
   then unplug one pedal lead; the table must stop.
8. In lap mode with a paper index mark, hold the pedal through completion. The
   final mark must be 20° past its start and motion must not repeat until a
   release.
9. Run a complete disabled-laser rehearsal with head, wire guide, purge hose,
   work lead and operator position present. Nothing may enter the belt or wrap
   around the tube.

## Per-weld sequence

1. Clamp the base to the bench. Confirm laser disabled, pedal released and
   controller in `mode jog`.
2. Seat the tube's opposite end in the nest. Bring all three tube adjusters to
   light contact and indicate the working end to ≤0.25 mm radial TIR.
3. Seat and tack the end plate per `pressure-vessel.md`; verify ≤0.30 mm face
   TIR. For the first closure, feed back-purge argon through the open held end.
   For the second, connect purge to one completed lower-plate port through the
   raised Ø90 mm passage and leave the other lower port open as the outlet.
4. Clean and engage the copper shoe. Prove uninterrupted continuity for one dry
   revolution.
5. Set `mode lap`, selected speed and overlap while stopped. Return the index
   to the first tack. Establish shielding and place the wire on the arriving
   side of the puddle for the verified direction.
6. Hold the head at the qualified angle and standoff, then press and hold the
   pedal. Once rotation is steady, hold the laser trigger for the bead. The
   fixture stops after [15,200](LAP_PULSES) pulses.
7. At the stop, keep the trigger held and lift the head straight away so the
   X1 Pro retract/patch cycle breaks the wire in air. Then release trigger and
   pedal.
8. Continue with PT and hydrostatic inspection in `pressure-vessel.md`. Record
   speed, direction, overlap and runout with the result.

This sequence does not relax laser guarding, eye protection, extraction,
argon-asphyxiation controls or pressure-vessel inspection. Rotation is an
additional bench motion and receives its own pinch-point clearance before the
laser is enabled.

## Regenerate

```bash
tools/cad-venv/bin/python hardware/assembly/_weld_rotation_rig_sync.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py
~/.platformio/penv/bin/pio test -e native -f test_weld_rotator_policy
~/.platformio/penv/bin/pio run -e weld_rotator
```

## Reference data

[value](NAME) texts are updated by:
- `/hardware/assembly/_weld_rotation_rig_sync.py`

Purchased drive data:
- [STEPPERONLINE 23HS30-2804S motor](https://www.omc-stepperonline.com/nema-23-bipolar-1-8deg-1-9nm-269oz-in-2-8a-3-2v-57x57x76mm-4-wires-23hs30-2804s)
- [STEPPERONLINE DM542T V4.0 manual](https://www.omc-stepperonline.com/download/DM542T_V4.0.pdf)

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_weld_rotation_rig_sync.py`
