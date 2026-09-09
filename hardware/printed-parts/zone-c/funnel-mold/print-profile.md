# Funnel mold print project

[**Default project — +0.04 mm trim**](funnel-mold-petg-hf08-variable-016-040.3mf)
uses the H2C's **left 0.8 mm High Flow nozzle**, PETG Translucent at 255 °C,
0.16 mm layers through the shallow slopes and 0.40 mm through straight
structural sections. It contains five editable bodies, two surface-speed
modifiers, native thumbnails and all three plates of sliced G-code.

[**Alternate project — +0.18 mm trim**](funnel-mold-petg-hf08-variable-016-040-z018.3mf)
is also fully sliced. The [printer preset bundle](funnel-mold-hf08-z-trim-presets.bbscfg)
contains both trims for Bambu Studio's printer selector. Import the bundle with
**File → Import → Import Configs** if those presets are not already installed.
The trim is the user's observed build-plate correction across nozzle, size and
material changes. **+0.04 mm is the default for translucent PETG on the current plate.**

[Structure and finishing](README.md) and [extraction hardware and use](extraction.md)
accompany the project. The forming geometry has a 0.20 mm net finishing allowance.

## Plates

Bambu Studio 02.08.02.61 estimates for the default project:

| Plate | Orientation | Time | PETG | Layers |
|---|---|---:|---:|---:|
| 1 — Finish, hardware and guide witnesses | Flat datums on bed | 1 h 15 min 0 s | 60.56 g | 171 |
| 2 — Cavity | Opening up | 22 h 49 min 7 s | 1271.49 g | 315 |
| 3 — Core | Open back on bed; forming plug and blades up | 18 h 22 min 9 s | 1025.95 g | 309 |

Each plate is an independent job. Total material is **2,358.00 g**; prepare
approximately **3 kg of dry PETG** including reserve. Both large plates exceed
a 1 kg spool. Arrange compatible automatic spool backup, or a supervised runout
change, before starting. The project does not configure physical backup spools.
These are estimates rather than measured print durations; the cavity has about
71 minutes of estimated margin below one day.

Print all three witnesses first. Inspect the 17.6 mm backing bridge, test the
square-nut and guide fits, and trial the complete coating/release/silicone
combination. The 18 mm³/s flow target and 60 mm/s surface speed need to produce
sound extrusion on the actual dry spool and high-flow nozzle before either long
print. The witness is a useful part trial; it is not a measured maximum-flow
calibration or an extraction-load certification.

## Layer height and flow

The forming ramps are shallow: at 15°, an ideal 0.16 mm layer makes a terrace
about 0.60 mm wide. At 0.32 mm that becomes 1.19 mm, and at 0.40 mm 1.49 mm.
These geometric figures describe the staircase, not measured deposited beads.
Coarse layers on the shallow undersides also extend farther than a nominal
0.82 mm road can overlap. Fine bands cover both the undersides and the finished
forming ramps. The backing walls and straight guide sections use coarse layers.

| Body | Fine-layer bands, measured up from its print bed |
|---|---|
| Cavity | 0.40–5, 9–11, 30.5–54, 70.5–74.65 mm |
| Inverted core | 0.40–5, 8–14.5, 22–23.5, 32–57 mm |
| Finish witness | 0.40–5, 6.2–15.4 mm |
| Hardware witness | 0.40–5, 8–14 mm |
| Guide witness | 0.40 mm nominal layers throughout |

The first layer is 0.40 mm. Each fine band has an individual geometric reason in
[print-recipe.json](print-recipe.json). On the shared witness plate, Bambu merges
the objects' layer schedules; the reported plate layer count includes that schedule.

