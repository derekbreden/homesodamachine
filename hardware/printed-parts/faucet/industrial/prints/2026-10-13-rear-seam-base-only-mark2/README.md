# One-time base-only rear seam evaluation — Mark2 task 1337160395

Mark2 accepted this evaluation at 6:20 pm CDT on October 13 after one Send
click. The receipt reports RUNNING, layer 0 of 1,244, with no printer error
or HMS fault. The completed print reached 1,244/1,244 with no reported fault.
The [physical result](physical-result.json) confirms the middle-neck seam
correction and reports continued displacement at the lower gooseneck and
lower-to-upper base transition.

Derek authorized the exception explicitly:

> Alright, mark2 is open, let's try your fix for the seam. I think for this evaluation, and this evaluation only, this is a one time exception I am making, print just the faucet base, thanks.

The plate contains only the Industrial faucet base. The normal saved project
and preparer retain the complete five-part faucet. This exception belongs to
this identified evaluation and supplies no standing authorization for partial
faucet prints.

The base and its infill-only foot modifier are copied byte-for-byte from the
[corrected complete Mark2 project](../../seam-placement/rear-center-v1/README.md),
including the 459 rear seam-enforcer facets. The −15° pose, A2/Back/150% seam,
wipe off, inherited walls, 100% zig-zag foot reinforcement, eight 0.24 mm lip
layers, 0.12 mm shoulder bands, temperatures, cooling and automatic supports
are retained. The sole base translates X+80 mm to the center of the usable
bed; there is no scale or rotation change.

The [native reading](native-review.json) follows 695 neck contours over CAD
Z80–237. Their starts remain within 0.450 mm of rear center, matching the
corrected complete slice. The full emitted bead footprint has at least
111.31 mm edge clearance. There are no wipe or periodic G39 blocks. Mark2's
normal +0.04 mm trim emits `G29.1 Z0.02` after reset to zero.

Native estimate: 3 h 54 min 14 s and 101.67 g at the saved density. Timelapse
and bed leveling are On; flow dynamic and nozzle offset calibration are Auto.
Mark1's preceding acceptance was 2 h 31 min earlier, exceeding the 180-second
startup interval. The single-object slice uses OBJECT_ID markers; the manual
trace reader maps those to the retained base identify ID.

The [complete-height re-reading](../../seam-placement/rear-center-v2/printed-base-trace/trace.json)
measures the omitted lower regions: 1.955 mm lateral displacement on the foot,
1.307 mm on the body and 1.556 mm near the lower neck. The original native
review's CAD Z80–237 scope did not include those regions. The
[current complete preparation](../../seam-placement/rear-center-v2/README.md)
includes the stage shoulders and a matching tip rear meridian.

- [Exact launched native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/industrial/prints/2026-10-13-rear-seam-base-only-mark2/2026-10-13-industrial-base-rear-seam-petgf-left04-z004-mark2.gcode.3mf)
- [Editable one-time project](2026-10-13-industrial-base-rear-seam-petgf-left04-z004-mark2.3mf)
- [Source, retained meshes and exception scope](2026-10-13-industrial-base-rear-seam-petgf-left04-z004-mark2.print.json)
- [Measured emitted seam starts](seam-starts.json)
- [Launch receipt](launch.json)
- [Preflight printer observations](preflight.json)
- [Fresh startup observation](startup.json)
- [Manual preparation script](prepare.py)
