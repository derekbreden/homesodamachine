# Dry-observation camera stages

Two manually retractable, level-camera mounts for the FoMaKo K20UH 4K and
Raynox DCR-250. Each camera and its removable lens module move together on two
400 mm SBR12 rails. The camera remains at zero pan/tilt during an experiment.
This assembly has no live-laser optical barrier.

The [manifest](manifest.json) owns dimensions, quantities, source links,
geometry checks and export hashes. The [shop guide](../../../gun-positioner-guide/README.md)
owns illustrated assembly operations and full-size printing instructions.
The [purchase list](../../../gun-positioner/purchases.md) covers both stages
without duplicating metal stock or fastener packs with the gun fixture.

## Fabrication set

| Part | Quantity | Stock or print |
|---|---:|---|
| camera-fixed-plate | 2 | 400 × 300 × 6.35 mm 6061 aluminum |
| camera-carriage-plate | 2 | 300 × 300 × 6.35 mm 6061 aluminum |
| lens-upright | 2 | 100 × 200 × 6.35 mm 6061 aluminum |
| lens-angle | 2 | 50.8 × 50.8 × 6.35 mm aluminum angle, cut 80 mm wide |
| camera-rail-stop | 8 | Same angle, cut 60 mm wide; trim upright and fork per STEP |
| 4040 riser | 4 | 300 mm length, 40-series slot 8 |
| lens-cassette | 2 | PET-GF, flat rear lip on bed |
| lens-retainer | 2 | PET-GF, flat on bed |
| lens-shim | 4 | PET-GF, 0.40 mm each, printed as two 0.20 mm layers; fit spares |

The metal plates have STEP and millimeter DXF files. The two angle faces have
separate drilling projections. The forked rail stop is a three-dimensional
angle; its STEP and guide view govern the notch, rather than a flat-plate
outline. Printed pieces have STEP, STL and viewer payloads.

The SBR12 drawing gives a 30 mm-wide, 4 mm-thick rail base; the shaft center
is 22.5 mm above the base and the block top is 40 mm above it. The four M5
holes on each block are 26 mm along the rail and 28 mm across. Use the actual
rails as transfer-drilling templates for the fixed plate: the catalog base
holes are diameter 4 mm, 22 mm across and 100 mm along, but their phase from
the end is not specified. Drill 3.5 mm clearance for M3 bolts, deburr, and
verify that the supplied holes pass those bolts. Do not force M4 bolts into
the rail bases.

## Mount and height

Two 4040 risers under each fixed plate attach to the same rigid bench frame
as the rotator. Four M8 threaded posts anchor in slot-8 T-nuts. Support and
lock the fixed plate between metal nuts and washers, maintaining a horizontal
plate and a 20–70 mm gap above the risers. The default 55.70 mm gap puts the
proxy optical axis at 278.40 mm above the bench. The 130 mm camera optical
height is an envelope assumption; set the actual height from the seam image
after the camera is parked, without tilting its PTZ head.

Lock both plate faces and each extrusion foot. Trim each post to no more
than 22 mm above the fixed-plate underside; the carriage underside is 46.35 mm
above it, or 40 mm above the rail base. Deburr the cut. Sweep the full carriage by hand with power removed
to verify post, nut and cable clearance. Use the metal corner brackets to
attach the risers to the station; do not rely on camera mass to keep them
stationary.

Four blocks span 100 mm along the rails and 180 mm across. The carriage center
runs from +100 mm forward to −100 mm retracted. The metal stops meet the
block edges at ±169.5 mm, below the carriage. At the forward position, two
M5 × 70 bolts and two 40 mm metal spacer tubes bridge the fixed and moving
plates. Fit washers and nuts, then lock the carriage without bending the
plates. Remove both bolts and tubes before retracting. Store the loose clamp
parts together. Every return requires a fresh calibration; it has no claimed
micrometer return accuracy.

Place the two stages where complementary views expose the seam, actual wire
endpoint, aiming dot and rigid gun references. Begin with the lens front
approximately 109 mm from the work, then find the measured focus and useful
field. That distance is the Raynox manufacturer's infinity-focus reference,
not a calibrated measurement for the assembled camera. Keep cable strain
relief on the stationary frame and a slack loop for the 200 mm retraction.

## Lens module and camera startup

Remove the complete front module—angle, upright, cassette and retainer—before
powering the PTZ camera. Its startup movement has no qualified clearance with
the module installed. Power up the unobstructed head, park at zero pan and
tilt, disable autofocus/tracking, and establish manual optical settings.
Reinstall the module on its marked carriage datums. Do not move the head by
hand or use it as a lifting handle.

The manufacturer's drawing gives a 53 mm lens outer diameter, 18.5 mm overall
length, and a 3 mm rear-thread projection; the body excluding that projection
is 15.5 mm long. The cassette has a 53.4 mm pocket, a 2 mm rear lip and a
43.6 mm rear opening. The rear thread passes the lip; the metal body shoulder
rests on it. The 18 mm cassette leaves 0.5 mm axial clearance before the
retainer. Use M3 × 20 cover screws with no head washer. Support the four rear
nut-pocket roofs locally; remove those supports through the open rear pockets
and check flat seating before fitting the nuts. The captive hex nuts
seat at the back of their 2.8 mm pockets; verify full nut engagement and that
the screw tips remain clear of the aluminum upright. Use the 0.4 mm shim
where needed and adjust cover screws to retain
the metal rim without squeezing the optics. The retainer's 49.4 mm opening
must not touch the glass. Verify fit on one printed cassette before printing
the second set; the 0.4 mm diametral allowance is a proposed fit, not an
accepted print result.

The upright's slots set lens height to the parked camera; the camera tripod
slot adjusts the gap behind the lens. Verify camera clearance, a clear field
and focus before tightening. Choose the washer stack under the 1/4-20 tripod
screw so it clamps the camera without bottoming in its socket. No socket
depth is assumed.

## Qualification and regeneration

CAD validity and hashes establish file integrity and nominal geometry. They
do not establish lens fit, optical uncertainty, loaded stiffness or hot-weld
survival. Record those results in the commissioning dataset. Before a live
weld, remove and retract this dry-only observation assembly; the process's
live observation and beam containment have separate acceptance requirements.

Regenerate by hand:

```sh
tools/cad-venv/bin/python tools/gun-positioner-optics/mounts.py
```

This opens no camera, controller, printer or welder. The source is
[mounts.py](../../../../tools/gun-positioner-optics/mounts.py).
