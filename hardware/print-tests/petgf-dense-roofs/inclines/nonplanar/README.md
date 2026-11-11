# Bounded faucet contact bands

This study changes the layer family near the inclined contact of the complete
retained faucet coupon. Its [parameters](parameters.json) own the band spacing,
blend region and motion limits. The [Rust recipe](experiment.rs) maps the frozen
posed mesh into slicer coordinates and restores the cooled native G-code to
physical coordinates. It contains no printer submission operation.

Run the recipe as a sandbox example through `tools/run`. Its `geometry`
operation takes the frozen posed mesh, parameters and an output directory;
`paths` takes native G-code, the saved mapping and an output G-code path.
Retain the native plate references when packaging the restored paths with the
physical target model.

The [active Mark1 article](../prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/print-job.json) binds the complete coupon, component meshes, mapping and executable. The fins carry the same interface as the trees. The [completed comparison](https://github.com/derekbreden/homesodamachine/blob/b06ab316f6c796a314a30f0dc8ffda66113b2e4e/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-gap024-widebands-mark1/physical-result/physical-result.json) supplies the physical rim and insert observations for this test.

The [rim contour editor](rim-contour.rs) reads the restored physical G-code.
It takes the selected object identity, seat center in print coordinates,
seat tilt, rim semi-axes, and supported angular interval. It replaces the
first suspended outer wall with matching arcs and trims the neighbouring
roads where they meet it. The [prepared Mark1 plate](../prints/2026-11-10-faucet-continuous-rim-mark1/print-job.json)
records the executable and its coverage review.
