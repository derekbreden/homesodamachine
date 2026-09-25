# Magnetic float

An RC62 ring magnet inside a continuous PETG Translucent Clear envelope, backed
by PLA Aero. A plain Aero ring is pressed into the body before the roof prints.
This is a bench float and reed test article.

[Bambu Studio project](magnetic-float.3mf) · [CadQuery source](magnetic_float.py) ·
[Assembly](/3d?file=printed-parts/cold-core/magnetic-float/magnetic-float.step) ·
[Section](/3d?file=printed-parts/cold-core/magnetic-float/section.step) ·
[Exploded view](/3d?file=printed-parts/cold-core/magnetic-float/exploded.step)

In `/3d`, open **Enclosure assembly**, select an existing float (`float-carb`,
`float-a` or `float-b`) with **Select → Component**, then choose **Open magnetic-float**.
**Beside it** offers the section, exploded view and individual materials.

## Geometry

| Feature | Dimension |
| --- | --- |
| Finished diameter | [28 mm](FLOAT_DIAMETER) |
| Finished height | [50 mm](FLOAT_HEIGHT) |
| Open guide bore | [6 mm](FLOAT_BORE) |
| PETG outer wall, bore lining, floor and roof | [1 mm](FLOAT_SKIN) each |
| Seated Aero insert, OD × ID × height | [26 × 8 × 10 mm](INSERT_SIZE) |
| RC62 magnet, OD × ID × thickness | [19.05 × 9.525 × 3.175 mm](MAGNET_SIZE) |
| Magnet seat above finished bottom | [35.825 mm](MAGNET_SEAT) |
| Insert bottom / top | [39 / 49 mm](INSERT_STATIONS) |
| PETG roof underside | [49 mm](ROOF_BOTTOM) |
| Nominal unfilled internal volume | [0.000 cm³](UNFILLED_VOLUME) |
| Water displacement, fully submerged | [29.37 g](DISPLACEMENT) |

The assembled CAD fills the space between the PETG skin and magnet with Aero.
The insert meets the body core, outer wall, bore lining and roof. The guide bore
is open through the float and carries water. Foamed material contains pores;
printed surfaces and manufacturing tolerances determine the actual contact.

The Aero insert uses a press fit. The two copies on plate 1 have slicer radial
allowances of [0.05 / 0.1 mm](FIT_ALLOWANCES): contour expansion and bore reduction.
The nominal CAD and STL show the seated dimensions. The print targets are
26.10 / 7.90 mm OD / ID and 26.20 / 7.80 mm for the snugger spare.
The magnet pocket follows the nominal magnet; its ±0.1 mm dimensional tolerance
is taken in the Aero surrounding it, clear of the PETG skin.

## Print and assemble

The project assigns PETG to the **left 0.4 mm standard flow nozzle** and PLA Aero
to the **right 0.4 mm standard flow nozzle**. Both print at 250 °C on textured PEI
at 65 °C. PETG uses 0.97 flow; Aero uses 0.38. Layers are 0.2 mm. The Aero regions
use 100% infill. The insert supports the sealing roof.

1. Load dry PETG Translucent Clear and PLA Aero into their assigned feeds. Keep
   the chamber ventilated for the Aero. Open `magnetic-float.3mf` in Bambu Studio.
2. Print **plate 1 — Aero inserts**. It holds the insert and snugger spare. Keep
   the materials and nozzles loaded for plate 2.
3. Print **plate 2 — Float**. It pauses before the layer at [49.2 mm](PAUSE_LAYER).
4. Seat one RC62 in the Aero pocket. Press the insert down evenly until its top
   is flush with the printed PETG rim. The snugger spare is on the first plate
   if the first insert is loose. Retention comes from the fit: the insert needs
   to stay seated without a hand holding it when the printer resumes.
5. Resume. The remaining [5 layers](ROOF_LAYERS) form the PETG roof, joining the
   outer wall and bore lining across the insert.

With the magnet seated, its upper face is at least [9.9 mm](MAGNET_ROOF_GAP) below
that roof underside, including its thickness tolerance. Hotend attraction and
press-fit holding force have no measured results. The seated insert and magnet
must remain below the rim; a proud insert interferes with the roof toolpaths.

## Buoyancy and print evidence

`design.json` contains material volumes and a density sweep. PETG density is
1.25 g/cm³ from the installed preset; one RC62 contributes 5.09 g.

| Aero bulk density | Estimated assembled mass | Spare lift in water |
| --- | --- | --- |
| 0.45 g/cm³ | [23.04 g](MASS_045) | [6.33 g](LIFT_045) |
| 0.55 g/cm³ | [25.28 g](MASS_055) | [4.09 g](LIFT_055) |
| 0.60 g/cm³ | [26.40 g](MASS_060) | [2.97 g](LIFT_060) |
| 0.65 g/cm³ | [27.52 g](MASS_065) | [1.85 g](LIFT_065) |

Bambu's [PLA Aero foaming table](https://bambulab-eu.myshopify.com/nl-nl/products/pla-aero)
lists 250 °C, 0.38 flow and a minimum specimen density of 0.45 g/cm³, with a
0.4 mm nozzle at 80 mm/s. That specimen is 80 × 10 × 4 mm. The float's expansion,
fit and density are results of the first float print; the project includes its
assembly parts together with the spare.

