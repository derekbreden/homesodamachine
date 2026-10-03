# Back-top native print review

The [manifest](manifest.json) binds the current back-top STEP/STL, exact native
Mark2 archive and every review. The native geometry, emitted bearing paths,
protected faces and support-removal lanes are reviewed. **This job has not been
submitted.** Its 813 layers estimate **26 h 8 min 54 sec**.

The source STL is one closed body. It prints ceiling-down, yawed 87.7° in the
plate plane, on the fixed left 0.4 mm Standard hardened nozzle with the saved
black PET-GF recipe. The bed layer is 0.20 mm; other layers are 0.24 mm, with six
walls through the expanding roof-side band and two walls elsewhere. Saved wall
order, speeds and 15% infill/wall overlap are retained. Mark2's requested
+0.04 mm trim emits +0.02 mm on Textured PEI.

The [first-layer overlap](first-layer-overlap.json) has 75.27% and 72.43% nominal
outer-road support for the first two transitions. The
[complete expanding band](round-layer-verification.json) passes. The model has
**15.136 mm** plate border; every extrusion's own
half-width plus 0.10 mm has **8.306 mm** border,
meeting the respective 15 mm model and 5 mm support requirements. The additional
10 mm support-border diagnostic stays visible as false.

The [PRV crown](prv-crown-emission-review.json) stands at the lip's height.
Its first two actual model slabs each cover the complete 8 × 18 mm native crown:
55 and 82 model roads, with 99.992% and 99.813% nominal own-width bead coverage.
Removable support carries the full crown. The exact 12 mm mouth/duct, inner
45° roof, tube axis, seam and existing foam-flank lip plane are preserved. The
[current native integration](prv-crown-current-native-integration.json) checks
all 215 other placed bodies: eight exact nearby BREPs are held byte-identical
to their native overlap/gap reading, and the remaining bodies retain explicit
bbox lower bounds. No added stock overlaps a neighbour.

The [emitted-path review](emitted-path-review.json) reads all 813 model slabs.
Every whole stock component receives finite left-tool model walls. The two exact
coplanar mesh-section planes have [both one-sided native contours](native-coplanar-section-review.json)
read against the same actual slab roads. The 19 retained
[surface diagnostics](emitted-perimeter-diagnostics.json) name one ground-stack
D-stem round terminal, two keystone swing-entry bevel strips, fourteen SIG-9
clip entry-ramp/rear-R12 transitions and two PRV open-groove roof strips. Their
[complete native stock](native-functional-stock.json), full 3D host connectivity,
[actual local paths](native-functional-surface-emission.json) and
[bearing footprints](native-functional-bearing-footprints.json) remain explicit.
These records do not resolve a feature by a nearby road alone.

Both complete rooted keystone catches have roads in all 19 required slabs and
at least **99.893%** nominal section coverage. The cable clip's full central
3 × 6 × 9 mm retaining seat is present in the native part, with roads in all
36 complete seat slabs and at least **99.931%** nominal bead coverage. Its two
6 mm entry ramps retain the recessed S-channel profile; they are separate from
the full retaining seat.

The R3.5 ground mounting annulus is connected to its full-width ceiling column
and keeps its complete canonical native stock. Actual model roads reach 30 of
its 31 native sections. The final 2.496 mm² curved terminal section has no road;
the emitted free-annulus bead envelope ends **0.126 mm** short of that exact
round terminal. This layer-lattice approximation is retained as a geometric
emission limitation. It does not establish printed insert retention, fastening
capacity or dimensional fit.

All **1,050,514 support roads** clear the nine protected
exact native exterior faces under conservative own-width/height bead envelopes.
The separate [flat rear-field reading](rear-port-support-contacts.json) has zero
potential contacts in this archive. Functional C14 pocket/flange and internal
mounting contacts remain intentional; their cleanup and whole rear-field finish
are physical observations. Accepted C14 hardware fit keeps its existing scope.

The [support-removal review](support-removal-review.json) assigns all **13 bodies**
and **34 labelled contact regions**, including six short 1.68 mm build-up bodies,
to empty-shell routes. Release contacts through exposed flanks, rear openings
and the unobstructed forebay, then break connected sacrificial branches into
removable portions. Remove every fragment before hardware, insulation, tubes,
frame or loom are installed. Ten [exact native air lines](support-removal-native-lanes.json)
illustrate these regions; no entire connected tree is assumed to leave intact.

The native archive passes ZIP CRC and embedded G-code MD5 checks. The
[stock tool diagnostics](native-diagnostics-review.json) match the saved native
start/end recipe; special tool tokens do not occur in model layer routines.
Physical removal effort, show finish, complete assembled fit, cable retention,
insert load capacity and lifetime remain outside this native software review.
