# Funnel mold print project

[**funnel-mold-guided-vacuum-petg-08-016.3mf**](funnel-mold-guided-vacuum-petg-08-016.3mf)
contains five editable bodies, two precision-speed modifiers, the complete
printer/filament/process configuration, native thumbnails and three plates of
sliced G-code. The mold includes vented structural backing, 0.20 mm of net
finishing allowance and four guided M5 screw jacks.

[Structure and finishing](README.md) and [extraction hardware and use](extraction.md)
are part of the print instructions. The forming faces require finishing before
casting to nominal dimensions.

## Plates

Bambu Studio 02.08.02.61 estimates:

| Plate | Orientation | Time | PETG | Layers |
|---|---|---:|---:|---:|
| 1 — Finish, hardware and guide witnesses | Flat datums on bed | 1 h 26 min 3 s | 31.04 g | 168 |
| 2 — Cavity | Opening up | 23 h 27 min 47 s | 696.20 g | 466 |
| 3 — Core | Open back on bed; forming plug and guides up | 21 h 49 min 55 s | 642.51 g | 374 |

Each plate is an independent print job. Total filament across the three plates
is **1,369.74 g**. Start each large plate with a full, dry 1 kg spool; the
remainder from the cavity will not cover the core. The cavity's estimated margin
under 24 hours is approximately **32 minutes**, so pauses or longer startup can
put it over a day. These are estimates, not measured print durations.

Print the three witnesses first. Use them to verify the 17.6 mm backing bridge,
finishing process, square-nut fit, washer fit and guide sliding fit. The existing
M5 × 10 screws can check the nut thread before the M5 × 50 pack arrives. The
assembled extraction mechanism uses the 50 mm screws.

## Settings

| Setting | Value |
|---|---|
| Printer | Bambu Lab H2C 0.8 Standard +0.04 Z trim |
| Assignment | Left nozzle, Standard flow; manual assignment on all plates |
| Filament | PETG Translucent, 255 °C, flow ratio 0.97 |
| Bed | Textured PEI, 70 °C |
| Layers | 0.16 mm; first layer 0.30 mm |
| Walls | Arachne, four requested loops, nominal 0.80 mm width |
| Fill / top / first-layer width | 0.90 mm |
| Top / bottom shell | 20 layers; minimum vertical thickness 3.20 mm |
| Residual fill | 100% rectilinear (`zig-zag` in the project format) |
| Precision zones | Forming skins, registration, rod boss, guide posts/sleeves, nut seats and washer pockets |
| Precision outer / inner walls | 30 / 80 mm/s; acceleration 1,000 / 3,000 mm/s² |
| Exposed reinforcement outer / inner walls | 100 / 100 mm/s requested; acceleration 6,000 mm/s² |
| General / top-surface acceleration | 8,000 / 1,000 mm/s² |
| Solid fill / other fill / top surfaces | 90 / 100 / 30 mm/s requested |
| Bridges / internal bridges | 20 / 30 mm/s |
| First-layer walls / fill | 25 / 35 mm/s |
| Volumetric limit | 12 mm³/s requested |
| Normal cooling | 20–40%; first three layers off; auxiliary fan off |
| Overhang cooling | 90% override |
| Seam | Aligned scarf, including inner walls; conditional scarf off; gap 0% |
| Brim | Outer only, 6 mm wide, 0.15 mm separation |
| Travel | Avoid crossing walls; maximum additional detour 30 mm |
| Supports / ironing | Disabled / disabled |
| XY contour / hole compensation | Zero / zero |

All remaining modeled material prints solid. The open rib bays provide backing
ventilation. The Y-side extraction braces have short feet tied into the X ribs;
the 3 mm air channels pass through those feet. The guide-sleeve crosswalls bridge
8.6 mm between their braces, and the nut-slot lips bridge the 8.4 mm slot width.
The steel nuts bear against substantial roofs printed on the bed side of the core.

