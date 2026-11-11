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

The [Mark1 tree trial](../prints/2026-11-11-faucet-trees-only-mark1/print-job.json) binds the complete
coupon to the reviewed executable. The [release observation](https://github.com/derekbredensteiner/homesodamachine/blob/b388123d2ac2fdc31fd091f980334b9c99443ab8/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json)
records the common interface coming off with the supports and leaving open
insert pockets.

The [rim contour editor](../../../../../tools/hsm/print-prep/src/rim_contour.rs)
takes the object identity, seat center, tilt, rim semi-axes and supported
angular interval. It replaces the first suspended outer wall with matching
arcs and trims the neighbouring roads where they meet it. The
[standalone command](rim-contour.rs) uses the same implementation.
