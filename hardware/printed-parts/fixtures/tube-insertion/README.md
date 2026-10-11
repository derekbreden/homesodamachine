# Tube-insertion T handle and bench press

The split T handle grips the 3/8-inch LLDPE tube while its TPU sealing thimble
is fitted evenly onto the tube end. The horizontal bench press then inserts
that sleeved tube into the bare Touch-Flo water port. The accepted faucet
lever is attached throughout this operation, down at its unpressed rest.

The [assembly guide](/hardware/tube-insertion-guide/) shows printing, fixture
assembly, bore-depth setup, sleeve fitting, donor insertion and removal.

## Printed parts

| Guide letter | Part | Quantity | Material | Print envelope, mm |
| --- | --- | ---: | --- | --- |
| A | [Base, cradle and guides](tube-insertion-base-print.stl) | 1 | PET-GF15 | 208 × 234 × 49 |
| B | [Guided ram with jaw shelf](tube-insertion-ram-print.stl) | 1 | PET-GF15 | 90.5 × 64 × 28 |
| C | [Bench-press lever](tube-insertion-press-lever-print.stl) | 1 | PET-GF15 | 24 × 174 × 8 |
| D | [Lower T-handle jaw](tube-insertion-lower-jaw-print.stl) | 1 | PET-GF15 | 38.5 × 77 × 11 |
| E | [Upper T-handle jaw](tube-insertion-upper-jaw-print.stl) | 1 | PET-GF15 | 38.5 × 77 × 11 |
| F | [Preformed half-round grip liner](tube-insertion-liner-print.stl) | 2 | TPU 85A | 8 × 20 × 28 |
| G | [Sleeve-cap support puck](tube-insertion-cap-support-puck-print.stl) | 1 | PET-GF15 | 54 × 54 × 8 |

Every `-print.stl` already has its intended bed face at Z=0. Both rigid jaws
print with their liner pockets open upward. The TPU liners print with the
tube axis vertical, so the grip semicircle is an XY perimeter in each layer.
Each liner is a solid block with a 3.375 mm minimum backing; it is printed
to shape and placed directly into its jaw pocket. It is not bent or wrapped.

The base's 49 mm height is its rigid annular thrust wall. Its donor saddle,
shank slot, clocking pad and ram guides are open above. The short underside
pivot-head recess is accessible for removal of automatically generated
support. Retain the native slicer's saved automatic tree-support decisions.

The native print projects are:

- [Base on H2C](ready/tube-insertion-rigid-base-h2c.3mf)
- [Rigid tool parts on H2C](ready/tube-insertion-rigid-parts-h2c.3mf)
- [Two solid TPU 85A liners on Mark2](ready/tube-insertion-tpu-85a-mark2.3mf)

The [printing record](PRINTING.md) links process settings, machine mapping,
plate placement and the per-project preparation and slice reports. The current
[part manifest](parts.json) contains STEP names, quantities, materials and
print bounds.

## Hardware and load path

The [acquired fixture stock](/hardware/ledger/purchases.md) supplies three
M5 × 50 mm socket-head screws, four M5 square nuts and three Ø25 mm M5 fender
washers. Two screws close the T handle. The third is the press-lever pivot;
two jammed nuts retain its washer with the lever free to swing. No heat-set
insert or printed thread carries the press load.

The 30 mm short arm and 120 mm hand arm provide a nominal 4:1 leverage ratio.
The circular nose drives a guided ram; the two ram fingers bear symmetrically
on the rear of the T handle. Its full-length shelf supports the lower jaw at
the tube's height. The 52 mm guide span and 0.2 mm nominal side clearances
control the ram's lateral position and yaw. The free 330 mm tube passes
through the open top and continues beyond the fixture.

The donor's metal base annulus bears against the thrust wall. A tangent
floor supports the cylindrical base at the tube-axis height, and a flat pad
under the lower rectangular column locates its clocking. The threaded
shank extends freely through the open slot. The fixture does not bear on
the arches, plunger or attached faucet lever.

The grip liners have 28 mm contact length and a nominal Ø9.25 mm bore when
the rigid jaw mating faces close. This is a 0.1375 mm radial interference
against the Ø9.525 mm tube. Rigid closure stops limit squeeze, and the
3.35 mm front and 6.85 mm rear pocket end walls retain the liner under axial
load, with 3 mm of rigid backing below the pocket. The bare tube has
0.6375 mm radial clearance to the rigid jaw end openings.

The opposite hand holds the clear fixed palm area on the base while the
press lever moves. Existing bench clamps or bolts can secure the fixture
using its two mounting holes when useful. Keep the base stationary during
the operation.

## Seating setup

The donor reference records a water-port depth of at least 20 mm. Set up
the actual donor using its caliper-measured annular floor depth **D**:

- Mark the tube **D − 2.1 mm** from its square-cut end for the final port-lip
  witness.
- Mark it **D + 16.9 mm** from that end for the T handle's front face.

Fit the thimble to the tube first, using the T handle and cap-support puck
while walking its wall evenly around the tube. The tube end must contact
the thimble's cap before the sleeved tube enters the donor. Fit the T handle
at its front-face witness after this sleeve-fitting operation.

The press has 20 mm travel between its rear start stops and front seating
stops. For D greater than 20 mm, begin **D − 20 mm** of insertion with the
T handle so the collar fits onto the ram at its rear stop. The front stop
places the jaw front 19 mm beyond the port lip, with 12 mm clearance to
the donor's arch peak. Stop travel and the port-lip witness should agree.
If they do not, check the sleeve, grip, marks and alignment before continuing.

Cap compression and printing tolerances mean the stop is a geometric
overtravel limit. It does not independently establish full seating,
leak tightness or a load rating. The accepted sealing thimble's
[physical seating record](../../faucet/tpu-o-ring/print-log.md) retains its
original scope.

## Geometry and physical scope

The [manual geometry review](geometry-review.json) covers all seven part
variants, the actual donor reference, a 330 mm tube, the sleeve and every
screw, washer and nut. It samples the full 0–20 mm stroke at 0.5 mm
increments. All parts are valid single analytic solids; the 41 poses have
no unintended B-rep intersections. Designed TPU grip and port interference
are identified separately.

The [accepted faucet lever](../../faucet/lever-replica/physical-acceptance.json)
has physical fit and functional evidence, with no measured assembled rigid
pose. The working assembly therefore shows the donor and its open front
side without inventing a lever placement. The user's attached, down,
unpressed lever is the assembly authority.

This fixture is a prepared print design. Physical grip, printed sliding
fit, complete insertion, load capacity and lifetime are unqualified. The
ordinary assembly operation checks that the collar holds without slipping
or permanently marking/flattening the tube, the sleeve remains even, and
the tube reaches its seating witness.

## Source and manual regeneration

[`tube_insertion.py`](tube_insertion.py) provides `build_parts`, the individual
part builders and `build_assembly(stroke=0..20)` for assembly figures. Importing
the builders writes no files. `parts.json`, the STEP files and print STLs are
generated explicitly:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/tube_insertion.py
```

The optional question-specific dimensional review runs separately:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/review_geometry.py
```

Neither command is added to a build, hook, watcher or print-launch path.
