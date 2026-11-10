# Assembly scenes

Named subsets of the built machine are posed for the parts viewer and bench
assembly guides. The current native [installed machine](../../manifold-layout/installed_machine.rs)
composes each view from its fastening, rider, anchor and bearing tables in
[scenes.rs](../../manifold-layout/installed-machine/scenes.rs). Cold-core members use
that model's own solids in the machine's frame.

The native scene exporter draws the current shared meshes and writes `glb/` views
with the machine. Run the focused print build when those source placements or
parts change; completed producers reach the website while other parts continue.

[Letter shop guides](../guides/README.md) own the human instructions. Their
illustrations and PDFs are authored and built by hand outside the print build.