`verification.json` records the nominal solid fill, sealing skin, magnet tolerance
location, insert compensation, material paths and insertion pause. Its mass
estimate counts object extrusion and excludes prime towers, brims and the spare.
`print-profile.json` records the presets and slicer estimates.

## Experimental 0.2 mm nozzles

[Experimental Bambu Studio project](magnetic-float-0.2-experimental.3mf) uses
0.2 mm standard-flow nozzles on **both** sides: PETG on the left, Aero on the
right. These are different parts: a standard hotend on the left and an induction
hotend on the right. [Confirmed 0.2 mm stock](/hardware/ledger/tools.md#02-mm-hotend-availability)
is right-side only; this project also needs a left-side 0.2 mm standard hotend.
The 0.4 mm project remains the recommended first float print.

The float geometry, PETG thickness and insert fits are identical. The experimental
project uses 0.10 mm layers, nominal 0.22 mm lines, five wall loops, ten roof/floor
layers and a 1 mm³/s volumetric-flow limit for both materials. The temperatures
are 250 °C with a 65 °C bed. PETG uses the installed 0.2 mm preset's 0.95 flow;
Aero uses 0.38. The body pauses before Z49.1, leaving ten PETG roof layers.

Studio estimates 3 h 5 min for both inserts and 19 h 20 min for the body,
excluding the operator's pause. The 0.4 mm project estimates 43 min and
3 h 15 min respectively. `verification-0.2.json` checks both material assignments,
all 500 body layers, the compensated inserts and the pause. `print-profile-0.2.json`
records the source presets, effective settings, nozzle evidence and slicer results.

The manufacturer's documents give different answers about nozzle compatibility:

- [PLA Aero's product page](https://bambulab-us.myshopify.com/products/pla-aero)
  recommends 0.4 mm and advises against 0.2 mm. Its
  [TDS](https://store.bblcdn.com/cbc8b808aaf84ead9bb3b0b9b43e66af.pdf)
  lists 0.4, 0.6 and 0.8 mm.
- The [H2C manual](https://csm.bblcdn.com/hub/eff78da43720461787dc8bbe5fa0372d.pdf),
  printed pages 120–122, includes PLA Aero under PLA compatible with all nozzle
  sizes, explicitly including 0.2 mm.
- [PETG Translucent's TDS](https://cdn.shopify.com/s/files/1/0574/3116/2995/files/Bambu_PETG_Translucent_Technical_Data_Sheet.pdf?v=1704680051)
  lists 0.2 mm, and Studio includes a dedicated H2C 0.2 mm preset. Studio's
  [incompatibility list](https://github.com/bambulab/BambuStudio/blob/master/resources/info/nozzle_incompatibles.json)
  nevertheless flags PETG Translucent with 0.2 mm nozzles.

There is no installed Aero 0.2 mm preset. This project uses an explicitly named
experimental adaptation of the Aero 0.4 mm recipe. Slicing success establishes
the emitted paths; it establishes no foam expansion, fit, sealing or pressure
result. The 0.4 mm foaming data does not validate the 0.2 mm nozzle's density.

## Reed reach

Measured on the bench with one RC62 and one Littelfuse MDSR-7-10-15 reed, the
reed standing parallel to the magnet's axis. Each distance runs from the reed to
the magnet's outer edge nearest it. The figures are where the signal stayed
stable while the magnet was turned up to about 45° off that orientation in any
direction. The reed also closes beyond them, at some orientations and not at
others.

| Reed to magnet edge | Height of magnet travel with a stable signal |
| --- | --- |
| 30 mm | about 30 mm, ±15 mm about the reed's centre |
| 40 mm | about 25 mm, ±12.5 mm |
| 50 mm | the limit of stable detection |

## Application and pressure

The existing reservoir rod position spends the donor float's larger bore
clearance to hold it against the wall. This concentric float uses a separate
bench guide position. Its bore fits a 3.175 mm guide rod.

The carbonator operates at 90 psi with a 180 psi hydrostatic test requirement.
This printed float has no established pressure rating. The CAD verifies material
backing behind the skin at nominal dimensions. Foam crushing, creep, actual
contact, water sealing and pressure endurance have no physical results recorded.

Bambu's [PLA Aero TDS, v4](https://store.bblcdn.com/cbc8b808aaf84ead9bb3b0b9b43e66af.pdf)
reports tensile and bending properties for specimens printed at 210 °C and
annealed. It provides no compressive or hydrostatic endurance value for the
250 °C foamed material in this project.

## Rebuild

From the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/prepare_print.py
mkdir -p .cache/magnetic-float-print/sliced
cd .cache/magnetic-float-print/sliced
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --arrange 0 --orient 0 --slice 0 --export-3mf magnetic-float.3mf --outputdir "$PWD" ../magnetic-float-input.3mf
```

From the repository root, verify the result:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/verify.py --project .cache/magnetic-float-print/sliced/magnetic-float.3mf
```

For the experimental 0.2 mm project:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/prepare_print.py --nozzle 0.2
mkdir -p .cache/magnetic-float-print-0.2/sliced
cd .cache/magnetic-float-print-0.2/sliced
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --arrange 0 --orient 0 --slice 0 --export-3mf magnetic-float-0.2-experimental.3mf --outputdir "$PWD" ../magnetic-float-input.3mf
```

From the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/verify.py --nozzle 0.2 --project .cache/magnetic-float-print-0.2/sliced/magnetic-float-0.2-experimental.3mf
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py`
