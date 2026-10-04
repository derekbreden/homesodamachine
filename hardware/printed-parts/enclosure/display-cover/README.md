# Machine display cover

The accepted face-up PET-GF bezel uses two coplanar horizontal wings. It passes the
shake test and has acceptable appearance with a small residual bow. The suspected
residual bend from insertion is unverified. The
[physical record](face-up-trial/physical-acceptance.json) identifies the exact tested pair.

The cover is 125.5 × 83 × 3.84 mm with R6 outer corners and a 107.5 × 71 mm window.
Each wing is 1.44 mm thick, projects 3.60 mm and spans 70 mm, with R0.6 ends.
The back and both wings lie directly on the bed; print face up without supports.

Front-top carries the matching pockets. Main-body clearance is 0.30 mm per side
in X and 0.15 mm per side up the display. Each wing has 0.60 mm above its seated
bearing face and 0.15 mm at either end. Wing-tip clearance is 0.55 mm centered,
0.25 mm at full sideways float. Capture remains at least 3.00 mm. The retaining
lip is 1.80 mm thick. Flex the middle outward to enter the wings, then let the
bezel seat against its back datum.

The visible face is flush with the enclosure's 30° display plane. A 1 mm TPU ring
and 1 mm glass lie beneath the cover. Glass back depth is 5.84 mm. The complete
17 mm module behind the glass has 1 mm rear clearance; the supporting rib retains
3 mm stock. The PCB opening and funnel clearance are checked in the
[current integrated geometry](../enclosure/accepted-fit-integration/current-geometry-check.json).

The wing pockets open down through the display storey to its existing floor.
Remove shared-profile tree supports through the empty bay before installing the
screen. No short support strip is enclosed beneath a wing pocket.

[`display_cover.py`](display_cover.py) and
[`_display_wing_interface.py`](../enclosure/_display_wing_interface.py) generate the
cover and production receiver. Their cover solid equals the accepted specimen.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-cover/display_cover.py`
