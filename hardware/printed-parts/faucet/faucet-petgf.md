# Faucet PET-GF print project

[`faucet-petgf.3mf`](faucet-petgf.3mf) contains all four parts on one plate,
with separate spaces for their automatic tree supports and brims.

| Position | Part | Rotation about the CAD X axis |
|---|---|---:|
| Left | Faucet shell base | −35° |
| Right rear | Faucet shell tip | −105° |
| Far right rear | Faucet display cover | +130° |
| Right front | Above-counter plate | 0° |

The cover prints with its broad planar bezel face down and its open underside up.
The above-counter plate stands on its gasket face, with the locating pedestals up.
The shell halves use the angular midpoint of each half's gooseneck sweep as
its print direction. Supports are removed before hardware assembly.

The project carries the Bambu Lab H2C 0.4 mm printer, 0.24 mm process and
Polymaker PET-GF settings saved in its complete `project_settings.config`.
`refresh_print_project.py` preserves those bytes and the embedded filament
settings, replaces the four meshes from their generated STLs, seats them on
the bed and places them within the shared printable area of both extruders.

Regenerate the CAD/STL files, then refresh the project:

```
tools/cad-venv/bin/python hardware/printed-parts/faucet/refresh_print_project.py
```

[`faucet-petgf.print.json`](faucet-petgf.print.json) records the project and
settings hashes, each source STL hash, its watertightness, its exact bed
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
estimates 8 h 2 min 26 s and 149.56 g under the saved profile. The four parts'
actual extruded toolpaths, including supports and brims, have at least
24.95 mm of shared-bed border and 34.03 mm separation. The refresh checks
require at least 15 mm and 10 mm respectively. Removal effort and contact
finish are read from the physical print.

## Support reading

The slice generates one bed-rooted support body for the base, one for the tip
and three for the plate. The face-down cover has no generated supports.
There are no model-rooted support bodies.
One base interface island is explicitly labelled, with 20.64 mm of build-up
to that labelled contact. Other support contacts have no explicit
`Support interface` labels. The audit retains those connected bodies and
records their roots and bounds; their contact-island count and build-up to
first contact remain unknown. An empty interface list on a retained body
does not mean that the part prints without support.

The regions below identify the retained supports against the CAD and their
toolpath bounds. Exact contact boundaries on unlabelled bodies are a physical
print reading.

| Piece / body | Root | Supported region and retained function |
|---|---|---|
| Base / tree-1 | Bed | Counter-end face, lower body and underside of the continuous neck roof. The plate seats, donor opening and lever clearance keep their full working shapes. Its labelled interface 1 supports the first turn of the lower signal lane, at CAD X6.60–10.60 / Y16.28–18.53 / Z13.93–15.70 mm. Cleanup uses the bottom cable/flavor passage and actual donor/lever openings before fitting the metal body or plate. Removal at the roof and small cable branch needs a physical reading. |
| Tip / tree-1 | Bed | Curved neck and open display-chassis underside region. The annular neck engagement, tube and ribbon passages, 3 mm snap arms and metal-foot supports retain their working sections. Support removal precedes tubes and display installation. Its exact unlabelled contact boundaries need the physical print. |
| Cover | — | No support toolpaths in this slice. The planar bezel rests on the bed; the shroud and internal receivers build toward the open underside. |
| Plate / trees 1–3 | Bed | The three underside screw counterbores. Their flat seats carry the factory base screws; the supports are removed through the counterbore openings. |

The support reader's `--include-unlabelled-support` option produces this
complete body inventory. Callers that omit the option retain the explicit
interface-only reading.
