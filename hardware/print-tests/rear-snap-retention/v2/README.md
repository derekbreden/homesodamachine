# Reinforced rear equipment fit samples

The [physical result](physical-result/physical-result.json) records
loose PISCO hardware with no useful retention, large water-regulator play,
and good ASSE, pump and meter receiver fits. Meter and water-regulator caps
need broader shaped contact stock.
The 2.6 mm leaves concentrate visible bending at their roots; an intermediate
section and the root transition are under review. The PISCO
[print-mesh reading](physical-result/pisco-reading.json) finds that the
central bridge lies below the entire admitted neck circle, leaving the
intended neck lip absent. At native station 58.5 mm it leaves 5.044 mm of
vertical air to the reference neck. These records describe the tested
revision below.

Five complete receiver/cap pairs fit the pump, ASSE chain, PISCO regulator,
water regulator and Digiten flow meter. The [physical report](../physical-result/physical-result.json)
records the rejected first trial. Each cap is a single piece with 2.6 mm
spring leaves and flat 2.6 mm retention bearings. Free bending length is
22.5 mm, with a 21.5 mm water-regulator exception that preserves its existing
height. A 2 mm-rise insertion ramp sits above a 0.6 mm solid hook nose; the
retaining underside stays flat.

All five caps print on one axial end, with wing bending within the deposited
layer plane. Receivers retain the lid or back-top production orientation and
its root stock. PET-GF uses three Classic walls, solid cap infill, 15% gyroid
receiver infill, 0.20 mm first layers, 0.24 mm normal layers and the shared
localized cooling policy. Tree(auto)/Default supports remain enabled.

PISCO's admitted neck and body diameters have 1.5 mm of extra clearance in
both halves. The [scan reading](../../../reference/compact-inline-candidates/regulator-scan-model-check.json)
reports a 0.395 mm absolute 95th-percentile residual at the outlet fitting and
collet; the cap's original nominal radial air was 0.15 mm. This residual is
not a signed interference measurement. The physical test establishes the
need for more clearance; it does not isolate scan scale, surface fitting or
print error as the cause.

The meter has 0.75 mm hardware clearance in both halves, a solid 6 mm spine,
and two complete 38 mm-long leaves. Flexible leads turn west against the body
above the lower leaf. The water regulator cap covers 36 mm of the housing and
smaller outlet neck, with 187.2 mm² of flat retention bearing. Its lowest face
remains Z315.924 mm. The pump retains the filled 6.2 mm-crown box body.
The ASSE's threaded-part cavity is retained. Derek notes that the finger-tight
3/8 NPT to 1/4 NPT female adapter may seat differently with tape; no adjustment
is made from that observation.

[geometry.json](geometry.json) records ten valid single native solids and
watertight print meshes, zero seated cap/receiver and installed-hardware
interference, and flat bearing obstructing empty-cap removal. The meter's
16 mm forward insertion is clear at the five recorded stations. These checks
do not establish physical force, fatigue or running-pump vibration.
[revision.json](revision.json) records the selected dimensions and fit scope.

| Printer | Samples | Native estimate | PET-GF | Minimum bead margin |
| --- | --- | --- | --- | --- |
| Mark1 | Pump receiver, ASSE pair, PISCO pair | 3 h 19 min | 118.90 g | 85.547 mm |
| Mark2 | Pump cap, meter pair, water regulator pair | 3 h 47 min | 156.40 g | 95.700 mm |

[print-jobs.json](print-jobs.json) binds both native slices and print-only
archives. First-to-second-layer bead overlap is at least 90.1% on Mark1 and
88.9% on Mark2. The deposited bead envelopes include model, support and brim.
The printer-specific textured-plate trims are Z0.16 and Z0.02 respectively.
Mark2 accepted task **1398871736** at 02:52:58 UTC; Mark1 accepted task
**1398879198** at 02:57:15 UTC, 257.622 seconds later.

Remove the cavity supports with a tiny flathead screwdriver that fits inside
the opening. Derek reports easy removal of the first trial's tiny automatic
supports with that tool. Preserve the flat retention undersides. Fit each
empty cap first, then the real hardware; record insertion, release, rocking,
whitening, residual bending and any fracture. Test the pump's fixed rail seats
with all four removable rubber foot assemblies removed.

The trial’s [geometry recipe](https://github.com/derekbreden/homesodamachine/blob/f5e8bed0919827aec6fba620a4b8f15010b70d3d/hardware/print-tests/rear-snap-retention/build.py) and [print preparer](https://github.com/derekbreden/homesodamachine/blob/f5e8bed0919827aec6fba620a4b8f15010b70d3d/hardware/print-tests/rear-snap-retention/prepare.py) are archived in Git.
