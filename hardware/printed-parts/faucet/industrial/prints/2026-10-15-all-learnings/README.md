# Complete faucet with selected finish and supports

One complete set of five rigid PET-GF parts is printing across both machines.
There are no controls or duplicate parts. Derek's authorization is:

> Please start me a complete faucet with ***EVERYTHING*** we've learned. Both beds are free.

| Printer | Parts | Accepted job and local time, 2026-10-15 | Native estimate |
| --- | --- | --- | --- |
| Mark2 | Full base with seven segmented rim arcs | [1342687225](mark2/launch.json), 13:19:25 CDT | 4 h 21 min 51 s, 102.39 g, 1245 layers |
| Mark1 | Full tip, display cover, rigid counter plate, side-down lever | [1342697013](mark1/launch.json), 13:22:57 CDT | 2 h 29 min 42 s, 59.05 g, 574 layers |

The starts are 212.222 seconds apart. Each job received one Send in Bambu
Connect and a successful printer reply. The exact names, reviewed G-code
hashes, spool verification and startup readings are beside each launch receipt.
Both machines use their fixed left hardened standard-flow 0.4 mm nozzle and
external black PET-GF spool 254, reported as PET-CF. Mark2 retains its requested
+0.04 mm trim, emitted +0.02 mm; Mark1 retains +0.18/+0.16 mm. Timelapse and
bed leveling are On; Flow Dynamics and Nozzle Offset Calibration are Auto.

## Retained geometry and finish

The [complete parent project](../../faucet-industrial-petgf.md) supplies the
current source meshes, 70° curved joint, smooth passages, continuous reinforced
foot and 0.50 mm longer cover wings. Production part geometry and seam paint
are unchanged. Layout changes are rigid XY translations; rotations and build
heights are preserved. The base remains at −15°, tip −105°, cover −50° and
lever on its accepted side-down surface.

The first bed layer is 0.20 mm and ordinary layers are 0.24 mm. The base retains
the two 0.12 mm shoulder bands and E's eight coarse starting-lip layers before
the first fine course at Z17.12. A2 Back seams with 150% ordinary gap serve the
base, tip and rigid plate; rear seam enforcement covers the full base silhouette
and exposed curved tip. The cover and lever retain ordinary corner seams.
Wipe remains off. Base Arachne, the solid infill-only foot modifier, two ordinary
walls, 15% grid infill and 15% infill/wall overlap are retained.

Every part receives native 125% bridge flow, 70% part cooling after three fan-off
bed courses, 15 mm/s bridges and overhang speeds limited to 10/15 mm/s. Cooling
also covers Floating vertical shell and support moves. Ordinary supported-wall
and infill speeds retain their saved values. Temperatures are 265 °C on the
first layer, 280 °C thereafter and an 80 °C bed. There are no post-slice motion,
extrusion or fan edits. TPU gasket and lever sleeve remain separate parts.

## Local supports and anchorage

The base carries the exact seven arc walls and narrow contact-strip blockers
from the [accepted Mark2 section](../../../finish-coupons/2026-10-15-edge-supports/base-mark2/physical-result/physical-result.json).
The 0.90 mm walls follow the visible outer edge in 41° arcs with 4° release
gaps and a requested 0.24 mm vertical gap. The front arc is uninterrupted under
the lever. Tree(auto)/Default serves the remaining annulus and gaps. The
physical source result accepts excellent edge support, the best observed
underside and very easy removal.

The tip carries the exact eight fins and root disc from the
[accepted Mark1 section](../../../finish-coupons/2026-10-15-tip-root-anchor/mark1/physical-result/physical-result.json).
The local seam-side lip tree enforcers use the accepted geometric selection
on the complete tip's tessellation. Tree(auto)/Default remains elsewhere,
including Bambu's automatic normal sections. The disc bonds to the hidden
male insertion terminal end. Derek accepts its removal scuff there; that
bonded contact is unsuitable for visible surfaces. The disc's scope is bed
anchorage of the starting plug layers, independently of overhang angle.

## Native review

The [Mark2 review](mark2/native-review.json) confirms exact support mesh transfer
at unchanged build Z and lower bead bearing along the entire sampled front
rim course at Z15.32. The [Mark1 review](mark1/native-review.json) finds 58.21 mm²
of bed-course deposition beneath the root and direct predecessor-course overlap
through Z1.16. At the priority lip the longest sampled run without lower bead
overlap is 1.95 mm. Its trees adapt to the complete object and layout.

Both native settings dictionaries exactly match their printer's physically
accepted section archive. The full-bead bed margins are 97.53 mm on Mark2 and
88.86 mm on Mark1; Mark1's smallest separation between complete object bead
bounding boxes is 7.20 mm. The support audits include small automatic bodies
without interface labels. Packaging preserves every native G-code byte and
its embedded checksum.

These readings bind the submitted commands and contact locations. The local
physical acceptance records retain their identified scope; the complete
faucet's finish, cleanup and mating fit await its own physical result.

`prepare.py` and `review.py` are manual preparation/review tools and do not send
prints. Submitted projects and archives are preserved.
