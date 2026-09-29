# Receiver for framed nameplate wings

H2C accepted job **1294406296** at 2026-09-29 21:29:10 UTC, more than nine
minutes after Mark2's acceptance observation. The coupon uses CAD −Z as build-up,
matching the back-top enclosure orientation, with black PET-GF on the left
0.4 mm nozzle. Launch options are the usual Timelapse On, bed leveling On,
flow calibration Auto and nozzle-offset calibration Auto.

Native estimate: **43 minutes 16 seconds**, 20.04 g, 192 model layers. Support
settings come from the shared PET-GF profile: tree Auto, 0.40 mm XY clearance,
0.45 mm upper Z gap and 0.30 mm lower Z gap. Support and interface material are
explicitly black. The emitted paths form one bed-rooted tree with one interface;
no support bead enters either wing slot. Physical removal remains unqualified.

The slots provide 0.48 mm total thickness clearance for the 1.68 mm wings,
with a 1.20 mm retaining lip and at least 2.00 mm lateral engagement. The
print-down slot ends and pocket edge receive an additional 0.75 mm allowance
for rough supported surfaces. The rear diamond opening provides removal access.

[`geometry-check.json`](geometry-check.json) verifies seated fit and capture.
[`insertion-envelope.json`](insertion-envelope.json) checks the central bend
cross-section, without establishing insertion force or fatigue.
[`verification.json`](verification.json) checks the native slice and support
placement. [`manifest.json`](manifest.json) and [`launch.json`](launch.json)
identify the exact files and accepted job. Insertion, retention, flatness and
support removal require the physical coupon test before enclosure integration.
