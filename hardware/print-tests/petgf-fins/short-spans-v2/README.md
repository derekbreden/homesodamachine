# PET-GF short bridges and full-length ramps — Mark2

This comparison asks whether small bridges form on dependable model anchors,
whether a removable fin provides a usable landing, and whether fixed part-fan
cooling improves the retained surface. The customer outcomes are clean visible
surfaces and smooth sliding faces after support removal.

The two plates use the same 16 test meshes and placements. A separate embossed
FAN 0 or FAN 30 tag identifies the cooling treatment. Mark2 accepted the fan-off
plate as **task 1339729875** on 2026-10-14; [its launch record](launch-fan0.json)
binds the submitted archive to acceptance. The 30% plate is prepared for the
subsequent cleared-bed print.
[Plate map](plate-layout.png).

Each native estimate is **about 56 min 42 s and 21.18 g**, across **115 layers**.
The complete emitted model-bead envelope stays at least **101 mm** inside the
usable bed boundary. The native review confirms 0%/30% part-fan commands on
every ramp feature and the first roof layers, with 25 mm/s axial bridge rasters.

| IDs | Geometry and question |
| --- | --- |
| C2, C4, C6, C8 | 2, 4, 6 and 8 mm clear bridges between two permanent 3 mm model posts. Both end anchor regions exist before the roof starts. |
| F2, F4, F6, F8 | The same clear spans from a permanent model post to seven one-layer teeth on a removable fin. The lower teeth reach 1.2 mm under the roof; the two corner teeth are 0.8 mm wide and the five interior teeth 0.5 mm wide. Six upper tines cross 0.24 mm side clearance. |
| C4Y, F4Y | 4 mm comparisons rotated 90° to bridge along bed Y. The others bridge along X. |
| S30, S35, S40 | Unsupported 30°, 35° and 40° ramps measured up from the bed, each with 14 mm horizontal reach and 12 mm depth. |
| R30, R35, R40 | The same ramps reversed 180° to compare the side that develops the edge defect. |

All IDs are embossed on bed feet. The roof is 1.92 mm thick and 12 mm deep.
Its underside starts at Z18.20 for the 2 mm span, Z20.60 for 4 mm, Z23.00 for
6 mm and Z25.40 for 8 mm. The first roof extrusions are respectively Z18.44,
Z20.84, Z23.24 and Z25.64. All ramps finish first; each shorter roof finishes
before the next span begins. An AI interruption at a longer span therefore
leaves the completed shorter roofs and ramps available for assessment.

The fin cases have one permanently anchored model end. They measure landing on
a fin after establishing a model anchor; they do not qualify a shelf that starts
entirely on two opposing fins. The fin's lower teeth and permanent post must
actually hold, which the physical result will determine.

## Basis and print process

The [first plate result](../physical-result.json) records AI interruption with
no continuation. The named failed bridges are its first three roof attempts
on layer 44, Z10.52. Its ramps have only their layer-43 extent, so S40's reported
clean edge concerns about 8.44 mm of commanded reach, not the planned 14 mm.

The [first shelf-path review](../shelf-start-review.json) shows perimeter paths
starting over sparse teeth before the axial bridge raster. A failed roof there
combines initial perimeter formation, attachment and clear-span bridging.
The C/F comparison gives those mechanisms distinct witnesses.

- Polymaker Fiberon PET-GF15, fixed left hardened Standard 0.4 mm nozzle,
  external spool 254, Textured PEI. PET-CF is its printer metadata.
- Mark2 +0.04 mm requested Z trim, emitted `G29.1 Z0.02` on textured PEI.
- 0.20 mm first layer and fixed 0.24 mm layers. Two walls, 15% grid infill,
  265°C first layer, 280°C normal temperature and 80°C bed from the working profile.
- Slicer supports, brims and skirts disabled. Feet belong to the model geometry.
- Part fan held at either 0% or 30% after the first three layers, including
  overhangs and bridges. Auxiliary-fan setting remains 0%; other working-profile
  temperatures, speeds, exhaust settings and layer-time slowdown remain the same.
- The 30% treatment is a surface-quality experiment local to this plate.
  [Polymaker's data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf)
  recommends fan off. A smoother surface does not establish layer bonding,
  load capacity, lifetime or annealed behavior; the production profile is unchanged.

The emitted fan commands, bridge axes and speeds, contact footprints, first
roof anchors, completed-ramp order and bead envelope are recorded separately in
each `.native-review.json`. The editable projects and native `.gcode.3mf`
archives carry the treatment in their filenames. Each print-only archive retains
the reviewed G-code bytes for Studio's saved-slice send. Launch metadata binds
the submitted archive, reported printer name and task ID when a plate is sent.

## Read the physical result

Keep each ID with its part and photograph the undersides before sanding or
removing loose strands. Record both formation and retained finish. Use the
existing calipers and straightedge where measurements help; fingers first and
ordinary pliers only if needed for fin removal.

1. A usable C bridge must complete with a continuous retained underside and
   no drooping loose strands. Start at C2 and bracket the first failing span.
2. Compare F to C at each span. A clean C and failed F points toward fin landing
   or attachment. Failure of both leaves bridging/process behavior unresolved.
   A fin that held but tore the roof during removal is a separate failure.
3. Compare C4Y/F4Y with C4/F4. A direction difference remains part of the result.
4. On S/R, inspect the entire 14 mm reach, especially the final corner and
   each lateral edge. Note curling, sag, missing material and snagging texture.
   Reversal helps distinguish an edge/direction effect from a symmetric angle limit.
5. Compare each corresponding ID across FAN 0 and FAN 30. Use the same surface
   judgement and record downward projection when measurable. Prefer a cooling
   treatment only within the demonstrated surface scope.

The CSV sheets leave unobserved values blank. Completion alone establishes no
sliding fit. A candidate still requires a matched real joint with clean full-travel
motion and retention at its intended clearance. The staged support heights,
17-object layer return time, 12 mm depth, contact pattern and 1.92 mm section are
part of this evidence; a result is not a universal PET-GF bridge limit.

## Manual reproduction

Run `tools/cad-venv/bin/python
hardware/print-tests/petgf-fins/short-spans-v2/make_plate.py` from the repository
root. Slice each `.3mf` with the installed Bambu Studio using
`--arrange 0 --orient 0 --slice 0` and an absolute output directory.
Run `inspect_slice.py <saved-native-archive>` to collect native path evidence.
These commands are manual experiment tools and do not join a build or commit path.

Use the documented [saved-slice print submission](../../../../tools/bambu-printers.md#bambu-studio-send-from-an-existing-slice)
with Timelapse On, Bed Leveling On, Flow Dynamics Calibration Auto and Nozzle
Offset Calibration Auto. Observe at least 180 seconds between starts on the
shared printer circuit. Send the 30% comparison after a cleared-bed report.
