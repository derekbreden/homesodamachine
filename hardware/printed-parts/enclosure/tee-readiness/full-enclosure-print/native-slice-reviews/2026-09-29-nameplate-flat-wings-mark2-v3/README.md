# Mark2 face-up nameplate with measured registration

Mark2 is running job **1294611267**, acknowledged at **2026-09-29T23:05:34.266818+00:00**.
The nameplate prints face up with its back and both flat wings on the bed,
**no supports**, and all lettering, logo, drop and QR raised 0.48 mm.
Native estimate: **32 minutes 48 seconds**, **12.25 g**, **14 layers**.
The matching horizontal-wing receiver is required.

White model coordinates receive **X −0.50 mm, Y +0.70 mm**, based on
[coupon job 1294488907](../2026-09-29-registration-mark2-v3/physical-result.json).
The selected positions are twelfth and eighth from the left, corresponding to
zero-based indices 11 and 7. The Y choice is tentative because of slight oozing.

Bambu Studio 02.08.02.61 uses native extruder offsets `0x0` and `0.5x-0.7`.
The nominal model meshes are identical to the reviewed uncorrected input.
The effective settings differ only in `extruder_offset`. Every model layer is
compared with the nominal slice after removing its requested coordinate shift;
the maximum path discrepancy is **0.000691 mm**, within native XY rounding.
The native purge-tower endpoints retain their machine positions, with five
white entry roads starting at the compensated approach point. No G-code is
edited after native slicing.

Launch options are Timelapse On, bed leveling On, flow Auto and nozzle-offset
Auto. Black PET-GF uses the left external spool and white the right external
spool, both 0.4 mm; the printer labels both PET-CF. The user confirmed Mark2's
plate clear. The send occurred at least **28 minutes 45 seconds** after H2C's
display job was acknowledged, exceeding the required three-minute interval.

Physical colour registration, QR scanning, wing insertion, relaxed flatness and
retention remain pending. TAP and FLAVOR ring prints await the nameplate result.

- [Exact archive and source hashes](manifest.json)
- [Native layer, support and artwork checks](verification.json)
- [Emitted coordinate comparison](registration-verification.json)
- [Printer preflight and spacing](preflight.json)
- [Printer acknowledgement and launch options](launch.json)
