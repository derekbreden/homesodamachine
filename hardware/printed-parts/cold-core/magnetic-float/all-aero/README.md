# All-ASA Aero magnetic float

One connected ASA Aero body encloses an RC62 ring magnet at its axial midplane.
The guide and reed interface serves the carbonator and both flavor reservoirs.

[Assembly](/3d?file=printed-parts/cold-core/magnetic-float/all-aero/assembly.step) ·
[Section](/3d?file=printed-parts/cold-core/magnetic-float/all-aero/section.step) ·
[Insertion view](/3d?file=printed-parts/cold-core/magnetic-float/all-aero/insertion.step) ·
[CAD source](all_aero_float.py) · [Calculations](design.json) ·
[Installation and reed calibration](installation.md)

## Geometry and lift

| Feature | Nominal dimension |
| --- | --- |
| Body diameter × height | 36 × 28 mm |
| Through guide bore / rod | 4.8 / 3.175 mm |
| Magnet center above bottom | 14 mm |
| RC62 OD × ID × thickness | 19.05 × 9.525 × 3.175 mm |
| Pocket OD × ID × depth | 19.35 × 9.225 × 3.60 mm |
| Collar between pocket and guide bore | 2.2125 mm |
| Outer radial band beside pocket | 8.325 mm |
| Magnet seat / pocket roof | Z12.4125 / Z16.0125 mm |
| Foam below magnet / above pocket | 12.4125 / 11.9875 mm |

The annular body displaces 27.994 cm³, excluding its open guide bore. Its
closed magnet pocket occupies 0.818 cm³; ASA Aero occupies 27.176 cm³.
At 0.9997 g/cm³ water density, full immersion displaces 27.985 g.
The RC62 contributes 5.09 g.

The sizing target is **5 g of spare lift at an assumed foam density of
0.65 g/cm³**. The calculated minimum height is 27.339 mm, rounded upward to
28 mm. The allowance is provisional; density and water uptake remain unmeasured.
Bambu's [ASA Aero data](https://bambulab-us.myshopify.com/products/asa-aero)
show that temperature, flow, speed and geometry affect foaming. The manufacturer's
0.46 g/cm³ specimen at 270 °C used 0.45 flow; this trial uses 0.52 flow.

| Assumed foam density, g/cm³ | Assembled mass, g | Spare lift, g | Guided upright freeboard, mm |
| --- | --- | --- | --- |
| 0.46 | 17.59 | 10.39 | 10.40 |
| 0.53 | 19.49 | 8.49 | 8.50 |
| 0.55 | 20.04 | 7.95 | 7.95 |
| 0.60 | 21.40 | 6.59 | 6.59 |
| 0.65 | 22.75 | 5.23 | 5.23 |
| 0.70 | 24.11 | 3.87 | 3.87 |

These estimates assume a dry pocket, retained body volume and no liquid uptake.
The design mass is 22.754 g and its magnet center is **8.766 mm below the water
surface** in the conservative sizing model. The midpoint of the solid is not
the liquid surface. Reed mounting heights need the finished float's measured
immersion and directional switching offsets.

## Current CAD and print preparation

The current CAD has a 3.60 mm pocket and preserves the magnet's Z14.0 center.
The expected insertion pause is before the first covering plane at Z16.2,
layer 81 at 0.20 mm. A separate native slice review must verify the seat,
last open pocket, pause and covering roads before another submission.
[`prepare_print.py`](prepare_print.py) writes into `mark2-print/v2` and a
separate v2 archive; no v2 archive has been prepared or submitted.

Mark2's recipe is the glued Engineering plate, +0.04 mm user trim, fixed right
hardened standard-flow 0.4 mm nozzle and ASA Aero White GFB02 from the Polymaker
drybox through external right slot 255. Use 270 °C nozzle, 90 °C bed,
60 °C chamber, 0.52 flow, 0.20 mm layers and 300 wall loops, with no sparse
infill, top/bottom skin, skirt, brim or support. The nested perimeters still
contain seams, wipes and short transitions.

At the insertion pause, seat one RC62 completely on the pocket floor, keeping
the guide bore open and the float attached to the plate. The ring must sit
below the pocket rims. Clear loose strings and manually resume once seated.
The inner collar and outer band anchor the covering roads.

## Accepted print evidence

The [v1 slice review](mark2-print/v1/float-preflight.json),
[native project](all-aero-float.3mf), [source snapshot](mark2-print/v1/source-snapshot/README.md)
and [launch receipt](mark2-print/v1/float-mark2-launch.json) identify Mark2 task
**1306080180**, accepted once at 15:01:48 CDT on 2026-10-03. That article uses
a 3.40 mm pocket, insertion after layer 79 at Z15.8 and covering from layer 80
at Z16.0. Its estimate is 88 minutes excluding the manual pause. The frozen
source and native project belong to that geometry.

The operator reports successful paused insertion and overprinting: the first
covering layer was a bit too tight and the second deposited beautifully.
The [physical record](physical-observations.json) and photo cover insertion and
the initial covering layers. Final roof integrity, cooled completion, retained
magnetic signal, buoyancy and service exposure are unreported.

![Operator photo during magnet overprinting](mark2-print/v1/evidence/magnet-insertion-overprint-2026-10-03.jpg)

## Qualification

ASA Aero is the selected trial material throughout the body. Pressure endurance
and compatibility with the actual flavoring remain physical results. Relevant
observations are water uptake, permanent dimensional change, retained lift and
surface softening. Bambu's [ASA Aero TDS](https://store.bblcdn.com/2bb7c6814cdc42d19ffc62570cfc1fb2.pdf)
provides general material descriptors, not qualification of this foamed print
in pressurized liquid or the flavor mixture.

The [RC62](https://www.kjmagnetics.com/rc62-neodymium-ring-magnet) is N42 with an
80 °C continuous operating limit. Fresh plastic is deposited at 270 °C;
magnet temperature and retained field after insertion have not been measured.
The finished float's reed calibration checks its actual signal.

The [v1 queue](mark2-print/v1/queue.json) records the accepted trial. The user's
monitor remains paused. Completion does not clear the bed or authorize another
submission.

## Rebuild

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/all-aero/all_aero_float.py
```

A future print preparation uses `prepare_print.py` and requires review of the
new native slice. Geometry regeneration alone creates no accepted print job.
