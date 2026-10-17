# PET-GF cooling

Ordinary PET-GF paths print with part cooling off. High cooling belongs to the
bridges and unsupported underside paths that need it. A short layer time does
not turn cooling on for an entire part or layer. Auxiliary part cooling is off.

| Bambu setting | Current value |
| --- | ---: |
| Minimum / maximum part fan speed | 0% / 0% |
| Force cooling for overhangs and bridges | On |
| Overhang fan threshold | 50% unsupported bead width |
| Overhang / bridge fan speed | 70% |
| Keep fan always on | Off |
| Fan pre-start time | 0 s |
| Auxiliary part fan | 0% |
| First three bed layers | Fan off |

Up to 100% cooling is acceptable for a feature whose underside needs it. Apply
that choice to the qualifying overhang/bridge paths. Ordinary walls, infill and
support paths retain zero part cooling unless they themselves qualify. Exhaust
and hotend heatsink fans serve other purposes and retain their machine settings.

Bambu Studio's **0% overhang threshold means all exterior walls**, even walls
with no overhang. It does not mean cooling is restricted to overhangs. The
[installed-version configuration definitions](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp)
describe the threshold and fan-always-on behavior. Fan pre-start is zero so a
bridge does not request cooling on preceding ordinary paths. The native G-code
still needs a reading for a particular plate: the physical fan takes time to
change speed, and a setting does not establish mechanical strength.

The [successful fan-off display cover](../faucet/faucet-display-cover/prints/2026-10-17-cooling-off-prepared-mark2/physical-result.json)
passed normal display loading and cover installation. Derek also reports other
faucet parts breaking during that installation. These observations support
removing general cooling. They do not establish strength, endurance or a
single cause for every fracture. Polymaker's
[PET-GF15 printing guidance](https://wiki.polymaker.com/polymaker-products/polymaker-filaments/fiberon-tm/fiberon-tm-pet-gf15)
specifies fan off and suggests slower printing for layer-adhesion trouble.
The faucet's existing bridge flow and bridge/overhang speeds remain selected
for underside finish; ordinary process speeds and temperatures are unchanged.

## Current projects

[petgf.3mf](../petgf.3mf) contains the selected values in both the project
settings and embedded filament preset. [petgf_cooling.py](../cadlib/petgf_cooling.py)
applies them when the shared project writer prepares PET-GF from a source
profile, including a retained historical profile. It leaves other materials
alone. The Industrial and Sculpted faucet preparers also apply the selected
localized recipe explicitly. This is configuration preparation, not an
additional build or commit check.

The [editable-template inventory](current-projects.json) identifies the updated
enclosure, label, tool, lever, vent-tool and organizer projects and their
hashes. Their mesh and build members are unchanged. Re-slice these editable
projects to obtain the current cooling commands. Native archives of completed
prints retain the exact commands used for their reported physical results;
they are historical evidence, not the current production recipe. Older
identified trial projects, including the September display trial, retain their
original hashes too. The current complete faucet recipes are
[Industrial](../faucet/industrial/faucet-industrial-petgf.md) and
[Sculpted](../faucet/sculpted/README.md).
