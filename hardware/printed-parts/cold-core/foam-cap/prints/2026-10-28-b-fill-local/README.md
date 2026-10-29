# Local B-fill cup and lid tests

Each printer receives one cup and its matching lid, cropped to the rectangular
B-fill block: world X−60…−27, Y182.6…248.3, Z233.55…253.4 mm. The crops preserve
the production channel, 0.25 mm supported-roof allowance, 0.5 mm cup-mouth relief,
0.15 mm seating allowance, and complete insert and recessed-head pockets.

| Printer | Fore screw centers | Fore span to edge | Aft span to screw |
| --- | --- | ---: | ---: |
| Mark1 | X−54/−33, Y219.3 | 36.70 mm | 23.00 mm |
| Mark2 | X−54/−33, Y212.45 | 29.85 mm | 29.85 mm |

Both aft screws are at X−43.5/Y242.3. The midpoint version fills the two original
fore holes and cuts the matching pilot, clearance and head pockets at Y212.45.
Production geometry is retained; these are comparison coupons.

Use three M3 × 10 screws and full RX-M3×5.7 inserts to clamp each pair. Compare
tube insertion, the seating faces, and lid lift under the tube's natural bend.
The actual small cup roof over the descending bore is present in both test sets.
Physical fit and finish await inspection of the printed parts.

Both plates use the left hardened 0.4 mm Standard nozzle and loaded black PET-GF,
reported by the printers as PET-CF. They retain their production print orientation,
three Classic wall loops, 15% gyroid infill, 0.20 mm first layers and 0.24 mm normal
layers. The cup retains its support-free production recipe; the lid retains
Tree(auto)/Default. Remove the lid's groove support before assembly.

Mark1 uses its +0.18 mm user trim (Textured PEI emission +0.16 mm); Mark2 uses
+0.04 mm (+0.02 mm emitted). Each complete deposited bead envelope is at least
89.768 mm inside the usable bed. Starts are separated by at least three minutes.

`generate.py` reads the production STEP files and writes local test files under
`.cache/prints/2026-10-28-b-fill-local/`. `geometry.json` binds those files to their
source. `prepare.py` makes and manually reviews each native slice; the two
`*-preflight.json` records bind the archives, settings and bead bounds. The
`*-launch.json` records hold the accepted printer task IDs: Mark1 **1385666436**
and Mark2 **1385672893**. Both acceptance readings report RUNNING with no print
errors. The recorded lower bound on startup spacing is 190.99 seconds.