The installed Bambu H2C 0.8 PETG Translucent preset supplies **16 mm³/s** for
both Standard and High Flow. This mold's High Flow variant requests **18 mm³/s**;
the Standard variant remains at the manufacturer's 16. With all other recipe
settings held constant, slicing at 16 estimates **24 h 35 min** for the cavity
and **19 h 46 min** for the core. The 18 target estimates the times above.
A volumetric cap is a setting for a particular material/hotend/temperature
combination, not an intrinsic PETG limit. [Prusa's explanation](https://help.prusa3d.com/article/max-volumetric-speed_127176)
describes its interaction with line width, layer height and requested speeds.

![Layer bands and flow comparison](layer-plan.png)

## Active settings

[The configuration audit](profile-audit.md) explains the complete setting stack.

| Setting | Active value |
|---|---|
| Printer / assignment | H2C 0.8; left High Flow; one PETG filament; manual assignment on each plate |
| Bed / trim | Textured PEI, 70 °C; default +0.04 mm, alternate +0.18 mm |
| Nozzle temperature | 255 °C, including the first layer |
| Flow ratio / volumetric cap | Vendor 0.97 / requested 18 mm³/s for High Flow |
| Nominal widths | Vendor 0.82 mm; Arachne varies widths locally |
| Walls | Four requested loops; inner then outer |
| Residual fill | 100% alternating rectilinear (`zig-zag`) |
| Top / bottom stock | Eight requested layers and a 3.20 mm physical minimum on each side |
| Top surfaces | 60 mm/s; 2,000 mm/s² acceleration |
| Surface modifiers | Outer walls 60 mm/s; 2,000 mm/s² acceleration |
| Structural speeds | Stock H2C 0.40 process; actual speeds limited by flow, feature geometry and cooling |
| General / structural outer acceleration | Stock 8,000 / 5,000 mm/s² |
| First-layer walls / fill | Stock 50 / 105 mm/s requests, also limited by flow |
| Bridges | Stock 30 mm/s process setting |
| Cooling | Stock 20–60%; first three layers off; auxiliary fan off; overhang override 90% |
| Seam | Conventional aligned seam; 0% gap; scarf disabled |
| Brim | External only, 6 mm wide, stock 0.10 mm separation |
| Supports / raft / ironing / prime tower | Disabled |
| XY contour / hole compensation | Zero / zero; stock 0.15 mm elephant-foot compensation |
| Travel | Stock retract/lift and travel behavior; avoid-crossing-wall detours disabled |

All remaining CAD stock prints solid. The CAD rib bays and air channels supply
ventilation. Preserve them through finishing. Keep guides, nut seats, washer
seats and the rod socket uncoated.

The machine's start, end, tool-change and calibration templates come from the
installed H2C preset. The only custom machine-code edit is the explicit plate-trim
block. On textured PEI with this 0.8 mm nozzle, the default issues
`G29.1 Z0` then `G29.1 Z0.02`: stock −0.02 plus user +0.04. The alternate issues
`G29.1 Z0` then `G29.1 Z0.16`: stock −0.02 plus user +0.18.
Confirm left 0.8 mm High Flow and the intended trim after any hardware sync.
Re-slice all plates after changing the printer, nozzle, material, process or geometry.

## Verification

[Print inspection](print-profile.json) records project and G-code digests, slice
results, the configuration audit, geometry comparisons and toolpath measurements.
Both trim projects return success with empty plate warning fields. All six
embedded G-code files match their CLI exports and MD5 entries. No support paths
are present. Model and brim footprints stay inside the bed.

The five bodies are closed, consistently wound, connected meshes. All seven
components, including modifiers, retain their geometry and placement within
0.000002 mm through slicing. The cavity CAD envelope is 270 × 270 × 74.649 mm;
the inverted core is 270 × 270 × 68 mm. Layer quantization puts their final
commanded heights at 74.64 and 68.16 mm respectively; these are not metrology
readings from a physical print.

Across 80 sampled mold layers, **24,407** outer-wall segments inside the surface
modifiers stay at or below 60 mm/s. The full shallow-ramp bands use 0.16 mm
layers. The greatest calculated flow on extrusion moves longer than 1 mm is
about **17.48 mm³/s**, including the 0.97 flow ratio and G-code rounding. The
inspection also records the larger ratios on tiny rounded segments. Circular
paths are included in these measurements.

| Passage / fit | Reading from the final paths |
|---|---|
| Four guide blades | 12.00 × 40.00 mm |
| Four guide bearings | 12.60 × 40.60 mm clear |
| Four square-nut slots | 8.40 mm clear width |
| Four jack-screw bores | About 5.75–5.76 mm diameter |
| Four washer pockets | About 25.37–25.39 mm diameter |
| Backing-air channels and tower exits | About 2.99 mm clear at the sampled mid-height |
| Silicone vents | About 2.43–2.45 mm above the first layer |
| Pour throat | About 10.97 mm diameter |
| Rod socket | About 6.40 mm through its body; about 6.10 mm at the thin entry lip |

Clearance readings subtract half the annotated road width from the distance to
its centreline. Arc sampling adds at most 0.002 mm sagitta. They describe nominal
toolpaths, not measured plastic. **Deburr the rod socket's narrow entry lip and
fit the actual 6.35 mm rod before coating.** It must slide freely to 28.8 mm depth.
Use a depth stop and preserve the blind end. Check all small fits on the witnesses.

[Mechanical verification](mechanical-verification.json) records the guide sweep,
hardware clearances and chamber envelope. At 32 mm working lift the guides retain
12 mm nominal engagement; the screw heads retain 1.8–3.0 mm clearance for
0.8–2.0 mm washers. [Section checks](extraction-loads.json) screen the arms and
blades for vertical and lateral loads. The [extraction instructions](extraction.md)
state the assumptions; no measured extraction force or certified capacity is assigned.

![Mold extrusion sections](print-paths.png)

![Extraction hardware extrusion sections](hardware-paths.png)

## At the bench

Dry the PETG, feed it from dry storage and print the witnesses. Let the mold halves
cool on the bed before removal. Clear the backing-air paths, silicone vents, pour
passage and rod entrance. Dry-assemble the halves and check the complete extraction
stroke before finishing. Finish both forming faces to the measured 0.20 mm net
growth described in [the finishing procedure](README.md#measure-the-finish).
Test the actual coating, release and silicone batch together before casting.
Use a hand hex key for extraction, advancing opposite sides equally.
