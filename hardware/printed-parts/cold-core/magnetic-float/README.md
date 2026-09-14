# Magnetic float

An RC62 ring magnet inside a continuous PETG Translucent Clear envelope, with a
solid-print PLA Aero interior. This is a bench prototype for float and reed tests.

[Bambu Studio project](magnetic-float.3mf) · [CadQuery source](magnetic_float.py) ·
[Assembly](/3d?file=printed-parts/cold-core/magnetic-float/magnetic-float.step) ·
[Section](/3d?file=printed-parts/cold-core/magnetic-float/section.step) ·
[Exploded view](/3d?file=printed-parts/cold-core/magnetic-float/exploded.step)

In `/3d`, open **Enclosure assembly → Prototypes → magnetic-float**. The cold core,
carbonator tube and reservoir models carry the same link. **Beside it** offers the
section, exploded view, separate materials, inserts and turning key.

## Geometry

| Feature | Dimension |
| --- | --- |
| Finished diameter | [28 mm](FLOAT_DIAMETER) |
| Finished height | [50 mm](FLOAT_HEIGHT) |
| Open guide bore | [6 mm](FLOAT_BORE) |
| PETG outer wall, bore lining, floor and roof | [1 mm](FLOAT_SKIN) each |
| Aero insert height | [10 mm](INSERT_HEIGHT) |
| RC62 magnet | [19.05 × 9.525 × 3.175 mm](MAGNET_SIZE), OD × ID × thickness |
| Magnet pocket | [19.55 × 9.025 × 3.6 mm](MAGNET_POCKET), OD × ID × depth |
| Magnet seat above finished bottom | [35.2 mm](MAGNET_SEAT) |
| Insert bottom / top | [38.8 / 48.8 mm](INSERT_STATIONS) |
| PETG roof underside | [49 mm](ROOF_BOTTOM) |
| Water displacement, fully submerged | [29.37 g](DISPLACEMENT) |

The PETG insert collar has two entry slots, two bayonet grooves, and two sockets
for the plastic turning key. The Aero is captured between the collar's upper and
lower inward lips. The collar locks under two lugs inside the outer shell. All
retaining features stand inside the full PETG sealing envelope.

The nominal insert has [0.2 mm](INSERT_RADIAL_CLEARANCE) radial clearance. The spare
has [0.35 mm](LOOSE_RADIAL_CLEARANCE). The insert's top stands
[0.2 mm](INSERT_ROOF_CLEARANCE) below the roof underside; its upward travel stops
at that underside. Assembly clearances occupy [0.622 cm³](ASSEMBLY_CLEARANCE).
The Aero regions print at 100% infill, with foamed material occupying the core.

## Print and assemble

The project contains two plates, with PETG assigned to the **left 0.4 mm standard
flow nozzle** and PLA Aero to the **right 0.4 mm standard flow nozzle**. Both
materials print at 250 °C on textured PEI at 65 °C. PETG uses 0.97 flow; Aero uses
0.38. The layer height is 0.2 mm. Supports are disabled; the separate insert
supports the sealing roof. The project includes a prime tower and adhesion brims.

1. Load dry PETG Translucent Clear and PLA Aero into their assigned feeds. Keep
   the chamber ventilated for the Aero. Open `magnetic-float.3mf` in Bambu Studio.
2. Print **plate 1 — Inserts and turning key**. It holds the nominal insert, the
   spare with looser clearance, and the plastic key. Keep the same materials and
   nozzles loaded for plate 2.
3. Print **plate 2 — Float**. The stored pause occurs before the layer at
   [49.2 mm](PAUSE_LAYER). The body and open magnet pocket remain on the bed.
4. Lower one RC62 over the central tube into its pocket. Align the insert's two
   outside slots with the body's two lugs and lower the insert onto its seat.
   Engage the plastic key in the two top sockets. Turn **counterclockwise by
   [90°](LOCK_ANGLE), viewed from above**, to the groove stops. The spare fits the
   same body if the nominal insert is tight.
5. Remove the key. The insert sits below the body's top rim and is captured
   against lifting. Resume. The remaining [5 layers](ROOF_LAYERS) close the
   PETG roof onto the outside wall and bore lining.

The magnet is absent during all printing below the insertion plane. Once
captured, its upper face remains at least [10 mm](MAGNET_ROOF_GAP) below the roof
underside. Hotend attraction with this magnet and printer has no measured result
yet; the insert mechanically restrains the magnet before the hotend returns.

## Buoyancy and print evidence

`design.json` contains the exact material volumes and a density sweep. The PETG
density is 1.25 g/cm³, from the installed Bambu PETG Translucent preset. One RC62
contributes 5.09 g. These figures include the insert's PETG collar.

| Aero bulk density | Estimated assembled mass | Spare lift in water |
| --- | --- | --- |
| 0.45 g/cm³ | [24.09 g](MASS_045) | [5.28 g](LIFT_045) |
| 0.55 g/cm³ | [26.10 g](MASS_055) | [3.27 g](LIFT_055) |
| 0.60 g/cm³ | [27.11 g](MASS_060) | [2.26 g](LIFT_060) |
| 0.65 g/cm³ | [28.11 g](MASS_065) | [1.26 g](LIFT_065) |

Bambu's [PLA Aero foaming table](https://bambulab-eu.myshopify.com/nl-nl/products/pla-aero)
lists 250 °C, 0.38 flow and a minimum specimen density of 0.45 g/cm³, measured with
a 0.4 mm nozzle at 80 mm/s. The specimen is 80 × 10 × 4 mm; the float's actual
expansion and surface finish are print results. The profile uses those published
temperature and flow settings. A separate calibration print is not part of this
job.

`verification.json` records the solid and mesh checks, magnet tolerance envelope,
insert entry and rotation sweeps, mechanical capture, material assignments,
insertion pause and roof layers. It also calculates assembled mass from the
extrusion commanded on the actual object paths, excluding prime towers, brims,
the spare insert and key. `print-profile.json` records the source presets and
slicer estimates. No physical float print or pressure test is recorded.

## Application

The bore fits a 3.175 mm guide rod. The existing reservoir rod position spends the
donor float's larger bore clearance to bias it against the wall; that position
does not fit this concentric prototype's envelope. The bench float and reed test
uses a separate guide rod position. The production assembly still carries its
donor float geometry and level-sensor positions.

The carbonator operates at 90 psi and has a 180 psi hydrostatic test requirement.
This printed float has no established external-pressure rating. Its PETG
enclosure's dimensional closure is digitally verified; water sealing, foam
compression and pressure endurance have no physical results recorded.

## Rebuild

Run from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/prepare_print.py
```

The preparation script writes the editable input project and resolved presets to
`.cache/magnetic-float-print/`. Bambu Studio's installed CLI slices that project:

```sh
mkdir -p .cache/magnetic-float-print/sliced
cd .cache/magnetic-float-print/sliced
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio --arrange 0 --orient 0 --slice 0 --export-3mf magnetic-float.3mf --outputdir "$PWD" ../magnetic-float-input.3mf
```

From the repository root, verify the resulting file:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/magnetic-float/verify.py --project .cache/magnetic-float-print/sliced/magnetic-float.3mf
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/magnetic-float/magnetic_float.py`
