# Fitted rear retention samples

Three complete receiver/cap pairs test the ASSE adapter capture, PISCO
body/neck bearings and meter housing socket. Each receiver is cropped from
the production printed surface with its parent wall, complete catches and
all hardware retention points in X, Y and Z. Both rear bulkhead bores and the
meter wire exit are included. Caps print on an axial end; receivers retain
the production roof-down orientation.

The ASSE cap captures both axial sides of the 1/4 NPT–3/8 NPT adapter hex.
Its lower body reaches Y461.078; its spring span remains Y396.453–438.114.
The drain-sleeve window ends at Z309.4, leaving solid backing beneath the
adapter pocket. The 0.15 mm fitted adapter pocket locates the adapter independently of the
ASSE's ±1.5 mm taped-thread engagement allowance. The sleeve window carries
the same fore/aft allowance; [native readings](threaded-joint-room.json)
find zero overlap at five positions through that travel.

The PISCO cap follows its scanned body and short exposed neck with 0.15 mm
radial and 0.25 mm axial air. One 3 mm upper receiver bearing locates the
largest body ring. Its rear hole, axis, Y stops, spring datums and stock
planes retain their positions. The [focused review](pisco-fit-review/README.md)
binds the scanned profiles and emitted geometry. For installed removal,
spread the leaves, lower the cap 3.6 mm, depress the outlet collet and remove
the stem check, then slide the cap 45 mm fore. Actual release force and
collet operation require this physical trial.

The meter's two mating surfaces follow the housing taper, flange and
label-side bevel with 0.15 mm radial and axial air. Four bosses and screw
heads have separate fitted passages. Its 16 mm loading corridor, spring
station, flexible-wire route and outside tube-clearance bevel are retained.
The pump and water-regulator fits remain as accepted in the
[v4 physical result](../v4/physical-result/physical-result.json).

[geometry.json](geometry.json) binds the production STL hashes and six
watertight single-solid prints. All three caps have zero seated overlap and
obstructed 0.5 mm pullout. Every purchased component clears these new
bearings; the existing 0.001314 mm³ meter bulkhead-nut residue is below the
print resolution. [hardware-motion.json](hardware-motion.json) measures rigid
contact travel; friction, clamp force, spring life and actual play require
the bench trial.

| Printer | Pieces | Native estimate | Black PET-GF15 |
| --- | --- | --- | --- |
| Mark1 | ASSE pair, PISCO pair | 3 h 47 min | 120.34 g |
| Mark2 | Meter pair | 2 h 57 min | 86.14 g |

The [print jobs](print-jobs.json) bind native slices and launch receipts.
Both use a left hardened 0.4 mm Standard nozzle, 0.20 mm first layer,
0.24 mm normal layers, three Classic walls, solid caps, 15% gyroid receivers
and Tree(auto)/Default supports. The full-bead edge margins are 93.159 mm
and 102.688 mm. Mark1 emits Z0.16; Mark2 emits Z0.02.

Remove the small automatic cavity supports with a tiny flathead screwdriver
that fits inside the cavity. Preserve the flat catch undersides. Release a
cap through its centered 5 mm-wide, 1 mm-high screwdriver entries.
The [longer tip study](wing-tip-study.md) keeps insertion-tip tuning separate
from this hardware fit trial.

Mark1 accepted task **1401825806**; Mark2 accepted task **1401838081**,
314.5 seconds later. Both launch receipts report RUNNING with zero print
errors and no HMS alerts.

The active Mark1 job uses [initial-geometry.json](initial-geometry.json) and
[initial-asse-cap.stl](initial-asse-cap.stl). Its adapter stops and springs
match the fitted trial; its drain opening extends to Z328. The current cap
has solid backing above the sleeve's measured Z309.15 exterior. The
[backed Mark1 plate](backed-Mark1-print.json) is prepared at 3 h 51 min and
122.96 g for a fresh bed. The meter plate uses the current meter geometry.

Derek requests that the active Mark1 trial finish. The backed plate remains
prepared for a fresh bed; it has not been submitted.
