# Print preparation

[`prepare.py`](prepare.py) writes a fresh native Bambu Studio project for each piece of the
print set from its current STL, and [`pieces.json`](pieces.json) declares the pieces. The set
covers the enclosure quadrants, the pump bay, the funnel family, the cold-core stack, the small
PETG parts and the TPU joints and seals. Each piece names its printer, the hotend it is sliced
for (side, diameter, flow, and whether the stock needs a hardened one) and its material. Every
layer band, painted face, ribbon, window and modifier box is read from the mesh.

The [readiness objective](../print-readiness.md) is a complete working appliance ready
to ship. This preparation records manufacturing inputs and emitted paths; it does not
reduce that objective to fit or qualify the assembled machine by itself.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py list
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py back-top --slice --review
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py all --slice --review
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/labels.py --slice
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/step_meshes.py hardware/printed-parts/cold-core/prv-shroud/prv-shroud.step
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/step_meshes.py --check
```

`list` prints each piece's printer, hotend and material, its meshes and their digests, and
whether the region record binds them. A run writes
`.cache/prints/trial/<date>-<piece>-<printer>-<mesh digest>/`: the project, `preparation.json`
and `show-faces.npz`, the painted show faces in plate coordinates. `preparation.json` holds
the input digests, the hotend and material, pose, yaw and plate placement, each derived band
and its measured span, the painted face counts, the ribbon, window and modifier boxes, and each
recipe change with its reason. `--printer` selects Mark1 (connection key `H2C`) or Mark2;
`--part` replaces a plate's declared parts, with per-part quantity, axis turns, walls and
infill. Preparation imports no CAD kernel. `--slice` runs the installed Bambu Studio command
line on the project and keeps its archive beside it. No printer is contacted. Run it through
`tmp/takeover/cadq` while the swarm shares the machine.

Three kinds of piece are not prepared here. A piece with `external` names its own preparer,
which `--slice` runs. A piece with `archive` prints from a retained archive, and `list` checks
its bytes against the recorded digest. A part whose generator writes only a STEP gets its print
mesh from [`step_meshes.py`](step_meshes.py). That script reads the STEP's bodies, fuses a
part's lettering into it, and writes `<part>.stl` beside the STEP with
[`cadlib/print_mesh.py`](../../cadlib/print_mesh.py). It binds each STL to the STEP digest in
[`step-meshes.json`](step-meshes.json), and `prepare.py` refuses an STL whose STEP has moved
since.

[`labels.py`](labels.py) prepares the identification plates under the CAD lock, one plate per
chip colour: the six rear chips, the six tube collars, the DATA plate and nameplate 0001. Each
part's body and lettering come from its published STEP, posed face up. The chips, the DATA
plate and the nameplate lie on their flat backs; the collars lie on their flat faces. Each
plate uses `petgf.3mf` on both 0.4 mm nozzles, with white on the left and the plate's colour on
the right, at Mark2's +0.04 mm trim. The right nozzle takes its measured registration offset.
There are no supports or brim. One closing layer schedule puts a layer top on every face-up
face and lettering top. The plate's `review.json` reads integrity, the emitted trim, the bead
envelope against the border, the absence of support, every part printed and every closing top.

## Recipe

A piece starts from [`petgf.3mf`](../../petgf.3mf) unless it names its own saved project as
`profile`. The petgf.3mf recipe is two ordinary walls, 15% gyroid infill, a 0.20 mm first
layer, 0.24 mm layers, `auto_brim` and Tree(auto)/Default supports. Two walls and 15% gyroid
remain the production baseline unless Derek explicitly requests a change. The local solid
modifiers, six-wall surface bands and part-specific recipes below retain their specified settings.
`filament_from` takes another saved project's filament block: every setting the filament's
system presets define, with the per-hotend variant index. `z_trim_mm`, `filament_colour` and
`filament_mapping` replace the printer's defaults, each with its reason. `nozzle` is checked
against the recipe: the diameter and flow type the slice uses on that side, and the hotend its
filament maps to.

The requested Z trim is Mark1 +0.18 mm and Mark2 +0.04 mm, written as
`faucet/refresh_print_project.py` writes it, unless a piece states its own.
[`petgf_cooling.py`](../../cadlib/petgf_cooling.py) applies the localized cooling to PET-GF
slots. Black PET-GF on the left 0.4 mm nozzle prints model, support and interface on the
enclosure pieces. The solid-host modifiers come from
[`print-regions.json`](../enclosure/heat-set-review/print-regions.json) and set 100% zig-zag
infill only. A piece with regions stops when that record binds other STL/STEP digests;
`heat-set-review/print_regions.py` writes it from the current geometry under the CAD lock.
The model, support and brim beads keep the plate border (20 mm on unseasoned plates,
[`tools/bambu-printers.md`](../../../../tools/bambu-printers.md)); a single part takes the
yaw that leaves it the most room and sits centered, or at its declared `plate_offset_mm`
where its emitted envelope is lopsided. `auto_brim` sizes each volume group's brim while
slicing, so the review reads the emitted envelope; the footprint precheck adds a brim only
for fixed-width brim types.

| Piece | Printer, hotend | Material | Read from the mesh, or pose | Recipe changes |
| --- | --- | --- | --- | --- |
| `front-top` | Mark1, left 0.4 | PET-GF black | 0.08 mm band over the R6 roof side edges' level run and the R18 display-to-roof roll | Support XY 0.50 mm |
| `front-bottom` | Mark1, left 0.4 | PET-GF black | Six-wall band through the handhold lifting-edge transition and its corner returns; 0.8 mm boundary strip of the flat lifting ceiling; removable arc fins along the lifting edges | — |
| `back-top` | Mark2, left 0.4 | PET-GF black | Six-wall band through the roof side edges on the bed; one ribbon per sliding groove; tie-channel review windows | 50 mm bridge limit; 3 mm tree branches, 0.5° growth; plate offset X −5.4 mm |
| `back-bottom` | Mark2, left 0.4 | PET-GF black | Six-wall band through the handhold lifting-edge transition and its corner returns; 0.8 mm boundary strip of the flat lifting ceiling; removable arc fins on feet along the lifting edges | Plate offset Y +18.8 mm |
| `pump-cradle-clamp` | Mark1, left 0.4 | PET-GF black | Pump cradle as exported; clamp crown-down | — |
| `funnel-frame` | Mark2, left 0.4 | PET-GF black | On its lower feet, as exported | No brim or elephant-foot compensation; support XY 0.50 mm |
| `factory-tools` | Mark2, left 0.4 | PET-GF black | Tube tip setting jig as exported | — |
| `display-cover` | Mark1, left 0.4 | PET-GF black | Face up, back and wings on the bed, as exported | — |
| `elbow-cradle` | Mark1, left 0.4 | PET-GF black | On its bottom, as exported | — |
| `soda-bend-holder` | Mark1, left 0.4 | PET-GF black | The flat back of the D on the bed, as exported | Six walls, 100% zig-zag (the accepted 2026-10-23 article) |
| `foam-shell`, `foam-cap-top`, `foam-cap-lid-top`, `foam-cap-lid-bottom` | Mark2, left 0.8 High Flow | PET-GF black | As exported, each on its flat face | The 0.8 mm shell project's process with petgf.3mf's filament; the exterior's Standard-hotend temperature, flow and 18 mm³/s cap on the High Flow entry |
| `foam-cap-bottom` | Mark2, left 0.8 High Flow | PET-GF black | Half a turn about X, onto its flat face | As the other cold-core pieces |
| `labels` | Mark2, both 0.4 | PET-GF, two colours | [`labels.py`](labels.py) | — |
| `funnel-cover` | Mark1, left 0.4 | PETG Basic black | [`zone-c/funnel-cover/prepare_print.py`](../../zone-c/funnel-cover/prepare_print.py) | — |
| `funnel-mold` | Mark1, right 0.4 | PETG Translucent | [`tools/funnel-mold-print/prepare_print.py`](../../../../tools/funnel-mold-print/prepare_print.py) | — |
| `reservoirs` | Mark1, right 0.8 | PETG Translucent | Retained two-plate native archive | — |
| `level-floats` | Mark2, right 0.4 | ASA Aero white | Retained three-float archive with its RC62 pause | — |
| `pump-elbows` | Mark2, right 0.6 | Siraya TPU 85A | Retained processed archive with its deposited links | — |
| `asse-vent-sleeve` | Mark1, right 0.6 | Siraya TPU 85A | Upright, the large socket on the bed | The accepted Siraya single's project: zero user Z trim, glued Engineering Plate |
| `asse-cuffs` | Mark1, right 0.6 | Siraya TPU 85A | Half a turn about X, onto each tube end | As the vent sleeve; 2 mm part gap |
| `seals` | Mark2, right 0.6 | Bambu TPU 85A | Flat, as exported | The 2026-10-08 flat gasket project; 3 mm part gap |
| `small-petg` | Mark1, left 0.4 | PETG Basic black | Copper covers on their interior flange; PRV shroud cap down; reed bridge on its convex face; fuse clamp on its side | petgf.3mf's process with the funnel cover's PETG filament |
| `factory-petg` | Mark1, left 0.4 | PETG Basic black | Coil mandrel and setting gauge as exported | As `small-petg` |

## Declared features

Each feature selects faces by orientation and by place on the part's own bounds in its
print frame, and states an `expect` range. A feature whose faces are missing, or whose
measured extent leaves its range, stops the preparation and reports what was found.

- **`fine_band`** — an inward/top show round. Its connected faces' print-Z extent is the
  span; the 0.08 mm layer range starts one ordinary layer below it and ends one fine layer
  above it, so the span's top lies inside a fine layer. Its faces are painted support-blocked.
- **`transition_band`** — an expanding print-down round with the 0.5:1 additive chamfer of
  [`overhang_round.py`](../../cadlib/overhang_round.py). The foot is the flat face most
  chamfer area starts from; the measured chamfer rise matches the declared radius within
  10%. The band runs from the lowest chamfer face through the retained arc at 0.24 mm with
  six walls, and its downward exterior faces are painted support-blocked.
- **`ceiling_inset`** — the flat ceiling at a transition's foot keeps tree contacts the
  declared distance inside its boundary, painted on subdivided facets.
- **`groove_ribbons`** — each long, narrow flat face printing down at the top of the part is
  a caught face over a sliding groove. A two-wall, hollow ribbon stands in the groove one empty
  layer above its floor and stops two empty layers under the caught face, 0.40 mm inside its
  edges. Automatic support is blocked on the caught faces and the ribbons, and the solid-host
  modifiers stop at the ribbons.
- **`tie_windows`** — each rectangular print-down roof one zip-tie channel wide, inside the
  exterior skin, is the top of a tie channel; its room down to the floor or the declared
  cavity depth is a window. `blockers` puts a support blocker in each window.
- **`edge_fins`** — interrupted removable walls from the bed to a flat ceiling's exterior
  edge, with narrow blockers over their contact strips
  ([printed-parts/AGENTS.md](../../AGENTS.md#supports)). Both bottoms carry them along the
  handhold lifting edges. `foot_outboard_mm`, `foot_inboard_mm` and `foot_height_mm` stand
  each fin on a flat foot of the same removable part, its own bed anchor; back-bottom's
  fins have feet.

A part may also declare one **`pause`**: parts loaded into closed slots mid-print. Its slot
boxes become support blockers, overlapping their roofs by `blocker_roof_overlap_mm` so the
roof faces cannot request support in the loading slots. `--slice` slices twice: the first slice gives the emitted
layers, the pause (`M400 U1` with its loading text) goes on the first layer sliced above the
slots' roof, and that layer's bottom must clear the loaded stack's top.

## Review

`review.py <directory>` reads the written project back against its record and the STLs
(`--project-only` before slicing), then the sliced archive:

- archive and G-code integrity and the emitted Z trim;
- emitted wall layers across each measured fine span
  ([`verify_round_layer_band.py`](../../../scripts/verify_round_layer_band.py)) and 0.24 mm
  layers through each six-wall band;
- the complete model, support and brim bead envelope against the plate border;
- support beads against the painted show faces, inside tie windows, ribbons and pause
  slots, and the ribbons' own layers;
- the one emitted pause opening its planned layer before any of that layer's moves;
- sampled bead coverage of the model section inside each solid-host modifier;
- unbacked model roads in the fine bands, and the second layer's beads over the first;
- each object's support bodies, roots, build-up and interface islands, in plate and CAD
  coordinates ([`enclosure_support_audit.py`](../../../scripts/enclosure_support_audit.py)),
  written as `support-audit-<object>.json` for the removal-lane reading.

`review.json` records every reading and the checks it passes. Support removal, surface
finish, fit and strength are observations of the printed part.
