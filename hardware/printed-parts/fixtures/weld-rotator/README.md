# Cap-weld tube rotator

PET-GF fixture that stands a 5-inch 316L carbonator tube vertically and turns
it under the operator-held laser-weld head. The stationary structure is a
[300](WR_BASE_X) × [250](WR_BASE_Y) × [12](WR_BASE_Z) mm base, four
[24](WR_BASE_CLEARANCE) mm riser feet, and a separate motor tower. The feet
leave the already-welded lower plate's two ports reachable from below. The
rotating structure is a large ball-race turntable, an integral
[90](WR_TABLE_TEETH)-tooth HTD-5M pulley, and a replaceable tube nest.

The purchased 550-5M-15 belt runs from that pulley to the purchased
[20](WR_MOTOR_TEETH)-tooth 6.35 mm-bore motor pulley. The reduction is
[4.5:1](WR_RATIO), and the belt sets a nominal shaft centre distance of
[125.1](WR_CENTER) mm. The motor slots begin one millimetre inside that point
and run seven millimetres outward. The complete motor cradle slides in those
slots, so belt tension is an assembly adjustment and never a reprint.

## Printed parts

| File | Qty | Function |
|---|---:|---|
| `weld-rotator-base.step` | 1 | Stationary bed, bearing race, bench-clamp holes, motor-tower inserts |
| `weld-rotator-base-foot.step` | 4 | Raises the base above the bench without obstructing the lower-port service path |
| `weld-rotator-motor-tower.step` | 1 | Stationary shelf with outward belt-tension slots |
| `weld-rotator-motor-cradle.step` | 1 | Sliding pilot-register cup for the purchased 23HS30-2804S motor |
| `weld-rotator-motor-clamp-pad.step` | 2 | Load-spreading pads for the cradle's four M3 side screws |
| `weld-rotator-ground-tower.step` | 1 | Stationary support for the continuity shoe |
| `weld-rotator-ground-arm.step` | 1 | Replaceable in-plane leaf spring that holds the copper shoe on the tube |
| `weld-rotator-turntable-90t.step` | 1 | Moving disk, upper bearing race, 90T pulley, nest register, purge bore |
| `weld-rotator-pulley-coupon.step` | 1 first | Twelve grooves and both flanges; verifies the actual belt before the turntable print |
| `weld-rotator-ball-cage.step` | 1 | Spaces the [36](WR_BALLS) stock Ø[10](WR_BALL_D) mm PP balls |
| `weld-rotator-retainer.step` | 1 | Captures the turntable below the base without preloading the race |
| `weld-rotator-tube-nest.step` | 1 | Replaceable dual-surface register for the 5-inch tube end |
| `weld-rotator-jaw-cap.step` | 3 | Curved pressure shoe between each radial M3 screw and the tube OD |
| `weld-rotator-ground-shoe.step` | 1 C110 | 6.35 × 20 × 30 mm stationary contact cut from the acquired copper bar |
| `weld-rotator-assembly.step` | — | Reference assembly with tube, balls, motor, and 20T pulley proxies |

All thirteen printable shapes are PET-GF. The base is deliberately a single
large print: the [165](WR_BALL_RACE) mm race and the motor-tower mounting
stations read the same uninterrupted bed plane, so no bolted base seam can
become angular runout.

## The moving datum

The tube end lands in one annular pocket:

- a Ø[123.30](WR_PILOT_OD) × [4.5](WR_PILOT_H) mm ID pilot, with
  [0.20](WR_PILOT_CLEAR) mm nominal radial clearance;
- a Ø[127.80](WR_OUTER_BORE) outer guide, with
  [0.40](WR_OUTER_CLEAR) mm nominal radial clearance;
- three 14-degree jaw caps, each driven by an M3 × 25 screw through a heat-set
  insert in the outer collar.

The ID pilot is shorter than the welded plate's [6.35](WR_RECESS) mm recess, so
the same nest accepts a bare tube end or the already-welded first end. The
outer guide starts the tube without forcing its ovality round. The three jaw
caps then take up clearance and provide the indicator adjustment. Their
curved faces spread the screw load across the tube instead of point-loading the
0.065-inch wall.

A Ø[90](WR_SERVICE_BORE) mm passage continues through the nest, turntable,
retainer, and base. It clears a 25.4 mm service envelope around either recessed
end-cap port, and the four feet leave [24](WR_BASE_CLEARANCE) mm below the base.
For the second closure, attach the purge hose to one lower port before loading
the vessel, route it through this passage, and leave the other lower port open
as the purge vent.

