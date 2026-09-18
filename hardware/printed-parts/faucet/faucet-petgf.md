# Faucet PET-GF print project

[`faucet-petgf.3mf`](faucet-petgf.3mf) contains all four parts on one plate,
with separate spaces for their automatic tree supports and brims.

| Position | Part | Rotation about the CAD X axis |
|---|---|---:|
| Left | Faucet shell base | −15° |
| Right rear | Faucet shell tip | −105° |
| Far right rear | Faucet display cover | +130° |
| Right front | Above-counter plate | 0° |

The cover prints with its broad planar bezel face down and its open underside up.
The above-counter plate stands on its gasket face, with the locating pedestals up.
The base's long straight neck is 15° from vertical. The tip uses the angular
midpoint of its gooseneck sweep as its print direction. Supports are removed
before hardware assembly.

The project takes the Bambu Lab H2C 0.4 mm printer, 0.24 mm process and
Polymaker PET-GF settings from the shared [`petgf.3mf`](../petgf.3mf).
`refresh_print_project.py` copies that profile's complete settings and embedded
filament settings, replaces the four meshes from their generated STLs, seats
them on the bed and places them within the shared printable area of both
extruders. `--settings-from` selects an explicit alternative profile.

The saved user process preset `0.24mm PET-GF faucet` includes the 0.45 mm
support top gap. The saved user filament preset `Polymaker PET-GF @BBL H2C`
includes the shared profile’s 0–70% cooling and 265/280 °C temperatures.
The project reopens without an unsaved support-preset indicator.

The shared profile uses a 0–70% part fan according to layer time, with cooling
off for the first three layers. In this four-part slice, the base's final 10 mm
of outer walls receives 68–70%, reaching 70% at the top; the tip's final 10 mm
receives 63–68%. These are emitted G-code readings. Nozzle temperatures are
265 °C for the first layer and 280 °C thereafter, with an 80 °C textured plate.

Regenerate the CAD/STL files, then refresh the project:

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/refresh_print_project.py
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
The current offline slice completes successfully with no slice warnings. It
estimates 4 h 25 min 59 s and 125.20 g under the saved profile. The four parts'
actual extruded toolpaths, including supports and brims, have at least
24.53 mm of shared-bed border and 28.15 mm separation. The refresh checks
require at least 15 mm and 10 mm respectively. Removal effort and contact
finish are read from the physical print.

## Support reading

The slice generates one bed-rooted support body for the base and two tiny
single-layer patches classified as model-rooted. The tip has one bed-rooted
body, the cover has two and the plate has three.
The main base tree ends at print Z61.16 mm, below the exposed long neck.
Twenty-two base interface islands are explicitly labelled, beginning at the bed
under the tilted foot and continuing inside the lower body. The two isolated
patches at Z11.48 mm have no labelled
interfaces. The tip's support ends at Z134.60 mm; its contacts are unlabelled.
The cover has two labelled interfaces beginning at Z14.84 mm after 14.64 mm of build-up.
Other contacts have no explicit `Support interface` labels; their contact-island count and
build-up to first contact remain unknown. An empty interface list on a
retained body does not mean that the part prints without support.

The regions below identify the retained supports against the CAD and their
toolpath bounds. Exact contact boundaries on unlabelled bodies are a physical
print reading.

| Piece / body | Root | Supported region and retained function |
|---|---|---|
| Base / tree-1 | Bed | Counter-end face, plate and donor pockets, curved aft lever-roof underside and lower signal passage. The exposed long neck carries no support. Cleanup uses the bottom cable/flavor passage and donor/lever openings before fitting the metal body or plate. Removal at the roof and small cable branch needs a physical reading. |
| Base / trees 2–3 | Model | Two isolated patches under the tilted counter-end face at print Z11.48 mm, with no labelled interfaces. Clear them before fitting the plate. |
| Tip / tree-1 | Bed | The tree spans the neck-joint end and open display-chassis interior. Its exact contacts are unlabelled. Preserve the annular engagement, tube and ribbon passages, retaining grooves and metal-foot supports with 3 × 3 mm bearing faces and 2 mm depth. Inspect the curved neck and working faces during removal, before tubes and display installation. |
| Cover / trees 1–2 | Bed | Undersides of the broad retaining lips: one support body reaches each lip. The supports rise from Z0.20 to Z15.08 mm in the print pose, with labelled interfaces from Z14.84 mm. The bezel lies directly on the bed. Remove through the open underside before installing the display, preserving the lip bearing faces. |
| Plate / trees 1–3 | Bed | The three underside screw counterbores. Their flat seats carry the factory base screws; the supports are removed through the counterbore openings. |

The support reader's `--include-unlabelled-support` option produces this
complete body inventory. Callers that omit the option retain the explicit
interface-only reading.

[`faucet-petgf.readiness.json`](faucet-petgf.readiness.json) records the submitted
Mark2 job `faucet-open-lever-mark2.gcode.3mf`, its archive and source hashes,
native toolpath audits and confirmed startup telemetry. It uses the left external
PET-GF spool and +0.04 mm Z trim; combined with the stock −0.02 mm textured-plate
correction, the emitted trim is +0.02 mm. The submitted archive estimates
4 h 25 min 57 s and 125.20 g across 1,019 layers. Bed leveling is On, timelapse
Off, and flow and nozzle-offset calibration Auto. Startup telemetry at
2026-09-18 05:01:05 UTC reports the exact job RUNNING with no reported errors.
