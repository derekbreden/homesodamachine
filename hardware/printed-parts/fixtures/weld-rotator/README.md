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
[125.1](WR_CENTER) mm. The motor carriage's slots begin one millimetre inside
that point and run seven millimetres outward, so belt tension is an assembly
adjustment and never a reprint.

## Printed parts

| File | Qty | Function |
|---|---:|---|
| `weld-rotator-base.step` | 1 | Stationary bed, lower bearing race, bench-clamp holes, motor-tower and ground-tower inserts |
| `weld-rotator-base-foot.step` | 4 | Raises the base above the bench without obstructing the lower-port service path |
| `weld-rotator-motor-tower.step` | 1 | Two rails and a rear wall outside the belt's swept path; carries the carriage on four M3 inserts |
| `weld-rotator-motor-carriage.step` | 1 | Sliding pilot skin and clamp walls for the purchased 23HS30-2804S motor |
| `weld-rotator-motor-clamp-pad.step` | 2 | Load-spreading pads for the carriage's four M3 side screws |
| `weld-rotator-ground-tower.step` | 1 | Stationary support for the continuity shoe |
| `weld-rotator-ground-arm.step` | 1 | Replaceable [5.0](WR_GROUND_BEAM_T) mm in-plane leaf spring that holds the copper shoe on the tube |
| `weld-rotator-turntable-90t.step` | 1 | Moving disk, 90T pulley, nest register, purge bore; flat underside carries the race ring and spool |
| `weld-rotator-race-ring.step` | 1 | Upper bearing race, printed groove-up and screwed groove-down to the turntable |
| `weld-rotator-spool.step` | 1 | Hub and lift-catch flange, inserted through the base and screwed up into the turntable |
| `weld-rotator-pulley-coupon.step` | 1 first | Twelve grooves and both flanges; verifies the actual belt before the turntable print |
| `weld-rotator-ball-cage.step` | 1 | Spaces the [36](WR_BALLS) stock Ø[10](WR_BALL_D) mm PP balls |
| `weld-rotator-tube-nest.step` | 1 | Replaceable dual-surface register for the 5-inch tube end |
| `weld-rotator-ground-shoe.step` | 1 C110 | [6](WR_GROUND_SHOE_T) × [25](WR_GROUND_SHOE_W) × [50](WR_GROUND_SHOE_Z) mm stationary contact cut from nominal 1/4 × 1 inch bar |
| `weld-rotator-assembly.step` | — | Reference assembly with tube, balls, belt, motor, and 20T pulley proxies |

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
- three radial M3 × 25 adjusters through heat-set inserts in the outer collar,
  with their tips bearing directly on the tube OD.

The ID pilot is shorter than the welded plate's [6.35](WR_RECESS) mm recess, so
the same nest accepts a bare tube end or the already-welded first end. The
outer guide starts the tube without forcing its ovality round. The three
direct-contact screws then take up clearance and provide the indicator
adjustment. Bring each tip only to contact; the screws locate the tube and do
not supply forming or clamp force to its 0.065-inch wall.

A Ø[90](WR_SERVICE_BORE) mm passage continues through the nest, turntable,
spool, and base. It clears a 25.4 mm service envelope around either recessed
end-cap port, and the four feet leave [24](WR_BASE_CLEARANCE) mm below the base.
For the second closure, attach the purge hose to one lower port before loading
the vessel, route it through this passage, and leave the other lower port open
as the purge vent.

The nest is the only tube-size-specific printed part. A tapered Ø80 register
centres it on the turntable and three M3 screws retain it. A fit correction or
a later tube size therefore costs one [150](WR_NEST_OD) mm part, not the base,
bearing, pulley, or motor mount. The tube-adjuster screws ride on the
turntable, so any screw is brought to an open side of the fixture by jogging
the table before it is adjusted.

Each nest retainer is driven from above. Its Ø[6.2](WR_NEST_RETAINER_ACCESS) mm
straight access well passes through the ID pilot to the recessed head seat in
the 8 mm base.

Each tube adjuster enters from the collar's outside face through a 5.2 mm-deep
Ø4.0 heat-set-insert bore. A continuous
Ø[3.4](WR_TUBE_ADJUSTER_BORE) mm passage runs from the insert to the tube guide;
the screw tip is the tube contact. The adjuster stations are staggered between
the nest-retainer wells and bear against the tube over the ID pilot.

