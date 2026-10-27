# Tube insertion tooling

Printed M5 threaded passages use the shared Ø5.2 mm fit selected in the
[M5 sample comparison](/hardware/print-tests/m5-seam-bearing/physical-result.json).

Current PET-GF editable projects follow the [localized cooling policy](../../cooling/README.md).
Re-slice them for current cooling commands. Identified native archives retain
their original commands and physical-evidence scope.

A split plus-shaped handle holds two thick, preformed 85A TPU liners for
gripping the 3/8-inch LLDPE tube. The closure screws, liners and crossbar
share the same axial centre. A cap-support puck assists fitting the sealing thimble to the
tube. The assembled T handle and guided carrier are used together for
sleeve fitting. For donor insertion, two complete factory screw clamps
supply the axial force and reaction.
The donor is supported on its metal base with its faucet lever attached,
down and unpressed.

The [physical acceptance record](physical-acceptance.json) documents Derek's
successful insertion on October 13, 2026. The handle alone works well for
starting insertion, and the full tool makes the final press very easy.
Derek reports the operation is far easier than before.

The separate [TPU hand hold-down cover](donor-hold-down/README.md) is an
inverse of the donor's upper half below the attached lever. It wraps around
the cylindrical portion, rounded transition and flat-sided column. Its
flat hand face stands 2 mm above the reaction walls. Hand pressure supplies
downward restraint; the compression tongue in the open shank canyon
retains the cover's position. Physical fit and hand-pressure performance
remain unqualified.

Use the [illustrated assembly guide](../../../tube-insertion-guide/README.md)
for the assembly sequence and the [print instructions](PRINTING.md) for
prepared native projects. [parts.json](parts.json) gives all quantities,
hardware and actual print bounding boxes. The
[load basis](load-basis.md) records the sections, unequal-input scenarios,
manufacturer references and limits of the analysis.

## Parts and hardware

| Label | Part | Quantity | Material | Print bounding box, mm |
| --- | --- | ---: | --- | --- |
| A | Base, donor reaction block and guides | 1 | PET-GF15 | 272.5×234×54 |
| B | Guided carrier and narrow jaw shelf | 1 | PET-GF15 | 162.5×100×10 |
| C1 / C2 | BESSEY GSCC2.506 factory screw clamps | 2 | Factory metal tool | Purchased tool |
| D | Lower T-handle jaw | 1 | PET-GF15 | 44×100×15 |
| E | Upper T-handle jaw | 1 | PET-GF15 | 44×100×15 |
| F | Preformed half-round grip liner | 2 | TPU 85A | 9×20×28 |
| G | Sealing-thimble cap-support puck | 1 | PET-GF15 | 54×54×8 |

