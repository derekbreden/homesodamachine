# Sandbox

A concept, a throwaway part or a study starts here, in Rust on the `hsm` kernel. A concept is
one file in `examples/`. It needs no crate and no manifest edit, and the build reads none of
it. Copy the worked example, then edit it and rerun it:

    cp tools/hsm/sandbox/examples/plate.rs tools/hsm/sandbox/examples/<concept>.rs
    tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
        -p hsm-sandbox --example <concept> -- <output directory>

Each rerun recompiles only the concept, against the kernel the workspace has already built, and
writes the viewer's files: `<name>.step`, `<name>.step.npz` and `<name>.step.mesh`. The run
prints the STEP's path. The native `hsm render` command draws its payload with the viewer's
materials and lighting; [the render interface](../README.md#render) lists the camera and
selection options. Run rendering through `tools/run`. Show completed parts through their
published model links, as the [visualize skill](../../../.claude/skills/visualize/SKILL.md) describes.

## What a concept has

[`examples/plate.rs`](examples/plate.rs) uses most of it:

- outlines with holes on a plane, extruded: `Profile::rect`, `Profile::circle`,
  `Profile::polygon`, `with_hole`, `Plane::XY.extrude`;
- booleans on whole solids: `cut`, `union`, `intersect`, `cut_all`;
- moves: `translate`, `rotate`, `mirror`, `placed`;
- lettering in a system font: `Font::find`, `Plane::text`;
- the catalog's colours by name, as the parts in the tree carry them: `hsm_sandbox::material`;
- a model already in the tree, by the path /3d names it with: `hsm_sandbox::part`, and
  `hsm_kernel::import::body` to pick one body;
- the viewer's files: `hsm_sandbox::show`, or `hsm_kernel::part::write_part` for a concept to
  print, which adds the STL.

The kernel's own parts are worked examples too: the nameplate
(`hardware/printed-parts/enclosure/nameplate/nameplate.rs`) cuts the brand mark from its
outlines, and the end cap (`hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_step.rs`) is
a part whose numbers come from other parts.

## Where things go

The output goes in the session's scratchpad or in `.cache/runs/<purpose>-<run-id>`, never in the
tree. Git ignores every file in `examples/` but `plate.rs`, so a concept is never committed by
accident. Delete it when its question is answered. A concept that becomes a part gets a program
of its own, held to [`conversion.md`](../conversion.md) › "What an output is made from".
