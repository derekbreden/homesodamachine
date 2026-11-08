# Print preparation

The `enclosure-print-prep` program ([`prepare.rs`](prepare.rs)) writes a fresh native Bambu
Studio project for each piece of the print set from its current STL, and
[`pieces.json`](pieces.json) declares the pieces. The set
covers the enclosure quadrants, the pump bay, the funnel family, the cold-core stack, the small
PETG parts and the TPU joints and seals. Each piece names its printer, the hotend it is sliced
for (side, diameter, flow, and whether the stock needs a hardened one) and its material. Every
layer band, painted face, ribbon, window and modifier box is read from the mesh.

The [readiness objective](../print-readiness.md) is a complete working appliance ready
to ship. This preparation records manufacturing inputs and emitted paths; it does not
reduce that objective to fit or qualify the assembled machine by itself.

```sh
python3 tools/run.py -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep
tools/hsm/target/release/enclosure-print-prep list
tools/hsm/target/release/enclosure-print-prep back-top --slice --review
tools/hsm/target/release/enclosure-print-prep all --slice --review
tools/hsm/target/release/enclosure-labels --slice
```

`list` prints each piece's printer, hotend and material, its meshes and their digests, and
whether the region record binds them. A run writes
`.cache/prints/trial/<date>-<piece>-<printer>-<mesh digest>/`: the project, `preparation.json`
and `show-faces.npz`, the painted show faces in plate coordinates. `preparation.json` holds
the input digests, the hotend and material, pose, yaw and plate placement, each derived band
and its measured span, the painted face counts, the ribbon, window and modifier boxes, and each
recipe change with its reason. `--printer` selects Mark1 (connection key `H2C`) or Mark2;
`--part` replaces a plate's declared parts, with per-part quantity, axis turns, walls and
infill. Preparation reads the exported meshes and builds no geometry. `--slice` runs the
installed Bambu Studio command line on the project and keeps its archive beside it, and
`--review` reads the project and archive back as the review below does. No printer is
contacted. Preparing and slicing take one of the Mac's run slots.

Some pieces are not prepared here. A piece with `external` names its own preparer, which
`--slice` runs. A piece with `archive` prints from a retained archive, and `list` checks its
bytes against the recorded digest. Every other piece prints the STL its part's generator
writes beside the STEP.

The `enclosure-labels` program ([`labels.rs`](labels.rs)) prepares the identification plates,
one plate per chip colour: the six rear chips, the six tube collars and nameplate 0001. Each
part's body and lettering are the two solids its generator writes into `<part>.step.npz`,
posed face up. The chips and the
nameplate lie on their flat backs; the collars lie on their flat faces. Each
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

`cap_finish_lifts` limits the saved end routine's clearance moves to the printer's
available vertical travel, allowing for the requested trim. Back-top retains its ceiling-down pose.

Native support regions distinguish functional interiors from exterior request blockers.
An exterior blocker marked `review_interior: false` still masks support requests; its
box does not define an inaccessible void. The native record also names accessible
support targets, which become enforcers in the manual-tree preparation.

The native review intersects each reinforcement modifier's posed section with
the model section. Solid-host coverage measures the interior beyond the local
bead radius; the outline coverage remains in the reading. Layer-height coverage
uses the project's declared bed layer and preserves feature tags across layers.

Each printer's Z trim in `pieces.json` goes into the start G-code's plate compensation,
unless a piece states its own. The `petgf-cooling` program
([`petgf_cooling.rs`](../../cadlib/petgf_cooling.rs)) applies the localized cooling to PET-GF
slots. Black PET-GF on the left 0.4 mm nozzle prints model, support and interface on the
enclosure pieces. The solid-host modifiers come from
[`print-regions.json`](../enclosure/heat-set-review/print-regions.json) and set 100% zig-zag
infill only. A piece with regions stops when that record binds other STL/STEP digests;
`enclosure-print-regions` ([`print_regions.rs`](../enclosure/heat-set-review/print_regions.rs)) writes it from the current geometry.
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
| `back-top` | Mark2, left 0.4 | PET-GF black | Ceiling-down, rear flutes clear of the bed; additive roof-edge transition; local solid catch and rail bands | Manual Tree Slim at native accessible contacts; support-free receiver bridges, passages and sockets |
| `back-bottom` | Mark2, left 0.4 | PET-GF black | Six-wall band through the handhold lifting-edge transition and its corner returns; 0.8 mm boundary strip of the flat lifting ceiling; removable arc fins on feet along the lifting edges | Plate offset Y +18.8 mm; automatic-tree branch angle 20° |
| `pump-retainer` | Mark1, left 0.4 | PET-GF black | Broad lower retainer, Y-minus end on the bed; build axis +Y | Three Classic walls; local solid snap hosts |
| `rear-equipment-caps` | Mark2, left 0.4 | PET-GF black | ASSE, Pisco, regulator and meter caps as exported, mouths up; 15 mm spacing | — |
| `single-regulator-cap` | Mark2, production cap hotend | PET-GF black | Approved regulator cap pose; combined cap and tower envelope centered | Native smooth timelapse and constant-width prime tower; [layer-time record](../rear-equipment-caps/prints/2026-11-07-single-regulator-mark2/job.json) |
| `regulator-entry-comparison` | Mark2, production cap hotend | PET-GF black | Standard and taller lead-in covers on axial ends; complete matching receivers in back-top's print pose | Production layer schedules, ceiling-down support-free receivers and cooling time from the other articles; [comparison](../rear-equipment-caps/entry-study/README.md) |
| `funnel-frame` | Mark2, left 0.4 | PET-GF black | On its lower feet, as exported | No brim or elephant-foot compensation; support XY 0.50 mm |
| `factory-tools` | Mark2, left 0.4 | PET-GF black | Tube tip setting jig as exported | — |
| `display-cover` | Mark1, left 0.4 | PET-GF black | Flat back on the bed, counterbores facing upward | Solid deposition; support-free |
| `elbow-cradle` | Mark1, left 0.4 | PET-GF black | On its bottom, as exported | — |
| `soda-bend-holder` | Mark1, left 0.4 | PET-GF black | The flat back of the D on the bed, as exported | Six walls, 100% zig-zag (the accepted 2026-10-23 article) |
| `foam-shell`, `foam-cap-top`, `foam-cap-lid-bottom` | Mark2, left 0.4 Standard | PET-GF black | As exported, each on its flat face | Classic, three loops, 15% gyroid; 0.24 mm layers and 0.20 mm first layer; support-free |
| `foam-cap-lid-top` | Mark1, left 0.4 Standard | PET-GF black | As exported, on its flat face | Classic, three loops, 15% gyroid; 0.24 mm layers and 0.20 mm first layer; Tree(auto)/Default |
| `foam-cap-bottom` | Mark2, left 0.4 Standard | PET-GF black | Half a turn about X, onto its flat face | As the other cold-core pieces |
| `labels` | Mark2, both 0.4 | PET-GF, two colours | [`labels.rs`](labels.rs) | — |
| `funnel-cover` | Mark1, left 0.4 | PETG Basic black | [`zone-c/funnel-cover/prepare_print.rs`](../../zone-c/funnel-cover/prepare_print.rs) | — |
| `funnel-mold` | Mark1, right 0.4 | PETG Translucent | [`tools/funnel-mold-print/prepare_print.rs`](../../../../tools/funnel-mold-print/prepare_print.rs) | — |
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

