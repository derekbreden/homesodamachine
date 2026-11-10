# Native CI image

[`Dockerfile`](Dockerfile) supplies the toolchain and render dependencies used by
the explicit [derive workflow](../../.github/workflows/derive.yml).
[`hsm-ci-image-digest`](../hsm/cargo-config/README.md) identifies its repository
inputs; [cad-image](../../.github/workflows/cad-image.yml) publishes that exact image.

The derive job compiles the native runner, engine, planner, print driver and
publication commands for its checked-out source. It asks the print driver for the
full wanted output set. The engine validates recorded program inputs and reuses
completed results; changed inputs and absent cache entries determine the work that runs.
Explicit local requests can select target or source aliases through the same driver.

## Reused state

The workflow restores Cargo's `tools/hsm/target` and the engine's existing caches:

- `.cache/hsm/parts` holds compiled programs, recorded runs and immutable output blobs.
- `.cache/hsm/import` holds imported STEP payloads.
- `.cache/realized`, `.cache/meshes` and `.cache/boxes` retain shared geometry and scene data.

`HSM_STORE` names the checkout's native store. `HSM_KEEP_HOURS` in the workflow
retains genuinely reusable records between scheduled runs; the engine still
validates their inputs and output blobs. Cache keys include the image identity,
and each run saves independently completed work, including after a partial failure.

## Completed outputs

CI uses `hsm-print-build --no-publish` and an explicit run directory. The driver
carries completed outputs progressively and writes `receipt.json` plus final
`result.json` telemetry. Native cut comparison and carrying read that receipt;
derived staging accepts only declared outputs of usable target records. Failed
and blocked outputs stay out while independent successes can land.

The source-head check before landing the derived commit retains the workflow's concurrent
edit handling. The native producer graph remains authored metadata. Ordinary local
print builds request progressive publication as their producers finish.

[`tools/cloud_session.sh`](../cloud_session.sh) prepares the same native tools in
a cloud checkout. Its `--check` mode reads the setup state without building it.
