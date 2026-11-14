# Sculpted faucet PET-GF print project

The [editable project](faucet-petgf.3mf) contains the Sculpted base, shared tip, display cover, above-counter plate and side-down lever. The TPU seals, gasket and umbilical organizer are separate prints. [The print report](faucet-petgf.print.json) binds the source meshes, saved settings and sloped underside paths.

The [selected Sculpted process](sculpted/README.md) uses Mark2's left hardened hotend and white PET-GF. The offline slice lays the base's scaffold, sloped roof and skin before the rest of the plate. The project carries the selected per-part seams, localized cooling, infill reinforcement and tip support aids. Black and white use the same geometry.

| Part | CAD X rotation |
|---|---:|
| Sculpted base | −15° |
| Shared tip | −105° |
| Display cover | −50° |
| Above-counter plate | 0° |
| Lever, print-oriented STL | 0° |

Prepare the project and its executable offline slice.

```sh
tools/run -- tools/hsm/target/release/sculpted-faucet-print-project hardware/printed-parts/faucet/faucet-petgf.3mf --slice-output path/to/new-slice-directory
```

The [slice review](faucet-petgf.support-audit.json) records the native paths and
the complete bead envelope after the sloped underside stage.
Use the [assembly guide](../../faucet-assembly-guide/faucet-assembly-guide.pdf) and
[flavor-line specification](flavor-lines/README.md) for the current tubing and interfaces.
