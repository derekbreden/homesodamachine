# Complete Industrial faucet with lowered display — Mark2

One complete set of five rigid black PET-GF parts: Industrial base, shared tip,
Industrial display cover, above-counter plate and side-down lever. The tip and
cover are the exact reviewed [display-seat candidate](../../display-seat-review/2026-10-24/README.md).
The display and cover sit 4.5 mm lower: 1.5 mm additional tube clearance, 2.0 mm
original support height and 1.0 mm foot recess depth. Four diameter-4 mm foot
pockets occupy the original locations. The other three parts use the production
source STLs.

The [physical result and eight photographs](physical-result/physical-result.json)
record Derek's report: “It is a bit tight, but it works.” This acceptance belongs
to the identified lowered Industrial head. Numerical tube clearance, seating
force and endurance are unmeasured. The conservative component/tube and
component/tip overlaps remain model readings with that separate scope.

The project is prepared for Mark2's left fixed hardened steel 0.4 mm Standard-flow
nozzle, black Polymaker PET-GF on external spool 254, reported as PET-CF
`#161616`. The current slice selects Textured PEI, 80°C bed temperature and
+0.04 mm user Z trim, emitted as +0.02 mm after stock plate compensation.
Native startup first clears trim to zero. Plate confirmation and submission are
recorded in the [preflight](preflight.json) and [launch receipt](launch.json).
Derek confirms that ready means Textured PEI for this requested print.

Mark2 accepted task **1369497043** at **01:20:19 CDT** on 2026-10-24, in
PREPARE with no print error or HMS. Bambu Connect received one Send through
foreground CUA input, with the left external PET-CF tile and all four standing
launch options verified. The [startup reading](startup.json) at **01:20:54 CDT**
reports RUNNING, layer 0/1245, 407 minutes remaining and no print error or HMS.

The [complete settings export](all-settings.json) retains all 582 prepared and
583 native project settings, filament presets, object/component overrides and exact
layer-range/model-settings XML. Arrays retain Bambu's nozzle/flow ordering;
this job uses the left Standard-flow entry. Machine and filament G-code templates
are included.

| Setting | Value |
| --- | --- |
| First / subsequent nozzle temperature | 265 / 280°C |
| First / normal layer height | 0.20 / 0.24 mm |
| Base fine bands | 0.12 mm at print Z17–29 and Z55.16–68.12 mm |
| Walls / infill | 2 / 15% grid; foot modifier 100% zigzag |
| Maximum volumetric flow / filament flow ratio | 18 mm³/s / 0.9555 |
| Bridge flow / speed | 125% / 15 mm/s |
| Overhang speeds | 15 / 15 / 15 / 10 mm/s; fully overhung 10 mm/s |
| Ordinary part / auxiliary fan | 0% / 0% |
| Bridges and qualifying overhangs | 70% fan at 50% unsupported-width threshold |
| First three bed layers | Fan off |
| Retraction / Z hop | 0.8 mm at 30 mm/s / 0.4 mm Auto Lift |
| Wipe | Off |
| Base / tip / plate seam | Back, A2 scarf, 150% ordinary gap |
| A2 scarf | 60 mm, 0% gap, 10% start height, 10 steps, smart 155° |
| Cover / lever seam | Aligned, 15% gap, scarf off |
| Automatic supports | Tree(auto), Default, 35° threshold |
| Support top / bottom / XY gaps | 0.45 / 0.30 / 0.40 mm |
| Support top / bottom interfaces | 2 / 2 layers, 0.50 / 0.50 mm spacing |
| Base supports | Seven accepted rim arcs and local contact blockers |
| Tip supports | Eight fins, local lip trees and hidden-root anchor disc |
| Auto brim | 5 mm, 0.1 mm object gap |
| Part rotations X | Base −15°, tip −105°, cover −50°; plate flat, lever side-down |
| Timelapse / bed leveling | On / On |
| Flow dynamic / nozzle-offset calibration | Auto / Auto |

The base and exposed curved tip retain rear-center seam paint. The inherited
A2 scarf applies to inner walls and partial loops. The base uses Arachne walls;
the other four parts use Classic. Top shells use four layers with a 1 mm minimum;
bottom shells use three layers. Nominal wall/infill speeds and machine motion
limits are retained in the complete settings export; emitted bridge and overhang
speeds are checked in the [native command review](native-review.json).

The native slice has no warnings and estimates 6 h 47 min 40 s / 161.33 g using
the saved 1.29 g/cm³ filament density. The native archive binds all five reviewed
meshes and their selected support components. The
[support audit](2026-10-24-industrial-complete-display-low45-petgf-left04-z004-mark2.support-audit.json)
records 41.8756 mm minimum full-bead clearance inside the shared usable bed.
Mark2 reports FINISH at 1245/1245 layers. The linked physical record supplies
the reported head fit; complete hydraulic operation is unmeasured.
