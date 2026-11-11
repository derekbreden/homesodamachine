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

The [active Mark1 article](../prints/2026-11-10-faucet-nonplanar-bands-mark1/print-job.json)
binds the complete coupon, mapping, actual paths and printer configuration.
This is an experimental contact treatment. It does not qualify another
incline or change the shared Support D profile.
