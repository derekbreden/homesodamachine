# Complete Industrial faucet — held Mark2 candidate

The print is held at Derek's request: “Apologies, pause on that print”.
No import or Send has occurred. A separate go-ahead and fresh readings of both
printers are required before any start.

The [editable project](2026-10-09-industrial-faucet-complete-shoulders012-wing050-drip4-petgf-left04-z004-mark2.3mf) and [native archive](2026-10-09-industrial-faucet-complete-shoulders012-wing050-drip4-petgf-left04-z004-mark2.gcode.3mf)
contain all five rigid parts: corrected base, shared tip, Industrial cover,
counter plate and side-down lever. The native estimate is **5 h 54 min 52 s**,
with 155.51 g at the saved density.

The shared tip uses a round Ø4 mm underside drip hole and an unsealed pocket
with two plain 2 mm tube-guide walls. The 4 mm OD / 2.5 mm ID drain tube ends
square inside the pocket. No drain bung, gasket or insertion tool is fitted.
The [geometry reading](../../../vent-qualification/simple-drip-check.json)
records nominal tube clearance and the open hole-to-pocket connection.
The cover's wings extend 0.50 mm with matching arch clearance; its retaining
lip datum is preserved. Physical drip behavior and cover seating are unmeasured.

The process uses 0.20 mm first bed layers and 0.24 mm normal layers. The base
alone uses 0.12 mm at print Z13.40–29.00 and Z55.16–68.12 mm. One continuous
six-wall solid foot with Arachne and 15% infill/wall overlap preserves insert
reinforcement while removing the repeated exterior screw-host tracks.
Tree (auto), saved Default style and automatic sections are retained.

Mark2: black PET-GF, external left slot 254 labeled PET-CF/GFT01, fixed left
hardened standard-flow 0.4 mm nozzle, Textured PEI, +0.04 mm requested trim
and +0.02 mm emitted. Planned Timelapse On, leveling On, automatic flow and
nozzle-offset calibration. Probing clump detection stays disabled.

The [native check](native-check.json) covers all five embedded meshes, actual
layer heights, the full bead envelope (24.83 mm bed margin),
and absence of repeated outer-wall endpoints at the three screw-host boundaries.
The [insert review](insert-beads.json) checks all three host/root/cap regions.
The [first/second-layer reading](first-second-layer-review.json) records overlap
with labelled first-layer model, brim and support roads. These are commanded
geometry readings; they do not establish physical adhesion, easy support cleanup,
finish, fit, strength or lifetime.

The [preparation](preparation.json) and [launch plan](launch-plan.json) bind all
archive/source hashes and retain the hold. The earlier 0.08 mm shoulder
[physical reference](../2026-10-09-two-shoulders008-with-lever-mark2/physical-result/physical-result.json)
retains its accepted finish and support-removal scope.
