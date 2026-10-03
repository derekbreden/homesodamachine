# ASA Aero float installation

The carbonator and both flavor reservoirs use the same one-piece ASA Aero
float: **[36 × 28 mm](FLOAT_SIZE)**, **[4.8 mm](FLOAT_BORE)** open guide bore,
and an RC62 center **[14 mm](MAGNET_CENTER)** above its bottom. Each
**[3.175 mm](ROD_DIAMETER)** rod stands **[20 mm](WALL_DATUM)** from the inside
wall. The guide-axis distance is a drilling datum. The reed-distance limit is
**[18 mm](FLOAT_REED_DESIGN_MAX) from the nearest float edge to the reed center**,
including upright guide play. Liquid switching heights need calibration.

## Rod and drilling datums

| Location | Datum and dimension |
| --- | --- |
| Carbonator, both end caps | Register center **(0, −[41.849 mm](CARB_RADIUS))** from the disc center, along the −Y axis perpendicular to the two-port line |
| Same carbonator position, inches | **(0, −[1.6476 in](CARB_RADIUS_IN))**; radius equals half the 4.870 in tube ID minus 20 mm |
| Carbonator register drill | 9/64 in (3.5719 mm), blind **0.100 in (2.54 mm) to drill tip**, on the inside face; 0.150 in (3.81 mm) of plate remains |
| Reservoir body and matching cap | Rod axis **(x = ±[106.25 mm](RES_X), y = +[32.5 mm](RES_Y))** in the assembled cold-core frame; sign selects the mirrored reservoir |
| Reservoir local datum | Rod axis is 20 mm inward from its wet far wall, x = ±126.25 mm; body and cap registers share this axis |
| Carbonator rod blank | **[131.08 mm](CARB_ROD_LENGTH)** starting length; hand-fit the actual conical register pair before tacking, with positive top engagement and fully seated plates |
| Reservoir rod cut | **[176.515 mm](RES_ROD_LENGTH)**, with **[0.15 mm](RES_ROD_CLEARANCE)** axial clearance |

Use the [end-cap drawing](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole-drawing.pdf)
and [pressure-vessel procedure](/hardware/assembly/pressure-vessel.md) for
fabrication. The laser-cut file contains the disc and two port holes; the rod
register is the separate blind drilling operation. The inside-wall datum uses
the tube bore, not the end-cap disc edge. On the 4.860 in disc the register is
19.873 mm inward from that edge. Clock both registers onto the same rod axis.

The reservoirs' lower and upper bosses are already modeled at their matching
positions in [`reservoir.py`](../../reservoir/reservoir.py). Print the current
body/cap pair; a native project must bind the current STEP and archive hashes before
submission. A saved project alone does not establish that its guide has moved.

## Running room and magnetic path

The 4.8 mm bore gives **[0.8125 mm](GUIDE_SLOP)** radial motion on the 3.175 mm
rod. Nominal body-to-wall clearance is **[2 mm](WALL_CLEARANCE)**, with an upright
CAD range of **[1.1875–2.8125 mm](WALL_CLEARANCE_RANGE)**. Foam expansion,
rod alignment, tilt and finished sliding are physical checks.

| Vessel | Greatest float-edge to reed-center distance | Greatest RC62-edge to reed-center distance |
| --- | --- | --- |
| Carbonator, reed against the bare tube | **[5.713 mm](CARB_FLOAT_REED_PATH)** | [14.188 mm](CARB_REED_PATH) |
| Reservoir, reed in the foam-shell channel | **[11.062 mm](RES_FLOAT_REED_PATH)** | [19.538 mm](RES_REED_PATH) |

Both distance columns include the float's maximum upright retreat through the
bore. The RC62 edge is 8.475 mm inside the float perimeter. The 20 mm
guide-axis-to-inside-wall datum is neither of these reed distances.

The [printed-float bench report](physical-observations.json) gives a usable
float-edge-to-reed-center limit of **[20 mm](FLOAT_REED_REPORTED_LIMIT)**,
intermittent response at 21–24 mm and consistently absent response at 25 mm.
The provisional 18 mm design maximum keeps below that reported limit. Both
installed layouts meet it; the rod/drill coordinates above retain running room.
The reported reed identity and wall/fixture conditions are unspecified, so the
report does not establish installed directional switching or all-reed acceptance.
Use vertical reeds parallel to the guide and the actual MDSR-7-10-15 stock.
The CAD capture envelope remains 14 × 2.5 mm for glass, tape and leads; the
manufacturer gives 12.7 mm glass length.

## Vertical datums

All carbonator Z values below are measured upward from the **bottom tube rim**.
Reservoir Z values are in the **assembled cold-core frame**, as in the reservoir
CAD; use the assembly datum rather than the local underside of a loose printed cap.

| Quantity | Current design datum |
| --- | --- |
| Carbonator target liquid levels, pump-on / pump-off | **[67.098 / 95.250 mm](CARB_WATER_LEVELS)** |
| Carbonator provisional reed centers, CLO / CHI | **[58.332 / 86.484 mm](CARB_REED_CENTERS)** |
| Carbonator magnet-center mechanical travel | **[28.200–125.700 mm](CARB_TRAVEL)** |
| Reservoir magnet-center mechanical travel | **[52.485–188.150 mm](RES_TRAVEL)** |
| Reservoir four provisional reed centers | **[52.817, 97.817, 142.817, 187.817 mm](RES_REED_CENTERS)** |
| Reservoir provisional reed pitch | **[45 mm](RES_REED_PITCH)** |

