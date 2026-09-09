# Funnel mold print project

[funnel-mold-vacuum-petg-08-016.3mf](funnel-mold-vacuum-petg-08-016.3mf) holds three
editable objects, two surface-speed modifiers, the complete printer/filament/process
settings, native thumbnails and all three plates' sliced G-code. The mold geometry
comes from [funnel_mold.py](funnel_mold.py); [structure and finishing](README.md)
define the intended finished dimensions and bench procedure.

## Plates

Bambu Studio 02.08.02.61 estimates:

| Plate | Orientation | Time | PETG | Layers |
|---|---|---:|---:|---:|
| 1 — Finish witness | Flat datum on bed | 39 min 7 s | 15.32 g | 95 |
| 2 — Cavity | Opening up | 22 h 3 min 15 s | 588.43 g | 466 |
| 3 — Core | Open back on bed, forming plug up | 19 h 41 min 41 s | 567.48 g | 314 |

Each plate is a separate job. The combined estimate is 1,171.24 g. Start each
large plate with enough dry filament: one full 1 kg spool covers either half,
but the remainder after the cavity will not cover the core. These are slicer
estimates; the cavity has less than two hours of margin under 24 hours.

Print the witness first. Physical print time, vacuum behavior, finishing and
silicone-release results have not yet been established for this geometry.

## Settings

| Setting | Value |
|---|---|
| Printer | Bambu Lab H2C 0.8 Standard +0.04 Z trim |
| Assignment | Left nozzle, Standard flow; manual assignment on all plates |
| Filament | PETG Translucent, 255 °C throughout, flow ratio 0.97 |
| Bed | Textured PEI, 70 °C throughout |
| Layers | 0.16 mm; first layer 0.30 mm |
| Walls | Arachne, four requested loops, nominal width 0.80 mm |
| Fill / top / first-layer width | 0.90 mm |
| Top and bottom shell | 20 layers; minimum vertical thickness 3.20 mm |
| Residual fill | 100% rectilinear (`zig-zag` in the project format) |
| Forming / registration outer walls | 30 mm/s through CAD-shaped modifiers |
| Exposed backing-rib outer walls | 80 mm/s |
| Witness outer walls / top surfaces | 30 / 30 mm/s |
| Inner walls / solid fill / other fill | 80 / 90 / 100 mm/s requested |
| Bridges / internal bridges | 20 / 30 mm/s |
| First-layer walls / fill | 25 / 35 mm/s |
| Maximum volumetric speed | 12 mm³/s requested |
| Outer-wall / top-surface acceleration | 1,000 mm/s² |
| Normal cooling | 20–40%; first three layers off; auxiliary fan off |
| Overhang cooling | 90% override |
| Seam | Aligned scarf, including inner walls; conditional scarf off; gap 0% |
| Brim | Outer only, 6 mm wide, 0.15 mm separation |
| Travel | Avoid crossing walls, with a 30 mm maximum additional detour |
| Supports / ironing | Disabled / disabled |
| XY contour / hole compensation | Zero / zero |

The large air spaces are modeled open bays. Solid fill applies only to the skins,
ribs and frame. The cavity registration band has a 45° supporting corbel; the
blind spout floor stands on a pedestal. The core's rod socket has a closed boss.

The active printer retains an early `G29.1 Z0` and a final `G29.1 Z0.02` on
textured PEI, corresponding to the stock PEI adjustment plus the saved +0.04 mm
trim. Both nozzle slots are configured as 0.8 mm Standard. Machine start, end and
filament-change templates match the retained printer profile. Re-slice after
changing printer, nozzle, trim, filament, geometry or finishing allowance.

## Inspection

[Machine-readable inspection](print-profile.json) identifies the project, meshes
and G-code by digest. All three embedded G-code files match their CLI exports and
MD5 entries. Each mesh is one closed, consistently wound body. The sliced mesh
coordinates agree with the generated input within 0.000002 mm after accounting
for local-origin translation; triangle connectivity is unchanged.

All plates return success with empty warning fields. All model and brim extrusion
stays within the 330 × 320 mm printable area, and no support paths are present.
The final cavity has 85,010 triangles; core 30,390; witness 56. The cavity is
189 × 189 × 74.649 mm; the core is 201 × 201 × 50.436 mm in its print orientation.

Across 16 inspected mold layers, 7,381 outer-wall segments whose midpoints lie
inside the surface modifiers stay at or below 30 mm/s. Exposed ribs reach 80 mm/s.
On extrusion segments longer than 1 mm, the largest calculated filament flow is
11.653 mm³/s after the 0.97 flow ratio. Submillimetre G-code segments have larger
local ratios from coordinate/extrusion rounding; the JSON retains those readings.

At backing-channel mid-height, every row retains approximately 3.00 mm of clear
width through the ribs. The five silicone vents retain about 2.42 mm diameter
above the first layer. The pour throat retains about 10.96 mm; its dish is wider.
The rod socket reads about 6.39–6.40 mm through its body, but its final thin entry
lip narrows to about 6.16 mm in the toolpath. **Clear that entry lip and fit the
actual 6.35 mm ground rod before coating.** It must slide freely to 28.8 mm depth;
use a depth stop and keep the blind end intact. Keep the socket uncoated.

These passage readings use minimum distance to an extrusion centreline less half
the annotated line width. They describe nominal toolpath footprints, not measured
plastic. Final core extrusion reaches Z 50.38 mm.

The geometry was published and then reviewed with geometry lint in the intended
print orientations. Its 21 findings have specific anchored answers: finishing
steps, small corbel-start ledges, the rod-boss bridge and the deliberate witness
bridge. The witness tests the 17.6 mm span before a large print.

![Selected extrusion centre lines](print-paths.png)

## At the bench

Dry the PETG and feed it from dry storage. Bambu specifies
[65 °C for 8 hours](https://us.store.bambulab.com/products/petg-translucent?id=42479468281992)
in a blast drying oven. Let each plate cool before removing it, then clear all
backing channels, pour/vent passages and the rod entrance. Dry-assemble the halves
and check that the registration lands seat flat.

Both forming faces require the measured 0.20 mm net finishing growth described
in [the finishing procedure](README.md#measure-the-finish). Mask registration
lands, the socket and every backing-air passage. Trial the actual coating,
release and BBDINO batch on the witness before coating the mold or casting.
