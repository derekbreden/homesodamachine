# Back-top: unsupported fine roof rounds

Both visible roof side rounds have painted support blockers. Their complete 0.08 mm band
continues from the 0.08 mm first layer through print Z 9.28 mm, covering the roof curves and
their fluted run-outs. The rest of the model uses the inherited 0.24 mm process.

The blockers are the only change to the prepared v6 input: every vertex, triangle, placement,
layer range and process setting is identical. The native slice retains all 7,024 blocked
triangles and all 40 labelled functional support interfaces. Their XY bounds and upper Z
stations match; one interface begins 0.007 mm higher after support layer scheduling changes.
The separate 0.59 mm-high east-roof support sliver is absent.

This applies Derek's direction to keep visible 0.08 mm rounds unsupported. The completed
[tee-carrier trial](../../../../tee-carrier/physical-acceptance.json) has a clean upper curve
and localized lower-curve curling, with a fan-off thermal trial in progress. This support
exclusion review does not establish the roof rounds' physical finish.
Supports for the independent internal and mounting features remain. The native slice has
15 support bodies, including one unlabelled internal body beginning above print Z 12 mm.
The roof projection measurements include bed feet serving higher features, so they are not
support-contact counts.

The archive is prepared offline and has not been sent to a printer. This review establishes
the roof exclusions, layer heights and retained functional contacts; it does not replace the
complete support-removal and current-input review for a print request.

`prepare.py` binds the original input and current geometry by digest, adds the face annotations
and invokes native Bambu Studio. `verify.py` checks the exported archive and emitted paths.
`preparation.json`, `verification.json` and `support-audit.json` retain their readings.