The nest is the only tube-size-specific printed part. A tapered Ø80 register
centres it on the turntable and three M3 screws retain it. A fit correction or
a later tube size therefore costs one [150](WR_NEST_OD) mm part, not the base,
bearing, pulley, or motor mount.

## Bearing and drive

The turntable runs on [36](WR_BALLS) of the acquired 10 mm polypropylene
balls. Their centres lie on a [165](WR_BALL_RACE) mm circle, spaced
[14.4](WR_BALL_PITCH) mm apart in a 2 mm cage. Matching toroidal grooves in the
base and turntable receive 2 mm of each ball. The wide race carries the 2.01 kg
finished vessel without asking the centre hub to locate the axis; the hub only
retains the two halves and leaves a Ø30 purge/service passage.

The 90T pulley is integral to the turntable. Its 5 mm angular pitch and 2.1 mm
groove depth match the HTD-5M belt; the printed groove is a clearance profile,
not a metrology transfer standard. Check the first 12-tooth coupon against the
actual belt before committing the turntable print. The installed 20T pulley has
[127.1°](WR_WRAP) of wrap, just over seven engaged teeth. That is ample for
bearing drag and the vessel's inertia; it is intentionally not a wire-stick
lock. If filler wire catches, release the deadman pedal and let the belt/motor
yield instead of using the fixture as a rigid puller.

## Fasteners and stock already in the ledger

- 36 × 10 mm PP bearing balls.
- 1 × ESP32-DevKitC-32E, 1 × ESP32 screw-terminal breakout, and 1 ×
  ULN2803A module for the controller.
- The acquired 5 V / 3 A 11-tip adapter with its Micro-USB tip for logic
  power, and the acquired USB-C-to-TTL adapter for flashing and the stopped
  serial console. No unrecorded USB cable is required.
- Acquired 22 AWG wire, ferrules, 1/4-inch braided sleeve, and heat-shrink for
  the pedal and low-voltage control harness, plus one acquired 4.7 kΩ resistor
  for the pedal input's external pull-up.
- 6 × ruthex M5 × 9.5 inserts and 6 × M5 × 10 SHCS: four
  motor-tower-to-base and two ground-tower-to-base.
- 27 × ruthex M3 short inserts. Screws from acquired stock: 8 × M3 × 25
  base-foot retainers, 4 × M3 × 10 cradle retainers, 4 × M3 × 8 motor-pad
  screws, 3 × M3 × 10 nest retainers, 3 × M3 × 25 jaw adjusters, 3 × M3 × 8
  underside retainers, 2 × M3 × 12 ground-arm retainers, and 1 × M3 × 10
  ground-shoe screw into tapped copper.
- One 6.35 × 20 × 30 mm shoe cut from the acquired 1/4-inch C110 copper flat
  bar; drill and tap its lower side M3 for the retaining screw.
- The ordered NEMA 23 + DM542T kit, 24 V supply, foot pedal, 20T pulley, 550 mm
  belt, and test indicator.

## Print

Material: Polymaker Fiberon PET-GF15, dried and printed with the project's PET-GF
profile. Use the 0.4 mm tungsten-carbide nozzle for the nest and jaw caps; the
0.8 mm hardened high-flow nozzle is suitable for the base, tower, turntable,
cage, and retainer.

- Base: bottom face on the bed, 6 walls, 6 top/bottom layers, 25% gyroid. Do
  not use a brim inside either race.
- Base feet: broad face on the bed, 5 walls, 40% gyroid. Keep both vertical
  screw bores clear.
- Turntable: hub opening on the bed, pulley and nest pedestal upward, 6 walls,
  30% gyroid. Keep the upper race free of support material.
- Motor tower: print on either Y side so the shelf and both gussets are layer
  profiles, not a bridge.
- Motor cradle: base down, with the Ø38.6 passage vertical. Motor clamp pads:
  print on either 48 × 12 mm face; keep the screw-tip sockets clean.
- Ground tower: print on its foot. Ground arm: print flat, with the leaf and
  shoe fork in the bed plane; use 100% infill and reject any layer separation.
- Nest and jaw caps: 0.20 mm layer, 6 walls, 100% infill. Print the nest on its
  register face and the jaw caps on either flat radial end.
- Cage and retainer: flat.

Deburr the races with a plastic scraper only. Abrasive changes their common
radius and becomes axial runout.

## Assembly

1. Heat-set six M5 tower inserts in the base. Heat-set three M3 nest inserts in
   the turntable, three M3 retainer inserts in the hub, three M3 jaw inserts in
   the nest, two M3 ground-arm inserts in the ground tower, four M3 inserts
   upward from the motor-cradle underside, four M3 inserts inward from its two
   outside walls, and two M3 inserts downward from the top of each base foot.
