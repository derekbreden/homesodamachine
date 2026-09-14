# Copper-slot covers

Two identical PETG covers close the foam shell's copper slots, one in each lane.
Each slides down from the open top and seats its bottom arch around the copper.
Its flat top finishes at the shell rim beneath the cap and gasket.

The continuous interior flange overlaps both slot edges by 1 mm. Foam pressure
bears this flange against the shell's recessed inner seat. The 6.5 mm web fills
the slot through the 3.2 mm wall and finishes flush with the exterior wall face.
Two 8 mm exterior tabs, one near each end, retain the cover against inward
movement before the pour. Each tab stands 1 mm outside the wall.

The long middle span has **0.44 mm clearance to the enclosure's valve tray** in
the assembled CAD. The interior flange, copper arch and cap seating plane use
the shell's existing interface. The small clearance around the copper remains
part of the body pour.

Print with the continuous interior flange flat on the bed. The exterior tabs
have 1 mm lateral overhangs with accessible undersides. Install both covers before
the body pour.

- [West cover](copper-plug-west.step)
- [Port cover](copper-plug-port.step)
- [Geometry verification](clearance-check.json)

Regenerate both covers:

```sh
tools/cad-venv/bin/python hardware/printed-parts/cold-core/copper-plugs/copper_plugs.py
```