The carbonator target water-level difference displaces one 338.1 mL water
serving. Its provisional reed centers assume 0.65 g/cm³ foam, a dry pocket,
0.9997 g/cm³ water, and closure at the magnet midplane. That model puts the
magnet **[8.766 mm](MAGNET_SUBMERGENCE)** below the surface. The actual float
mass, syrup density and reed's directional activation lobes change the offset.
The reservoir centers distribute four reeds over accessible travel; they are
not measured quarter-volume marks or calibrated full/empty thresholds.

Reed closures are pulses as the float passes the sensors. The reservoir
firmware retains the last crossing and flow direction between reeds; it does
not count simultaneously closed reeds as liquid volume. Carbonator low and
high windows may overlap. A valid high signal stops/inhibits refill, including
when low also remains closed; a latched refill timeout still needs a clear.

## Reed calibration

**Decision:** set the final reed heights before soldering fixed columns or
printing a bridge intended to establish operating levels. The rod/drill XY
datums above do not depend on this measurement. A short finished-float test
answers the missing question; another long-range magnet bench survey does not.

Use the finished, cooled float, its 1/8 in rod, the existing reeds, a ruler or
calipers, a multimeter in continuity mode, tape/clips, a kitchen measuring cup and plain water. Use the
actual flavoring for the reservoir check. Use the actual vessel wall and reed
mounting position when measuring switch crossings. No new tool is required.

1. Hold the rod vertical and move the float through its usable travel. Include
   motion toward and away from the wall within its bore clearance. It must slide
   freely without wall rubbing, hanging on a boss or catching near a stop.
2. Float it on water and record the liquid surface height and float-bottom
   height from the same datum. Magnet center = bottom + 14 mm. Record center
   minus surface, with its sign. Repeat in the actual flavoring; bubbles must
   clear before reading. Dry mass is useful to check the buoyancy calculation,
   but the direct waterline measurement is sufficient to position the reeds.
3. Tape a vertical reed at its installed radial position. Use the finished
   float's magnet. Sweep the float slowly upward and downward past it, recording
   **every** closure and release height relative to the glass center. Include
   any separate activation lobes. Repeat three times at nominal position and
   with the float at its greatest permitted retreat from the reed. Test the
   intended low/full reeds, not just a spare whose sensitivity may differ.
4. For each control threshold, use the closure encountered in the operating
   direction: rising for pump-off/full, falling for pump-on/empty. If `a` is
   measured magnet-center minus surface, and `d` is magnet-center minus
   reed-center at that directional closure, then **reed center = target liquid
   height + a − d**. Record the release boundary too. Keep the two carbonator
   liquid targets in the table; the glass centers move to achieve them.
5. Confirm the resulting crossings with liquid in the intended vessel. Rising
   must reach the full/pump-off crossing before the mechanical top stop, and
   falling must reach the low/empty crossing before the bottom stop. The
   reservoir's usable full and empty liquid volumes are defined by those
   accessible crossings; locate the two intermediate reeds at measured volume
   fractions. Preserve four reeds and the existing channel/wire exit.

**Acceptance for height placement:** all three cycles give the intended low/high
order and usable directional crossings at nominal and maximum retreat. The
spread of repeated carbonator liquid crossing heights is at most 2 mm:
12.01 mL/mm makes that 24.02 mL, below 10% of its 338.1 mL refill serving.
For reservoir crossings, use the same 2 mm placement repeatability criterion
and record the corresponding liquid volumes. The gauge's quarter steps are
calibrated from those volumes, not assumed from evenly spaced height marks.
No missed closure or unintended additional pump-trigger crossing is acceptable
in the working range. Overlap is allowed when the high input safely inhibits
refill. Record results in [`reed-calibration.json`](reed-calibration.json).

This establishes guided motion and operating signal placement. Pressure life,
liquid uptake and flavor compatibility are recorded separately with the article.
The 36 mm float cannot pass the carbonator's NPT ports: it is captured before
final end-cap closure. Welding exposure of the ASA body and RC62, and their
post-closure function, have no acceptance record.

## Source

Dimensions and geometry checks: [`integration.py`](integration.py),
[`integration-check.json`](integration-check.json), and shared
[`_float_interface.py`](../../_float_interface.py).
[Littelfuse activation guidance](https://www.littelfuse.com/assetdocs/reed-switch-and-reed-sensor-activation-application-note?assetguid=fa9045a4-e577-4f55-9e9b-4232faacffd9)
distinguishes closure, hold and release regions and the effects of magnet/reed
orientation. The [selection guide](https://www.littelfuse.com/assetdocs/reed-switch-selection-guide?assetguid=91cf50d6-a742-4b6d-9795-b99177e45b72)
gives the MDSR-7 glass length. These sources do not supply this installation's
measured switching heights.

[value](NAME) figures are updated by `integration.py` from the CAD sources.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/magnetic-float/all-aero/integration.py`
