# Fluid-14 clearance evidence

The production route uses a 6 mm fall run, with a 1.5 mm valve-side drop and
8 mm return. Its two-valve guard uses the same complete surface query as the
assembly scorecard and retains the 1 mm clearance floor.

[review.json](review.json) binds the exact source change, native inputs and final
canonical assembly. The final STEP is
`0bf745015625bde33b3672941b49fe7acb1cbbfcdbc652e2b2dc55959f883a67`;
its [scorecard](final-scorecard.json) passes every gate, with no pack clashes or
unanswered contacts, all 67 port leads clear, and no pair under its clearance
floor. Fluid-14 reads 1.075 mm to V-A, 1.125 mm to V-K and 1.370 mm to water-7.

The [bounded native check](candidate-clearance.json) uses 210 exported body
bounds and queries 24 nearby surfaces; V-F's joined starting collet is the one
excluded row. It retains all R14 bends and the complete required cap-bearing
interval Y254.4–263.2 mm within the actual straight Y253.701–288.710 mm. The
complete lid has 0.150 mm native air. A finer 0.005 mm mesh reads 1.074736 mm to
V-A. A recorded 2 mm gap is the query's lower-bound horizon.

The regression witness lies 0.0000023 mm from the former native tube and
0.888288 mm from the actual native V-A surface. The whole-shape OCC distance
returns 1.155 mm for that pair and misses the closer fore bend. The
[guard replay](guard-and-witness-replay.json) shows the current guard rejecting
that route at 0.882 mm and accepting the corrected route at 1.075416 mm. This
is a native surface witness; the failure is not dismissed as tessellation error.

`native-inputs.zip` retains the used native bodies, all 210 body bounds, both
source texts and the route seed. The original bounded probe and logs preserve
their exact execution scope. The final complete production scorecard supplies
independent current placement validation; this record makes no separate equality
claim for the optional, incomplete G-pump port-frame reconstruction.

Replay the witness and exact source guard without constructing the assembly:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/final-fluid14-clearance/verify.py
```

Add `--full` to repeat the bounded neighbor and bearing queries from the archived
native inputs. Source and input digests are checked before use. The command writes
only an explicitly supplied `--output` path. Physical tube forming and the complete
enclosure assembly test remain unmeasured here.
