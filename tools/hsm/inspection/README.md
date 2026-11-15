# Manual inspection

`hsm-pick` composes browser picks and locates pasted coordinates on existing exports.
`hsm-gcode` reads the paths a saved slice commands. `hsm-project` compares two print projects
by value. Each runs when a question needs it; none is a producer, hook or normal-build check.

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

## Print projects

`hsm-project compare` tells whether a re-prepared project is the one before it by value, and
where it is not. It takes two `.3mf` projects, two `.gcode.3mf` archives or two preparers'
output folders, and lists each member that differs with what differs in it.

```sh
hsm-project compare BEFORE.3mf AFTER.3mf
hsm-project compare BEFORE-FOLDER AFTER-FOLDER [--all] [--limit N] [--mesh-tolerance MM]
```

- JSON members, `.config` settings and records compare by value, with key order ignored. A
  number equals the same number written another way, with trailing zeros or without, wherever
  it appears, inside text too. `different_settings_to_system` names a preset's changed keys
  and compares as a set of them.
- XML compares by element, attribute and text. Children that a key or an id names pair in any
  order; the others pair in order, and the same elements in another order read as such.
- A mesh compares as its triangles and their paint, each corner within `--mesh-tolerance` of
  its counterpart however the vertices are numbered. Triangles in another order are told from
  triangles only one side has, which are located.
- G-code that is equal by value line by line is equal; other G-code goes through the bead
  matching of [`hsm-gcode compare`](../../gcode/README.md).
- Hashes, thread addresses and preparation times, which are dates with their times and Bambu
  Studio's slicing durations, are masked and only counted. A path into A's checkout reads as
  the same path into B's.

Bambu Studio does not always slice one project the same way twice, so slices of two projects
that are equal by value can differ in a few beads. `--all` lists every member with its
verdict. The exit status is 0 when the two are equal by value and 1 when they differ.

`hsm-project` runs the build last installed, so after an edit to its source, build it and
install it again with `hsm-run --install-tools "$PWD" tools/hsm/target/release/hsm-project`.

## Requested fixtures

```sh
tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-inspection
node --test web/tests/pick-format.test.js
```

Rust and browser tests share the composer fixture. The browser test invokes an already
built `hsm-pick` when available and starts no native compilation. It also checks the shared
fixture without a native installation. These commands add no automatic check path.
