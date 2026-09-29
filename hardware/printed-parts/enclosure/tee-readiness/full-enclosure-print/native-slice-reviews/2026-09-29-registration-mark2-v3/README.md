# Mark2 shifted-range registration coupon

Mark2 accepted job **1294488907** at 2026-09-29 22:06:59 UTC. The six-layer
coupon tests white correction candidates **X −1.05 to −0.35 mm** on its top row
and **Y +0.35 to +1.05 mm** on its bottom row, each in **0.05 mm** steps. Indices
0–14 increase from left to right with X above Y. The two rows are read independently.

The shifted ranges follow the endpoint observations in
[`v2's physical result`](../2026-09-29-registration-mark2-v2/physical-result.json).
The previous best endpoint appears at the right of X and left of Y in this coupon.
The current test does not apply a measured correction to any product print.

Native estimate: **13 minutes 41 seconds**, **5.57 g**. All 60 emitted marker
checks match their intended offsets. Black reference geometry, layer heights,
speeds and all slicer settings match v2. There are no supports. Black PET-GF
uses the left 0.4 mm nozzle and white PET-GF the right 0.4 mm nozzle.

Launch options remain Timelapse On, bed leveling On, flow Auto and nozzle-offset
Auto. Mark2's plate was confirmed clear. Its start is more than 37 minutes after
H2C's receiver acceptance observation.

[`manifest.json`](manifest.json) identifies the exact archive and source hashes;
[`verification.json`](verification.json) contains the emitted-coordinate checks;
[`launch.json`](launch.json) records the accepted job and normal launch options.
[`physical-result.json`](physical-result.json) records the user's selected twelfth
top-row position and eighth bottom-row position: zero-based indices 11 and 7,
giving white X −0.50 mm and Y +0.70 mm. “Fourth from the right” confirms the
top-row ordinal. The bottom-row choice is tentative because of slight oozing.
The corrected raised-artwork nameplate provides the pending physical validation.
