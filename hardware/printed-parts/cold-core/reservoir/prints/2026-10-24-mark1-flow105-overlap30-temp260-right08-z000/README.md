# Mark1 reservoir: temperature-only 255/260 °C trial

Mark1 task **1371867808** completed the full-height **left reservoir and matching
cap** through the **right 0.8 mm Standard** hotend. Fresh status before the next
launch confirms **FINISH 833/833**, print error 0 and no HMS. On October 25,
Derek reports that it turned out well so far and is **holding water** alongside
the older reservoir, which is still holding water. Hold duration and water head
are unspecified. [Physical result](physical-result/physical-result.json) ·
[Terminal status](terminal-observation.json).

The printer acknowledged one Studio Send with **SUCCESS** at **16:59:19 CDT /
21:59:19 UTC, October 24, 2026**. [Launch receipt](launch.json) ·
[Startup observations](startup.json).

This trial uses **255 °C first layer / 260 °C subsequent layers**, retaining
**flow 1.05, five requested Arachne walls, 30% Infill/Wall overlap**, 100% solid
zig-zag floor fill, 0.30/0.24 mm first/subsequent layers, 0.8 mm nominal lines,
70 °C bed, 21 mm³/s and May motion/cooling. Arachne retains its **10°** threshold.
**No brim, zero added user Z trim and ironing Off**; stock Textured PEI
compensation is **`G29.1 Z-0.02`**.
[Complete frozen settings](settings.json) · [Exact changes](adaptation.json).

The comparison baseline is the [task-1365626370 printed portion](../2026-10-22-mark1-flow105-overlap30-right08-z000/physical-result/physical-result.json),
which Derek reports held water for one hour at 265/270 °C. He has aesthetic
concerns with that article and selected the previous nozzle temperatures for
this trial. Its [native comparison](native-review.json) checks **1,350,143
executable commands** against the baseline: **12 temperature-related commands
differ; every other command is identical**, including motion, extrusion,
cooling and supports. The only saved-setting changes are the two temperature
fields and the filament preset's temperature label. The native estimate is
**5 h 42 min, 444.28 g and 833 layers**; full deposited beads retain at least
**70.519 mm** of bed-edge inset. Derek's water-hold report is positive physical
evidence for this article; specific surface defects and corner flatness are
not separately assessed.

**A1 PETG R** is visibly selected in Studio's Send dialog. AMS A unit 0 trays
0–3 carry matching Bambu PETG Translucent Clear (`GFG01`, transparent `00000000`),
all reporting **100%**. A1 breaks the depletion tie. **AMS filament backup is
On**, and Studio's right-side Auto Refill group contains **A1–A4**. No specific
backup priority order is established. Use the most depleted suitable spool
first when readings differ, and use each spool fully.
[Preflight and Send selections](preflight.json).

**Timelapse On, Auto Bed Leveling On, Flow Dynamics Calibration Auto and Nozzle
Offset Calibration Auto** were visibly verified before sending. The same
Mark2 job was freshly read at final preflight, providing a shared-circuit
startup-spacing lower bound of **475 seconds**,
above the required 180 seconds. Mark2 was left running.

The [print-only archive](packaging.json) contains only the left body/cap plate
and preserves the native G-code byte for byte. The printer reports
**`Flavor_reservoirs_-_PETG_0.24_mm`**, the normalized native project title.
The visible archive, its hash, the SUCCESS acknowledgment and the new task ID
bind that name to this trial. No scheduled monitor was created or reactivated.
Runtime material loading and timelapse at model deposition are distinct from
these selected Send options; see startup.json for the observed stage.

Derek requested the [right pair with these same settings](../2026-10-25-mark1-right-flow105-overlap30-temp260-right08-z000/README.md):

> That turned out well so far. It is holding water along with its older sibling that is still holding water. Please print me the other side (left or right) from what you just printed, same settings, mark1 bed is clear.

Derek authorized this left print:

> Mark One is available now and loaded up with an AMS 2 Pro with four spools of Translucent PETG connected to that right hot end for the 0.8 millimeter there. So please go ahead and start our next print on Mark One. Thanks.
