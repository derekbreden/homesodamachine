# Mark1 left reservoir and matching lid: Engineering Plate repeat

The **left reservoir body and its matching lid** are running as **Mark1 task
1375878568**, accepted at **22:03:53 CDT October 25 /03:03:53 UTC October 26**.
They use the fixed **left 0.8 mm Standard** hotend and glued **Engineering Plate**,
starting with **A2**, with automatic refill available to matching A3/A4.
A1 is empty; A2–A4 each report 100%. Use the most depleted matching spool first
when fresh depletion values differ. [Launch](launch.json) · [Preflight](preflight.json) ·
[UI review](ui-review.json) · [Startup observations](startup.json).

The preceding [right reservoir, task 1374963298](../2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-left08-z000/physical-result/physical-result.json)
completed 833/833 layers and has a reported water hold. This print retains its
recipe: **flow 1.05, five Arachne walls at 10°, 30% Infill/Wall overlap,
255/260 °C first/subsequent nozzle, 70/70 °C bed, 0.30/0.24 mm layers,
0.8 mm nominal widths and 21 mm³/s**. The floor and cap use 100% solid zig-zag
fill; May motion/cooling and Tree(auto)/Default bed-only supports are retained.
**No brim, no added Z trim, ironing Off.** Both native trim commands are
**`G29.1 Z0`**, including Engineering Plate compensation: **0.00 mm**.
[Complete frozen recipe](settings.json) · [Adaptation](adaptation.json).

The current body/cap source STEP hashes and all source-project geometry match
the preceding print. The **right lid needs no geometry replacement**, including
its port and float-guide positions. The new plate contains **one left body and
one left lid**. [Geometry and lid decision](geometry-review.json).

The pair is centered on the fixed-left usable bed with a **15 mm X translation**
from the source pair. Orientations and Z are retained, with a **10.042 mm** native
full-bead body/cap gap and minimum **80.519 mm** full-bead bed-edge inset.
Native Studio slicing estimates **5 h 42 min 2 s, 444.28 g, 833 layers**.
Engineering Plate detection, temperatures, left selection, full-bead placement,
ironing Off and embedded checksums are verified. Studio's global default-plate
metadata differs from the selected per-plate Engineering setting; the emitted
header and commands are Engineering. Imported preset labels and printer-resource
metadata differences are recorded in the [native review](native-review.json).
[Exact packaged G-code and hashes](packaging.json).

Send verifies **Mark1, Engineering, A2 PETG L, Auto Refill, Timelapse On,
Bed Leveling On, Flow Dynamics Auto and Nozzle Offset Calibration Auto**.
Fresh startup is RUNNING at layer 0/833, print error 0 and no HMS. Runtime
confirms A2 loaded into the left 0.8 mm nozzle. Two changing live frames show
the clear glued Engineering Plate during preparation. Timelapse is selected
On; runtime activation at deposition is unobserved. Deposition,
adhesion, surface finish and water holding of this new article are unassessed.
No scheduled monitor is created or reactivated.

Derek:

> That print turned out well also and is holding water also. So I'd like to print at least one more reservoir here. I'm not sure whether the one you just printed was left or right, but let's switch back to the other one, whatever the other one would be now. And so give me a new print of that. The Mark 1 is glued and ready to go. And then if the geometry hasn't changed and that last reservoir lid that we printed is good as far as the locations on everything and the current geometry, then great. I don't need anything else. But if we need to reprint that last lid to match the current geometry, then include that last lid on this new plate also. Do you follow me? Let me know.

> You're printing both a lid and a body, right?

> The only thing that was optional was whether you were printing two lids or not.
