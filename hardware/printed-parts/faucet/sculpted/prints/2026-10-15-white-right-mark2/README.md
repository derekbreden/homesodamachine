# Complete white Sculpted faucet — Mark2

The complete five-part white PET-GF set is printing as Mark2 task **1343785668**.
The right hardened standard-flow 0.4 mm hotend uses external spool 255.
The printer reports that spool as white PET-CF, the material identifier used
by the PET-GF process.

The [launch record](launch.json) binds the accepted file and unchanged G-code
bytes. The [startup observation](startup.json) reports RUNNING, layer 0 of
1022, error 0 and no HMS at 02:16:34 UTC on October 16.
Timelapse and bed leveling are On; flow and nozzle-offset calibration are Auto.
The slice estimate is **6 h 14 min 27 s**, approximately **155.39 g** using the
saved profile density. Physical finish, cleanup and fit are pending.

## Selected process

The [Sculpted recipe](../../finish-selection.json) carries the physically
accepted [complete black Industrial process](../../../industrial/prints/2026-10-15-all-learnings/physical-result.json)
to the current Sculpted base, shared tip, Sculpted cover, matching mounting
plate and side-down lever. There are no product CAD or STL changes in this
preparation.

The first bed course is 0.20 mm and every subsequent nominal course is
0.24 mm. No Industrial shoulder bands or separate eight-layer override are
present. The normal 0.24 mm courses provide the coarse starts above supports.

Base, tip and plate retain A2/Back/150%: 60 mm scarf, 0% scarf gap,
150% ordinary seam gap, smart scarf at 155°. Cover and lever retain
Aligned/15% with scarf off. Wipe is off. The base retains Arachne and its
infill-only solid foot; other parts retain Classic. Modifier wall-count
overrides are absent.

The selected 125% bridge flow, 15 mm/s bridges, 10/15 mm/s overhang caps,
70% cooling after the first three bed courses, 265/280°C nozzle and 80°C
bed settings carry over. Ordinary supported-wall and infill speeds carry
over as well.

The seven accepted rim arcs are fitted to the Sculpted 58 × 59 mm foot
ellipse. The shared tip retains eight fins, low-lip tree enforcers and the
removable disc on its hidden male root. Tree(auto)/Default remains elsewhere.
Part poses retain the base at −15°, tip at −105°, cover at −50°, and plate
and print-oriented lever at 0° about CAD X. The right hotend retains native
XY registration and the normal Mark2 +0.04 mm requested Z trim (+0.02 mm
emitted on Textured PEI).

## Native evidence

[Native review](native-review.json), [material commands](material-commands.json),
[front-rim contacts](front-rim-contacts.json) and all five seam CSVs describe
the submitted toolpaths. The main rear-seam maximum lateral offsets are
0.367 mm for the base, 0.188 mm on the curved tip and 0.029 mm on the
mounting-plate outer rim. Tip plug, display-frame and straight dispense
terminal contours remain in the raw CSV and are outside the curved-neck
comparison. Cover and lever have no scarf ramps.

Both sampled front starting-rim courses at Z15.32/15.56 have no missing XY
bead-envelope overlap against the preceding 0.80 mm in Z. This measures
geometric bearing, not adhesion. The complete bead footprint, including
automatic and custom supports, retains at least 31.90 mm to the right
nozzle's usable-area boundary.

[Packaging](packaging.json) records the print-only container; it has identical
G-code bytes to the full native archive. [Readiness](readiness.json) binds the
review, editable project and launch.
