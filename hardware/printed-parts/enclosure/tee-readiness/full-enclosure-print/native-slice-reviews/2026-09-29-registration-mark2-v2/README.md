# Mark2 coplanar registration print

Mark2 accepted job **1294385772** at 2026-09-29 21:19:52 UTC. The ordinary
six-layer print uses black PET-GF on the left 0.4 mm nozzle and white PET-GF on
the right 0.4 mm nozzle. Launch options are the usual Timelapse On, bed leveling
On, flow calibration Auto and nozzle-offset calibration Auto.

Native estimate: **13 minutes 41 seconds**, 5.57 g. All 60 candidate alignments
pass the emitted-path comparison against their intended offsets. The physical
reading is **outside the tested range**: the top/X left endpoint is best but
insufficient, and the bottom/Y right endpoint is best but insufficient. See
[`physical-result.json`](physical-result.json). This constrains the white
correction to X below −0.35 mm and Y above +0.35 mm without measuring either
value. No alignment correction has been applied to the nameplate.

[`verification.json`](verification.json) contains the toolpath checks;
[`manifest.json`](manifest.json) pins the source and archive hashes;
[`launch.json`](launch.json) records the accepted job and launch options. The
initial acceptance snapshot includes an HMS entry carried across startup;
later status observations are in [`postlaunch-status.json`](postlaunch-status.json).
