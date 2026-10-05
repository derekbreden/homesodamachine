# Six-axis gun-positioner control

The development controller executes small, coordinated, signed screw moves. A host
computer observes the gun and seam, learns the response, and requests another
correction. This package provides the controller firmware, USB client, nominal
kinematics, local-response fitting and dry simulation. It provides no laser output.
Physical construction and camera measurements are unqualified until commissioning
records actual results.

## Controller and coordinates

Use a **headered RP2040 Raspberry Pi Pico**, six **BIGTREETECH TMC2209 V1.3 modules** on separately
labeled, home-built socket/terminal carriers, and a regulated **24 V / at least 5 A enclosed brick**. The host's
Micro-USB data cable and a separate 24 V-to-5 V buck power the Pico through
isolated supply paths. Driver VIO is Pico 3.3 V. Motor 0 V and logic
GND meet at the controller distribution star; this is a common-ground system.
The buck's 5 V output feeds VSYS through a 1N5819, band toward VSYS; the Pico's
onboard diode supplies the USB path. External 5 V does not connect to VBUS.
Unconverted 24 V never connects to a Pico power pin or an unprotected GPIO.
[Raspberry Pi dual-power guidance, §4.5](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf).

The [purchase requirements](controller-purchase-requirements.json) define electrical
ratings and counts. The [wiring manifest](wiring-manifest.json) names every node,
wire route, color and Pico header position. Selected Prime purchases and stock
reconciliation belong in [sourcing](sourcing/).

Axis order is always **X, Y, Z, U, V, W**. U is yaw-screw extension, V pitch-screw
extension, and W roll-screw extension. Their zero is 180 mm pin-to-pin clevis
length; increasing extension is positive angular motion. The mechanics use
TR8×2 screws, 4:1 belts and 200-full-step motors. At 16 external microsteps,
**6,400 issued STEP edges mean 1 mm nominal slide travel or angular screw extension**.
Positive Z raises the carriage and decreases physical screw span from its fixed
top thrust. Its initial electrical DIR polarity is inverted; accept every
axis's sign by observed motion. A full motor step
has 2.5 µm nominal extension. Neither value establishes attained displacement.

| Coordinate | Firmware soft range | Physical switch / stop design |
|---|---:|---|
| X, Y, Z | −544,000…+544,000 counts, corresponding to ±85 mm nominal | Switch near ±89 mm; metal stop at ±94 mm |
| U, W | −326,307…+329,471 counts relative to 180 mm length, ±20° | Switch at ±21°; metal stop at ±22° |
| V pitch | −326,307…+166,782 counts relative to 180 mm length, −20…+10° | Switch at −21 / +11°; metal stop at −22 / +12° |

The angular count bounds conservatively enclose the attainable integer targets
inside each axis's angular range for the 150 mm lever / 180 mm neutral clevis geometry. Camera calibration establishes the
actual center, mounting transform and useful workspace. Central datum is a
manual fixture/reference operation, not an automatic move to a hard limit.
After every reset, stop, limit trip or disarm, establish that datum again before
referencing. Do not issue `REF` at an arbitrary stopped position.

## Fixed driver settings

The firmware reads all six drivers separately. Address straps are:

| Driver | UART bus | Address | MS1 | MS2 |
|---|---|---:|---|---|
| X | A | 0 | GND | GND |
| Y | A | 1 | 3V3 | GND |
| Z | A | 2 | GND | 3V3 |
| U | B | 0 | GND | GND |
| V | B | 1 | 3V3 | GND |
| W | B | 2 | GND | 3V3 |

