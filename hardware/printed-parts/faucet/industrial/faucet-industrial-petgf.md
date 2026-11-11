# Approved Industrial faucet production print

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains the approved
five-part set: Industrial base, lowered shared tip, Sculpted display cover with
extended front skirts, rigid Industrial above-counter plate and side-down lever.
The [production selection](production-selection.json) binds the exact meshes and
[physical approval](../faucet-display-cover/prints/2026-10-25-front-overlap-black-mark2/physical-result/physical-result.json).
The small remaining front-corner gap is accepted as good enough. No further
iteration on that gap is requested.

The first bed layer retains **Bambu’s 0.20 mm default**; every later layer is
**0.24 mm**. There are no fine layer bands, and independent support layer
height is Off. The approved source meshes are preserved in
[the production source set](production/2026-10-25/README.md),
so preparation uses the actual printed parts. The display retains its 4.5 mm
inward reduction, four 1 mm foot recesses and two 1 mm switch pockets. The cover
retains the working glass and neck clearances and fixed snap datums.

The default project targets Mark2's fixed left hardened 0.4 mm Standard-flow
nozzle, black Polymaker PET-GF on external slot 254, and Textured PEI. Each
printer keeps its own Z trim when explicitly selected. The TPU gasket, lever
sleeve, PET-GF umbilical organizer and stainless under-counter plate are separate
prints or parts.

| Part | CAD X rotation | Seam |
| --- | ---: | --- |
| Industrial shell base | −15° | Back, A2 scarf |
| Lowered shared faucet tip | −105° | Back, A2 scarf |
| Extended-skirt Sculpted display cover | −50° | Aligned, scarf Off |
| Rigid Industrial above-counter plate | 0° | Back, A2 scarf |
| Side-down lever replica | 0° of its print-oriented STL | Aligned, scarf Off |

## Selected process

The [approval settings](production/2026-10-25/all-settings.json) and
[approval slice reading](production/2026-10-25/native-review.json) bind the
approved geometry, seam setup and calibration to the physical prints. The
[current process selection](finish-selection.json) and
[production path review](faucet-industrial-petgf.support-audit.json) record
the selected support contacts and emitted bridges.

| Setting | Value |
| --- | --- |
| First / later layer height | 0.20 / 0.24 mm |
| Nozzle / bed temperatures | 265°C first, 280°C later / 80°C |
| Flow / volumetric limit | 0.9555 / 18 mm³/s |
| Global walls / infill | 2 / 15% gyroid |
| Base foot | Continuous 100% zigzag infill modifier; base Arachne |
| Other objects | Classic wall generator |
| Top / bottom shells | 4 layers, minimum 1 mm / 3 layers |
| Bridge flow / speed | 125% / 15 mm/s |
| Overhang speeds | 15 / 15 / 15 / 10 mm/s; fully overhung 10 mm/s |
| Ordinary / auxiliary fans | Off / Off |
| Qualifying bridges and overhangs | 70% after three fan-off layers; 50% unsupported-width threshold |
| Wipe | Off |
| Automatic supports | Tree(auto), saved Default style, 35° threshold |
| Support gaps and interfaces | [Shared PET-GF recipe](../../petgf.3mf) with the [base contact overrides](finish-selection.json) |
| Brim | Off for the base. Auto on the rest of the plate |
| Mark2 requested / emitted Z trim | +0.04 / +0.02 mm on Textured PEI |
| Mark1 requested / emitted Z trim | +0.18 / +0.16 mm on Textured PEI |
| Timelapse / bed leveling | On / On |
| Flow / nozzle-offset calibration | Auto / Auto |

Base, tip and mounting plate use 150% ordinary seam gap with A2's 60 mm partial
scarf, 0% scarf gap, 10% layer-relative start height, ten steps, smart 155°
application and inner-wall scarf. The base's full rear silhouette and the tip's
exposed curved meridian retain their seam enforcement. Cover and lever keep
Aligned, 15% seam gap and scarf Off.

The base uses Slim trees and segmented outer fins beneath a shared dense
interface. The first supported outer perimeter follows the inclined rim and
joins the ordinary wall courses.
The base's insert shoulders and blind pilot
roofs bridge across the blocked recesses. The mounting plate uses bridges
over its counterbores. The [process selection](finish-selection.json) owns the
contact recipe and cavity clearances.

Slim trees and segmented outer fins carry the shared dense interface at the
tip's mating lip. The first outer perimeter follows the inclined rim and
joins the ordinary wall courses. The
inner dispense face has its own contact band and a keepout at the beverage
aperture. The removable root disc anchors the plug at the bed and confines
its contact to the hidden insertion end. The other parts use their selected
automatic supports.

## Prepare the next print

```sh
tools/run -- tools/hsm/target/release/industrial-faucet-print-project --slice-output path/to/new-slice-directory
```

The preparer uses the approved frozen meshes and print profile. The slice
output contains the complete executable plate with the restored contact
paths, contoured rim perimeters and original production meshes. Optional
`--printer Mark1 --filament-colour '#000000'` applies Mark1's own trim and the
specified spool colour. Check the destination's actual material and nozzle
mapping before sending.

The current [prepared project](faucet-industrial-petgf.3mf),
[preparation](faucet-industrial-petgf.print.json),
[support reading](faucet-industrial-petgf.support-audit.json) and
[readiness](faucet-industrial-petgf.readiness.json) describe the complete
production set. The preparer writes the executable archive to the specified
slice directory.
A cover-only project is available through the
[cover preparer](../faucet-display-cover/README.md#printing-and-checks).

## Assembly and accepted scope

The [assembly procedure](../faucet-shell/ASSEMBLY.md) gives the mounting, tube
routing and display seating order. Clear supports through the base's counter,
rear, donor and lever openings; through the tip's joint, display pocket and
outlets; and through the cover's open underside before display installation.
Preserve bearing, lip and groove surfaces.

The pictured head and latest cover have direct assembly and appearance approval.
The remaining corner gap is an accepted cosmetic condition. Numerical assembly
and retention forces, hydraulic fault discharge and endurance are unmeasured.
Historical physical results retain their identified articles and settings in the
[print log](print-log.md) and [shipping acceptance](physical-acceptance.json).
