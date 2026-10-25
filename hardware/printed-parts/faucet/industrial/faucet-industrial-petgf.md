# Approved Industrial faucet production print

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains the approved
five-part set: Industrial base, lowered shared tip, Sculpted display cover with
extended front skirts, rigid Industrial above-counter plate and side-down lever.
The [production selection](production-selection.json) binds the exact meshes and
[physical approval](../faucet-display-cover/prints/2026-10-25-front-overlap-black-mark2/physical-result/physical-result.json).
The small remaining front-corner gap is accepted as good enough. No further
iteration on that gap is requested.

Every layer is **0.24 mm, including the first bed layer**. There are no 0.08,
0.12 or 0.20 mm bands, and independent support layer height is Off. The approved
source meshes are preserved in [the production source set](production/2026-10-25/README.md),
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

The [complete settings export](production/2026-10-25/all-settings.json) preserves
all prepared/native settings, filament presets and object overrides. The
[native reading](production/2026-10-25/native-review.json) verifies the exact
approved source geometry, uniform layer heights and emitted commands. The
[process selection](finish-selection.json) retains the accepted supports and seams.

| Setting | Value |
| --- | --- |
| First / later layer height | 0.24 / 0.24 mm |
| Nozzle / bed temperatures | 265°C first, 280°C later / 80°C |
| Flow / volumetric limit | 0.9555 / 18 mm³/s |
| Global walls / infill | 2 / 15% grid |
| Base foot | Continuous 100% zigzag infill modifier; base Arachne |
| Other objects | Classic wall generator |
| Top / bottom shells | 4 layers, minimum 1 mm / 3 layers |
| Bridge flow / speed | 125% / 15 mm/s |
| Overhang speeds | 15 / 15 / 15 / 10 mm/s; fully overhung 10 mm/s |
| Ordinary / auxiliary fans | Off / Off |
| Qualifying bridges and overhangs | 70% after three fan-off layers; 50% unsupported-width threshold |
| Wipe | Off |
| Automatic supports | Tree(auto), saved Default style, 35° threshold |
| Support top / bottom / XY gaps | 0.45 / 0.30 / 0.40 mm |
| Support interfaces | 2 top and 2 bottom layers, 0.50 mm spacing |
| Brim | Auto, 5 mm, 0.1 mm gap |
| Mark2 requested / emitted Z trim | +0.04 / +0.02 mm on Textured PEI |
| Mark1 requested / emitted Z trim | +0.18 / +0.16 mm on Textured PEI |
| Timelapse / bed leveling | On / On |
| Flow / nozzle-offset calibration | Auto / Auto |

Base, tip and mounting plate use 150% ordinary seam gap with A2's 60 mm partial
scarf, 0% scarf gap, 10% layer-relative start height, ten steps, smart 155°
application and inner-wall scarf. The base's full rear silhouette and the tip's
exposed curved meridian retain their seam enforcement. Cover and lever keep
Aligned, 15% seam gap and scarf Off.

The base retains seven accepted segmented rim arcs and their narrow contact
blockers at the −15° pose. The tip retains eight fins, local lip trees and the
removable hidden-root disc. The disc's accepted removal scuff is confined to
the hidden male insertion end. Tree(auto)/Default serves the remaining surfaces,
including its automatically generated normal sections.

## Prepare the next print

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prepare_print_project.py
```

The preparer uses the approved frozen meshes and print profile. Optional
`--printer Mark1 --filament-colour '#000000'` applies Mark1's own trim and the
specified spool colour. Check the destination's actual material and nozzle
mapping before sending. Optional `--slice-output <empty-directory>` performs a
local native slice without contacting a printer.

The current [prepared project](faucet-industrial-petgf.3mf),
[native archive](faucet-industrial-petgf.gcode.3mf),
[preparation](faucet-industrial-petgf.print.json),
[support reading](faucet-industrial-petgf.support-audit.json) and
[readiness](faucet-industrial-petgf.readiness.json) describe the complete uniform-layer
production set. Preparing or reviewing it does not authorize or submit a print.
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
