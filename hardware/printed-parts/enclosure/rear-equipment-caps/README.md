# Rear equipment caps

Four PET-GF caps close the integral seats on back-top. Their geometry and the
seats share [rear_snaps.py](../../../manifold-layout/rear_snaps.py) and
[rear_plumbing.py](../../../manifold-layout/rear_plumbing.py).

The ASSE cap holds the lower halves of both hexes, bears against the inlet
coupling, and passes the downward vent cup through its bottom flat. The Pisco
cap catches the outlet fitting's neck. The meter cap enters from the west
and has a solid 6 mm spine with two complete 38 mm-long leaves. Its flexible
leads turn west against the housing above the lower leaf. The water regulator
cap spans 36 mm of the housing and smaller outlet neck, with its lowest face
at Z315.924 mm. Each cap is one solid, with two integral spring walls and hooks.

The ASSE seat uses 0.25 mm running clearance and its cap uses 0.15 mm slip
clearance. The ASSE seat allows 1.5 mm of threaded-joint position variation.
The Pisco seat and cap include an additional 0.75 mm of radial relief on the
admitted body and neck. The meter's housing, flange and bosses have 0.75 mm
clearance in both halves, including the receiver's closed back.
All leaves are 2.6 mm thick, with 22.5 mm of free bending length; the water
regulator uses 21.5 mm within its retained height. The insertion face has a
2 mm-rise lead-in ramp above a 0.6 mm solid nose land. The retaining face is
flat and retains the complete 2.6 mm overlap.
ASSE, Pisco and meter enter their seats 16 mm forward and slide aft. The
regulator enters directly upward. The caps close after their bodies seat.

The standalone STEP and STL files use the print frame, with one axial end
on Z0 and spring bending within the layer plane. The appliance uses their installed frames.
Use the shared PET-GF Tree(auto)/Default support policy. These fits describe
the modeled assembly; snap force and fatigue remain physical properties.

Remove the small cavity supports with a tiny flathead screwdriver that fits
inside the opening. Derek reports that the original trial's small automatic
cavity supports removed easily with that tool. Preserve the flat catch
undersides while clearing them. The [physical record](../../../print-tests/rear-snap-retention/physical-result/physical-result.json)
records this removal result and the hardware fit observations.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py
```
