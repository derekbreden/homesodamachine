# Regulator and connected-route evidence

The selected placement is **+1.5 mm inboard on the shared split/regulator column,
30° regulator roll, and no aft displacement**. These frozen probes support that
selection against the completed assembly STEP
`fdaddbd03976b6f843df4cd5059635640a75a0676a1c7ba2e893d8737acb37b3`.
They are bounded candidate evidence; final regenerated geometry, gates and print
qualification remain separate.

| Reading | Preserved result |
| --- | ---: |
| Fluid-1 to front-top, native air | 1.486581 mm |
| Regulator to funnel, native air | 1.560313 mm |
| Regulator inlet lead | Full requested 17.175 mm cast, no hit |
| Fluid-1, fluid-2, water-2, water-3 minimum bends | R14 mm each |
| Water-3 to front-top / back-top | 1.325 mm each |
| Rejected 10 mm aft alternative: fluid-2 / water-2 overlap | **152.684598 mm³** |

[report.json](report.json) retains the selected/rejected values, close seating
readings and screening limits. Empty near-neighbor lists are not measured exact
global minima. The old back-top anchor and water-3 lid-bearing distances remain
explicit; they do not waive final regenerated seating and clearance checks.
Fluid-14 is covered by its separate proof and is outside this package.

The original results are preserved byte-for-byte under [raw](raw/), from
`/tmp/scanner-review/integration-correction/final-route-gaps/`:

- [regulator-column-probe.json](raw/regulator-column-probe.json)
- [regulator-options.json](raw/regulator-options.json)
- [connected-routes.json](raw/connected-routes.json)
- [connected-routes.log](raw/connected-routes.log)
- [connected-routes-verified-frames.log](raw/connected-routes-verified-frames.log)
- [current-ports.json](raw/current-ports.json)

The two column/options logs are also retained. The verified-frames log matches
`connected-routes.json` exactly. It uses the completed facts' published ports and
translates retained valve ports only after proving zero native added/missing
volume for both translated valve bodies. The earlier connected-routes log is
retained as an intermediate reading.

Three exact script snapshots are in [scripts](scripts/), with `.py.txt` extensions
so they remain archival text. [artifact-manifest.json](artifact-manifest.json)
records every original path, retained path, byte count and SHA-256.
**Do not rerun these scripts against current sources:** they add `dx` to the column
loaded at execution, and production source already includes +1.5 mm. They also
read live canonical STEP/facts and retained temporary valve inputs. A reproduction
must restore the matching probe source/input state or use a new absolute-pose
checker. The result files do not record a complete imported-source closure.

The [readiness update plan](readiness-update-plan.md) applies after the final
combined gates and exact receipt are available. This package does not mark any
queued plate ready or modify the immutable launch/cancellation records.
