# Pump mount fit trial

The base carries the production motor saddle, continuous snap pockets and broad
joined fixed-rail stops on a 7.4 mm lid plate. The clip is the exact production
54.5 mm printable cap. The pump's four complete rubber foot-and-leg assemblies
slide off before fitting it.

The stopping faces have 9.329 mm wide stock, with 7.1 mm of continuous outside
backing joined to the saddle. The straight rail corridor stays open. Fore stock
ends below the head lug; rear stock reaches the saddle top. The receiving
pockets retain their complete clearance. The base is one native solid and one
watertight printable mesh. [geometry.json](geometry.json) binds its source and
exported bytes.

## Print recipes

| Piece | Printer | Loaded nozzle/material | Estimated time | Material |
| --- | --- | --- | --- | --- |
| Base | Mark1 (`H2C`) | Left hardened 0.4 mm Standard, black PET-GF | 90 min | 52.26 g |
| Clip | Mark2 | Left hardened 0.4 mm Standard, black PET-GF | 50 min | 26.23 g |

The base prints flat in the production lid orientation, with three Classic
perimeters and 15% gyroid. Tree(auto)/Default remains enabled; Bambu generates
no support roads on this plate. The cap stands on its axial end, with three
Classic perimeters and a solid core. Both use the saved PET-GF cooling policy,
0.20 mm first layer and 0.24 mm layers above it. Full-bead bed margins are
114.785 mm for the base and 127.002 mm for the cap.

Mark1's +0.18 mm user trim emits `G29.1 Z0.16`; Mark2's +0.04 mm user trim
emits `G29.1 Z0.02`. [print-jobs.json](print-jobs.json) names the reviewed
archives and launch receipts. Submission uses Timelapse On, Bed Leveling On,
Flow Calibration Auto and Nozzle Offset Calibration Auto. Starts are separated
by at least 180 seconds.

## Pump trial

1. Lower the bare pump vertically into the saddle. Check that the fixed rails
   seat and the center cable cover and rough head underside remain clear.
2. Press the continuous upper clip down until both hooks seat along their
   length. Check rocking and fore/aft play against the broad stop faces.
3. Release both hooks and lift the pump vertically. Record seating force,
   retention, release, contact marks and any printed interference.

The [physical result](physical-result.json) reports failed empty-cap retention.
The [rear snap retention trial](../rear-snap-retention/README.md) carries the
replacement pump and four rear equipment pairs.

## Reproduce

[`build.py`](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/print-tests/pump-mount-fit/build.py) exports the isolated base from the production mount generator.
Run it through [`python3 tools/run.py --cad -- <CAD Python> .../build.py`](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/tools/run.py).
[`prepare.py --piece pump-fit-base`](https://github.com/derekbreden/homesodamachine/blob/f5e8bed0919827aec6fba620a4b8f15010b70d3d/hardware/print-tests/pump-mount-fit/prepare.py) prepares and reviews only the base; it never
sends a job. The cap archive retains the already reviewed production G-code
without reslicing.

The [recorded preparation source](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/print-tests/pump-mount-fit/build.py) retains the source revision for these physical artifacts.
