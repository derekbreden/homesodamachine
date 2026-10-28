# V-B southward layout and return pedestal

V-B's native origin is X40/Y239.60434/Z279.41 mm. Its return elbow is at
X5.16348/Y275.39954/Z279.41 mm. Both return fittings are level, with an
8° change in clocking. The pump, PCB and four WAGO bodies retain their datums.

The lid carries the return elbow's forward leg on one filled 11.24 × 11.5 mm
pedestal. Its fixed-body seat has 0.15 mm nominal radial air and a peaked
2.8 mm tie passage. The nominal 2.5 × 0.8 mm retaining strip has a 76.96 mm
route and fits the allocated six-inch tie. Both release collets remain free.

The inlet uses two tangent R14.07 arcs. The return follows a straight fore
leg to Y239 and one R20.99 minimum curve into Y-B. The drain stem is 16.7 mm
past its shoulder, including 1 mm showing above the receiving collet; use
the actual fitting's insertion mark when preparing it.

The drain cradle has a flat collar-clearance face and a continuous 45°
underside into its full 3 mm snap roots. Native collar clearance is 1 mm.
The existing drop and wing checks pass. Its 1.3 mm snap leaves retain their
specific flexure exception and physical qualification limits.

`native-fit.json` records the selected native gaps, including 1.47 mm to
the pump. `wiring.json` records the source-bound local dressing comparison
and the clearance of the added cradle stock. `publication.json` binds the
published artifacts and live payloads.

`print-review.json` binds the reviewed Mark1 slices to the current STLs.
Both use the left hardened 0.4 mm Standard nozzle, black Fiberon PET-GF15
and Tree(auto)/Default. The lid's full emitted-bead bed margin is 21.2 mm;
its nominal retaining-strip core has no model or support bead crossings.
The current archives and complete preparation records are held under the
recorded `.cache/prints/trial/` paths.

The full-lid geometry lint did not complete under the 0.45 GiB resident-memory
cap. The cradle's completed post-publication lint identifies the retained
1.3 mm snap leaves; the relief has no flat ledges. See `geometry-lint.txt`.
These CAD and slice checks do not qualify physical fit, tie retention,
snap force or lifetime.