The two [GSCC2.506 clamps](https://www.amazon.com/dp/B000FA0BL8) provide
independent screw inputs. The owned hardware is two M5×50 socket-head
closure screws, two M5×20 DIN7991 countersunk carrier screws, four 8×4 mm
M5 square nuts and two Ø25 mm fender washers. The countersunk screws use
a 3 mm hex key; the socket-head screws use a 4 mm hex key. Two owned 4-inch
steel C-clamps hold the base at a bench edge while the factory screw handles
are operated. No printed thread or insert carries the axial press load.

Each rigid half has a 7 mm backing under its 8 mm deep liner pocket.
The 28 mm liners occupy X8–36, centred at X22. Both closure screws and the
36 mm crossbar share X22. The 44 mm central body extends 4 mm beyond each
end of the crossbar, giving the handle a symmetric plus shape.

Each liner retains its Ø7.75 mm half-round groove and adds 1 mm to its flat
backing. The liner is 9 mm thick, so it stands 1 mm proud of its pocket.
Together the liners provide 2 mm of additional closing travel before the
rigid mating faces meet. The seated uncompressed liner references overlap
at that closure limit; the loaded TPU shape is not a deformation solution.
Print the liners upright with the tube axis vertical, using the solid
9×20 mm end footprint and 5.125 mm minimum TPU backing. Both axial pocket
walls are 7.85 mm thick.

## Fixture setup and motion

The insertion axis is X; the workpiece moves toward −X. Tube axis is Y8.75,
Z30. Factory screw stations are 32 mm either side of the tube at the same
height. Their feet bear against the 30 mm high rear crossbar
faces at X98; the fixed jaws back the 26 mm thick donor reaction block immediately
behind its matching flat stations. Only the donor's metal base annulus
carries intended axial reaction. Its threaded shank passes through an open
slot, and a tangent saddle floor plus a flat lower-column pad locate the
body and clocking.

The factory-clamp drawings are schematic. Capacity and throat come from
BESSEY; pad, frame, handle and spindle outlines are envelopes for the
assembly illustrations. During ordinary unloaded setup, verify that the
actual factory feet remain fully backed, the attached faucet lever stays
down at unpressed rest and untouched, and each spindle covers the complete
20 mm travel without repositioning its sliding jaw. Keep the clamp rails
outward and handles clear of the tube and bench. The reference model does
not invent the faucet lever's measured installed pose.

The full-width carrier foot begins at X96.5 and has a 124 mm guide bearing
span with 0.1 mm nominal side gaps. A narrow 38.5 mm shelf supports the
lower jaw at Z15. Locating keys and two metal carrier screws couple the
lower jaw to the carrier without a free yaw joint. The carrier's complete
print length is 162.5 mm; the bearing span is 124 mm. To release the
workpiece, unload and remove both factory clamps, release the two closure
screws, and remove upper jaw E and its liner. Lift out the donor hand pad,
then lift the donor and tube out
of the lower liner and open donor nest while carrier B and lower jaw D
remain bolted together.

With the TPU donor pad fitted, hold its broad face down with one hand and
alternate the screw handles with the other. Advance one screw by one very
small step, then immediately take up the opposite pad gap before another
advance. The common guided collar supports limited alternation; the forces
need not be equal. The
[one-station analysis](load-basis.md) accounts for complete unequal input.
Stop at the first of the seating witness or geometric travel limit.
Unload and recheck the setup if they disagree, the grip slips or the
carrier binds.

## Seating setup

Measure the actual bare donor's annular seating-floor depth D with the
existing caliper, avoiding the central flow hole and plunger. The donor
reference records at least 20 mm.

- Mark the tube D−2.1 mm from its square-cut end for the final port-lip
  witness.
- Mark it D+16.9 mm from that end for the collar's front face.

Fit the sealing thimble to the tube first, using the assembled B/D/E
T handle and carrier together out of the guides. Use the cap-support puck
while walking the TPU wall evenly around the tube; the square-cut end must
contact the cap before the sleeved tube enters the donor. Put the collar
front at its witness after sleeve fitting, with B and D still coupled.
Return the assembled unit to the guides for pressing. The donor port
remains bare until the sleeved tube enters it.

The carrier has 20 mm travel between its start and seating stops. For D
larger than 20 mm, begin D−20 mm of insertion with the T handle so the
carrier can reach its rear stop. At the front stop, the collar front is
19 mm beyond the port lip and 12 mm behind the donor's arch peak. The
port-lip witness and stop should agree. Cap compression and printing
tolerances mean the stop is a geometric overtravel limit; it does not
independently establish full seating, leak tightness or a force rating.

## Evidence and regeneration

The [manual fixture geometry review](geometry-review.json) covers the rigid
variants, the donor reference, 330 mm tube, sealing thimble, four
screws, four nuts, two washers and the schematic factory clamp envelopes.
It samples 0–20 mm travel at 0.5 mm increments. All six print variants are
valid single analytic solids. The 41 sampled poses have no unintended
B-rep intersections; designed TPU interference is recorded separately.
All four nominal Ø30 contact disks have uninterrupted solid backing.

The [centred grip review](centered-grip-review.json) establishes zero axial
screw offset, 1 mm of added flat backing per liner, 1 mm projection beyond
each pocket and reuse of the existing base and carrier. Its reference
comparison adds 560 mm³ per liner without removing the existing grip shape.

The [physical acceptance record](physical-acceptance.json) accepts functional
grip and successful insertion with the identified centred plus handle and
proud TPU inserts. It addresses the
[earlier grip failure](prints/2026-10-12-liners-d775-mark1/grip-failure.json)
for this configuration. The individual effects of centering and added
backing, and the physical pressure distribution, are not measured separately.

The [Mark1 PET-GF jaw launch](prints/2026-10-13-centered-grip-mark1/README.md)
preserves the exact two-jaw slice for task 1335878319, accepted on October
13 at 10:08 am CDT. Its [completion observation](prints/2026-10-13-centered-grip-mark1/completion.json)
reports 63/63 layers without errors. The
[matching TPU insert launch](prints/2026-10-13-centered-liners-mark1/README.md)
records task 1336534713, accepted at 1:59 pm CDT with startup free of
reported errors. The physical acceptance record binds both jobs' exact
archives and meshes to the reported successful operation.

Successful insertion and functional grip are accepted for the reported use.
Numerical insertion and grip forces, printed strength and lifetime remain
unmeasured. Factory clamp force does not rate the
printed tool or workpiece. The accepted sealing thimble's
[seating record](../../faucet/tpu-o-ring/print-log.md) and accepted faucet
lever's [physical record](../../faucet/lever-replica/physical-acceptance.json)
retain their identified scope.

[`tube_insertion.py`](tube_insertion.py) supplies `build_parts`, the
individual builders, `build_assembly(stroke=0..20)`, `clamp_stations` and
the separately scoped `build_clamp_reference` schematic. Importing builders
writes no files. Generate CAD explicitly:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/tube_insertion.py
```

The question-specific review remains separate:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/review_geometry.py
```

Neither operation is added to a build, hook, watcher or print-launch path.
