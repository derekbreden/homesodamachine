# Complete retention samples

Each receiver is a crop of the production STL, including its real parent wall,
complete spring pockets and all hardware-bearing shoulders in X, Y and Z.
The PISCO cap spans Y420.345717–462.050000 mm (41.704283 mm), with 3 mm of
receiver end stock before the rear port land. Its receiver includes the full
rear CO2 bulkhead bore. The ASSE sample includes the rear water bore, the meter
sample includes its wire exit and rear soda bore, the water regulator includes
both axial shoulders, and the pump sample includes both fixed motor-rail stops.

Caps retain their production axial-end print poses. Receivers retain the
production parent orientation: the pump lid face up, and the rear enclosure
roof down. The 2.0 mm leaves, blended roots and centered screwdriver slots are
present. Use a tiny flathead screwdriver that fits inside the cavity to remove
the small automatic supports; use the centered pry entries to release a cap.

[geometry.json](geometry.json) records the actual source STL hashes, crop bounds,
one watertight solid per print, seated cap clearance and obstructed pullout.
The hardware check reports no overlap except 0.001314 mm³ at the meter,
below the print surface resolution. Physical clamping, insertion and release
force, repeated-cycle life and pump vibration require the bench trial.

| Printer | Pieces | Native estimate | Black PET-GF15 |
| --- | --- | --- | --- |
| Mark1 | Pump receiver, ASSE pair, PISCO pair | 4 h 32 min | 149.66 g |
| Mark2 | Pump cap, meter pair, water-regulator pair | 5 h 49 min | 205.18 g |

The [print jobs](print-jobs.json) bind the native slices, review reports and
launch receipts. Both plates use the left hardened 0.4 mm Standard nozzle,
three Classic walls, solid caps, 15% gyroid receivers and Tree(auto)/Default
supports. Full deposited-bead edge margins are 80.983 mm and 78.822 mm.
Requested Z trims are +0.18 mm on Mark1 and +0.04 mm on Mark2; native textured
PEI G-code emits Z0.16 and Z0.02 respectively.

Mark1 accepted task **1400544434** and Mark2 accepted task **1400555954**,
more than three minutes apart. Both report RUNNING with zero print errors and
no HMS alerts in their launch receipts.
