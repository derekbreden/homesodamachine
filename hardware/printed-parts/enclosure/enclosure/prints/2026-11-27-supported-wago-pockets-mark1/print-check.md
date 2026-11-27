# Back-top WAGO pockets on Mark1

The full back top is prepared for the Mark1 left hardened 0.4 mm Standard nozzle, black PET-GF and textured PEI. Bambu Studio estimates 36 h 7 min and 862 g. Both banks of 221-413 pockets have removable roof support. The two chamfered rear label channels print clear. [Printer project and sliced archive](print-plan.json)

| WAGO bank | Top of each dense interface layer, from the bed | First roof layer |
| --- | --- | --- |
| Compressor neutral, compressor hot and diaphragm-pump positive | 59.00, 59.24, 59.48 mm | 59.96 mm |
| Mains hot, earth and neutral | 30.68, 30.92, 31.16 mm | 31.64 mm |

Each roof spans 8.70 mm. Across all six pockets the longest stretch of a first roof bead with no overlap onto the interface or preceding model is 0.331 mm. The bead is 0.438 mm wide. The equivalent stretch in the previous file was 8.262 mm. The two perimeter beads at every mouth also reach backing. Both gripping cheeks retain their solid local infill. [Six-pocket native G-code measurements](six-well-toolpaths.json) · [Gripping wall measurements](gripping-wall-toolpaths.json) · [Toolpath sections](wago-roof-toolpaths.png)

Remove the trees while the enclosure is empty. Clip the exposed branches and the links between adjacent sockets from inside the enclosure, then pull each freed insert and its dense mat straight out through its connector mouth. The eight exterior clip sites leave six independent inserts. Each clears its mouth in a 14 mm pull with at least 0.47 mm of lateral clearance. The three near the front seam share a bed-rooted trunk. Each mains pocket also has a local root on its floor. The first physical print will establish release force, roof finish and retention with the actual connectors. [Clip positions, approach and withdrawal](six-well-toolpaths.json)

The roof relief brings nominal clearance above each body to 0.40 mm. Each socket retains its 9.45 mm insertion depth, 8.70 mm width and at least 3.00 mm of backing. The new stock clears all 715 other installed bodies. [Installed fit and neighboring components](installed-fit.json)

Both rear labels retain their measured seating surfaces. The flow-meter supports, rail supports and fill-tube jaw support were checked in this G-code. All 1,761 connected permanent shell sections receive extrusion. The slicer repeated its polygon-clipping diagnostic. The lower flow-meter hook has the same tip coverage as in the prior plate. [Shell toolpath measurements](shell-toolpaths.json)

The front top uses the two manifold connector fits accepted on November 13. The earlier full front tops had roof supports. The five-dot comparison included a supported and a bridged coupon. The six-dot coupon used floor-rooted trees. The production decision specified transverse bridges in the two front sockets. The November 21 front-top G-code carries that choice. [November 13 production decision](https://github.com/derekbreden/homesodamachine/commit/e9da74690ecbe7fa73ca73692ef4f498bbbe71fd) · [November 21 front-top slice](../2026-11-21-front-top-production-mark1/print-plan.json)
