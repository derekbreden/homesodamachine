# Enclosure insert and seam construction

The customer outcome is an enclosure that keeps its internal components secured,
captures both pumps in the fixed upper mount and lower retainer and can be handled without its joints opening.
The current insert schedule is
[enclosure mechanical §1](/hardware/assembly/enclosure-mechanical.md#1-stage-the-printed-pieces).
The snap-fit pump retainer uses two integral wings and no separate fasteners or inserts.

The [native audit](geometry-check.json) records 13 insert stations and 12 finished
knuckles in the five enclosure pieces it hashes. Its three pump-retainer stations belong
to the identified three-screw article; they are outside the current snap interface.
Electronics and C14 hosts carried by the above-core assembly are outside that audit.
The table below describes those bound exports. The audit reads complete installed insert
envelopes, open pilots, blind relief, closed stock, insertion access and the Y seam's
knuckles. Source and STEP hashes are checked before and after the run. These are geometry results;
installed fit, pullout, torque, transport and drop performance require physical
qualification. The [seam and handhold review](../y-seam-plain-review.json) records its
identified geometry and handhold scope. The [fit review](../y-seam-fit-review.json)
records PET-GF-to-PET-GF gaps and complete local stock at four M5 insert hosts and
four head floors for its bound inputs. The [M5×100 review](../y-seam-100-review.json)
records its bound head floors, blind caps, local assembly motion and screw passages.

## Supplier constraints and screw stacks

The [ruthex RX table](https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf)
specifies Ø4.0 mm pilots and 1.6 mm minimum wall for RX-M3Sx4.0 and RX-M3x5.7,
and Ø6.4 mm pilots with 2.6 mm minimum wall for RX-M5x9.5. The audit compares pilot
diameters to fixed supplier values independently of mutable CAD constants. Every
pilot has at least 1 mm beyond the installed insert; the enclosure's screw stack
also checks full seam-insert engagement and at least 0.5 mm beyond the longest specified
screw tip. The seam screws carry a ±0.8 mm length allowance.

Each Y-seam screw head bears directly on its printed floor in a Ø9 opening. The lower
opening runs up into the handhold ceiling and ends on the plane of the handhold's inner
wall; the upper runs 8 mm down into the roof and on into the funnel opening above the
frame. The rim at the handhold's R6 lip is in
[the enclosure specification](../README.md#seams--corner-stacks).

| Station | Body | Pilot depth | Nominal host / screw stack |
| --- | --- | --- | --- |
| Four Y-seam stack stations | M5, 9.5 mm | Lower 10.5 mm; upper 20.5 mm | Both are pressed into the top of their knuckles: the lower into back-bottom's knuckle under the Z seam, where the M5 × 100 enters from the deep end and its tip stands past the open top; the upper into front-top's lower knuckle above its closed tip pocket. Both keep full 9.5 mm engagement with the ±0.8 mm length allowance |
| Electronics / ground stations (above-core hosts) | M3 short, 4.0 mm | At least 5.0 mm | Ø8 mm exposed hosts give 2 mm radial material from the Ø4 pilot; four PSU inserts seat on the actual wall face; four PCBA inserts start 2.25 mm behind the PCB mounting face |
| Two condenser fingers | M3, 5.7 mm | 9.0 mm | Complete host and supporting finger |
| Three pump-retainer stations | M3, 5.7 mm | Ø4 × 6.7 mm insert pilot, followed by narrower screw-tip relief | Upward M3×60 from underside head seats; 1 mm steel-tip clearance in front-top’s fixed mount |
| Two C14 stations (above-core hosts) | M3 short, 4.0 mm | 5.25 mm | Full tunnel stock and closed rear wall |
| Four compressor posts | M5, 9.5 mm | 10.5 mm | Manufacturer pilot and minimum surrounding stock |

## Native seam load paths

The Y seam stands at Y200 mm with a 17.8 mm overlap. Each ±X corner carries a stack
of knuckles alternating between the front and back pieces, its screw axis mid-overlap
([corner stacks](../README.md#seams--corner-stacks)). The lower stack is a three-knuckle
hinge inside the bottom pieces: back-bottom's knuckle over the handhold, front-bottom's,
and back-bottom's under the Z seam. An M5 × 100 drives up from the handhold ceiling through
all three into the insert pressed into the top of the upper back knuckle, so back-bottom
holds the screw at both ends and front-bottom's knuckle hangs on it between them. The upper
stack has front-top's roof head block, back-top's middle block and front-top's lower insert
block. An M5 × 100 drives down through all three, with its tip enclosed in the lower block.
The lower blocks reach
13.75 mm from `interior_x`, leaving 0.25 mm to the core. Every face between knuckles keeps
0.25 mm of running fit measured square to the face; knuckle faces that print facing down
rise 45° off their own piece's stock. Clearance holes print at Ø5.6 mm. The audit reports
nominal and minimum thread engagement with the ±0.8 mm screw-length allowance.

A seam-opening load puts the screws in shear at the faces between knuckles: two per lower
corner and two per upper corner. All four screws are fully threaded
[SVLING M5×0.8×100, B0GHNNYVDH](https://www.amazon.com/dp/B0GHNNYVDH/).
Thread crests bear against the printed passages when a joint takes shear. At both heights,
the head and insert belong to one enclosure half and capture the other half's middle block;
the screw does not directly compress the middle block axially. The Ø5.6 mm
printed holes have clearance around the nominal Ø5 mm screws; print variation and
deflection determine which faces bear first. The audit reads every knuckle's whole native
section, its length along the screw and its ligament fore and aft of the clearance hole.
These are geometric quantities, not a measured shear or bearing capacity. The floor tongue
has no tensile interlock, and the joined tops do not establish a compression flange under
edge-first bending.

The Z hooks have 4.5 mm arms and 5 mm overlap over their 6 mm feet. Every sliding
face retains its stated running/support allowance; the end-stop clearance is
0.25 mm and the stop length is 3.75 mm. Whole hooks, roots, stops, entry sweeps
and the native 1 mm lifting engagement are checked by the enclosure producer.

## Deposition and evidence

[Print regions](print-regions.json) require local 100% infill through
the complete insert hosts, blind caps and supporting roots, every Y-seam knuckle
and its root, and Z hook/foot/stop roots. The manual specification binds the five
main pieces' STEP/STL by hash, with their prescribed source-to-print transforms.
Plate X/Y nesting remains part of the native project.

These modifiers change deposition
only inside the existing material. Reinforcement boxes set infill density and pattern
and inherit the ordinary wall settings.
General enclosure infill remains 15%; normal walls,
fine show-layer bands, production orientations and support policy remain part
of each native review. A CAD solid or a few perimeter loops do not make the
interior solid. Each production job requires these regions bound to its current
mesh and a fresh emitted-path and support-removal review. The
[RC62 archives](../magnet-retention/queue.json) retain their identified article
scope.

The corner stacks follow manufacturer insert geometry and carry the seam's load
path on steel screws. They do not establish survival of a 4–6 inch drop.
Polymaker's printed-specimen tensile data cannot supply a measured interlayer
shear allowable for these joints. A filled assembled enclosure, its landing
orientation and actual stopping distance determine the relevant drop result.

```sh
HSM_BUILD_SUPERSEDE=0 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/audit.py
HSM_BUILD_SUPERSEDE=0 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/print_regions.py
```
