# Mark1 right reservoir and cap: glued Engineering Plate

The **right reservoir and matching cap** are **prepared, not sent** for Mark1's
**right 0.8 mm Standard** nozzle. Derek reports the flat **Engineering Plate**
is installed, glued, clear and ready. Bambu Studio access is blocked by the
locked Mac; manual unlock is requested. Final Send selections and startup
verification remain pending. [UI access](ui-access.json) · [Preflight](preflight.json).

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

**A1 (55%)** is the intended first spool before matching **A2–A4 (100%)**,
following Derek's depletion preference. All four are Bambu PETG Translucent
Clear (`GFG01`, transparent `00000000`). Automatic refill and the standing
Timelapse On, Bed Leveling On, Flow Dynamics Auto and Nozzle Offset Calibration
Auto selections require final Studio verification. Mark2's same idle finished
job is to be re-read before Send for the required 180-second startup spacing.
No scheduled monitor is created or reactivated. Adhesion and water holding
on Engineering Plate are unassessed.

Derek authorized:

> So the lifting seemed to have gotten worse on that one. I don't know. Sometimes when I've cleaned the textured plate, it's worked a little better, but we've had persistent lifting here. So I've gone ahead and switched Mark 1 out to the engineering plate and glued it up. And I'd like you to try to start a print of this same reservoir we just tried to print, with all the same settings and everything, just adjusted to use the engineering plate instead. No Z offset. I hope we didn't have a Z offset before. If we did, let me know, because we'd want to fix that first instead. But assuming we didn't have that incorrect on the last print, I've got the flat engineering plate set up for you here on Mark 1 now, glued and ready to go.
