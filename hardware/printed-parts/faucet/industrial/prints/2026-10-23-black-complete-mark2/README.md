# Black complete Industrial faucet — Mark2

One complete set of five rigid PET-GF parts: Industrial base, shared tip,
Industrial display cover, above-counter plate and side-down lever. The project
uses the current source STLs, selected seams, shoulder bands, localized cooling,
seven base rim arcs, eight tip fins and hidden-root anchor disc.

Mark2 accepted task [1366512080](launch.json), observed at 03:06:47 CDT on
2026-10-23 in PREPARE with no print error or HMS fault. Bambu Connect received
one Send and the printer replied SUCCESS. The [preflight](preflight.json)
records both printers idle and Mark2's black left external spool. The same
finished Mark1 task was also observed at 02:59:32 CDT, more than three minutes
before this send. Derek confirms the left 0.4 mm hotend, loaded PET-GF and clear
textured plate in the print request.
The [startup reading](startup.json) at 03:08:31 CDT reports RUNNING, layer
0/1245, 408 minutes remaining and no print error or HMS fault.

The [complete settings export](all-settings.json) contains all 582 prepared
project settings, all 583 serialized native settings, embedded filament presets,
object/component overrides and exact layer-range and model-settings XML. Arrays
retain Bambu's nozzle/flow-variant ordering; this job uses the left Standard-flow
entry. Machine and filament G-code templates are included in that export.

| Machine and material | Setting |
| --- | --- |
| Printer | Mark2, Bambu Lab H2C |
| Active nozzle | Fixed left, hardened steel, 0.4 mm, Standard flow |
| External spool | 254, black `#161616`, PET-GF reported as PET-CF |
| Filament preset | Polymaker PET-GF @BBL H2C |
| Process preset | 0.24mm PET-GF faucet |
| Printer preset | Bambu Lab H2C 0.4 Standard +0.04 Z trim |
| Plate | Textured PEI |
| Requested / emitted Z trim | +0.04 / +0.02 mm; native start first clears trim to zero |
| Nozzle temperature | 265 °C first layer, 280 °C thereafter |
| Bed temperature | 80 °C throughout printing |
| Chamber temperature | 0 °C target, no chamber heating requested |
| Filament diameter / density | 1.75 mm / saved 1.29 g/cm³ |
| Filament / process flow ratios | 0.9555 / 1.0 |
| First-layer / top-surface flow multipliers | 1.0 / 1.0 |
| Maximum volumetric flow | 18 mm³/s |
| Bridge flow | 1.25 |
| Retraction / deretraction | 0.8 mm at 30 / 30 mm/s |
| Retraction minimum travel | 1 mm; retract at layer changes On |
| Extra restart length | 0 mm |
| Z hop | 0.4 mm, Auto Lift |
| Wipe | Off, 0 mm filament wipe distance |
| Manual pressure-advance override | Off; send-time Flow dynamic calibration Auto |

| Geometry and structure | Setting |
| --- | --- |
| Base / tip / cover X rotations | −15° / −105° / −50° |
| Counter plate / lever | Flat / accepted side-down STL |
| Printing sequence | By layer, one plate |
| First / normal layer height | 0.20 / 0.24 mm |
| Base fine bands | 0.12 mm at print Z17.00–29.00 and Z55.16–68.12 mm |
| Supported lip start | Eight 0.24 mm courses at nozzle Z15.32–17.00; first fine course Z17.12 |
| Walls | 2; inner wall before outer wall |
| Wall generator | Arachne on base; Classic on other four parts |
| Top shell | 4 layers, minimum 1 mm thickness |
| Bottom shell | 3 layers, no additional minimum thickness |
| General infill | 15% grid, 45° |
| Foot reinforcement | 100% zig-zag infill modifier, inherited ordinary walls |
| Infill/wall overlap | 15% |
| Top / bottom surface pattern | Monotonic line / monotonic |
| Ironing / fuzzy skin | Off / Off |
| Elephant-foot compensation | 0.15 mm |
| XY contour / hole compensation | 0 / 0 mm |
| Resolution / arc fitting | 0.012 mm / Off |
| Brim | Auto, 5 mm width, 0.1 mm object gap |
| Raft / skirt | 0 layers / 0 loops |
| Prime tower | Enabled in saved profile; none emitted for this single-filament slice |

