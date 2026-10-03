# PETG-shell bench reference

Reference geometry and recipes for the separate PETG-shell bench article.
The installed float interface is specified in [installation.md](all-aero/installation.md).

An RC62 ring magnet inside a continuous **Bambu PETG Translucent Clear 32101**
envelope, filled with Bambu ASA Aero White 46100. This is a separate bench float
and reed test article.
Its predicted assembled mass is **55.08 g** at 0.55 g/cm³ Aero density, against
**60.05 g** of water displacement: **4.96 g spare lift**.

[Illustrated assembly guide](../../../magnetic-float-guide/magnetic-float-guide.pdf)

[PETG shell project](magnetic-float.3mf) · [ASA Aero parts project](magnetic-float-aero.3mf) ·
[CadQuery source](magnetic_float.py) · [Material research](asa-aero-research.md) ·
[PETG shell recipe](petg-shell.md) · [Pressure-printing research](pressure-printing-research.md)

[Assembly](/3d?file=printed-parts/cold-core/magnetic-float/magnetic-float.step) ·
[Section](/3d?file=printed-parts/cold-core/magnetic-float/section.step) ·
[Exploded view](/3d?file=printed-parts/cold-core/magnetic-float/exploded.step)

In `/3d`, select an existing float in **Enclosure assembly** with **Select →
Component**, then **Open magnetic-float**. **Beside it** offers the section,
exploded view and individual materials.

## Geometry

| Feature | Dimension |
| --- | --- |
| Finished diameter × height | [36 mm](FLOAT_DIAMETER) × [60.06 mm](FLOAT_HEIGHT) |
| Open guide bore | [4.8 mm](FLOAT_BORE) |
| PETG outer wall | [3 mm](OUTER_WALL) |
| PETG bore lining | [1.8 mm](BORE_WALL) |
| PETG floor / roof | [3 mm](FLOOR) / [3.06 mm](ROOF) |
| Seated Aero insert, OD × ID × height | [30 × 8.4 × 10 mm](INSERT_SIZE) |
| RC62 magnet, OD × ID × thickness | [19.05 × 9.525 × 3.175 mm](MAGNET_SIZE) |
| Magnet seat above finished bottom | [43.6 mm](MAGNET_SEAT) |
| Insert bottom / top | [47 / 57 mm](INSERT_STATIONS) |
| Roof underside | [57 mm](ROOF_BOTTOM) |
| Nominal unfilled internal volume | [0.124 cm³](UNFILLED_VOLUME) |
| Water displacement, fully submerged | [60.05 g](DISPLACEMENT) |

The 3.175 mm bench guide rod has 0.8125 mm radial clearance. This float's guide
position and envelope are separate from the installed donor floats and their
rod registers. The larger bench article is not an installed drop-in replacement.

Both Aero pieces print independently, flat on Z=0. Each has 0.5 × 0.5 mm
45° lower-edge lead-ins at its outside and bore. The straight lands have
[0.05 mm](FIT_ALLOWANCE) radial contour expansion and bore reduction in Studio:
target OD/ID 30.10/8.30 mm. The leading edges start at OD/ID 29.10/9.30 mm.
The RC62 seats in a 19.35 × 9.225 × 3.40 mm pocket, providing at least 0.05 mm
nominal radial clearance after compensation and 0.125 mm depth clearance at
the magnet's ±0.1 mm dimensional tolerance. The [0.124 cm³](UNFILLED_VOLUME)
intentional internal relief is confined to those lead-ins and the magnet
pocket. The insert's full-width upper face supports the complete roof annulus.

## Print and assemble

Both projects describe an H2C with a **left 0.6 mm standard-flow nozzle** and a
**right 0.4 mm standard-flow nozzle**. Each plate contains one object and one
material; there are no supports or prime towers.

| Setting | ASA Aero, right nozzle | PETG Translucent Clear, left nozzle |
| --- | --- | --- |
| Nozzle, first / subsequent layers | 270 / 270 °C | 255 / 260 °C |
| Flow ratio | 0.52 | 1.02 |
| Bed | Engineering plate, 90 °C, glue | Textured PEI, 70 °C |
| Chamber | 60 °C | No active heating |
| Layer, first / subsequent | 0.20 / 0.20 mm | 0.30 / 0.18 mm |
| Nominal line width | 0.48 mm | 0.60 mm |
| Ordinary outer / inner wall speed | 80 / 80 mm/s | 40 / 60 mm/s |
| Part fan | Stock 30–50% | 10–20% |
| Auxiliary fan | Off | Off |
| Infill | 100% foamed ASA | 100% PETG |

ASA uses Bambu's unmodified filament preset and its guide's process speeds and
widths. PETG Translucent uses the sealing controls from the
[successful PETG Basic reservoir recipe](petg-water-recipe.json), with the
Translucent preset's density and 16 mm³/s flow ceiling. The material selection
is recorded in [petg-translucent-recipe.json](petg-translucent-recipe.json), and
the float's process adaptations are in [petg-shell.md](petg-shell.md).
Cooling slowdowns still apply. PETG has random, unconditional scarf seams on
both walls, zero seam gap, and top-surface ironing.