## Bearing

The turntable runs on [36](WR_BALLS) of the acquired 10 mm polypropylene
balls. Their centres lie on a [165](WR_BALL_RACE) mm circle, spaced
[14.4](WR_BALL_PITCH) mm apart in a 2 mm cage. Matching toroidal grooves
receive the balls from above and below. Both grooves are printed as top faces:
the lower one is in the base, and the upper one is in a separate
[6](WR_RACE_RING_H) mm race ring that is printed groove-up and then screwed
groove-down to the turntable's flat underside with three flush M3 × 8 screws.
The ball's running contact is therefore a first-layer flat in both directions,
never a bridged or supported ceiling.

The wide race carries the 2.01 kg finished vessel without asking the centre
hub to locate the axis. The spool — a Ø112 hub with a Ø124 flange — enters the
base's Ø114 bore from below and three M3 × 25 screws draw it up against the
platter. Its flange rim sits inside the base's Ø[126](WR_SPOOL_POCKET) × 6 mm
recess, 1 mm below the base shoulder, so it catches lift without carrying
running load, and its Ø90 bore continues the purge/service passage.

## Belt plane and drive

The purchased 20T pulley is 20 mm long with Ø35 flanges and no boss, and the
motor shaft is 21 mm. The pulley is gauged [0.25](WR_PULLEY_PILOT_GAP) mm away
from the front face of the motor's 1.6 mm-long Ø38.1 pilot. With the motor face
at [53.35](WR_MOTOR_FACE_Z) mm, the pulley's 16 mm land runs from
[33.5](WR_BELT_Z0) to [49.5](WR_BELT_Z1) mm above the base bottom and is centred
in the printed 90T tooth zone. The pulley's outer face stands
[0.85](WR_PULLEY_OVERHANG) mm beyond the nominal shaft end; the shaft end is
not its assembly datum. Nothing stands between the motor face and the belt
except the carriage's [2](WR_SKIN_H) mm skin. The skin's Ø38.6 hole registers
the face pilot and lets the Ø35 pulley flanges pass. Even the complete 16 mm
land envelope clears the skin by [1.85](WR_LAND_SKIN_CLEAR) mm; the centred
15 mm belt has another 0.5 mm.

The tower is two rails outside the belt's spans and a rear wall behind the
pulley's wrap, on the base's four M5 stations. Its rail feet seat the M5
heads at the same depth as the ground tower's; above the belt's height the
rails narrow away from the spans. The carriage's arms follow the belt's swept
path with 2 mm of clearance across the whole 8 mm tension travel and land on
the rail tops through four slotted M3 × 10 screws. Two side walls with 3 mm
pads clamp the 57.3 mm frame; the face pilot in the skin, not the pads, takes
the belt tension. The motor's four Ø5.2 flange holes are deliberately unused.
The fixture selftest intersects a belt proxy at both ends of the tension
travel with every stationary part and requires 1.5 mm of clearance.

The 90T pulley is integral to the turntable. Its 5 mm angular pitch and 2.15 mm
groove depth match the HTD-5M belt; the printed groove is a clearance
trapezoid, [3.6](WR_PULLEY_OPENING) mm wide at the tip circle, that accepts the
belt tooth's 3.05 mm root and absorbs the pitch error a printed 142 mm pulley
accumulates over its 45 engaged teeth. It is not a metrology transfer
standard. Check the first 12-tooth coupon against the actual belt before
committing the turntable print. The installed 20T pulley has
[127.1°](WR_WRAP) of wrap, just over seven engaged teeth. That is ample for
bearing drag and the vessel's inertia; it is intentionally not a wire-stick
lock. If filler wire catches, release the deadman pedal and let the belt/motor
yield instead of using the fixture as a rigid puller.

## Fasteners and stock

- 36 × 10 mm PP bearing balls.
- 1 × ESP32-DevKitC-32E, 1 × ESP32 screw-terminal breakout, and 1 ×
  ULN2803A module for the controller.
- The acquired 5 V / 3 A 11-tip adapter with its Micro-USB tip for bench
  power, and the Micro-USB data cable already used to flash the project's
  other DevKitC boards for upload and the stopped serial console.
- Acquired 22 AWG wire, ferrules, 1/4-inch braided sleeve, and heat-shrink for
  the pedal and low-voltage control harness, plus one acquired 4.7 kΩ resistor
  for the pedal input's external pull-up.
