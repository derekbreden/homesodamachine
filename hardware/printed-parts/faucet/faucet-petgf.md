# Sculpted faucet PET-GF print project

[`faucet-petgf.3mf`](faucet-petgf.3mf) contains all four parts on one plate,
with separate spaces for their automatic tree supports and brims.

| Position | Part | Rotation about the CAD X axis |
|---|---|---:|
| Left | Faucet shell base | −15° |
| Right rear | Faucet shell tip | +40° |
| Far right rear | Faucet display cover | +40° |
| Right front | Above-counter plate | 0° |

The tip stands on its dispense face and the cover on its front wall. Both
poses put local S along build Z, so the groove floors, retaining shoulders
and cover lip bearing faces print vertically. The above-counter plate rests
on its gasket face, with its locating pedestals up. The base's long straight
neck is 15° from vertical. Supports are removed before hardware assembly.

The project takes the Bambu Lab H2C 0.4 mm printer, 0.24 mm process and
Polymaker PET-GF settings from the saved successful Sculpted profile. The
source snapshot and its settings digest are recorded in the print report.
`refresh_print_project.py` copies that profile's complete settings and embedded
filament settings, replaces the four meshes from their generated STLs, seats
them on the bed and places them within the shared printable area of both
extruders. `--settings-from` selects an explicit alternative profile.

The saved user process preset `0.24mm PET-GF faucet` includes the 0.45 mm
support top gap. The saved user filament preset `Polymaker PET-GF @BBL H2C`
includes the shared profile’s 0–70% cooling and 265/280 °C temperatures.
The project reopens without an unsaved support-preset indicator.

The profile uses a 0–70% part fan according to layer time, with cooling off
for the first three layers. Nozzle temperatures are 265 °C for the first
layer and 280 °C thereafter, with an 80 °C textured plate.

Regenerate the CAD/STL files, then refresh the project:

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/prepare_display_print.py --refresh-production
```

[`faucet-petgf.print.json`](faucet-petgf.print.json) records the source profile,
project and settings hashes, each source STL hash, its watertightness, its exact bed
transform and the embedded mesh's agreement with that STL.

For an offline slice through the saved settings:

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/refresh_print_project.py \
  --slice-output /tmp/faucet-petgf-slice
```

This runs the installed Bambu Studio CLI and writes G-code to the requested
local directory. It sends no printer job. The resulting
[`faucet-petgf.support-audit.json`](faucet-petgf.support-audit.json) records the
measured connected support bodies, interface islands, bed or model roots and
build-up heights for each part, together with the complete slice's estimated
time and saved-profile filament estimate. Those grams use the preserved
profile's 1.29 g/cm³ density; they are not a measured PET-GF part mass.
The material ledger uses PET-GF15's 1.43 g/cm³ and the actual purchase price.
Object labels in the G-code identify each part's supports.
The current four-part project is prepared but has not been sliced. The
[readiness record](faucet-petgf.readiness.json) identifies that state.
The retained support audit belongs to project SHA256
`8abcdcc0cbd54f5bd9bc1717c0a64d52e1915aafe030af1d31a72f1a8bb2c090`;
its tip and cover readings do not apply to the current geometry and poses.

The [display print project](faucet-display-petgf.md) contains the actual tip
and two complete covers. Its native slice and reports carry the current
working-face support readings and printer readiness for that print.
Support removal, contact finish and retention are physical print readings.
