# Manual inspection

`hsm-pick` composes browser picks and locates pasted coordinates on existing exports.
`hsm-gcode` reads the paths a saved slice commands. Both run when a question needs them;
neither is a producer, hook or normal-build check.

## Picks and published links

```sh
hsm-pick compose request.json
hsm-pick compose request.json --link
hsm-pick link hardware/manifold-layout/enclosure-assembly.step pick.txt
hsm-pick read pick.txt
hsm-pick read pick.txt --surfaces authored,drawn --radius MM --json
```

An omitted input or `-` reads standard input. `--root PATH` selects the checkout.
The composer takes typed numeric picks, a model and an optional surface from JSON;
[`fixtures/picks.json`](fixtures/picks.json) contains a request and its browser text.
The library's `pick_format::Compose` and `Pick` types expose the same interface to Rust.
`link` accepts existing pick text and writes a published `/3d` URL with `?find=`.
It creates no scene. `demo` prints each geometric pick kind without building geometry.

The reader names each measured file, its hash and its representation. Authored readings
use the fine `.step.npz` model with analytic face records and complete source contributors.
For a standalone STEP with no fine model, the reader uses its existing import payload.
Printed readings use the sibling STL; drawn readings use every selected body in the
viewer payload. `solid:` lines restrict body identity when the export carries it.
Missing representations are reported separately; no import or geometry build starts.
Nearest points lie on the measured facets, including their edges and vertices. A reading
locates a surface; deciding what that surface means remains the current design question.

## Saved printer commands

[`tools/gcode`](../../gcode/README.md) documents the seam, speed and HTML view commands.
They accept a plain G-code file or a selected plate from a saved slice. Project seam paint
is read only for the requested part in its saved plate pose.

## Requested fixtures

```sh
tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-inspection
node --test web/tests/pick-format.test.js
```

Rust and browser tests share the composer fixture. The browser test invokes an already
built `hsm-pick` when available and starts no native compilation. It also checks the shared
fixture without a native installation. These commands add no automatic check path.