| Line width | mm |
| --- | ---: |
| Default / outer wall | 0.42 |
| First layer | 0.50 |
| Inner wall / sparse infill / top surface | 0.45 |
| Internal solid infill | 0.42 |
| Support | 0.62 |

| Nominal speed | mm/s |
| --- | ---: |
| First-layer walls / infill | 50 / 105 |
| Outer / inner walls | 200 / 300 |
| Sparse / internal solid / gap infill | 350 / 250 / 250 |
| Top surface | 200 |
| Supports / interfaces | 150 / 80 |
| Bridges | 15 |
| Overhang tiers | 15 / 15 / 15 / 10; fully overhung 10 |
| Travel | 1000 |
| Small perimeter | 50% of ordinary wall speed; threshold 0 |
| Vertical shell | 80% |
| Layer cooling slowdown | On; 1 s threshold, 10 mm/s minimum |

The volumetric limit, overhang treatment and motion planning can reduce nominal
speeds. Default acceleration is 8000 mm/s²; first layer 500, outer walls 5000,
top surfaces 2000, inner walls inherit, sparse infill 100% of default, travel
10000 and first-layer travel 6000. Saved machine travel acceleration limit is
9000 mm/s². Feature XY jerk settings are 9 mm/s. The complete export retains
all remaining machine limits and inactive flow-variant entries.

| Cooling | Setting |
| --- | --- |
| Ordinary part fan minimum / maximum | 0% / 0% |
| Force cooling on overhangs and bridges | On |
| Overhang fan threshold | 50% unsupported bead width |
| Overhang / bridge fan | 70% |
| First three bed layers | Fan off |
| Auxiliary fan | 0% |
| Keep fan always on / fan pre-start | Off / 0 s |
| Air filtration | Off; saved during/after-print exhaust defaults are 70% |

| Seams | Setting |
| --- | --- |
| Base, tip, rigid counter plate | Back, ordinary seam gap 150%, A2 contour scarf |
| Base and exposed curved tip | Rear-center seam enforcement paint |
| A2 scarf | 60 mm length, 0% scarf gap, 10% layer-relative starting height, 10 steps |
| Scarf application | Smart 155°, inner walls On, partial loop |
| Cover and lever | Aligned, 15% ordinary gap, scarf Off |

| Supports | Setting |
| --- | --- |
| Automatic supports | Tree(auto), Default style, 35° threshold |
| Build-plate-only / critical-regions-only | Off / Off |
| Top / bottom Z gap | 0.45 / 0.30 mm |
| Object XY / first-layer gap | 0.40 / 0.20 mm |
| Top / bottom interface layers | 2 / 2 |
| Top / bottom interface spacing | 0.50 / 0.50 mm |
| Base pattern / spacing | Default / 2.5 mm |
| Interface pattern | Auto |
| Independent support layer height | On |
| Branch angle / diameter / distance | 45° / 2 mm / 5 mm |
| Branch diameter angle / wall count | 5° / Auto |
| Base rim | Seven 0.90 mm arc walls, 41° arcs, 4° release gaps, requested 0.24 mm vertical gap; narrow contact blockers |
| Tip | Eight fin walls, selected low-lip tree enforcers and directly bonded hidden-root disc |
| Support material | Same black PET-GF |

Timelapse and Auto bed leveling are On. Flow dynamic calibration and Nozzle
Offset Calibration are Auto. Probing clump detection is disabled by the saved
start template. Bambu Connect verified these four send options and the left
external-spool mapping before Send; they are recorded in the complete settings
export. The launch receipt binds the archive, G-code hash and new task ID.

The [native command review](native-review.json) binds the archive and embedded
G-code checksum, emitted trim and all five parts' fan/bridge/overhang commands.
The [support audit](2026-10-23-industrial-faucet-black-complete-petgf-left04-z004-mark2.support-audit.json)
records the current paths and cleanup topology. Complete model/support/brim
beads retain 41.8755 mm minimum usable-bed clearance. The native slice has no
warnings, 1245 layers and an estimate of 6 h 48 min 35 s, 52.45 m / 162.74 g
using the saved filament density. Physical completion and assembly acceptance
are separate observations.
