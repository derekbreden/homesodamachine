# Rear equipment caps

Four PET-GF caps close the integral seats on back-top. Their geometry and the
seats share [rear_snaps.py](../../../manifold-layout/rear_snaps.py) and
[rear_plumbing.py](../../../manifold-layout/rear_plumbing.py).

The ASSE cap holds the lower halves of both hexes, bears against the inlet
coupling, and passes the downward vent cup through its bottom flat. The Pisco
cap catches the outlet fitting's neck. The meter cap enters from the west;
its lower wing passes the flavor-A tube beneath the meter housing through
an open fore corner, retaining the aft bearing and both catches. The water
regulator cap holds the lower half of the housing after it enters its seat
from below. Each cap is one solid, with two integral spring walls and hooks.

The seats use 0.25 mm running clearance and the caps use 0.15 mm slip
clearance. The ASSE seat allows 1.5 mm of threaded-joint position variation.
ASSE, Pisco and meter enter their seats 16 mm forward and slide aft. The
regulator enters directly upward. The caps close after their bodies seat.

The standalone STEP and STL files use the print frame, with the cap mouth
upward and the lowest face on Z0. The appliance uses their installed frames.
Use the shared PET-GF Tree(auto)/Default support policy. These fits describe
the modeled assembly; snap force and fatigue remain physical properties.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.py
```
