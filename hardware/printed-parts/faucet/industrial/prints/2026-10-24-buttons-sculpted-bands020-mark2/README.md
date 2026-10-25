# Complete Industrial faucet — switch relief, Sculpted cover, 0.20 mm bands

Mark2 accepted task **1372253517**, observed in PREPARE at **20:09:23 CDT**
on October 24, with no print error or HMS. One foreground CUA Send submitted
the exact [native archive](launch.json). The earlier Mark1 running observation
precedes Send by more than twelve minutes.

The [startup reading](startup.json) at **20:10:37 CDT** reports RUNNING at
0/1416 merged layer planes, 392 minutes remaining, no print error and no HMS.

The complete print contains the Industrial base, corrected shared tip,
corrected Sculpted display cover, rigid Industrial counter plate and side-down
lever. The TPU mounting gasket is a separate material-specific print.

The [fit review](../../../faucet-display-cover/fit-review/2026-10-24/README.md)
binds the two corrections to the reported physical failure. Two approximately
5.00 × 5.60 mm button pockets are 1.00 mm deep, with 0.50 mm side allowance.
Nominal clearance beneath each switch is 0.60 mm; the complete vendor switch
shapes have zero intersection with the corrected tip. The display retains its
4.50 mm inward reduction, original foot centers and four 1 mm foot recesses.
The four foot-bearing regions and snap region have no removed material.

The Sculpted cover has 0.50 mm additional bezel-to-lip reach and the matching
0.50 mm arch offset used by the working Industrial control. Nominal glass
clearance is 0.60 mm and arch-crown clearance is 0.65 mm. The bezel remains
1.30 mm thick and the lips retain N3.30–6.30 and 1.20 mm engagement. These
coordinated cover dimensions are one 0.50 mm adjustment. Physical installation,
retention and support removal require this print's observations.

The [full settings export](all-settings.json) retains complete prepared/native
project dictionaries, embedded filament presets and object/range XML.
The [native command review](native-review.json) binds the exact archive and
G-code hashes, deposited-bead bounds, cooling commands, speeds, trim and layer
planes. Layer-range object identifiers follow Bambu's one-based object order.

| Setting | Value |
| --- | --- |
| Printer / nozzle | Mark2 H2C / fixed left hardened 0.4 mm Standard flow |
| Material / mapping | Black Polymaker PET-GF / external 254, PET-CF `#161616` |
| Plate / bed | Textured PEI / 80°C |
| First / later nozzle temperature | 265 / 280°C |
| Requested / emitted Z trim | +0.04 / +0.02 mm; trim reset first |
| First / ordinary layer height | 0.24 / 0.24 mm |
| Base band layer height | 0.20 mm at print Z17.00–29.00 and Z55.16–68.12 mm |
| Other parts | 0.24 mm throughout |
| Independent support layer height | Off |
| Walls / infill | 2 / 15% grid; complete foot modifier 100% zigzag |
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
| Flow / nozzle-offset calibration | Auto / Auto |

The warning-free native slice estimates **6 h 32 min 9 s / 160.58 g**, using
the saved 1.29 g/cm³ density. Minimum full-bead bed margin is **42.1365 mm**;
minimum separation between object toolpath envelopes is **1.0881 mm**. The base
has 125 model layers at 0.20 mm and 917 at 0.24 mm. All model layers on the
other four parts are 0.24 mm. Native startup clears trim and emits +0.02 mm.
