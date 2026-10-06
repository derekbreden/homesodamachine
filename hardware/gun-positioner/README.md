# PGFUN two-axis weld positioner

Build one compact swivel-and-pivot gun fixture attached to the existing
rotator's stationary base. Each joint uses a coaxial NEMA 17 motor and PGFUN
50:1 reducer. Two lined bands support the measured gun housing from below.
Printed geometry fixes the other nominal pose coordinates. One camera
learns and checks the aiming dot and actual wire endpoint during dry runs;
the controller then replays the accepted periodic correction during welding.

This is the build package for the working attempt. It contains the printable
parts, assembly instructions, load calculations, wiring, compiled firmware,
camera extraction and dry-run trajectory learning. Physical commissioning
remains necessary for received fits, loaded positioning and the welding
process. No measured performance is asserted for unbuilt hardware.

## Build package

| Item | Governing source |
|---|---|
| Assembly | [Step-by-step instructions](assembly.md), [printable shop guide](../gun-positioner-guide/gun-positioner-guide.pdf) |
| CAD | [Editable parameters](../printed-parts/fixtures/pgfun-positioner/design.json), [complete STEP](../printed-parts/fixtures/pgfun-positioner/assembly.step), [STL print pack](../printed-parts/fixtures/pgfun-positioner/print-pack.zip) |
| Printing | [Part manifest](../printed-parts/fixtures/pgfun-positioner/print-manifest.json) and [print preparation](assembly.md#print-and-prepare) |
| Cost | [Prime purchases and exact fastener allocation](purchases.md) |
| Engineering | [Load paths, limits and accuracy](engineering.md), [numerical clearance](../printed-parts/fixtures/pgfun-positioner/clearance-check.json), [load screen](../printed-parts/fixtures/pgfun-positioner/load-screen.json) |
| Electrical | [Wiring and interlocks](control.md) |
| Software | [Firmware and host commands](../../firmware/src_pgfun_positioner/README.md), [compiled UF2](../../firmware/src_pgfun_positioner/assets/pgfun-positioner-r1.uf2) |
| Commissioning | [Loaded mechanical and control checks](commissioning.md), [one-camera learning and dry laps](observation.md) |

New purchases total **$479.36 before tax** for the mechanism and controller.
The specified camera and Raynox lens add **$524.50**, giving **$1,003.86**
before tax with observation. Filament, the existing rotator/welder, two cable
post clamps, wiring, resistor stock and the listed reused fasteners are
already on hand; their consumption is accounted for separately. Prices and
Prime delivery observations are dated in the purchase record.

## Motion and process limits

Both soft limits are +/-1 degree. Nominal printed hard stops are +/-1.5
degrees. At the 145 mm nominal working lever, one issued microstep corresponds
to approximately 1.42 micrometres. The advertised 20 arcsecond gearbox
backlash corresponds to 14.1 micrometres at that lever. Actual useful movement
is learned under the real gun and cable load, including both reversal
directions; neither specification establishes achieved accuracy.

The camera's qualification requirement is at most 0.010 mm observed error,
with a 0.005 mm 95th-percentile target, for both the dot and wire endpoint.
These are projected image-plane measurements. One view cannot establish
unobserved depth, incidence angle or working focus. The fixed print pose and
weld procedure establish those process coordinates.

The supplied 60-degree attitude and 16 mm nozzle gap are explicit editable
mounting parameters. No successful working values were recorded in the
available project history. Establish focus and working attitude on a
sacrificial joint and regenerate the mating cradle/cheeks if necessary.

The supplied release uses the existing rotator pedal as a timing input,
with its 200 ms cold-start settling interval. Every replay starts from the
same indexed tube orientation, speed, direction, fixture datum and cable
routing as the accepted dry laps. It has no tube-angle sensor. Independent
dry laps must demonstrate that this timing is sufficiently repeatable.

The camera stand withdraws before emission. First welding uses the factory
gun trigger and qualified trajectory replay. Automatic laser triggering
requires the welder's captured or manufacturer-specified protocol.
The already purchased isolated RS232 adapter and DB9 breakouts are sufficient
for [receive-only capture](../../tools/x1_control/README.md); no additional
interface purchase is required to begin that work. DB25 enable is not
documented as the trigger command.

## Rebuild and verification

From the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/pgfun-positioner/build.py
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/pgfun-positioner/check.py
python3 firmware/src_pgfun_positioner/make_geometry.py
```

The firmware header, release image and learned response/trajectory files
bind to the generated geometry hash. Regenerating geometry invalidates
their prior binding. Recompile and repeat the affected mechanical and
observational checks after a geometry change.
