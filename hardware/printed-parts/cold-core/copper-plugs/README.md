# Copper-slot covers

Two identical PETG covers close the foam shell's copper slots, one in each lane.
Each slides down from the open top and seats its bottom arch around the copper.
Its flat top finishes at the shell rim beneath the cap and gasket.

The continuous interior flange overlaps both slot edges by 1 mm. Foam pressure
bears this flange against the shell's recessed inner seat. The 6.15 mm web slides through the 6.65 mm slot in the 3.2 mm wall,
with 0.25 mm clearance at each side, and finishes flush with the exterior wall face.
Two 8 mm exterior tabs, one near each end, retain the cover against inward
movement before the pour. Each 1 mm thick tab clears the outside wall by 0.50 mm: 0.25 mm running
clearance plus 0.25 mm for the supported underside. The interior flange has
0.25 mm running clearance. The corner relief clears its sides and back by
0.25 mm. Short end connectors join the tabs to the flush middle web.

The long middle span stays flush with the shell outside face beside the
enclosure valve tray. The copper arch has 0.15 mm radial clearance, and the
flat top seats beneath the cap. The small clearance around the copper remains
part of the body pour.

Print with the continuous interior flange flat on the bed. The exterior tabs
have 1 mm lateral overhangs with accessible undersides. Install both covers before
the body pour.

- [West cover](copper-plug-west.step)
- [Port cover](copper-plug-port.step)

Regenerate both covers:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py
```
