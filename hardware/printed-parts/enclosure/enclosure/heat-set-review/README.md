# Enclosure insert and seam construction

The customer outcome is an enclosure that keeps its internal components secured,
seats the pump cartridge precisely and can be handled without its joints opening.
The [native audit](geometry-check.json) records 35 insert stations and 14 finished
knuckles for its exact source and native input hashes. Its front-top continuation
retains that same artifact scope. It reads complete installed insert envelopes, open pilots,
blind relief, closed stock, insertion access and the Y seam's knuckles. Source and
STEP hashes are checked before and after the run. These are geometry results;
installed fit, pullout, torque, transport and drop performance require physical
qualification. The [seam and handhold review](../y-seam-plain-review.json) records its
identified geometry and handhold scope. The [fit review](../y-seam-fit-review.json)
records current PET-GF-to-PET-GF gaps and complete local stock at the four M5 insert
hosts and four washer floors. The 35 station readings, 14 knuckle queries, screw
engagement and blind-tip reserve retain the insert audit's recorded artifact scope.

## Supplier constraints and screw stacks

The [ruthex RX table](https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf)
specifies Ø4.0 mm pilots and 1.6 mm minimum wall for RX-M3Sx4.0 and RX-M3x5.7,
and Ø6.4 mm pilots with 2.6 mm minimum wall for RX-M5x9.5. The audit compares pilot
diameters to fixed supplier values independently of mutable CAD constants. Every
pilot has at least 1 mm beyond the installed insert; the enclosure's screw stack
also checks full seam-insert engagement and at least 0.5 mm beyond the longest specified
screw tip. The seam screws carry a ±0.8 mm length allowance.

