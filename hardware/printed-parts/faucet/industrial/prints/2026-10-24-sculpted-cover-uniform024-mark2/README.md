# Complete Industrial faucet with Sculpted cover — uniform 0.24 mm

Mark2 accepted task **1370902777** at **11:11:59 CDT**
on 2026-10-24. The [startup reading](startup.json) at
**11:13:08 CDT** reports RUNNING, 0/1022 layers, 384 minutes
remaining, no print error and no HMS. Bambu Connect received one Send through
foreground CUA input. The [preflight](preflight.json) records both printers
finished and idle, the ready Textured PEI plate, and black PET-GF on the left
external spool. Mark1's same finished job was observed more than three minutes
before this send. The preflight's nozzle-camera-lens warning is a recorded
AI-monitoring notification; the startup reading reports no HMS.

The complete set contains one Industrial base, the accepted lowered shared tip,
a Sculpted display cover, the rigid Industrial above-counter plate and the
side-down lever. The TPU gasket remains a separate material-specific print.

The [reported tight but working Industrial-head fit](../2026-10-24-lowered-display-complete-mark2/physical-result/physical-result.json)
binds the reused tip to task 1369497043 and its eight photographs. The display
seat retains the complete 4.5 mm inward reduction: 1.5 mm additional tube
clearance, 2.0 mm original support stock and 1.0 mm foot recess depth. Four
Ø4 mm recesses keep their original foot locations.

The [Sculpted cover geometry reading](cover-geometry.json) records its matching
4.5 mm lower display position, fixed N3.30–6.30 snap lips, 1.30 mm bezel and
0.10 mm nominal glass-to-bezel gap. The printable cover is one valid solid;
the nominal seated cover has zero native intersection volume with the accepted
tip. This is a geometric fit check. The
[physical result and nine photographs](physical-result/physical-result.json)
record repeated Sculpted installation failure, a tight but working Industrial
control on the same printed tip, and the side button housing bearing at the tip
ledge. The [corrected fit print](../2026-10-24-buttons-sculpted-bands020-mark2/README.md)
includes local button pockets and the Industrial control's extra cover reach.

All 1,022 native layer planes advance by 0.24 mm, beginning at Z0.24. The
first bed layer is also 0.24 mm. Fine ranges and adaptive layer profiles are
absent, and independent support layer height is Off. Bridge-road diameters and
scarf-road extrusion-height comments describe their bead cross sections; they
do not introduce fine layer planes.

The [complete settings export](all-settings.json) contains all 582 prepared and
583 native project settings, embedded filament presets, object/component
overrides and complete model-settings/layer-range XML. Arrays preserve Bambu's
nozzle/flow ordering; this job uses the left Standard-flow entry. Machine and
filament G-code templates are included.

| Setting | Value |
| --- | --- |
| Printer / nozzle | Mark2 H2C / fixed left hardened 0.4 mm Standard flow |
| Material / mapping | Black Polymaker PET-GF, external 254, PET-CF `#161616` |
| Plate / bed temperature | Textured PEI / 80°C |
| First / later nozzle temperature | 265 / 280°C |
| Requested / emitted user trim | +0.04 / +0.02 mm; startup clears trim first |
| First / later layer height | 0.24 / 0.24 mm |
| Fine ranges / independent support heights | None / Off |
| Walls / infill | 2 / 15% grid; full foot modifier 100% zigzag |
| Wall generator | Arachne base; Classic on other parts |
| Top / bottom shells | 4 layers, minimum 1 mm / 3 layers |
| Filament flow / volumetric limit | 0.9555 / 18 mm³/s |
| Bridge flow / speed | 125% / 15 mm/s |
| Overhang tiers / fully overhung | 15 / 15 / 15 / 10 mm/s / 10 mm/s |
| Ordinary / auxiliary fan | 0% / 0% |
| Bridges and qualifying overhangs | 70% fan at 50% unsupported-width threshold |
| First three bed layers | Fan off through Z0.72 |
| Retraction / Z hop / wipe | 0.8 mm at 30 mm/s / 0.4 mm Auto Lift / Off |
| Base, tip and rigid plate seams | Back, A2 scarf, 150% ordinary seam gap |
| A2 scarf | 60 mm, 0% gap, 10% start, 10 steps, smart 155°, inner walls On |
| Cover and lever seams | Aligned, 15% gap, scarf Off |
| Automatic supports | Tree(auto), Default, 35° threshold |
| Support top / bottom / XY gaps | 0.45 / 0.30 / 0.40 mm |
| Top / bottom interfaces | 2 / 2 layers at 0.50 / 0.50 mm spacing |
| Base support components | Seven accepted rim arcs and local contact blockers |
| Tip support components | Eight fins, local lip trees and hidden-root disc |
| Brim | Auto, 5 mm, 0.1 mm gap |
| X rotations | Base −15°, tip −105°, cover −50°; plate flat; lever side-down |
| Timelapse / bed leveling | On / On |
| Flow dynamic / nozzle-offset calibration | Auto / Auto |

The base and exposed curved tip retain rear-center seam paint. The
[native command review](native-review.json) verifies layer spacing, checksum,
trim, all five parts' fan commands and reduced bridge/overhang speeds. The
[support audit](2026-10-24-industrial-sculpted-cover-low45-uniform024-black-left04-z004-mark2.support-audit.json)
records **42.1479 mm** minimum full-bead bed margin and **1.0819 mm** minimum
separation between object toolpath bounding envelopes. The native slice has no
warnings and estimates **6 h 24 min 36 s / 160.17 g**, using the saved
1.29 g/cm³ density. Printed completion, the Sculpted cover's seating and
support release are separate physical observations.