2. Fasten the four feet from the base top with eight flush M3 × 25 screws. Set
   the fixture on its feet and pass a 25.4 mm test cylinder through both lower
   port positions in the Ø90 mm service opening; neither the base nor retainer
   may obstruct it.
3. Place the base flat. Lay the cage in the lower race and load 36 sorted 10 mm
   balls. Reject any ball that differs visibly or by more than 0.05 mm from the
   median diameter.
4. Lower the turntable through the cage. Fit the underside retainer inside the
   Ø[126](WR_RETAINER_POCKET) × 6 mm base recess. Tighten its three flush SHCS
   against the 1 mm printed
   bosses; the bosses meet the hub while the retainer rim stays 1 mm below the
   base shoulder. Nothing projects below the base or carries running load.
5. Bolt the motor tower to its four registered stations. Put the cradle on its
   shelf and start four M3 × 10 screws upward through the slots; leave them
   loose. Drop the 23HS30-2804S face-down into the cradle so its Ø38.1 pilot
   enters the Ø38.6 passage. Slide one pad down each Y side and advance the
   four M3 × 8 side screws evenly until the frame cannot rock. The motor's
   official drawing calls out four plain Ø5.2 mm flange holes, so those holes
   are deliberately unused.
6. Fit the 20T pulley with its belt land level with the turntable's printed
   pulley. Install the 550 mm belt at the inboard end of the slots, slide the
   complete cradle outward until the long span twists about 90 degrees with
   finger pressure, then tighten the four underside cradle screws.
7. Bolt the nest to its register. Put one jaw cap on each M3 adjuster tip; the
   Ø2.85 blind socket is the retention fit.
8. Run the turntable dry for ten revolutions, clean the race, and re-check belt
   tracking before loading a tube.
9. Bolt down the ground tower and flexure arm. Fit the C110 shoe with its one
   M3 screw; its contact face sits 1.0 mm inside the nominal tube surface and
   deflects the long leaf outward when a tube is loaded.

## Continuous work contact

Clamp the laser welder's work lead to the exposed upper 18 mm of the C110 shoe,
not to the tube and never to the PP bearing. The stationary shoe wipes the tube
OD 15–45 mm above the nest and leaves the work cable still through every lap.
Scuff only that contact stripe and the copper face immediately before welding.
With the welder disabled, meter shoe-to-tube continuity while `mode jog` turns
two complete revolutions. Any blink is a stop condition: clean the faces or
increase the flexure preload before enabling the laser.

## Indicating the tube

Drop the tube into the nest until its cut rim seats. Bring all three jaw screws
to contact, then advance them in small equal increments. Put the ordered test
indicator on the tube OD close to the working end and adjust the three screws
until radial runout is at or below 0.25 mm TIR. Seat the indicator's magnetic
base on the exposed stationary steel lamination face of the NEMA 23; it will
not hold correctly on the PET-GF base or the 316L tube. Lock both arm joints
and shake-test the base before turning. Read the end-cap face separately; face
runout at the weld circle must be at or below 0.30 mm TIR.

The tube's working rim is [212.4](WR_TUBE_TOP) mm above the base bottom and
[236.4](WR_TUBE_TOP_BENCH) mm above the bench. The
highest PET-GF near the tube is the ground arm at 86 mm, leaving more than
126 mm of metal between the closure weld and printed structure.

## Control

`firmware/src_weld_rotator/` runs on an acquired ESP32-DevKitC-32E. The foot
pedal is a 3.3 V deadman input. The ESP32 drives DM542T PUL and DIR through an
acquired ULN2803A module with the driver's logic selector set to 5 V. The
acquired 5 V adapter and its Micro-USB tip power the ESP32/logic side; the
ordered 24 V brick powers only the DM542T and motor. The acquired USB-C-to-TTL
adapter supplies the stopped-only setup console without becoming a power
source.

Default mode is a 380-degree lap at 8 mm/s bead travel. The pedal must remain
held; release is an immediate abort, and a completed lap will not restart until
the pedal has been released. `speed 5` through `speed 15` changes the stored
travel-speed setpoint without changing any mechanical part. `mode jog` makes
the pedal a direct hold-to-turn setup control.

## Regenerate and verify

```bash
tools/cad-venv/bin/python hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py selftest
```

## Reference data

[value](NAME) texts are updated by:
- `/hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py`

Purchased motor dimensions and winding data:
- [STEPPERONLINE 23HS30-2804S](https://www.omc-stepperonline.com/nema-23-bipolar-1-8deg-1-9nm-269oz-in-2-8a-3-2v-57x57x76mm-4-wires-23hs30-2804s)

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py`
