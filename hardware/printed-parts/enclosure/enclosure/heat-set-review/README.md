# Enclosure insert and seam construction

The customer outcome is an enclosure that keeps its internal components secured,
seats the pump cartridge precisely and can be handled without its joints opening.
The [native audit](geometry-check.json) checks 37 insert stations in the current
six exported pieces. It reads the complete installed insert envelopes, open pilots,
blind relief, closed stock, insertion access and fore screw ligaments. Source and
STEP hashes are checked before and after the run. These are geometry results;
installed fit, pullout, torque, transport and drop performance require physical
qualification.

## Supplier constraints and screw stacks

The [ruthex RX table](https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf)
specifies Ø4.0 mm pilots and 1.6 mm minimum wall for RX-M3Sx4.0 and RX-M3x5.7,
and Ø6.4 mm pilots with 2.6 mm minimum wall for RX-M5x9.5. The audit compares pilot
diameters to fixed supplier values independently of mutable CAD constants. Every
pilot has at least 1 mm beyond the installed insert; the enclosure's screw stack
also reserves at least 0.5 mm beyond each revised seam/clamp screw tip.

| Station | Body | Pilot depth | Host / screw stack |
| --- | --- | --- | --- |
| Six Y seam stations | M3 short, 4.0 mm | 5.0 mm | 3.5 mm head recess, 5.5 mm shank, full insert engagement, 0.5 mm steel-tip clearance, 3 mm blind cap |
| Seventeen electronics / ground stations | M3 short, 4.0 mm | At least 5.0 mm | Ø8 mm exposed hosts give 2 mm radial material from the Ø4 pilot; four PSU inserts seat on the actual wall face; four PCBA inserts start 2.25 mm behind the unchanged PCB mounting face |
| Two condenser fingers | M3, 5.7 mm | 9.0 mm | Complete host and supporting finger |
| Two pump-clamp stations | M3, 5.7 mm | At least 6.7 mm | M3×60, at least 0.5 mm steel-tip clearance |
| Two C14 stations | M3 short, 4.0 mm | 5.25 mm | Full tunnel stock and closed rear wall |
| Four compressor posts | M5, 9.5 mm | 10.5 mm | Manufacturer pilot and minimum surrounding stock |
| Four pogo anchors | M1.4, 4.0 mm | 5.5 mm | Insert top 5 mm inside mating face; M1.4×8 tip 0.5 mm before blind end |

ZWMSSLL publishes Ø2.3 mm knurl, Ø2.0 mm lead and 4 mm body dimensions for its
M1.4 insert, without a host pilot, wall or pocket-depth recommendation. Ø2.0 mm is
the starting fit. The [SPIROL FDM guidance](https://www.spirol.com/resources/white-papers/how-to-select-a-threaded-insert-for-your-3d-printed-assembly/)
supplies the application rule of a solid host diameter at least 1.5 times the
knurl diameter. The audit reports this separately from supplier compliance.
The current pump-cap hosts retain at least 1.148 mm around the Ø2 pilot through
the whole insert body; front-top has more. The Ø2.6 entry passes the whole knurl
through the 2 mm setback. Install and cold-check the depth before fitting the
connector, following [enclosure assembly](../../../../assembly/enclosure-mechanical.md).
The [current coupon](../contact-pair-coupon/README.md) carries this exact geometry;
physical insertion and assembled contact compression remain unqualified.

## Native seam load paths

The Y seam stands at Y200 mm. Six M3 axes are at Y209.9 mm: lower Z48.9, middle
Z152.1, upper west Z282.05 and upper east Z291.05. The upper stations preserve
the functional funnel receiver and full insert/cap stock, with continuous outer
wall roots to the ceiling. The tongue overlap is 17.8 mm.

The lower and middle shanks retain an 8.25 mm net fore-edge ligament across
5.5 mm of X width. Each projected shear strip is 45.375 mm² per plane; the audit
reads its whole native volume. This geometric area is not a measured shear
capacity. Edge-first bending that opens the bottom seam puts the lower pair in
tension. The floor scarf has no tensile interlock, and the joined tops do not
establish a compression flange under that bending mode.

The Z hooks have 4.5 mm arms and 5 mm overlap over their 6 mm feet. Every sliding
face retains its stated running/support allowance; the end-stop clearance is
0.25 mm and the stop length is 3.75 mm. Whole hooks, roots, stops, entry sweeps
and the native 1 mm lifting engagement are checked by the enclosure producer.

The [placed comparison](placement-comparison.json) compares M3 stock and M5
candidates with actual packed component solids. For M5 it also tests the required
closed cap within only the pilot's Ø6.4 footprint, using both a supported socket-head
M5×10 / short-insert stack and the M5×12 candidate. This distinguishes required
material from a conservative surrounding envelope. The actual packed core,
rather than a compressor fit envelope or a solid model's nominal volume, controls
the available corner space. A 3 mm button-head recess on the fixed 9 mm flank
leaves a 6 mm shank: recess plus shank remains 9 mm, and the required M5 pilot
and cap still need a 15.8 mm inward band. A narrower 7 mm interface would change
the pin, socket and bearing stock. Head style alone does not establish fit or
improve the printed fore-ligament capacity.

## Deposition and evidence

[Print regions](print-regions.json) require local 100% infill through
the complete insert hosts, blind caps and supporting roots, both Y seam jambs and
their fore strips, and Z hook/foot/stop roots. These modifiers change deposition
only inside the existing material. General infill remains 15%; normal walls,
fine show-layer bands, production orientations and support policy remain part
of each native review. A CAD solid or a few perimeter loops do not make the
interior solid. The [current RC62 jobs](../magnet-retention/queue.json) must include
these regions and a fresh emitted-path review before submission.

The supported correction follows manufacturer geometry and increases material
on the identified load path. It does not establish survival of a 4–6 inch drop.
Polymaker's printed-specimen tensile data cannot supply a measured interlayer
shear allowable for these joints. A filled assembled enclosure, its landing
orientation and actual stopping distance determine the relevant drop result.

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/audit.py
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/print_regions.py
```

Load `placement_comparison.py` and call `compare(a)` inside the fresh full-assembly
run. It reuses those actual placed native solids and records unchanged input
hashes; it does not derive a second pack.
