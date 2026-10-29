# TPU elbow 0.4 mm departure lap — Mark1

**Status: stopped; threads persist, with a possible small reduction in thickness.** The
[launch receipt](launch.json) records RUNNING without errors at startup on
2026-10-16 at 00:10:38 CDT. The [startup spacing record](startup-spacing.json)
identifies Mark2’s continuing job and the interval before acceptance.
Two compact elbows use black
Bambu TPU 85A, Mark1's right fixed 0.6 mm hotend and the glued Engineering Plate.
Derek confirms the plate is glued, clear and ready. The useful outcome is fewer
strands across the bores and between objects, with sufficient physical clearance
and no added rim damage. The [physical record](physical-result.json) records
Derek’s report of persistent threads with a possible small improvement.
No printed clearance or finished-part acceptance is established.

## Movement and material

The [editable project](2026-10-16-elbow-pair-tpu85a-lap040-normal-right06-z000-mark1.3mf)
sets both machine and filament overrides to **0.4 mm, Normal Lift**. Each object
departure retracts standing still, rises vertically 0.4 mm above the printed
layer, reaches the selected wall loop, makes one nonextruding lap at 10 mm/s,
and returns to the native departure XY at the same height. Native travel then
continues. There are 368 laps across 184 layers.

The [command review](emitted-command-review.json) confirms all 368 laps begin
with a vertical 0.4 mm lift, every inserted XY move stays at that clearance,
and no lap extrudes. All 2,991 native rises within object blocks are vertical
0.4 mm hops, with no combined XY/Z rises. The nominal deposited layer is the
height reference; commanded clearance does not establish clearance above
curled material in the physical print.

The geometry, orientation and placement are byte-identical to the
[0.2 mm trial](../2026-10-15-departure-lap-tpu85a-mark1/README.md), whose
[physical observation](../2026-10-15-departure-lap-tpu85a-mark1/physical-result.json)
reports no benefit and insufficient apparent clearance. The existing pair's
2.708 mm brim separation and 135.695 mm bed inset retain their scope.

The recipe uses 225°C nozzle / 35°C plate, zero local user Z trim, 0.20 mm first
and 0.12 mm normal layers, six walls, 100% zigzag infill, a 5 mm outer brim and
supports off. Flow ratio is 1.00, maximum flow 2.2 mm³/s, and retraction is 1 mm
at 10 mm/s. Requested outer and relevant overhang speeds are 10 mm/s; inner
walls are 25 mm/s. Part and auxiliary cooling are 100%. Nearest seams,
wall-crossing avoidance and native wipe off are retained.

The [native readback](native-readback.json) records the complete setting
differences against the 0.2 mm trial. Native extrusion coordinates match that
trial; 2,946 emitted feed segments differ by −0.0167 mm/s. Post-processing
preserves all 3,958 extrusion runs' coordinates and speeds and all 124,015
E-command states from this native slice. Only the G-code and its MD5 ZIP
members change. The [lap record](lap-review.json) binds each route to the exact
archive. It selects 350 inner-wall loops, ten outer-wall loops on thin rims,
and eight contours within deposited terminal beads.

## Files and estimate

The [native slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-16-departure-lap040-normal-lift-tpu85a-mark1/2026-10-16-elbow-pair-tpu85a-lap040-normal-right06-z000-mark1-native.gcode.3mf)
estimates 121 minutes / 8.57 g. The laps add approximately 32 minutes of
commanded motion, giving a planning estimate of **about 2 hours 33 minutes**
before acceleration overhead. Native thumbnails and displayed time estimates
exclude the added laps.

The [processed archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-16-departure-lap040-normal-lift-tpu85a-mark1/2026-10-16-elbow-pair-tpu85a-lap040-normal-right06-z000-mark1.gcode.3mf)
is the print file. `prepare_mark1.py` slices offline and calls
[`departure_lap.py`](../../departure_lap.py) with `height=.4`; it does not send
or alter global presets. Reslicing the editable project alone omits the lap.
Submission uses an untouched separate copy in Bambu Connect, with Timelapse On,
Bed Leveling On, Flow Calibration Auto and Nozzle Offset Auto.

The Siraya single's exterior acceptance and the rough Bambu article's manual
fit acceptance retain their separate scopes. This trial has no finished-part,
pressure, retention or lifetime qualification.