The retained machine templates issue `G29.1 Z0` and then `G29.1 Z0.02` on textured
PEI, combining the stock PEI adjustment with the saved +0.04 mm trim. Both slots
are configured as 0.8 mm Standard. Machine start, end and filament-change templates
match the retained printer profile. If native Preview requests filament grouping,
retain **Custom** with PETG on **Left Extruder (1)**. Confirm the intended 0.8 mm
Standard nozzle after any hardware sync. Re-slice after changing the printer, nozzle,
trim, filament, geometry or finishing allowance.

## Verification

[Print inspection](print-profile.json) identifies the project, meshes and G-code
by digest. All three embedded G-code files match the CLI exports and their MD5
entries. All five bodies are closed, consistently wound, connected meshes. Triangle
connectivity is unchanged by slicing; vertices agree within 0.000002 mm after
accounting for local-origin translation. Two modifier volumes retain their
positions relative to the corresponding body.

All three plates return success with empty warning fields. Model and brim
extrusion stays inside the 330 × 320 mm printable area, with no support paths.
The cavity is 269 × 269 × 74.649 mm; the inverted core is 266 × 266 × 60 mm.

Across 49 sampled mold layers, **28,526** outer-wall segments inside the precision
modifiers stay at or below **30 mm/s**. Exposed reinforcement reaches 100 mm/s.
The largest calculated flow on extrusion segments longer than 1 mm is
11.653 mm³/s after the flow ratio. The JSON also retains the larger local ratios
on tiny segments caused by coordinate/extrusion rounding.

| Passage / fit | Nominal footprint read from the final paths |
|---|---|
| Four guide posts | 8.00 × 8.00 mm |
| Four guide sleeves | 8.60 mm clear width |
| Four square-nut slots | 8.40 mm clear width |
| Four jack-screw bores | About 5.75–5.76 mm diameter |
| Four washer pockets | About 25.37 mm diameter |
| Backing-air channels | About 2.96–3.00 mm clear width at mid-height |
| Silicone vents | About 2.42 mm diameter above the first layer |
| Pour throat | About 10.96 mm diameter |
| Rod socket | About 6.39–6.40 mm through its body; about 6.16 mm at the thin entry lip |

These readings subtract half the annotated extrusion width from the distance
to a path centreline. They describe toolpaths, not measured plastic. **Clear the
rod socket's narrow entry lip and fit the actual 6.35 mm rod before coating.** It
must slide freely to 28.8 mm depth. Use a depth stop and preserve the blind end.
Keep the socket, guides, nut seats, washer seats and air channels uncoated.

[Mechanical verification](mechanical-verification.json) records zero collisions
at 14 positions from closure through 50 mm lift, a continuous clearance check for
each guide's swept envelope, and clearance of the modeled hardware. At 32 mm
working lift, guides retain 12 mm engagement and screw heads retain 5.8–7.0 mm
clearance for 0.8–2.0 mm washers. The maximum mold radius is 142.13 mm, leaving
7.73 mm nominal radial space in the listed 299.72 mm chamber. Check the actual
opening and catch tray, including any holding hardware.

The geometry was published and then linted in the intended print orientations.
All 74 findings have specific anchored answers in the adjacent `.lint-answers`
files: finishing steps, guide chamfers and travel marks, brace transitions, and
deliberate bridges. The print and extraction forces still need bench validation.

![Mold extrusion sections](print-paths.png)

![Extraction hardware extrusion sections](hardware-paths.png)

## At the bench

Dry the PETG and feed it from dry storage. Bambu specifies
[65 °C for 8 hours](https://us.store.bambulab.com/products/petg-translucent?id=42479468281992)
in a blast drying oven. Let the parts cool on the plate before removal. Clear
all backing-air paths and the pour, silicone vents and rod entrance.

Check all small fits first, then dry-assemble the large halves and run the full
extraction stroke. Finish both forming faces to the measured 0.20 mm net growth
in [the finishing procedure](README.md#measure-the-finish). Trial the actual PETG,
coating, release and silicone batch together before coating the mold or casting.
Use a hand hex key for extraction, advancing opposite sides equally. The jacks
lift the core; the casting's holding arrangement keeps it seated during cure.