Each bus has a **330 Ω / 1% resistor** from Pico TX to the common PDN_UART node, RX connected
directly to that node, and a **1.8 kΩ / 1% pull-up** to 3.3 V. Three V1.3 modules
place their three 20 kΩ R6 pull-downs in parallel. Including conservative 5%
R6 tolerance, internal pulls and leakage, the released bus remains above
0.7 × VIO; a replying driver sinks less than 2 mA. Pico TX drives HIGH outside
reply windows, and both UART GPIO pad pulls are disabled. During each reply
the firmware releases TX only after the request has fully transmitted.
Verify the received backplane's undriven idle level before coupling motors.
These bounds use the [module schematic](https://github.com/bigtreetech/BIGTREETECH-Stepper-Motor-Driver/blob/master/TMC2209/V1.3/Schematic/TMC2209%20V1.3-SCH.pdf)
and [chip DC characteristics, §20.2](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf),
with the [RP2040 GPIO output limits](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf).
Keep these buses within the fixed control backplane. Module/carrier labels are authoritative: check the
received V1.3 pinout against its supplier drawing before socket insertion.
An A4988-style carrier label such as `MS3`, `RESET` or `SLEEP` does not identify
PDN_UART. Fit and photograph the named-pin map; do not orient a module by the
trimmer's position. VM, VIO and both GND positions must all match.

Build each carrier from isolated-pad protoboard, two eight-position female
sockets fitted to the received module, screw terminals and insulated jumpers.
The supplier's P1A schematic numbers below identify nets; they do not substitute
for checking the actual module's view and mating orientation. Mark the VM end
on socket and module, and mark the underside solder map before insertion.

| BTT P1A pin | Net | Carrier connection |
|---:|---|---|
| 1 / 2 | DIR / STEP | Named axis outputs |
| 3 | CLK | GND for internal oscillator |
| 4 | UART_TX | Leave unconnected; factory R10 bridge remains unpopulated |
| 5 | UART_RX / PDN_UART | Axis's A or B shared UART node |
| 6 / 7 | MS2 / MS1 | Address straps in the table above |
| 8 | EN / ENN | Shared GP16 enable node |
| 9 / 10 | VS / GND | Fused 24 V VM / 0 V star |
| 11 / 12 | A2 / A1 | Named motor-coil terminals |
| 13 / 14 | B1 / B2 | Named motor-coil terminals |
| 15 / 16 | VIO / GND | 3V3 logic rail / 0 V star |

P1B pads 17 INDEX, 18 DIAG and 19 VREF are not host outputs; VREF is the measured
trimmer test point. The IC's SPREAD pin has no module header; do not invent one.
Leave factory R7 unpopulated. UART selects SpreadCycle and firmware also rejects
DRV_STATUS.stealth. Route VM/motor current on the specified heavy wire directly
between terminals rather than through thin protoboard traces. Meter every
terminal-to-socket connection and adjacent-pin isolation with modules removed;
cover and strain-relieve the completed backplane.

The configuration uses fixed SpreadCycle, 16 external microsteps, no interpolation,
no adaptive current and no autonomous driver velocity. With R110 sense resistors,
the nominal manufacturer formula is
`IRMS = (CS+1)/32 × VFS/(0.110+0.020) / √2`.
VSENSE1 selects VFS=180 mV; loaded Z uses VSENSE0/VFS=325 mV.
Hold and run scales are equal on each axis.

| Profile | X / Y / Z / U / V / W current scales | Estimated RMS current | Peak rate |
|---|---|---|---:|
| bench | 10 / 10 / 10 / 10 / 10 / 10 | 0.337 A on all axes | 2,000 counts/s |
| loaded-development | 10 / 10 / 22 / 10 / 14 / 10 | Z 1.271 A; pitch V 0.459 A; others 0.337 A | 1,000 counts/s |

The **bench** image is for disconnected-belt motor/direction checks;
loaded development uses its named image only after retention acceptance. These
are initial current settings, not measured force limits or demonstrated running
torque. Status reports the named profile, six configured `current_scales`,
`configured_vsense` and decoded `vsense`/`microsteps` readings and rate.
Bench configured VSENSE is `[1,1,1,1,1,1]`; loaded is `[1,1,0,1,1,1]`.
Unverified readings are null. CHOPCONF is 0x04030005 on VSENSE1 axes and
0x04010005 on loaded Z, with each axis's full register checked before ARM.
Confirm both sense resistors are R110; a different value requires
recalculation and a rebuilt image. Loaded Z is nominally 1.797 A peak.
Applying the datasheet's +5% internal-reference tolerance and an **assumed**
−5% R110 tolerance gives 1.970 A peak. BTT's schematic specifies 0.11 Ω
but does not establish that resistor tolerance; this arithmetic is a sizing
screen, not a calibrated coil-current guarantee. The guarded fan and loaded
response/50°C temperature gates govern physical use. Retaining equal hold/run current avoids an
idle-current transition during initial response measurements. Motor and carrier
temperature, attained movement and overload behavior decide subsequent tuning.
UART SENDDELAY is 2, or 24 bit times, on both shared buses. IFCNT verifies
ten configuration writes per driver after all nodes' turnaround is primed.
The driver write counter and readable configuration registers are verified;
thermal-warning, shutdown, short, reset, changed configuration and failed UART
checks inhibit motion. [TMC2209 manufacturer datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC2209_datasheet_rev1.09.pdf).

Set each received module's VREF trimmer to its measured minimum before
mechanical coupling. With motors disconnected and ENN HIGH, identify its
VREF test point from the received module drawing, measure against module GND,
and record the minimum voltage; do not infer adjustment direction from another
board. Digital configuration disables analog current scaling, but a reset
driver can fall back to its trimmer and strap settings. Minimum VREF is a
backup condition that must be checked on the received modules.

## Wiring sequence

The [fixed controller mounting set](mounting/README.md) supplies the backplane,
28 insulating spacers and fan stand, with a quantified bolt/nut/washer
allocation. Transfer received component holes after arranging meter/fuse access;
use the specified unfilled PETG stock and two fan guards. Recheck cold isolation
after mounting.

1. With the 24 V brick unplugged and **MOTOR POWER OFF**, label carriers X/Y/Z/U/V/W.
   Meter carrier rails and map its socket to the received module's named pins.
   Install no driver until VM/VIO/GND correspondence and power polarity are checked.
2. Route red/black 18 AWG from the brick connector to F0, a 5 A DC fuse, and the
   0 V star. F0 feeds relay COM; relay NO feeds the switched VM distribution.
   Each of six VM branches has its own starting 1 A DC fuse. Keep motor returns
   separate from the thin signal wiring until the star.
3. Feed the 24 V relay coil from its own 500 mA branch fuse through
   **MOTOR POWER**, **STOP NC1**, then **BREAKAWAY CH1**. Coil minus
   goes to 0 V. Fit a 1N4007 across the coil, band at coil plus. A verified diode
   already in the socket can supply this function. The NO power contact must
   have a manufacturer rating of at least 24 V DC / 6 A; an AC-only rating is
   insufficient. Pressing STOP drops motor VM independently of the Pico.
4. Wire the independent **STOP NC2** low-voltage loop from GP26 through COM/NC
   back to GND. A 10 kΩ pull-up at the Pico makes an opened/unplugged loop HIGH.
   The two stop contact circuits share no switch terminal.
   Reserve separate BREAKAWAY CH1 terminals in the coil chain and BREAKAWAY
   CH2 terminals in the GP26 sense chain. Each channel contains an axial-release
   COM–NC contact and a plate-presence COM–NO contact in series. The seated plate
   holds the presence switch pressed; both complete channels are closed when
   healthy and open on release or a missing plate. Neither
   circuit shares a conductor/contact with the other. Unfitted contacts remain
   open; loaded operation requires the installed crash mount/contact acceptance.
   CH1 uses a **GX16-4** locking pair: pin 1 receives the fused/toggled/STOP-switched
   24 V line; pin 2 returns through the two crash contacts to relay COIL+;
   pins 3/4 remain unconnected. Neither used pole is a GND lead. CH2 uses a
   **GX12-2** pair: pin 1 comes from GP26 through STOP NC2, pin 2 returns to GND
   through its two independent crash contacts. These connector sizes cannot
   mate across the 24 V and GPIO circuits. Use the actual numbered contacts;
   plug/socket solder views are mirror images and must be continuity mapped.
5. Route one twisted white/black pair per axis. Wire low travel COM/NC,
   high travel COM/NC, negative overload COM/NC and positive overload COM/NC
   in series, returning to GND. Put a 10 kΩ pull-up from each input to 3.3 V.
   Leave axis-switch NO terminals unused. These are four contacts per axis,
   24 axis switches; the crash mount adds four, for 28 microswitches total.
   Either end, either force-link direction or any broken
   loop stops all six axes. Opening is acted on immediately; closing cannot
   restart motion. The same `travel_loop` fault reports which axis opened,
   not which of its four contacts. Static trip qualification is
   250–350 N for X/Y and upward Z, 440–500 N for downward Z,
   148–165 N for V pitch and 100–140 N for U yaw/W roll, including complete
   measurement uncertainty. Nominal electrical trip is
   ±0.75 mm XYZ and ±0.30 mm angular shuttle displacement; independent metal
   capture bounds each link at ±1.0 mm. Powered testing imposes only the upper
   force ceilings: 350 N X/Y/upward Z, 500 N downward Z, 165 N pitch and
   140 N yaw/roll, including measurement uncertainty. Use the per-axis
   acceptance table in the [wiring manifest](wiring-manifest.json) and the
   complete [commissioning gate](commissioning.md#3-passive-retention-and-load-support).
   A motor stall below preload is recorded, observed and stopped without retry;
   it does not qualify switch operation. Controlled switch actuation separately
   proves all-axis inhibition and latching. A tripped link has no powered escape.
6. Feed a regulated 24 V-to-5 V buck from unswitched F0 through a separate
   500 mA branch fuse. Meter its 5 V output before connecting. Feed output plus
   through a 1N5819 to Pico VSYS (physical pin 39), band toward VSYS; output
   minus goes to the 0 V star. Do not wire external 5 V to VBUS. This supply
   keeps Pico VIO and ENN logic valid when host USB is disconnected.
   Wire the Pico terminal adapter using the pin table below. Connect all VIO
   pins to the 3.3 V rail, all ENN pins to GP16, and a 10 kΩ pull-up on the
   shared ENN node. Reset/input-state GPIOs therefore leave drivers disabled.
   Fit UART address straps and connect only the correct three drivers per bus.
   Add a guarded 24 V fan across the six heatsinks, from switched VM through
   its own FFAN 500 mA fuse, returning to the 0 V star.
7. Fit at least 100 µF / 35 V local VM bypass at each carrier and 470 µF / 35 V
   at the switched VM distribution. Observe electrolytic polarity. Use short
   VM wiring and the module maker's carrier/bypass guidance; supply readings
   are not a measurement of switching transients.
8. Wire switched VM through 100 kΩ to GP27, then 10 kΩ from GP27 to GND, with
   100 nF across that lower resistor. Nominal 24 V gives approximately 2.18 V
   at GP27. Firmware screens 18–28 V with the nominal reference/divider values.
9. Identify each motor's two isolated coil pairs with a meter. Label them
   A1/A2 and B1/B2, and connect through a locking four-pole plug. Record actual
   wire colors. Keep coils in paired twists; support cables so they do not
   pull on a carrier socket or a moving axis. Mate motor/driver plugs with
   the brick unplugged, including when changing a coil's direction.

Connector allocation is seven GX16-4 pairs (six motors and one crash CH1) and
eight GX12-2 pairs (six axis loops, STOP sense and crash CH2). Label each pair
at both ends. A motor plug has pins 1/2=A1/A2 and 3/4=B1/B2; check the received
numbered contact view before soldering. Match actual harness continuity and
observed motor sign rather than wire-color conventions.

| Signal | Pico GP | Physical header pin |
|---|---:|---:|
| UART A TX / RX | 0 / 1 | 1 / 2 |
| X STEP / DIR | 2 / 3 | 4 / 5 |
| UART B TX / RX | 4 / 5 | 6 / 7 |
| Y STEP / DIR | 6 / 7 | 9 / 10 |
| Z STEP / DIR | 8 / 9 | 11 / 12 |
| U STEP / DIR | 10 / 11 | 14 / 15 |
| V STEP / DIR | 12 / 13 | 16 / 17 |
| W STEP / DIR | 14 / 15 | 19 / 20 |
| Shared ENN | 16 | 21 |
| X / Y / Z travel loops | 17 / 18 / 19 | 22 / 24 / 25 |
| U / V / W travel loops | 20 / 21 / 22 | 26 / 27 / 29 |
| STOP NC2 | 26 | 31 |
| Switched VM divider | 27 | 32 |
| 3V3 / GND star lead | — | 36 / 38 |
| Buck 5 V through external Schottky | — | VSYS 39 |

Header numbers refer to the Pico manufacturer's pinout, with Micro-USB at its
top. Terminal-adapter labels must agree before connecting.
[Raspberry Pi Pico pinout](https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf).

## Motion and faults

The Pico's 250 µs timer issues due axis edges together. A common cubic progress
curve starts and ends each segment at zero commanded velocity. Requests are
limited to 640 counts (0.1 mm nominal extension) per axis, 100–2,000 ms duration,
2,000 counts/s bench or 1,000 counts/s loaded-development peak rate and
12,000 counts/s² peak acceleration. Impossible
profiles are rejected. An interval over 500 µs or a need to emit multiple
catch-up edges at one tick latches a timing fault instead of sending a burst.
Stopping a partly issued segment preserves only issued-count history and
invalidates its reference; it never claims the gun reached its target.

The host sends a sequenced heartbeat every 100 ms. A 500 ms lapse inhibits
drivers and invalidates reference. A 250 ms hardware watchdog resets a stuck
foreground loop or pulse timer: it receives a kick only after a completed
timer cycle advances its counter. The external ENN pull-up disables reset GPIOs. Stop/limit/VM
inputs are sampled by the pulse timer. Driver polling checks one axis every
50 ms, covering six axes in about 300 ms. Every bad VM sample and observed
VM rising edge clears driver verification and reference in every state.
Restoring VM cannot restore a reference. `clear` reconfigures the six drivers;
`arm` performs a fresh six-driver GSTAT/DRV_STATUS/GCONF/CHOPCONF read while
ENN stays HIGH, completed within 50 ms and in the same VM epoch. It refuses a
failed read, reset, warning, configuration mismatch or interrupted supply.
These are programmed intervals, not
measured stop distances or a certified safety function.
[RP2040 watchdog documentation](https://www.raspberrypi.com/documentation/pico-sdk/hardware.html#group_hardware_watchdog).

**Gravity retention is mechanical.** Loss of USB, motor power, drive current,
controller firmware or a belt can release a load. The mechanical retainers and
catch capacity must be accepted with the assembled gun and supported
umbilical before loaded powered motion. Thread friction and motor holding
current are not the retention evidence. A fault does not return to a park
pose or reproduce a previous pose.

## USB interface and observation

Replies are newline JSON with boot token, device microseconds, controller state,
last accepted sequence, signed counts, completion sequence/time and input health.
Status also reports `vm_epoch` and completed safety `timer_ticks` for commissioning.
`STATUS`, `DRIVERS` and `STOP` require no token. Mutating requests require the
current boot token and exactly the next sequence number. Duplicate/stale
requests are rejected, and the host never retries an unacknowledged move.
`MOVE6` is acknowledged before completion; completion means issued edges ended,
not that the gun settled. See the [firmware protocol](../../firmware/src_gun_positioner/README.md).

The host records send/receive monotonic times around device timestamp replies.
Those brackets bound a software clock correspondence; USB receipt time is not
camera exposure time. Camera observations need native frame IDs, exposure/capture
times, fixed focus/zoom/exposure settings, detection uncertainty and paired-view
association. The rig's rotator has its own pedal, ESP32 and DM542T. Its console
services settings while stopped; it supplies no live phase stream. Use an
observed rotator fiducial in the camera records to learn phase during dry laps.
Do not infer live angle from USB arrival times or modify the accepted pedal
control as part of this controller build.

The supplied nominal kinematics convert each axis's bounded clevis angles to screw lengths,
preserve a nominal dot for an entered measured tool vector, and divide larger
targets into bounded actuator segments. Its local-response fitter accepts signed
trial vectors and independently observed feature changes; its correction solver
rejects insufficiently observable response matrices and bounds screw corrections.
Native camera acquisition, actual feature detection, frame/rotator registration,
loaded response data and a live welding observer are development integration
work. Their interfaces are in [commissioning](commissioning.md); synthetic examples
and computer tests do not qualify 5 µm physical positioning or live-weld visibility.
