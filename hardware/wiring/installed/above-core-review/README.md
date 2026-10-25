# Native electrical arrangement review

The installed graph has 98 conductors. Its terminal frames read the selected
native component poses. These explicitly invoked reviews cover CAD geometry;
they do not qualify physical harness dressing, wire packing, connector fit,
wire bend limits, donor terminals, grounding, mains isolation or energization.

- [Junction record](junction-review.json): nine purchased WAGOs, their rooted
  wells, the selected fluid spans, fixed hardware, PSU driver columns, C14
  housing/driver and complete insert-boss stock. Front manifold mouths use
  4 mm straight witnesses; rear/core mouths use 8 mm. Both witnesses are
  conservatively Ø3 mm; actual manifold conductors are Ø1.7 mm.
- [Composition record](native-review.json): complete native conductors,
  connector housings, sleeves, shared jacket and actual terminal frames.
- [Tube record](tube-review.json): the cached native electrical bodies against
  the current production native fluid spans.
- [Wall record](wall-review.json): the cached electrical bodies against both
  lid-mounted V-A/V-K uprights.
- [Assembly record](aggregate-review.json): every exported wiring body against the selected native
  above-core equipment, fixed front interfaces, termination bodies, all six
  enclosure pieces, top core caps and two roof closures. Both B-fill fittings are also
  checked against every wiring body. The external compressor jacket also clears
  the physical foam shell. Source-defined nominal retaining-strip paths
  are separate supplemental targets: the V-A/V-B union ties, both meter ties
  and the water-check tie.

Use the workstation CAD queue for these commands. They are separate from
production generation and are not invoked by builds or commits.

```sh
tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/review.py --pack-fixture --compose-only --export-wiring
tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/junction_review.py
tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/tube_review.py
tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/wall_review.py
```

The first command creates the explicit temporary native fixture and electrical
BREPs. `tube_review.py` derives its fluid spans directly from production APIs;
`--specs` optionally selects a saved span fixture. `--only` and `--bodies` narrow
a follow-up to named tube spans or cached electrical bodies.

After the populated appliance and its wiring manifest are materialized, review
that exported artifact directly:

```sh
tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/aggregate_review.py --refresh-cache
```

The aggregate review binds the actual STEP, its matching viewer payload and
wiring manifest. Its report names the current qualified component aliases;
local 8.5 mm endpoint neighborhoods apply only at each conductor's named device
or its own termination, following `installed/review.py`. Termination envelopes
receive those same local allowances at their named mating devices; native fuse
stubs use the existing 2.5 mm allowance. Native Booleans decide contacts after
bounding-box and inflated route-capsule candidate pruning. Native containment
witnesses retain fully embedded bodies as candidates. Wire-to-wire packing is
outside this review.

Housing records retain every physical pin's mating frame independently of the
wired graph. J4's empty IO23/IO27 cavities use the same 8.5 mm cells at their
own PCB header, after native containment of the residual contact is recorded.

`--refresh-cache` saves the actual exported wiring bodies for the tube and wall
reviews and binds the composition record's inventory, terminal frames and routes
to the same assembly and manifest. It does not compose the wiring again. The
report also records the four display-lead distances to the B-draw fore loop.
The tube and wall records retain that assembly digest and the cache index digest.
The same refresh saves actual fixed front hardware, the frame and tube bodies
for the junction review; its record retains the assembly and fixed-cache digests.
The assembly record also compares selected developed paths with the current
preparation cuts, including both pieces of the compressor hot core and the
continuing reservoir-A earth spans.
