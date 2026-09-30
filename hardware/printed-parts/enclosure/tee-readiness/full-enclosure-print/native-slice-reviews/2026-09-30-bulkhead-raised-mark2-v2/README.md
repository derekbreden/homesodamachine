# Face-up raised TAP and FLAVOR collars on Mark2

Mark2 accepted task **1295298484** at 2026-09-30T05:41:53.694673+00:00.
The native estimate is **26 min 37 sec**, **8.25 g** at the saved profile density.
The set contains one white TAP collar with black letters and two black FLAVOR
collars with white letters.

All three print face up with **0.48 mm raised lettering**, without supports.
The existing 2.0 mm fitting seat, outlines and bores are unchanged. Lettering
clears the fitting flanges by at least 1.20 mm in CAD. Layers are 0.20 mm first,
0.24 mm normal, with a 0.12 mm closing layer at the fitting face and two full
0.24 mm letter layers above it. Saved PET-GF speeds, wall order and 15% overlap
apply; Mark2 retains its +0.04 mm trim and ordinary startup settings.

The native extruder offset applies **X −0.50 mm, Y +0.70 mm** to white-nozzle
paths, including TAP's body. Black paths and nominal CAD remain aligned to
their original coordinates. The [registration comparison](registration-verification.json)
checks every object/tool/layer against an uncorrected native slice, with
unchanged nominal mesh members and no other effective setting changes.
[Verification](verification.json) confirms the raised-word tools, final layer
planes, archive checksums, source hashes and zero support paths.

The [nameplate appearance record](../2026-09-29-nameplate-flat-wings-mark2-v3/physical-result.json)
supports this process choice; the
[nameplate fit record](../2026-09-29-nameplate-y030-receiver-mark2-v7/physical-result.json)
is accepted for now. The [physical result](physical-result.json) records accepted collar finish and
excellent, clear lettering. Mounting fit was not separately reported. [Launch](launch.json) records the two external PET-GF spools,
Auto nozzle-offset startup option and spacing after H2C's prior job.
