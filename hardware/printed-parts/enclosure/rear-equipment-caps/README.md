# Rear equipment caps

Four PET-GF caps close the integral seats on back-top. Their geometry and the
seats share [rear_snaps.py](../../../manifold-layout/rear_snaps.py) and
[rear_plumbing.py](../../../manifold-layout/rear_plumbing.py).

The ASSE cap holds the lower halves of both ASSE hexes and captures both
axial shoulders of the inlet adapter's hex. Its solid lower body extends to
Y461.078, while its springs retain Y396.453–438.114. The adapter pocket follows
the captured profile and wrench clocking with 0.15 mm radial and axial air.
Within the hex band, its two lowest corners sit 0.25 mm deeper in one six-flat
pocket; the top flats and both axial shoulder stations retain their positions.
The downward vent cup passes through the bottom flat. The Pisco
cap has a raised lip around the short outlet fitting's neck and a broad body
bearing between its independent leaves. It spans 41.704 mm in Y, ending at
Y462.05 before a full 3 mm receiver end wall and the rear CO2 bulkhead bore.
The meter cap enters from the west
and has a solid 9 mm spine, shaped bearing stock extending toward the housing,
and two complete 38 mm-long leaves. A 6 mm lower outside corner bevel clears
the A-fill tube while retaining the 9 mm central spine, full fitted bearing
and spring-root geometry. Its flexible
leads turn west against the housing above the lower leaf. The water regulator
cap spans 36 mm of the housing and smaller outlet neck, with its lowest face
at Z315.924 mm. Each cap is one solid, with two integral spring walls and hooks.

The ASSE seat uses 0.25 mm running clearance. Its cap has one continuous
hex cavity with a 14.6 mm apothem at the two wrench flats' mean clocking.
The common envelope includes at least 0.15 mm slip clearance around both hexes. The ASSE seat allows 1.5 mm of threaded-joint position variation.
The drain-sleeve window carries that full fore/aft adjustment and ends at
Z309.4 above the sleeve's measured upper exterior.
The Pisco cap follows the scanned body and exposed neck with 0.15 mm radial
and 0.25 mm axial air. The receiver has a 3 mm-wide upper ring bearing at
Y438.125–441.125 with 0.15 mm radial air; its loading corridor retains 0.5 mm.
The neck lip excludes the release collet. The meter's cap and receiver follow
the housing taper, flange and label-side bevel with 0.15 mm radial and axial
air. Bosses and screw heads have separate fitted passages; the receiver's
fore corridor admits the complete 16 mm insertion slide. Its spring station,
wire exit and lower outside bevel retain their positions. The water
regulator uses its measured linear radius profile and true installed axis,
with 0.30 mm receiver radial air, 0.25 mm cap radial air and 0.25 mm axial air.
Its body-to-outlet shoulder retains the scanned position. The central cap
bearing ends 1 mm short of the spring ends beside the outlet release collet.
The PISCO, water-regulator and flow-meter hardware fits are physically approved;
their pointed wing tips remain for the [pointed snap trial](../../../print-tests/pointed-snaps/README.md).
All leaves are 2.0 mm thick, with a 1.5 mm inside root radius and 22.25 mm
root-to-catch length; the water regulator uses 21.25 mm within its retained
height. The straight wall above the root blend is 20.75 mm, or 19.75 mm on
the water regulator. The insertion face has a
3 mm-rise single planar lead-in ending at a pointed free edge, above a 1.6 mm
solid nose land. The matching receiver ceiling clears the complete point by
0.5 mm. The blade entry leaves
0.6 mm of solid nose above it. The retaining face is
flat with 2.6 mm overlap outside each centered 5 mm-wide by 1 mm-high flathead
entry. The nominal catch clearance is 0.4 mm.
ASSE, Pisco and meter enter their seats 16 mm forward and slide aft. The
regulator enters directly upward. The caps close after their bodies seat.

Fit the meter cap before the ASSE cap, with back-top ceiling-down on the
bench and separated from the cold core. Load the meter cap 20 mm west and
40 mm fore of its station, slide aft, then press east into its catches.
For removal, disconnect and dress the tubes and leads aside, remove the
ASSE cap, spread the meter leaves and withdraw 20 mm west. Relax the leaves
and move the cap 40 mm fore. Opening the meter's lower leaf requires the
cold core to be absent.

Remove the Pisco cap after the meter and ASSE caps. Spread its leaves,
lower it 3.6 mm, depress the exposed outlet collet and withdraw the stem check.
Then slide the cap 45 mm fore with the leaves held open. The dropped cap clears
up to 2 mm of modeled collet movement toward the body; the mechanism's required
release travel and operating force need the physical trial. The fore flank
exits end at the hook-bearing plane; the solid stops above that plane
retain the installed cap. Its receiver has full 3 mm side walls. Fit it by
reversing this path.

The standalone STEP and STL files use the print frame, with one axial end
on Z0 and spring bending within the layer plane. The appliance uses their installed frames.
Use the shared PET-GF Tree(auto)/Default support policy. These fits describe
the modeled assembly; snap force and fatigue remain physical properties.

Remove the small cavity supports with a tiny flathead screwdriver that fits
inside the opening. Derek reports that the original trial's small automatic
cavity supports removed easily with that tool. Preserve the flat catch
undersides while clearing them. The [physical record](../../../print-tests/rear-snap-retention/physical-result/physical-result.json)
records this removal result and the hardware fit observations.

For release, put a flat blade no wider than 5 mm and no thicker than 1 mm into
the centered notch beneath each hook. Ease the leaf outward until its flat
catch clears the receiver, then withdraw the cap along its installation path.
The tool entries leave the spring walls continuous below the hooks.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py
```
