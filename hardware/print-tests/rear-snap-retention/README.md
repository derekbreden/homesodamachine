# Rear equipment snap fit samples

The selected [intermediate-leaf trial](v3/README.md) uses 2.0 mm leaves,
rounded roots, centered flathead entries and shaped hardware bearings. The
[reinforced trial's physical result](v2/physical-result/physical-result.json)
records the accepted pump, ASSE and meter-receiver fits, concentrated root
bending, PISCO retention failure and water-regulator play.
The [first trial's physical result](physical-result/physical-result.json)
records wing fractures and fit failures. Its frozen geometry and print records
below identify those tested pieces.

Five complete hardware seats and their matching caps test the pump, ASSE
chain, Pisco CO2 regulator, water regulator and Digiten flow meter. Remove the
pump's four rubber foot assemblies before fitting its rigid casing.

The common joint uses the accepted funnel v4 dimensions from source
`29808fba7830848e59cbb740c11ff1b6d0b162fa`: 2.6 mm of flat hook overlap,
1.3 mm spring leaves, 2.0 mm flat hooks and at least 12.49 mm of free leaf.
The specific leaf section is the thinner flexure exception; ordinary receiver
walls, roof stock and end shoulders retain the nominal 3 mm section.
The cap-to-ledge clearance is 0.65 mm. Flat hooks require spreading the leaves
outward for insertion and release. The water regulator's leaves start 4 mm
below its axis so their free length fits beneath the existing roof.

[geometry.json](geometry.json) records valid single native solids, watertight
print meshes, zero seated cap/receiver intersection and blocked empty-cap
removal for each pair. The pump has 283.4 mm² of flat retaining area. These
geometric checks do not establish physical spring force, retention, fatigue
or vibration resistance.

The pump cable-cover underside projects 1 mm farther down at its front than
its rear datum. The selected installation origin is Z247.947963 mm; its first
modeled cover station clears the recessed lid floor by 0.274013 mm. The
hardware-fit sample already printing has a 7.4 mm lid root and the shared
saddle and flat-catch interfaces.

The [production pump block](production-pump-block.json) is one broad carved
body with stops on both fixed rails, 3.419 mm and 3.329 mm bearing strips,
and a straight 49.62 mm channel recessed 2.5 mm below the lid face. Its filled
box half-pipe cap has a 6.2 mm crown, one east clearance shoulder and independent
1.3 mm spring leaves. The flat catches retain 283.4 mm² of bearing and the
receiver interface [matches the sample already printing](box-cap-receiver-fit.json),
with zero seated overlap and the full 283.4 mm² bearing. The replacement cap
is [pump-box-cap.stl](parts/pump-box-cap.stl); the arch cap on the running Mark2
plate is a comparison specimen. The isolated production base has 41 native
faces and 114 edges, with a 4.9 mm remaining lid floor. The native
check finds no interference with the bare pump or cap. Full-parent integration
owns the remaining enclosure and routing clearances.

The [whole-cap elastic comparison](box-cap-elastic-comparison.json) includes
both the body and leaves under equal opposing hook loads. Its homogeneous,
linear 2D model predicts 7.7% of the thin arch's body-root opening for the box
cap. This relative comparison assigns no printed material modulus and does
not establish physical force, strength or life.

## Plates

| Printer | Samples | Native estimate | PET-GF |
| --- | --- | --- | --- |
| Mark1 | Pump seat, ASSE pair, Pisco pair | 3 h 38 min | 120.61 g |
| Mark2 | Pump cap, water regulator pair, flow meter pair | 2 h 39 min | 87.98 g |

All ten pieces retain their production print orientations. Receivers include
the parent roof or side-wall root stock. Caps have solid infill and three
Classic walls; receivers have three Classic walls and 15% gyroid. The process
uses left hardened 0.4 mm Standard nozzles, black Fiberon PET-GF15, 0.20 mm
first layers, 0.24 mm subsequent layers, Tree(auto)/Default supports and the
shared localized cooling policy. Full-bead margins are 79.961 mm and
93.058 mm. Printer-specific trims emit Z0.16 on Mark1 and Z0.02 on Mark2.

[print-jobs.json](print-jobs.json) binds the reviewed native archives and
launch records. Mark1 accepted task **1398257516**; Mark2 accepted task
**1398266343**, 215 seconds later. The [progress](prints/progress.json) records
both task IDs running without print errors or HMS alerts. `build.py` exports the samples; `prepare.py` prepares and
reviews the two plates. Both run through `python3 tools/run.py`; the native
export also takes `--cad`.

The [replacement cap job](box-cap-print.json) is prepared for Mark2 at
1 h 32 min and 71.07 g, with a 126.557 mm native bead margin. The emitted
first and second layers overlap across 95.4% of the second-layer bead area.
Its constant end-down profile generates no support roads under the retained
Tree(auto)/Default process. `prepare.py --plate box` prepares this cap without
replacing the two running plates' records. It has not been submitted.

## Bench fit

Remove the automatically generated supports from the open hook rooms and
check the flat bearing undersides. Mate each empty cap and receiver by
spreading the leaves outward, seating the cap, then releasing both leaves
over the ledges. Pull directly along the removal direction before adding
the real object. The cap must remain caught on both sides.

Fit the named hardware and repeat insertion, retention and release. For the
pump, check that the fixed rails seat, the molded cable cover clears the lid
and the head underside remains outside the bearing surfaces. Record rocking,
axial play, insertion/release force, whitening and residual leaf bend. Running
pump vibration and repeated-cycle endurance require their physical tests.