1. Dry ASA Aero in the AMS HT at **80 °C for eight hours** and keep it below
   20% RH. Dry PETG Translucent Clear in the AMS 2 Pro at **65 °C for twelve hours**, per the
   [shop drying table](/hardware/ledger/tools.md).
2. Open `magnetic-float-aero.3mf`. Print **plate 1 — ASA Aero core**, then
   **plate 2 — ASA Aero insert**. Use the Engineering plate with Bambu liquid
   glue. Let each piece and the plate cool to **35 °C or below**, then remove
   its brim and loose strings. Both are solid foam prints.
3. On the bench, seat one RC62 in the tall core's top pocket. Either pole can
   face up. Keep the prepared core upright and set out the short insert with
   its chamfered end down. Let the chamber cool to **35 °C or below** for PETG,
   fit the textured plate, and open
   `magnetic-float.3mf`. Load **Bambu PETG Translucent Clear** on the left. Print its single
   plate. The shell pauses before **[57.18 mm](PAUSE_LAYER)**, after its walls
   reach [57 mm](ROOF_BOTTOM).
4. Keep the bed at 70 °C and the shell attached during the pause. Lower the
   prepared core into the shell, chamfered end first, over the PETG bore
   lining. Place the short insert on top, chamfered end down. Press it evenly
   with a clean plastic pusher to seat the core on the floor and bring the
   insert top level with the PETG rim. Remove the pusher and loose strings.
5. Close the enclosure and resume promptly.
   **[17 layers](ROOF_LAYERS)** close the roof, joining the outer wall
   to the bore lining across the insert. Let the part and plate cool to
   **35 °C or below**; remove the float and trim its outer brim.

The seated magnet's top remains at least [10.125 mm](MAGNET_ROOF_GAP) below the
roof underside, including thickness tolerance. The close-fitting pocket locates
the magnet; the upper insert and printed roof retain it.
[Pause-bond research](pressure-printing-research.md) supports preparing the parts
before the pause and resuming promptly.

## Buoyancy and verification

| Aero bulk density | Assembled mass | Spare lift in water |
| --- | --- | --- |
| 0.46 g/cm³ | [51.99 g](MASS_046) | [8.06 g](LIFT_046) |
| 0.53 g/cm³ | [54.40 g](MASS_053) | [5.65 g](LIFT_053) |
| 0.55 g/cm³ | [55.08 g](MASS_055) | [4.96 g](LIFT_055) |
| 0.60 g/cm³ | [56.80 g](MASS_060) | [3.25 g](LIFT_060) |
| 0.65 g/cm³ | [58.52 g](MASS_065) | [1.53 g](LIFT_065) |

[design.json](design.json) records the exact volumes. Neutral buoyancy occurs
at 0.694 g/cm³ core density. The open guide bore contributes no displacement.
The 0.55 estimate includes margin over the manufacturer's stock-flow estimate;
it is not a measured material tolerance.

[verification.json](verification.json) checks the emitted material paths,
continuous bore/outer walls, open core insertion, magnet clearance, pause and
all 17 roof layers. Object extrusion predicts **54.62 g assembled mass and
5.43 g spare lift**, excluding brims and startup purge. Studio estimates **1 h
37 min** for the core, **37 min** for the insert and **2 h 2 min** for the shell,
excluding the operator's pause. The shell's insertion pause has about **15 min**
of printing left. [print-profile.json](print-profile.json) records
the source presets, overrides, hashes and exact estimates.

## Reed reach

Measured on the bench with one RC62 and one Littelfuse MDSR-7-10-15 reed, the
reed standing parallel to the magnet's axis. Each distance runs from the reed
to the magnet's nearest outer edge. The signal stayed stable while the magnet
was turned about 45° off that orientation in any direction.

| Reed to magnet edge | Height of magnet travel with a stable signal |
| --- | --- |
| 30 mm | about 30 mm, ±15 mm about the reed's centre |
| 40 mm | about 25 mm, ±12.5 mm |
| 50 mm | the limit of stable detection |

The magnet's nearest edge is 8.475 mm inside this float's outside surface.

## Pressure test

The carbonator's reference points are 90 psi nominal CO₂ feed, a 125 psi PRV,
and a 180 psi, 30-minute hydrostatic fabrication test. The float sees external
pressure on its shell and water pressure inside its open bore. It has **no
recorded pressure-test result**. [petg-shell.md](petg-shell.md) gives the shell
thickness calculation. [Pressure-printing research](pressure-printing-research.md)
records published successes, failures, exact source-project settings and the
limits on transferring them to this external-pressure float.

For the first float pressure test, record dry mass and dimensions, verify
upright float motion on its guide, and use a water-filled metal hydrostatic
fixture suitable for the test pressure. Record the 90 psi hold and the
180 psi/30-minute hold separately. After depressurization, dry the exterior
consistently, reweigh, and repeat float/guide/reed checks. A pressure gauge hold
alone does not detect water entering a submerged float. Record mass gain,
dimensional change and loss of lift as float failures. The test result belongs
to this article; sustained pressure, CO₂ exposure and wetted-surface acceptance
remain separate service qualifications.

## Rebuild

From the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/pressure_analysis.py
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/prepare_print.py --slice
```

The last command slices both projects, verifies them, and saves the projects
and their evidence here. Verification of an existing slice:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/verify.py --directory .cache/magnetic-float-print
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py`
