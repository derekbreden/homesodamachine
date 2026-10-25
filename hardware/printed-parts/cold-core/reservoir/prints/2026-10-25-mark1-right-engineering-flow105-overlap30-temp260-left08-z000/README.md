# Mark1 right reservoir and cap: left 0.8 mm Engineering Plate retry

The **right reservoir and matching cap** are **prepared, not sent**, for
Mark1's **left 0.8 mm Standard** hotend on the cleaned, glued **Engineering
Plate**. Studio Preview verifies the right model pair, Engineering Plate and
PETG assigned only to the left nozzle. Send verifies **A1 PETG L** and green
Auto Refill, but is disabled: the printer still reports **left 0.4 mm**.
Studio's Printer Parts controls are read-only and do not expose a left
refresh button. The **Read All** rack read completes without updating the
fixed left nozzle. A separate native **`refresh_nozzle`** request is rejected
with **“mqtt message verify failed”**; Studio reports a command-verification
warning. No software diameter override is sent, and no print is started.

The remaining read is on Mark1's touchscreen: **Settings → Nozzle & Extruder
→ Read Left Nozzle Info**. This automatically identifies the left hotend;
manual entry of 0.8 mm is not required. [Read result and manufacturer procedure](nozzle-read.json) ·
[UI review](ui-review.json) · [Preflight](preflight.json).

The preceding right-hotend **task 1374272357** has [reported polymer buildup and a motion-step-loss warning](../2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-right08-z000/physical-result/physical-result.json).
Four photographs show the warning **0300-800c 015526**, partial body/cap
footprints, loose strands and buildup around the right nozzle/hotend region.
Fresh retained status is **FAILED**, print error 0 and no HMS. The layer
field has reset to 0 and does not establish the stop, fault or lift-onset
layer. The photographs do not establish whether buildup, contact, lifting
or motion loss came first, or whether the right hotend has a general defect.
Earlier water-hold acceptance remains scoped to its tested articles.

## Retained recipe

**Flow 1.05**, **five Arachne walls at 10°**, **30% Infill/Wall overlap**,
**255/260 °C** first/subsequent nozzle, **70/70 °C** bed, **0.30/0.24 mm**
layers, nominal **0.8 mm** widths, **21 mm³/s**, 100% solid zig-zag floor/cap
fill, May three-bottom/three-top shells with 0.8 mm minimum top thickness,
May motion/cooling and Tree(auto)/Default bed-only supports.
**No brim, zero added Z trim, ironing Off**.

The Engineering Plate native G-code clears trim with **`G29.1 Z0`** and
applies **`G29.1 Z0`**: effective **0.00 mm**, with no added offset.
The complete frozen recipe differs only in `filament_map` **2 → 1**,
`filament_nozzle_map` **1 → 0** and both plates' `filament_maps` **2 → 1**.
The existing machine profile already defines both nozzles as 0.8 mm Standard.
Geometry and placement are unchanged. Native startup selects the left
hotend; no G-code is hand-edited. [Settings](settings.json) · [Adaptation](adaptation.json).

Native source plate 2 is packaged alone as plate 1 for Studio, retaining all
native G-code bytes and checksums. It estimates **5 h 42 min 27 s, 444.21 g,
833 layers**, with no plate warning. The complete model/support bead envelope
is at least **65.519 mm** inside the left nozzle's usable boundary.
[Native review](native-review.json) · [Archive and hashes](packaging.json).

**A1 (42%)** is selected before matching **A2–A4 (100%)**, following Derek's
most-depleted-first preference. All are Bambu PETG Translucent Clear, GFG01,
transparent 00000000. AMS unit 0 trays 0–3 address A1–A4.
**AMS filament backup is On**. Automatic backup priority order is unverified.
Final calibration selections, shared-circuit spacing, Send and startup remain
pending. No scheduled monitor is created or reactivated. Adhesion, nozzle
performance and water holding are untested for this left-hotend trial.

Derek authorized:

> I'm not sure exactly what went wrong there, but the nozzle clearly got pretty gunked up, wiped onto itself. We really hadn't been using the right hot end for PETG 0.8 very much, so I wonder if it just maybe doesn't work very well. So I've switched Mark 1 over to 0.8 left hot end. The AMS 2 with all the transparent filament is connected to that left hot end on Mark 1 now. I've still got the engineering plate there, and I've cleaned it and glued it up again. So I'd like you to try again on the left hot end on Mark 1 now. Thanks.
