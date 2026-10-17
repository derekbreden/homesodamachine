# Complete white Sculpted faucet — localized cooling and display clearance

One of each rigid part: Sculpted base, shared tip, Sculpted cover, matching
above-counter plate and side-down lever. Target: Mark2's right hardened
standard-flow 0.4 mm hotend, white PET-GF in external spool 255. The bed is
confirmed clear by Derek's print request. The [native review](native-review.json)
and [print preparation](2026-10-17-sculpted-white-localcool-clearance150-right04-z004-mark2.print.json)
bind the complete project. Physical assembly and finish remain pending.

The display and bezel move 1.50 mm along the display normal, giving
1.80064 mm minimum nominal clearance to both flavor tubes. Four existing
3 mm square bearing pads extend 1.50 mm. The neck pocket, tube routes,
retaining grooves, lower cover shoulder and lip datums stay fixed. The
[clearance reading](display-clearance.json) records the dimensions and stock.
The [retention reading](display-retention.json) passes the display/cover fit,
loading, axial approach, snap engagement, lip and neck-stock readings. It also
retains an existing nominal ribbon-clearance shortfall at the gooseneck:
0.018942 mm positive gap against the reader's 0.10 mm target, with zero
intersection. Rebuilding the pre-change source gives the same gap at the
same location. This is not a display-seat regression; physical cable fit
remains the relevant assembly observation.

[Localized PET-GF cooling](../../../../cooling/README.md) leaves general and
auxiliary part cooling off. Bridges and wall paths meeting the 50% overhang
threshold receive 70% after the first three bed layers. Fan-always-on and
fan pre-start are off. The [actual path reading](cooling-paths.json) and
[material commands](material-commands.json) show zero cooling on ordinary
infill, top surfaces and floating vertical shell. Over 99% of the cover's
exterior-wall travel has fan off; 120.6 mm of its overhang-classified exterior
paths receive 70%. Outer/inner-wall labels can include qualifying overhang
segments; a feature label alone does not identify their support condition.
Startup nozzle-cooling and other machine fans retain their normal commands.

The normal process remains 0.20 mm first layer and 0.24 mm subsequent courses,
two ordinary walls, 15% grid infill, 265/280°C nozzle and 80°C bed. Bridge flow
is 125%, bridges 15 mm/s, with the selected 10/15 mm/s overhang limits. The
Industrial-only shoulder bands are absent. Base, tip and plate retain the
Back/A2/150% seam recipe and rear seam paint. Cover and lever retain
Aligned/15%/scarf-off. Full-height maximum lateral seam offsets are 0.367 mm
on the base, 0.196 mm on the exposed curved tip, and 0.029 mm on the plate.
The ordinary corner seams use their own locations.

The −15° base, −105° tip, −50° cover and other poses retain their selected
support treatments: segmented base-rim arcs, tip fins, hidden root disc,
local lip trees and Tree(auto)/Default elsewhere. No new support blockers
are introduced. The complete native bead envelope has a 31.90 mm minimum
bed-edge margin. [Packaging](packaging.json) keeps G-code bytes unchanged in
the print-only archive. Estimate: **6 h 14 min 31 s**, 1,022 nominal layers.

The [successful fan-off cover](../../../faucet-display-cover/prints/2026-10-17-cooling-off-prepared-mark2/physical-result.json)
passed normal loading and installation before this clearance revision. It
does not establish acceptance of these new meshes or measured strength and
cycle life. The [launch](launch.json) and [startup](startup.json) identify the
actual submitted task when accepted.