The handhold selectors use `wall_x_mm`, measured from the declared straight walls in the
source frame. Projecting exterior columns do not move that reference. The lifting rounds
and ceilings are selected in the lower half of each bottom piece.

- **`fine_band`** — a show surface. Its connected faces' print-Z extent is the
  span; the 0.08 mm layer range starts one ordinary layer below it and ends one fine layer
  above it, so the span's top lies inside a fine layer. Its faces are painted support-blocked.
  `allow_support` retains accessible external contacts on a supported show surface.
- **`transition_band`** — an expanding print-down round with the 0.5:1 additive chamfer of
  [`overhang_round.py`](../../cadlib/overhang_round.py). The foot is where the straight run
  starts, the lowest point of the chamfer faces that reach its top; the rise from it matches
  the declared radius within 10%. A corner return follows its arc lower, so the band runs from
  the lowest chamfer face through the retained arc at 0.24 mm with six walls, and its downward
  exterior faces are painted support-blocked.
- **`ceiling_inset`** — the flat ceiling at a transition's foot keeps tree contacts the
  declared distance inside its boundary, painted on subdivided facets.
- **`native_support_free`** — reads support exclusions emitted by the native part
  generator and bound to the source STL. Source-frame bounds follow the object's
  print pose and plate placement. Downward faces are painted and the named volumes
  block support requests. The native review reads support beads against the actual
  passage profiles, including branches routed toward other features. Back-top uses
  this for its inaccessible receivers, teardrop bores, valve sockets and vent passage.
  Direction-specific exclusions apply when their source-frame direction matches the
  build direction. Its separate bridge regions add local solid modifiers with the
  corresponding plate-space bridge angle. These do not block supports.

- **`groove_ribbons`** — each long, narrow flat face printing down at the top of the part is
  a caught face over a sliding groove. A two-wall, hollow ribbon stands in the groove one empty
  layer above its floor and stops two empty layers under the caught face, 0.40 mm inside its
  edges. Automatic support is blocked on the caught faces and the ribbons, and the solid-host
  modifiers stop at the ribbons.
- **`tie_windows`** — each rectangular print-down roof one zip-tie channel wide, inside the
  exterior skin, is the top of a tie channel; its room down to the floor or the declared
  cavity depth is a window. `blockers` puts a support blocker in each window;
  `blocker_roof_overlap_mm` extends it into the requesting roof.
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

`tools/hsm/target/release/enclosure-print-review <directory>` ([`review.rs`](review.rs))
reads the written project back against its record and the STLs (`--project-only` before
slicing), then the sliced archive:

- archive and G-code integrity and the emitted Z trim;
- emitted wall layers across each measured fine span, and ordinary layers through each
  six-wall band;
- the complete model, support and brim bead envelope against the plate border;
- support beads against the painted show faces, inside tie windows and inside the declared
  support-free interiors;
- sampled bead coverage of the model section inside each solid-host modifier;
- the second layer's beads over the first;
- each object's support bodies, roots, build-up and interface islands, in plate and CAD
  coordinates (the support audit, `support-audit`), written as `support-audit-<object>.json`
  for the removal-lane reading.

`review.json` records every reading and the checks it passes. Support removal, surface
finish, fit and strength are observations of the printed part.

`--unbacked` requests adjacent-layer road-shadow statistics throughout every fine
band. The report records whether this optional diagnostic was requested.