- 6 × ruthex M5 × 9.5 inserts and 6 × M5 × 10 SHCS: four
  motor-tower-to-base and two ground-tower-to-base.
- 30 × ruthex M3 short inserts. Screws from acquired stock: 8 × M3 × 25
  base-foot retainers, 3 × M3 × 25 spool screws, 3 × M3 × 8 race-ring screws,
  4 × M3 × 10 carriage screws, 4 × M3 × 8 motor-pad screws, 3 × M3 × 10 nest
  retainers, 3 × M3 × 25 tube adjusters, 2 × M3 × 12 ground-arm retainers, and
  1 × M3 × 10 ground-shoe screw into tapped copper.
- Cut one [50](WR_GROUND_SHOE_Z) mm shoe from nominal 1/4 × 1 inch C110
  copper flat bar. The [12-inch HWYEE bar](https://www.amazon.com/dp/B0CSP36RQ7)
  and [8-inch VERNUOS bar](https://www.amazon.com/dp/B0GT1JFRVP) share this
  fit. The fork accepts 6–7 mm thickness and widths through 26.5 mm. From one
  25 mm edge, drill and tap M3 with its axis 3 mm behind the tube-contact face
  and 6 mm above the cut bottom; the retaining screw fixes the contact-face
  datum rather than relying on the stock's thickness tolerance.
- The NEMA 23 + DM542T kit, 24 V supply, foot pedal, 20T pulley, 550 mm
  belt, and test indicator.

## Print

Material: Polymaker Fiberon PET-GF15, dried and printed with the project's PET-GF
profile through the 0.4 mm nozzle.

This rig is what set that profile's first layer. Its two large parts are the ones in
the tree whose first layer is a single unbroken circle metres long — the
[165](WR_BALL_RACE) mm ball race round the base and the 90T pulley round the
turntable — so a point on that loop cools for a full lap before the nozzle returns to
it. Two plates failed there in the first layer or two, while the front-top, the pump
cartridge and the display covers came off the same profile clean. The profile lays its
first layer at the print's own 280 °C and stands the nozzle at a +0.17 mm z-trim
([`/hardware/printed-parts/z-trim.md`](/hardware/printed-parts/z-trim.md)). Both of these
plates are worth watching through their first two layers rather than left alone.

- Base: bottom face on the bed, 6 walls, 6 top/bottom layers, 25% gyroid. Do
  not use a brim inside the race.
- Base feet: broad face on the bed, 5 walls, 40% gyroid. Keep both vertical
  screw bores clear.
- Turntable: flat underside on the bed, pulley and nest pedestal upward, 6
  walls, 30% gyroid. Nothing on it needs support; disable support so none
  lands in the pulley grooves or the insert pockets.
- Race ring: flat back on the bed, groove upward, 100% infill. Deburr the
  groove with a plastic scraper only. Abrasive changes its radius and becomes
  axial runout.
- Spool: flange on the bed, hub upward, 5 walls, 30% gyroid.
- Motor tower: on its feet, rails upward. The four M5 access holes and the
  four rail insert pockets print as vertical bores.
- Motor carriage: on either Y side, so the skin, arms and clamp walls are
  layer profiles and the pilot hole is a vertical circle. Motor clamp pads:
  print on either 48 × 12 mm face; keep the screw-tip sockets clean.
- Ground tower: print on its foot. Ground arm: print flat, with its
  [5.0](WR_GROUND_BEAM_T) mm leaf and shoe fork in the bed plane; use 100%
  infill and reject any layer separation.
- Nest: 0.20 mm layer, 6 walls, 100% infill, on its register face. Keep the
  three radial stepped adjuster passages clear.
- Cage and coupon: flat.

Deburr the base race with a plastic scraper only, for the same reason as the
ring.

## Assembly

1. Heat-set six M5 tower inserts in the base. Heat-set M3 inserts: three nest
   inserts down from the turntable's register face; three spool and three
   race-ring inserts up from the turntable's flat underside; three tube-adjuster
   inserts inward from the nest collar's outside face; two in the ground tower;
   four inward from the carriage's two
   outside walls; four downward into the tower's rail tops; and two downward
   from the top of each base foot.
2. Fasten the four feet from the base top with eight flush M3 × 25 screws. Set
   the fixture on its feet and pass a 25.4 mm test cylinder through both lower
   port positions in the Ø90 mm service opening; neither the base nor spool
   may obstruct it.
3. Screw the race ring to the turntable's underside, groove down, with three
   flush M3 × 8 screws. Check that no screw head stands proud of the ring's
   groove face.
4. Place the base flat. Lay the cage in the lower race and load 36 sorted 10 mm
   balls. Reject any ball that differs visibly or by more than 0.05 mm from the
   median diameter.
5. Lower the turntable onto the balls. From below, pass the spool up through
   the base's Ø114 bore and drive three M3 × 25 screws through its flange into
   the platter. The flange rim stays 1 mm below the base shoulder and nothing
   projects below the base.
6. Bolt the motor tower to its four M5 stations with a 4 mm hex key down the
   access holes. Set the carriage on the rail tops and start four M3 × 10
   screws through its slots at the inboard end; leave them loose.
7. Before the motor goes in, measure the pulley's actual overall length. Slide
   it onto the shaft until the distance from the front face of the motor's
   Ø38.1 pilot to the pulley's outer face is that length plus
   [0.25](WR_PULLEY_PILOT_GAP) mm; a 0.25 mm / 0.010 inch feeler blade between
   the motor-side flange and pilot sets the same gap. Clock one set screw onto
   the D-flat, tighten it, then tighten the second screw against the round.
   Withdraw the feeler and spin the pulley by hand to verify an air gap to the
   stationary pilot. Hang the belt on the 90T pulley and hold the free bight
   open under the carriage's pilot hole. Lower the 23HS30-2804S face-down: the
   pulley passes through the hole into the bight, and the Ø38.1 pilot seats in
   the skin. Slide one pad down each Y side and advance the four M3 × 8 side
   screws evenly until the frame cannot rock.
8. Slide the complete carriage outward until the long belt span twists about
   90 degrees with finger pressure, then tighten the four carriage screws.
9. Seat the nest on its register and drive three M3 × 10 retainers straight
   down through its access wells. Thread the three M3 × 25 tube adjusters into
   their radial inserts, then back every tip fully clear of the OD guide before
   loading a tube.
10. Run the turntable dry for ten revolutions, clean the race, and re-check
    belt tracking before loading a tube.
11. Bolt down the ground tower and flexure arm. Slide the cut C110 shoe into
    the fork with its marked contact face toward the tube and fit its one M3
    screw. The tapped hole fixes that face 1.0 mm inside the nominal tube
    surface and deflects the long leaf outward when a tube is loaded.

## Continuous work contact

Clamp the X1 Pro work lead to the exposed upper
[38](WR_GROUND_SHOE_EXPOSED) mm of the C110 shoe, not to the tube and never to
the PP bearing. The stationary shoe wipes the tube OD 15–65 mm above the nest
and leaves the work cable still through every lap. Scuff only that contact
stripe and the copper face immediately before welding. With the welder
disabled, meter shoe-to-tube continuity while `mode jog` turns two complete
revolutions. Any blink is a stop condition: clean the faces before enabling
the laser.

## Indicating the tube

Drop the tube into the nest until its cut rim seats. Bring all three tube
adjusters to light contact, then advance them in small equal increments. Put
the test indicator on the tube OD close to the working end and adjust the three
screws until radial runout is at or below 0.25 mm TIR. Seat the indicator's
magnetic base on the exposed stationary steel lamination face of the NEMA 23;
it will not hold correctly on the PET-GF base or the 316L tube. Lock both arm
joints and shake-test the base before turning. Read the end-cap face separately;
face runout at the weld circle must be at or below 0.30 mm TIR.

The tube's working rim is [212.4](WR_TUBE_TOP) mm above the base bottom and
[236.4](WR_TUBE_TOP_BENCH) mm above the bench. The
highest PET-GF near the tube is the ground arm at 86 mm, leaving more than
126 mm of metal between the closure weld and printed structure.

## Control

`firmware/src_weld_rotator/` runs on an acquired ESP32-DevKitC-32E. The foot
pedal is a 3.3 V deadman input. The ESP32 drives DM542T PUL and DIR through an
acquired ULN2803A module with the driver's logic selector set to 5 V. The
acquired 5 V adapter and its Micro-USB tip power the ESP32/logic side on the
bench; the 24 V brick powers only the DM542T and motor. Flashing and the
stopped-only setup console use the DevKitC's own Micro-USB from the host.

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
