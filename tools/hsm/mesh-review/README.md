# Printed-mesh review

`geometry-lint` ranks local anomalies in the saved STL and emits Find text for the
published model. It runs when inspecting a changed print, after publication.

Build the native command through the shared host scheduler:

    tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-mesh-review

Inspect a saved piece:

    tools/run -- tools/hsm/target/release/geometry-lint hardware/printed-parts/enclosure/enclosure/enclosure-pump-retainer.stl

`--classes` selects the question: `step`, `bump`, `sliver`, `ceiling`, `slope`, `thin`
or `ledge`. `--all` includes answered findings; `--json` emits the complete report.
`--models DIR` reads a mold project's cavity and inverted core together.

Findings retain the saved model's coordinates. Known production pieces use their
print direction and lean; `--print-up` and `--tilt-x` state a different preparation
explicitly. The build direction informs unsupported faces, while picks continue to
locate those faces on the model.

`thin` measures closest opposing facets and rejects pairs that cross air or run
along a nearby surface. Its sampled regions rank the places where material is
thinnest; they do not infer the design's reason for that stock.

`--sources MODEL.step.npz` reads the native writer's emitted-facet mapping only
when its digest binds these exact STL bytes. Missing, stale or malformed optional
bindings report unknown attribution and leave the geometry readings unchanged.

Answers live beside the piece's path in
[`hardware/printed-parts/lint-answers/`](../../../hardware/printed-parts/lint-answers/AGENTS.md).
Only an anchored finding receives its explanation. Ranked thin material and ledges
retain their place in the report with that explanation alongside them.
