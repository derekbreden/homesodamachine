# Mark1 right reservoir and cap: glued Engineering Plate

Mark1 task **1374272357** is printing the **right reservoir and matching cap**
through the **right 0.8 mm Standard** nozzle on the glued **Engineering Plate**.
One Studio Send was acknowledged **SUCCESS** at **11:39:30 CDT / 16:39:30 UTC,
October 25, 2026**. Fresh startup status confirms **RUNNING, layer 0/833**,
print error 0 and no HMS. Changing live frames show the flat plate during
startup; model adhesion and water holding are unassessed.
[Launch receipt](launch.json) · [Startup](startup.json) · [Preflight](preflight.json).

The preceding **Textured PEI task 1372664582** has [reported persistent lifting](../2026-10-25-mark1-right-flow105-overlap30-temp260-right08-z000/physical-result/physical-result.json).
Derek supplied two photographs and says the lifting seemed worse. Fresh
retained status reports **FAILED**, print error 0 and no HMS. Its reported
layer has reset to 0, so it does not establish the stop or lift-onset layer.
The earlier left reservoirs' positive water holds remain recorded against
those articles in [water-hold-acceptance.json](../../water-hold-acceptance.json).

## Plate and Z offset

The prior submitted G-code clears the trim with **`G29.1 Z0`** and applies
**`G29.1 Z-0.02`**, Bambu's stock Textured PEI compensation. It has **zero added
user Z trim**. The Engineering Plate native slice emits **`G29.1 Z0`** for both
the initial reset and plate compensation: **0.00 mm**, with no added offset.

The global `curr_bed_type` and each plate's `bed_type` select **Engineering
Plate**. Geometry, placement, object identifiers and every other saved process,
filament and machine setting are retained. Both Engineering Plate bed-temperature
fields already specify **70 °C**, matching the preceding print.
[Complete settings](settings.json) · [Exact adaptation](adaptation.json).

Native temperatures, cooling and other nonmotion controls match the preceding
right print except plate-surface detection and **−0.02 → 0.00 mm** compensation.
After excluding `M73` progress reports, **832 of 833 model layers** retain
identical motion/extrusion sequences. Native path variation is limited to
**layer 816, Z195.9 mm**, with the same saved random-seam settings. Native
G-code is preserved without hand edits.
[Command comparison](command-comparison.json).

## Retained recipe and native plate

**255/260 °C** first/subsequent nozzle, **flow 1.05**, **five Arachne walls** at
**10°**, **30% Infill/Wall overlap**, 100% solid zig-zag floor fill, May's three
bottom/three top layers with 0.8 mm minimum top thickness, **0.30/0.24 mm** layers,
nominal **0.8 mm** lines, **70 °C** bed, **21 mm³/s**, May motion/cooling and
Tree(auto)/Default bed-only supports. **No brim, zero added user Z trim,
ironing Off**.

Native source plate 2 contains `reservoir-right` and `reservoir-cap-right`.
It is packaged alone as plate 1 for Studio, preserving every native G-code byte,
checksum and project setting. The native estimate is **5 h 42 min 27 s,
444.21 g and 833 layers**, with no plate warning and at least **70.519 mm**
full-bead bed-edge inset. [Native review](native-review.json) ·
[Packaging and archive hashes](packaging.json).

**A1 PETG R (55%)** is selected before matching **A2–A4 (100%)**, following
Derek's most-depleted-first preference. All four are Bambu PETG Translucent
Clear (`GFG01`, transparent `00000000`). **AMS filament backup On** was freshly
verified in Studio; the Send dialog shows **Engineering** and green Auto Refill.
Startup reports **unit 0 tray 0 (A1)** and the mounted right 0.8 mm nozzle.
A specific backup priority sequence is unverified.

**Timelapse On, Bed Leveling On, Flow Dynamics Auto and Nozzle Offset Calibration
Auto** were visibly verified before the single Send. Runtime timelapse is
disabled during layer-0 preparation; deposition activation is unobserved.
The same idle finished Mark2 task was freshly re-read at final preflight,
establishing at least **222 seconds** of startup spacing, above the required
180 seconds. The Mac restart restored Studio access. [Access record](ui-access.json).
No scheduled monitor was created or reactivated.

Derek followed up:

> The mac restarted. Try now.

Derek authorized:

> So the lifting seemed to have gotten worse on that one. I don't know. Sometimes when I've cleaned the textured plate, it's worked a little better, but we've had persistent lifting here. So I've gone ahead and switched Mark 1 out to the engineering plate and glued it up. And I'd like you to try to start a print of this same reservoir we just tried to print, with all the same settings and everything, just adjusted to use the engineering plate instead. No Z offset. I hope we didn't have a Z offset before. If we did, let me know, because we'd want to fix that first instead. But assuming we didn't have that incorrect on the last print, I've got the flat engineering plate set up for you here on Mark 1 now, glued and ready to go.
