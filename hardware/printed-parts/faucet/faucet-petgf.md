# Sculpted faucet PET-GF print project

The [editable project](faucet-petgf.3mf) contains the current 4 mm flavor-line Sculpted base, shared tip, display cover, above-counter plate and side-down lever. The TPU seals/gasket and umbilical organizer are separate prints. [The print report](faucet-petgf.print.json) binds the source meshes and saved settings. Native slicing and support review of this geometry remain pending; the project does not submit a printer job.

The [selected Sculpted process](sculpted/README.md) uses Mark2's right hardened 0.4 mm hotend, white PET-GF, a 0.20 mm first layer and 0.24 mm nominal layers thereafter. The project retains the selected per-part seams, localized cooling, infill reinforcement, segmented base-rim aids and tip support aids. Tree(auto)/Default handles the remaining surfaces. Black and White faucet styles use the same geometry.

| Part | CAD X rotation |
|---|---:|
| Sculpted base | −15° |
| Shared tip | −105° |
| Display cover | −50° |
| Above-counter plate | 0° |
| Lever, print-oriented STL | 0° |

Rebuild the editable project manually with:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/sculpted/prepare_print_project.py \
  hardware/printed-parts/faucet/faucet-petgf.3mf
```

The [readiness record](faucet-petgf.readiness.json) distinguishes the current preparation from its retained native archive. Dated native and physical records keep their identified source geometry and acceptance scope. They establish no black 4 mm tube fit or current support-removal result. Use the [assembly guide](../../faucet-assembly-guide/faucet-assembly-guide.pdf) and [flavor-line specification](flavor-lines/README.md) for the current tubing and interfaces.