Each screw head and flat washer sit in an inboard-open U-shaped access recess.
Both complete washer-bearing annuli retain 3 mm of stock below their floors.
Each pocket is 8 mm deep; the lower floor is Z37.25 and the upper floor is Z347.
Nominal head and washer poses retain the 2 mm head recess. Each steel washer
bears directly on its printed floor.
The lower entry has a 0.5 mm bevel; its head seat and washer floor stay flat.
The upper mouth continues inward into the funnel opening above the frame.
The upper recess's roof-edge mouth has the named local thin-section allowance in
[the enclosure specification](../README.md#seams--corner-stacks): the exterior taper
leaves a 1.81 mm minimum horizontal outboard rim width over its top 2.38 mm,
reaching at least 3 mm below Z352.6164 with 3.5 mm fore and aft ribs. This scope is
specific to the access mouth.

| Station | Body | Pilot depth | Nominal host / screw stack |
| --- | --- | --- | --- |
| Four Y-seam stack stations | M5, 9.5 mm | Lower 13.70 mm; upper 14.15 mm | The lower insert is in back-top's anchor block over the Z seam; the upper is in front-top's block under the funnel frame. The specified stack gives full 9.5 mm engagement and at least 1.7 mm blind-tip room with the ±0.8 mm length allowance at nominal CAD part poses |
| Seventeen electronics / ground stations | M3 short, 4.0 mm | At least 5.0 mm | Ø8 mm exposed hosts give 2 mm radial material from the Ø4 pilot; four PSU inserts seat on the actual wall face; four PCBA inserts start 2.25 mm behind the unchanged PCB mounting face |
| Two condenser fingers | M3, 5.7 mm | 9.0 mm | Complete host and supporting finger |
| Two pump-clamp stations | M3, 5.7 mm | At least 6.7 mm | M3×60, at least 0.5 mm steel-tip clearance |
| Two C14 stations | M3 short, 4.0 mm | 5.25 mm | Full tunnel stock and closed rear wall |
| Four compressor posts | M5, 9.5 mm | 10.5 mm | Manufacturer pilot and minimum surrounding stock |
| Four pogo anchors | M1.4, 4.0 mm | 5.5 mm | Insert top 7.25 mm behind the connector contact face, 7.375 mm behind the recessed seat's printed face; M1.4×8 engagement 2.75 mm, tip 2.75 mm before blind end |
| Four factory keeper locks | M3 short, 4.0 mm | Through the 5 mm keeper boss | Front-driven M3×8 screws and 0.5 mm washers sit in 3.75 mm deep crowned wall recesses. The head is recessed 0.25 mm; 3.25 mm of wall backs the washer. Each keeper boss has 3 mm radial material around the knurl. The screw reaches 4.10 mm past the insert entry, engaging the full 4 mm insert and ending 0.90 mm before the boss back |
| Eight shared cradle/cover locks | M3 short, 4.0 mm | 5.75 mm below the nominal host plane; 6.00 mm from the raised entry | M3×12 screws pass through the 3 mm cover tab, 0.15 mm supported inter-tab gap, 3 mm base tab and 0.5 mm washer. The insert entry is on the 0.25 mm raised host land. The tip projects 5.35 mm past that entry, or 5.10 mm below the nominal host plane, with 0.65 mm blind-tip room |

ZWMSSLL publishes Ø2.3 mm knurl, Ø2.0 mm lead and 4 mm body dimensions for its
M1.4 insert, without a host pilot, wall or pocket-depth recommendation. Ø2.0 mm is
the starting fit. The [SPIROL FDM guidance](https://www.spirol.com/resources/white-papers/how-to-select-a-threaded-insert-for-your-3d-printed-assembly/)
supplies the application rule of a solid host diameter at least 1.5 times the
knurl diameter. The audit reports this separately from supplier compliance.
The bound insert audit reports at least 1.148 mm around the pump-cap's Ø2 pilot through
the whole insert body, with more in front-top. The 2.6 mm wide loading stadium passes the whole knurl
through the 4.25 mm ear-to-anchor setback. Install and cold-check the depth before fitting the
connector, following [enclosure assembly](../../../../assembly/enclosure-mechanical.md).
The [coupon](../contact-pair-coupon/README.md) retains its identified geometry and
connector-fit acceptance. The [current mounting audit](../../../../reference/yyfkgcp-pogo-4p/mounting-audit.md)
records the complete recessed seats and tolerance stack; installed insert retention,
full-frame compression and electrical behavior remain physical qualifications.

## Native seam load paths

The Y seam stands at Y200 mm with a 17.8 mm overlap. Each ±X corner carries a stack
of knuckles alternating between the front and back pieces, its screw axis mid-overlap
([corner stacks](../README.md#seams--corner-stacks)). The lower stack runs from the
handhold ceiling through back-bottom, front-bottom, back-bottom and front-bottom to
back-top's hub over the Z seam, and an M5 × 150 drives up through it into the hub's
insert. The upper stack stands under the roof: front-top's knuckle under the funnel
frame and back-top's roof knuckle, with an M5 × 60 driven down into front-top's insert.
Lower axes stand at |X|98.25 and upper axes at |X|98. The lower blocks reach
13.75 mm from `interior_x`, leaving 0.25 mm to the core. Front-bottom's first block
starts at Z66.2 and its top block ends at Z174.696447, 0.353553 mm below the back-top hub.
This gives 0.25 mm measured normal to the adjacent 45° front-top rail bedding.
Front-top's upper insert mouth is Z299.65, 0.25 mm below back-top's Z299.9 block.
Every PET-GF-to-PET-GF block face requires its applicable static or running and supported-face
allowances, including the faces loaded when the screws seat.
One Ø10 × 1 mm flat washer bears directly under each head.
Clearance holes print at Ø5.6 mm. The audit reports nominal and minimum thread
engagement and tip clearance with the ±0.8 mm screw-length allowance.

A seam-opening load can put the screws in bearing against the alternating blocks.
The lower M5 × 150 screws are partially threaded McMaster 91290A298, with at least 27 mm
of thread at the tip; the upper M5 × 60 screws are fully threaded SVLING B0GHNHFYJN.
The Ø5.6 mm printed holes have clearance around the nominal Ø5 mm screws; print
variation and deflection determine which blocks bear first. Equal load sharing is
unestablished. The audit reads every block's whole native section, its length along the
screw and its ligament fore and aft of the clearance hole. These are geometric quantities,
not a measured shear or bearing capacity. Edge-first bending that opens the bottom seam
loads the lower screws. The floor tongue has no tensile interlock,
and the joined tops do not establish a compression flange under that bending mode.

The Z hooks have 4.5 mm arms and 5 mm overlap over their 6 mm feet. Every sliding
face retains its stated running/support allowance; the end-stop clearance is
0.25 mm and the stop length is 3.75 mm. Whole hooks, roots, stops, entry sweeps
and the native 1 mm lifting engagement are checked by the enclosure producer.

## Deposition and evidence

[Print regions](print-regions.json) require local 100% infill through
the complete insert hosts, blind caps and supporting roots, every Y-seam knuckle
and its root, and Z hook/foot/stop roots. The manual specification also covers all
twelve factory dock-lock hosts, keeper guides, SB443 rail and bedding-key roots,
rigid-stop bearings, stem-flange capture shoulders, recessed pogo hosts and the
actual cut TPU mounting keys. It binds the six main pieces and twenty
station-specific dock STEP/STLs by hash. The dock manufacturing exports already
contain their print poses; the main pieces retain their prescribed source-to-print
transforms. Plate X/Y nesting remains part of the native project.

These modifiers change deposition
only inside the existing material. Reinforcement boxes set infill density and pattern
and inherit the ordinary wall settings. The four station-specific keepers, four
cradles and four covers use six walls and 100% infill throughout their connected
load paths. The manual wet preparation records solid deposition through the
actual keys under its retained Siraya recipe.
General enclosure infill remains 15%; normal walls,
fine show-layer bands, production orientations and support policy remain part
of each native review. A CAD solid or a few perimeter loops do not make the
interior solid. Each production job requires these regions bound to its current
mesh and a fresh emitted-path and support-removal review. The
[RC62 archives](../magnet-retention/queue.json) retain their identified article
scope; their print pauses do not apply to the post-print SB443 mounts.

The corner stacks follow manufacturer insert geometry and carry the seam's load
path on steel screws. They do not establish survival of a 4–6 inch drop.
Polymaker's printed-specimen tensile data cannot supply a measured interlayer
shear allowable for these joints. A filled assembled enclosure, its landing
orientation and actual stopping distance determine the relevant drop result.

```sh
HSM_BUILD_SUPERSEDE=0 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/audit.py
HSM_BUILD_SUPERSEDE=0 tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/heat-set-review/print_regions.py
```
