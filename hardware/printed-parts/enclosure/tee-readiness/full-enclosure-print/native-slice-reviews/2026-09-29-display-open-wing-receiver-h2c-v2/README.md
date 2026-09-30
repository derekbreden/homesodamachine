# Display receiver with open wing pockets

H2C accepted task **1295044165** at 2026-09-30T02:44:58.834880+00:00,
433 seconds after Mark2's receiver start.
The receiver-only native estimate is **2 h 53 min 20 sec**, **69.97 g**.
Use the existing support-free horizontal-wing cover from the H2C v1 pair.

Both retaining pockets open through the frame along the actual print-down
direction. The wing-pocket floors are absent. The 2.00 mm retaining lips and
cover seating land remain. Geometric sweeps beneath both roofs clear the full
fixture, including its standing cheeks, without interference. The native tree
supports form one bed-rooted body, with zero model-rooted bodies, including
unlabeled support paths. Removal effort still requires the physical print.

The body has 0.15 mm static clearance on each side; wing tips have 0.25 mm
centered clearance and at least 0.10 mm at full body X float. The normal gap
above a wing is 0.40 mm: 0.15 mm static plus 0.25 mm for the one supported roof.
Wing-end clearance is 0.15 mm at that roof. There is no sliding or low-force
addition. The minimum retaining overlap is 3.30 mm. The cover STL is unchanged.

The receiver keeps its enclosure 30° orientation and shared PET-GF tree supports
(0.40 mm XY, 0.45 mm upper Z, 0.30 mm lower Z). It uses black PET-GF on the left
0.4 mm nozzle, H2C's established +0.18 mm trim, a 0.20 mm first layer and 0.24 mm
above it. Saved speeds, wall order and ordinary startup settings apply, with
Nozzle Offset Calibration Auto.

[Verification](verification.json) checks the source and archive hashes, profile,
241 model layers and support topology. [Geometry checks](geometry-check.json)
cover seating, capture, pure-axis travel and open exits; the
[insertion envelope](insertion-envelope.json) is an ideal central-section bend,
not a force, fatigue or corner-motion test. Geometry lint has zero unanswered
findings. [Launch](launch.json) records printer acceptance and startup spacing.
Support removal, bow and shake retention remain physical tests. Full enclosure
integration also requires the deeper display-module and rear-housing check.

The [physical result](physical-result.json) records engaged bowing. The inverted
cover checks only partial depth because its wings rest above the opening. The
responsible body or wing contact has not been isolated.
