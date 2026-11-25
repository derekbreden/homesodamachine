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
tools/run -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep
tools/hsm/target/release/enclosure-print-prep list
tools/hsm/target/release/enclosure-print-prep back-top --slice --review
tools/hsm/target/release/enclosure-print-prep back-top --bed 'Textured PEI Plate' --slice --review
tools/run -- tools/hsm/target/release/enclosure-print-prep machine --slice --review
tools/run -- tools/hsm/target/release/enclosure-labels --mark1-identification --slice
tools/run -- tools/hsm/target/release/enclosure-labels --collars-only --slice
```

`machine` prepares the enclosure quadrants, cold-core casing, funnel frame and consolidated
accessory plates from the `machine` list in [`pieces.json`](pieces.json).
The identification and faucet plates have their own preparers. The reservoir bodies and caps,
floats, seals and collars retain their material-specific projects.
`all` walks the diagnostic inventory, which also includes tooling, refill plates and trials.

`list` prints each piece's printer, hotend and material, its meshes and their digests, and
whether the region record binds them. A run writes
`.cache/prints/trial/<date>-<piece>-<printer>-<mesh digest>/`: the project, `preparation.json`
and `show-faces.npz`, the painted show faces in plate coordinates. `preparation.json` holds
the input digests, the hotend and material, pose, yaw and plate placement, each derived band
and its measured span, the painted face counts, the ribbon, window and modifier boxes, and each
recipe change with its reason. `--printer` selects Mark1 (connection key `H2C`) or Mark2.
`--bed` selects Textured PEI or the Engineering Plate for a named recipe.
`--part` replaces a plate's declared parts, with per-part quantity, axis turns, walls and
infill. Preparation reads the exported meshes and builds no geometry. `--slice` runs the
installed Bambu Studio command line on the project and keeps its archive beside it, and
`--review` reads the project and archive back as the review below does. No printer is
contacted. Preparing and slicing take one of the Mac's run slots.

Some pieces are not prepared here. A piece with `external` names its own preparer, which
`--slice` runs. A piece with `archive` prints from a retained archive, and `list` checks its
bytes against the recorded digest. The archive's `source_commit`, when present, identifies
its file in Git. Every other piece prints the STL its part's generator
writes beside the STEP.

The `enclosure-labels` program ([`labels.rs`](labels.rs)) prepares the identification plates.
`--mark1-identification` puts the current rear chips, unit nameplate and status plate into the
[accepted Mark1 project](../display-cover/prints/2026-11-08-identification-set-mark1-right-z005/README.md).
It reads the solids from their current STEP payloads and retains the fine-nozzle PETG recipe,
side-specific trim, bed positions and material assignments, including the clear status window.
The flat backs sit on the glued Engineering Plate.

`--collars-only` makes a Mark2 PET-GF plate for each collar colour. The right nozzle takes its
measured registration offset. The collars lie with the lettered faces on the bed and their bore
crowns clear of support. Both production modes keep the flat identification surfaces free of
supports and brim. The plate's `review.json` records archive integrity, emitted trim, bead
margins, support count, printed objects and layer heights at the face-up lettering tops.

## Recipe

A piece starts from [`petgf.profile.json`](../../petgf.profile.json) unless it names its own settings as
`profile`. The shared recipe is two ordinary walls, 15% gyroid infill, a 0.20 mm first
layer, 0.24 mm layers, `auto_brim` and Tree(auto)/Default supports. Two walls and 15% gyroid
remain the production baseline unless Derek explicitly requests a change. The local solid
modifiers, six-wall surface bands and part-specific recipes below retain their specified settings.
PET-GF contact and bridge settings inherit Support D from the shared profile, including
when the rest of a recipe comes from an accepted older project. Embedded filament bridge
speeds follow the same recipe. Part-specific support styles, roots, fins, manual targets
and support-free regions retain their own settings. The
[rollout record](../../support-D-rollout.json) binds the current projects and slice status;
historical machine archives retain their recorded process.
`filament_from` takes another saved project's filament block: every setting the filament's
system presets define, with the per-hotend variant index. `z_trim_mm`, `filament_colour` and
`filament_mapping` replace the printer's defaults, each with its reason. `nozzle` is checked
against the recipe: the diameter and flow type the slice uses on that side, and the hotend its
filament maps to.

`cap_finish_lifts` limits the saved end routine's clearance moves to the printer's
available vertical travel, allowing for the requested trim. Back-top retains its ceiling-down pose.

Native support regions distinguish functional interiors from exterior request blockers.
An exterior blocker marked `review_interior: false` still masks support requests; the
review does not read support inside its box. The native record also names
support targets, which become enforcers in the manual-tree preparation. Back-top's
same record carries its local rail caps as removable print stock.

The regulator cap's [contact recipe](../rear-equipment-caps/contact.json) samples its fitted
roof from the posed mesh. The preparer writes the physical project and the contact-band slicing
project. After native slicing and cooling, it restores the model and support moves to the
physical frame and binds their archive to the original cap meshes.

The native review intersects each reinforcement modifier's posed section with
the model section. Solid-host coverage measures the interior beyond the local
bead radius; the outline coverage remains in the reading. Layer-height coverage
uses the project's declared bed layer and preserves feature tags across layers.

Each printer's Z trim in `pieces.json` for the plate a piece prints on, Textured PEI or the
Engineering Plate, goes into the start G-code's plate compensation. For PET-GF on textured
PEI with the enclosure hotend, the preparer uses `textured_pei_z_trim` when every part on
the plate is listed for its large contact area on the print bed. A piece can also declare
its own trim for a material-specific recipe. The `petgf-cooling` program
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
| `front-bottom` | Mark1, left 0.4 | PET-GF black | Integral handhold corbels with the shared ordinary layer schedule | Tree(auto)/Default; short rail trees rooted on their cavity floors |
| `back-top` | Mark1, left 0.4 | PET-GF black | Ceiling-down on textured PEI, rear flutes clear of the bed; additive roof-edge transition; local solid rail bands | Manual trees at accessible contacts, receiver catches, meter floors and inlet roofs; removable rail caps and tube-wing strips rooted on the part; self-supporting nameplate ledges and protected corbelled catches, sockets and pilots |
| `back-bottom` | Mark2, left 0.4 | PET-GF black | Integral handhold corbels with the shared ordinary layer schedule | Saved plate offset and automatic-tree branch angle |
| `pump-retainer` | Mark1, left 0.4 | PET-GF black | Lower retainer on the Y-minus end | Classic perimeters, solid screw seats and bridged screw openings |
| `rear-equipment-caps` | Mark2, left 0.4 | PET-GF black | ASSE, Pisco, regulator and meter caps as exported, mouths up; 15 mm spacing | Nonplanar regulator contact, bridged meter shoulder |
| `single-regulator-cap` | Mark2, production cap hotend | PET-GF black | Approved regulator cap pose; combined cap and tower envelope centered | Nonplanar fitted contact, native smooth timelapse and constant-width prime tower; [layer-time record](https://github.com/derekbreden/homesodamachine/blob/0016c68223af1b237a3f23bc608fc248a7c0d7d5/hardware/printed-parts/enclosure/rear-equipment-caps/prints/2026-11-07-single-regulator-mark2/job.json) |
| `single-pisco-cap` | Mark2, production cap hotend | PET-GF black | Pisco cover on its exported axial end; combined cap and tower envelope centered | Textured PEI, support-free, native smooth timelapse and constant-width prime tower. [Fitted cover and production slice](../rear-equipment-caps/pisco-fit.json) |
| `regulator-entry-comparison` | Mark2, production cap hotend | PET-GF black | Standard and taller lead-in covers on axial ends; complete matching receivers in back-top's print pose | Production layer schedules, ceiling-down support-free receivers and cooling time from the other articles; [comparison](../rear-equipment-caps/entry-study/README.md) |
| `small-petgf` | Mark2, left 0.4 | PET-GF black | The accessory plate carries the rear caps, pump cap, machine display cover, pump retainers, bend holders, drain-elbow cradle, umbilical organizer and collet press in their print poses | Object settings preserve each part's walls, infill and support recipe. The shallowest overhangs print at wall speed. Smooth timelapse and the tower give the cap layers time to cool. |
| `funnel-frame` | Mark2, left 0.4 | PET-GF black | Frame on its lower feet, V-G tube clip on its flat fore end | Frame support XY 0.50 mm. Clip has three walls and solid fill. Both print without a brim or elephant-foot compensation. |
| `factory-tools` | Mark2, left 0.4 | PET-GF black | Tube tip setting jig as exported | — |
| `display-cover` | Mark1, left 0.4 | PET-GF black | Flat back on the bed, counterbores facing upward | Solid deposition; support-free |
| `elbow-cradle` | Mark1, left 0.4 | PET-GF black | On its bottom, as exported | — |
| `soda-bend-holder` | Mark1, left 0.4 | PET-GF black | The flat back of the D on the bed, as exported | Six walls, 100% zig-zag (the accepted 2026-10-23 article) |
| `foam-shell` | Mark2, left 0.4 Standard | PET-GF black | As exported, on its flat face | Classic, three loops, 15% gyroid; 0.24 mm layers and 0.20 mm first layer; support-free |
| `foam-cap-lid-top` | Mark1, left 0.4 Standard | PET-GF black | As exported, on its flat face | Classic, three loops, 15% gyroid; 0.24 mm layers and 0.20 mm first layer; Tree(auto)/Default |
| `foam-cap-bottom` | Mark2, left 0.4 Standard | PET-GF black | Half a turn about X, onto its flat face | As the other cold-core pieces |
| `labels` | Mark2, both 0.4 | PET-GF, two colours | [`labels.rs`](labels.rs) | — |
| `funnel-cover` | Mark1, left 0.4 | PETG Basic black | [`zone-c/funnel-cover/prepare_print.rs`](../../zone-c/funnel-cover/prepare_print.rs) | — |
| `funnel-mold` | Mark1, right 0.4 | PETG Translucent | [`tools/funnel-mold-print/prepare_print.rs`](../../../../tools/funnel-mold-print/prepare_print.rs) | — |
| `asse-vent-sleeve` | Mark1, right 0.6 | Siraya TPU 85A | Upright, the large socket on the bed | The accepted Siraya single's project: zero user Z trim, glued Engineering Plate |
| `seals` | Mark2, right | Bambu TPU 85A | Flat, as exported | Reservoir cap gaskets |
| `display-gasket` | Mark2, right | Bambu TPU 90A, black | Flat, as exported | Glued Engineering Plate, solid, support-free |
| `reservoir-grips` | Mark2, right | Bambu TPU 90A, white | Broad flanges on the bed, bores upright | Glued Engineering Plate; support-free |
| `cold-core-petg` | Mark1, left 0.4 | PETG Basic black | Refill plate with PRV shroud cap down and reed bridge on its convex face | Open shroud cavity and bridged lead groove |
| `small-petg` | Mark1, left 0.4 | PETG Basic black | Funnel cover, PRV shroud, reed bridge and fuse clamp in their established print poses | Support-free. The cover retains its solid infill, wall count, bridge settings and brim-free edge. |
| `factory-petg` | Mark1, left 0.4 | PETG Basic black | Coil mandrel and setting gauge as exported | As `small-petg` |

## Declared features

Each feature selects faces by orientation and by place on the part's own bounds in its
print frame, and states an `expect` range. A feature whose faces are missing, or whose
measured extent leaves its range, stops the preparation and reports what was found.

Both bottom quadrants print their continuous planar handhold corbels with the shared
ordinary layer schedule. The handholds use their integral geometry as the support-free
gripping surface, with no local layer band or added support fins.

- **`fine_band`** — a show surface. Its connected faces' print-Z extent is the
  span; the 0.08 mm layer range starts one ordinary layer below it and ends one fine layer
  above it, so the span's top lies inside a fine layer. Its faces are painted support-blocked.
  `allow_support` retains accessible external contacts on a supported show surface.
- **`transition_band`** — an expanding print-down round with the 0.5:1 additive chamfer of
  [`lib.rs`](/hardware/printed-parts/enclosure/enclosure/interface/lib.rs). The foot is where the straight run
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
  this for its receiver catch pockets, teardrop bores, valve sockets and vent passage.
  Direction-specific exclusions apply when their source-frame direction matches the
  build direction. Its separate bridge regions add local solid modifiers with the
  corresponding plate-space bridge angle. These do not block supports.
- **`support_region`** — an authored source-frame box targets native tree support
  beneath its downward faces. The preparation records the selected area and
  emits a support enforcer in the part's print pose. Back-bottom uses local
  targets at the handhold mouths and seam lips; the inclined gripping interior
  remains outside those forced regions.

- **`groove_ribbons`** — each long, narrow flat face printing down at the top of the part is
  a caught face over a sliding groove. A two-wall, hollow ribbon stands in the groove one empty
  layer above its floor and stops two empty layers under the caught face, 0.40 mm inside its
  edges. Automatic support is blocked on the caught faces and the ribbons, and the solid-host
  modifiers stop at the ribbons.
- **`edge_fins`** — interrupted removable walls from the bed to a flat ceiling's exterior
  edge, with narrow blockers over their contact strips
  ([printed-parts/AGENTS.md](../../AGENTS.md#supports)). `foot_outboard_mm`,
  `foot_inboard_mm` and `foot_height_mm` give each fin a flat foot as its bed anchor.

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
- support beads against the painted show faces and inside the declared support-free
  interiors;
- sampled bead coverage of the model section inside each solid-host modifier;
- the second layer's beads over the first;
- each object's support bodies, roots, build-up and interface islands, in plate and CAD
  coordinates (the support audit, `support-audit`), written as `support-audit-<object>.json`
  for the removal-lane reading.

`review.json` records every reading and the checks it passes. Support removal, surface
finish, fit and strength are observations of the printed part.

`--unbacked` requests adjacent-layer road-shadow statistics throughout every fine
band. The report records whether this optional diagnostic was requested.

## Print plan and project files

A sliced plate that passes its review becomes its part's print plan with
[`tools/print-plan.mjs`](../../../../tools/print-plan.mjs):

```sh
node tools/print-plan.mjs <plate folder> --material HSM-0081
node tools/print-plan.mjs <plate folder> --material HSM-0081 --dry-run
```

It encodes the Print tab's replay, updates the part's entry in
[the playback catalog](../../../../print-playbacks/README.md), writes `print-plan.json` beside
the plate folder and puts the project and the sliced archive in the print archive. The entry's
`process` lines are written by hand. `--dry-run` prints the entry and the record and changes
nothing. Commit the replay, the catalog, the record and the archive's index together.

The 3MF files of any other print go into the archive with
`node tools/print-archive.mjs add <name> <file>...`, and `node tools/print-archive.mjs <path>`
brings one back to its place. [`print-archive.json`](../../../print-archive.json) indexes them
by git blob ID inside the [print projects release](https://github.com/derekbreden/homesodamachine/releases/tag/print-projects).
