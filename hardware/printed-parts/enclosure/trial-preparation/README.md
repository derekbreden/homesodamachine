# Enclosure print preparation

[`prepare.py`](prepare.py) writes a fresh native Bambu Studio project for each piece of the
[complete enclosure print](../print-readiness.md) from its current STL. Every layer band, painted
face, ribbon, window and modifier box is read from that mesh, and every piece carries the
shared PET-GF recipe. [`pieces.json`](pieces.json) declares the pieces.

The [readiness objective](../print-readiness.md) is a complete working appliance ready
to ship. This preparation records manufacturing inputs and emitted paths; it does not
reduce that objective to fit or qualify the assembled machine by itself.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py list
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py back-top --slice --review
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py all --slice --review
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py dock-petgf --slice --review
```

`list` prints each piece's meshes, their digests and whether the region record binds them.
A run writes `.cache/prints/trial/<date>-<piece>-<printer>-<mesh digest>/`: the project,
`preparation.json` and `show-faces.npz`, the painted show faces in plate coordinates.
`preparation.json` holds the input digests, pose, yaw and plate placement, each derived band
and its measured span, the painted face counts, the ribbon, window and modifier boxes, and
each recipe change with its reason. `--printer` selects Mark1 (connection key `H2C`) or Mark2;
`--part` replaces a plate's declared parts, with per-part quantity, axis turns, walls and
infill. The `dock-petgf` plate is the whole dry dock: four keepers and the one return
block. Their manufacturing STLs already contain the print pose; use `turns=x:0`
for explicit declarations. Preparation imports no CAD kernel. `--slice` runs the installed Bambu Studio command
line on the project and keeps its archive beside it. No printer is contacted.

## Recipe

Every project starts from [`petgf.3mf`](../../petgf.3mf): its process and filament
presets, 0.20 mm first layer, 0.24 mm layers, `auto_brim` and Tree(auto)/Default supports.
The requested Z trim is Mark1 +0.18 mm and Mark2 +0.04 mm, written as
`faucet/refresh_print_project.py` writes it. [`petgf_cooling.py`](../../cadlib/petgf_cooling.py)
applies the localized cooling. Black PET-GF on the left 0.4 mm nozzle prints model,
support and interface. The solid-host modifiers come from
[`print-regions.json`](../enclosure/heat-set-review/print-regions.json) and set 100% zig-zag
infill only. A piece with regions stops when that record binds other STL/STEP digests;
`heat-set-review/print_regions.py` writes it from the current geometry under the CAD lock.
The model, support and brim beads keep the plate border (20 mm on unseasoned plates,
[`tools/bambu-printers.md`](../../../../tools/bambu-printers.md)); a single part takes the
yaw that leaves it the most room and sits centered, or at its declared `plate_offset_mm`
where its emitted envelope is lopsided. `auto_brim` sizes each volume group's brim while
slicing, so the review reads the emitted envelope; the footprint precheck adds a brim only
for fixed-width brim types.

| Piece | Printer | Read from the mesh | Recipe changes |
| --- | --- | --- | --- |
| `front-top` | Mark1 | 0.08 mm band over the R6 roof side edges' level run and the R18 display-to-roof roll; tie-channel rooms with local support blockers | Support XY 0.50 mm |
| `front-bottom` | Mark1 | Six-wall band through the handhold lifting-edge transition and its corner returns; 0.8 mm boundary strip of the flat lifting ceiling; removable arc fins along the lifting edges | — |
| `back-bottom` | Mark2 | Six-wall band through the handhold lifting-edge transition and its corner returns; 0.8 mm boundary strip of the flat lifting ceiling; removable arc fins on feet along the lifting edges | Plate offset X −5.1, Y +18.8 mm |
| `back-top` | Mark2 | Six-wall band through the roof side edges on the bed; one ribbon per sliding groove; tie-channel review windows | 50 mm bridge limit; 3 mm tree branches, 0.5° growth; plate offset X −5.4 mm |
| `pump-cartridge-cap` | Mark1 | Cartridge: 0.08 mm band over the lower hand-pocket rims, six-wall band through the upper rim transitions; cap crown-down | — |
| `funnel-frame` | Mark2 | — | No brim or elephant-foot compensation; support XY 0.50 mm |
| `factory-tools` | Mark2 | Tube tip setting jig as exported | — |
| `dock-petgf` | Mark1 | Four keepers and the return block, manufacturing exports already in print pose; the block lies on its top face | Six walls, 100% zig-zag per part |
| `labels` | Mark2 | [`../../drain-readiness/prepare.py`](../../drain-readiness/prepare.py) `labels`, under the CAD lock: closing layers on each face-up chip and DATA face and lettering top | — |

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

## Review

`review.py <directory>` reads the written project back against its record and the STLs
(`--project-only` before slicing), then the sliced archive:

- archive and G-code integrity and the emitted Z trim;
- emitted wall layers across each measured fine span
  ([`verify_round_layer_band.py`](../../../scripts/verify_round_layer_band.py)) and 0.24 mm
  layers through each six-wall band;
- the complete model, support and brim bead envelope against the plate border;
- support beads against the painted show faces, inside tie windows and inside ribbons, and
  the ribbons' own layers;
- sampled bead coverage of the model section inside each solid-host modifier;
- unbacked model roads in the fine bands, and the second layer's beads over the first;
- each object's support bodies, roots, build-up and interface islands, in plate and CAD
  coordinates ([`enclosure_support_audit.py`](../../../scripts/enclosure_support_audit.py)),
  written as `support-audit-<object>.json` for the removal-lane reading.

`review.json` records every reading and the checks it passes. Support removal, surface
finish, fit and strength are observations of the printed part.
