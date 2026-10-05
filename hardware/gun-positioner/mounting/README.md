# Fixed controller mounts

Print one [300 mm backplane](controller-backplane.stl), 28
[6 mm M3 spacers](m3-insulating-spacer-6mm.stl) and one
[80 mm fan stand](fan-stand-80mm.stl). Editable STEP models and viewer payloads
sit beside those files. The [manifest](manifest.json) specifies quantities,
hardware, orientation, print settings and fitting checks; the
[source receipt](source-receipt.json) binds the exports to the generator and
the recorded H2C bed profile. These parts carry the fixed controller only.

Use the owned **SunTop unfilled clear PETG B0FP34MJ94** reservoir-candidate
stock listed in the [inventory](../../ledger/inventory.md). Use its matching
filament preset and drying procedure, a 0.4 mm nozzle, 0.20 mm first layer,
0.24 mm layers, four walls, six top/bottom layers, 40% gyroid for the panel/stand
and solid spacers. Put the panel's broad face and each spacer's annular end on
the bed. The fan-stand STL already puts its rear wall on the bed, with its
airflow bore vertical. Inspect each part's own slice; these orientations need
no supports. No print has been launched or physically accepted.

The recorded H2C profile has a 330 × 320 mm area. The weld-rotator generator
uses a conservative **325 × 320 mm left-nozzle envelope**. The 300 mm blank
plus a 5 mm brim measures 310 × 310 mm and fits that envelope. Print the
blank separately, with its brim inside the bed; do not import another part's
support settings. Check the cooled panel flat before drilling or mounting.

Mount with this additional controller allocation:

| Joint | Bolts | Nuts | Flat washers |
|---|---|---|---|
| Six carriers, four points each | 24 M3×25 | 24 M3 locking | 48 M3 |
| Pico terminal adapter | 4 M3×25 | 4 M3 locking | 8 M3 |
| DIN rail | 2 M3×25 | 2 M3 locking | 4 M3 |
| Six-way fuse block | 4 M3×25 | 4 M3 locking | 8 M3 |
| Fan-stand base | 2 M3×25 | 2 M3 locking | 4 M3 |
| Fan frame and two guards | 4 M4×50 | 4 M4 locking | 8 M4 |
| Backplane to fixed 4040 | 4 M6×16 | 4 slot-8 M6 T-nuts | 4 M6 |

The complete allowance is **36 M3×25 / 36 M3 locknuts / 72 M3 washers**,
**4 M4×50 / 4 M4 locknuts / 8 M4 washers**, and **4 M6×16 / 4 M6 T-nuts /
4 M6 washers**. Two fan guards come from the sourced six-pack. Four insulating
spacers serve each carrier and four serve the Pico adapter: 28 total.

Keep USB and 24 V unplugged for mounting. Transfer actual module/socket,
board, rail and fuse-block footprints before drilling the blank. Start with
two columns of three carriers, one UART group per column; lay the Pico, fuse
block and clipped buck/relay beside them. Use only the selected terminal
blocks that fit the sourced 203.2 mm DIN rail with the buck, relay and end
stops; start with at most nine blocks. Motor feeds/returns already have the
fuse block and carrier terminals. Confirm the received footprints fit with
meter, fuse and plug access before drilling.

Drill component holes 3.4 mm, and the four fixed-frame holes 6.5 mm with at
least 12 mm panel edge distance. Place carrier/Pico mounting holes on clear
lands; preserve copper isolation. The 6 mm spacers set the PCB-to-panel
standoff. Every actual solder pin and joint must remain visibly clear of the
panel and all mounting metal. Trim only excess leads with USB and 24 V
unplugged, then inspect and verify continuity/isolation before power.
Never drill a populated module or cut an unmapped carrier trace. Meter every
mounted carrier again using the control guide's VM/VIO/STEP/DIR/ground
isolation checks. The nominal PCB/spacer/panel/two-washer/nut stack is
18.6 mm, leaving 6.4 mm with M3×25; inspect the actual stack and leave two
full threads beyond the nut. Tighten the fixed mounts only enough to seat
them without bending the boards or crushing spacers.

The stand has a 76 mm airflow opening, centered 45 mm above its installed
base. Center the received 80 mm fan, transfer its four holes and drill 4.5 mm
only where they leave sound wall outside the opening. Fit a guard on **each
open face**, with four M4×50 bolts through both guards, fan and 4 mm stand.
Check actual thickness, two full threads beyond each nut, free blade
rotation and wire clearance. Base holes are 3.4 mm at X=±32, Y=20 mm;
transfer those two holes to the blank. Aim the fan along both columns of
driver heatsinks and verify real airflow. Driver/motor surface temperatures
must pass the commissioning upper-bound **50°C** gate with these mounts and
both guards installed.

Attach the blank to fixed 4040 outside all motion/optics/catch envelopes,
using four M6×16 / slot-8 T-nut points. Keep this board horizontal with the
fan stand's base on it; the fan blows along the board. Confirm the actual
slot stack seats without bottoming and that no movable cable can load a
board, solder joint or socket. Firm mounting, cold isolation, retained wire
routes and the actual thermal trial accept the installation; mesh validity
does not establish those physical results.

Regenerate from the repository root:

```text
tools/cad-venv/bin/python hardware/gun-positioner/mounting/generate.py
```
