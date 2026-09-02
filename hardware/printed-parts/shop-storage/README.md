# Shop storage

A job kit holds one bench job's tools and consumables on one Gridfinity footprint and
grows upward. At rest a kit is one column standing on a printed bench dock; at work its
storeys are set out on the bench. Horizontal bench space is the scarce dimension in this
shop, so a kit spends height instead.

## The family

- **Footprint.** A kit stands on a 3 x 3 Gridfinity footprint (126 mm x 126 mm), or
  2 x 3 where its contents allow. Every storey of a kit shares the kit's footprint, so
  the storeys stack in whatever order the contents map gives them.
- **Storeys are stock bodies.** Each storey is a body the
  [`cq-gridfinity`](https://github.com/michaelgale/cq-gridfinity) library renders: an
  open bin with the library's own label ledge, dividers and scoops, or a solid lipped
  blank with sockets cut from its plateau, which is a rack. The library's stacking lip
  and base profile are the only joint between storeys. There are no pins, keys or
  custom sockets between one storey and the next.
- **Seats.** A storey above seats on the top reference plane of the storey below, at
  7 mm per height unit of that storey. Every open bin carries a label ledge or a divider,
  both of which rise to that plane, and a rack keeps its lip, so a closed kit takes another
  kit on top of it.
- **Two forms.** A *job stack* is bins closed by a rack or a tray, for a job run in
  campaigns: unstack, work out of the trays, restack. A *job tower* is a carcass with
  storeys and head-down tool sockets, for a job whose tools stay standing on the bench.
  Each kit's README names its form in one sentence.
- **Dock.** Each kit ships its bench dock: the library's baseplate on a 6 mm slab. Any
  Gridfinity baseplate docks any kit.
- **Contents are modelled.** Every stored thing is an envelope from public dimensions,
  the maker's or the listing's, placed in the kit's presentation assembly and asserted
  to fit its compartment or socket. No caliper measurements are inputs.
- **Labels.** The label ledge takes 12 mm label tape. Nothing is lettered in the plastic;
  each kit's README carries the contents map.
- **One tool, several homes.** A tool two jobs share has a socket in both kits.
- **Material.** Every kit prints in Bambu PETG Basic black from the AMS 2 Pro on the
  H2C's right hotend, so shop storage never queues for the left hotend the exterior
  and the cold core share. Storeys print base down without supports; the library's
  base and lip profiles are printable as drawn, and every cut socket opens upward.

## Shared code

[`_kit.py`](_kit.py) is the family's vocabulary, and every kit generator reads it:

- `bin_body`, `blank_body`, `dock_body` render the three storey stocks;
  `bin_cavity` is the void a bin holds below its top reference.
- `Storey`, `stack_seats`, `exploded_seats` and `kit_assembly` place a kit in its frame,
  closed or exploded, with its contents riding on their storeys.
- `assert_stack_seated`, `assert_contained`, `assert_clear`, `assert_one_solid` and
  `assert_h2c_fit` are the checks every kit runs before it exports.
- `rounded_prism`, `placed_prism`, `cylinder`, `pocket`, `round_pocket` and
  `socket_ring` are the envelopes and cutters a rack or a reference is built from.
- `export_parts` and `export_kit` write one coloured STEP per printed part and one per
  presentation assembly.

The frame is the JST tower's: world +Z is up, +Y is the operator-facing front, and +X is
the operator's right. The library's label ledge stands on the +Y wall, so a bin rendered
here already faces the operator.

## Kits

| Directory | Job | Form | Footprint |
|---|---|---|---|
| [`copper/`](copper/) | The copper tube bench | stack | 3 x 3 |
| [`drill-press/`](drill-press/) | End-plate tapping and drilling | stack | 3 x 3 |
| [`fasteners/`](fasteners/) | Inserts and screws | stack | 3 x 3 |
| [`fittings/`](fittings/) | Tube and push-fit fittings | stack | 3 x 3 |
| [`harness/`](harness/) | Harness build: crimp, ferrule, sleeve | stack | 3 x 3 |
| [`hotends/`](hotends/) | H2C hotend swaps | stack | 3 x 3 |
| [`jst-crimping/`](jst-crimping/) | JST XH crimping | tower | 3 x 3 |
| [`pour/`](pour/) | Foam and silicone pours | stack | 3 x 3 |
| [`solder/`](solder/) | Solder and heat-set inserts | stack | 3 x 3 |
| [`umbilical/`](umbilical/) | Umbilical termination | stack | 2 x 3 |

## Prior art

- The 42 x 42 x 7 mm module, the base profile, the stacking lip and the 12 mm label
  ledge are the [Gridfinity specification](https://github.com/gridfinity-unofficial/specification),
  rendered by the MIT-licensed [`cq-gridfinity`](https://github.com/michaelgale/cq-gridfinity).
- A rack is the Gridfinity bit-holder pattern: a solid bin blank with sockets cut from
  its top, one per tool, on the same base and lip as every bin.
- A head-down tool socket is the Gridfinity plier-and-cutter holder pattern: the tool's
  head drops into a loose rectangular well and its handles stand above the rack.

## Build

Each kit's generator writes its STEP parts, its presentation assemblies and its README's
figures from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/shop-storage/<kit>/<kit>_kit.py
```

A new generator is traced into the build graph and the graph is written to Bazel:

```sh
tools/cad-venv/bin/python tools/bazel/trace_inputs.py hardware/printed-parts/shop-storage/<kit>/<kit>_kit.py
tools/cad-venv/bin/python tools/bazel/gen_build.py
```
