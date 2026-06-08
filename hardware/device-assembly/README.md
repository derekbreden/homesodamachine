# Kitchen Edition device assembly

Every internal subsystem packed inside the H2C left-nozzle build envelope
(325 × 320 × 320 mm). Detailed STEP imports where they exist, placeholder
boxes for parts that have no STEP yet (condenser+fan, SeaFlo diaphragm pump).
A layout model for fit and visualization, not a printed part.

## Frame

+X right, +Y back, +Z up. Origin at the lower-front-left corner of the H2C
build envelope.

## Arrangement

| Item | XYZ range (mm) | source |
|---|---|---|
| Cold-core foam shell | X [0, 283]  Y [0, 181]  Z [0, 213] | [foam-shell.step](../printed-parts/cold-core/foam-shell/) |
| Compressor shroud | X [0, 178]  Y [181, 314]  Z [0, 152] | [compressor-shroud.step](../cut-parts/compressor-shroud/) |
| Source-select tray | X [178, 267]  Y [181, 244]  Z [0, 225] (vertical) | [source-select-assembly.step](../printed-parts/valve-manifold/source-select-tray/) |
| Bag-circuit tray | X [178, 251]  Y [244, 307]  Z [0, 158] (vertical) | [bag-circuit-assembly.step](../printed-parts/valve-manifold/bag-circuit-tray/) |
| Condenser + fan | X [0, 178]  Y [0, 151]  Z [213, 269] | placeholder box, 178 × 151 × 56 |
| SeaFlo pump | X [178, 238]  Y [0, 175]  Z [213, 288] | placeholder box, 60 × 175 × 75 |
| Pump case 1 | X [238, 312]  Y [0, 136]  Z [213, 289] | [pump-case-assembly.step](../printed-parts/flavor/pump-case/) |
| Pump case 2 | X [0, 74]  Y [151, 287]  Z [213, 289] | same |
| Bib-gate tray | X [178, 317]  Y [181, 254]  Z [225, 288] (flat) | [bib-gate-assembly.step](../printed-parts/valve-manifold/bib-gate-tray/) |
| Nozzle-gate tray | X [74, 173]  Y [151, 224]  Z [213, 276] (flat) | [nozzle-gate-assembly.step](../printed-parts/valve-manifold/nozzle-gate-tray/) |

Contents envelope **317.3 × 314.0 × 289.4 mm** — fits both the 3 mm-walled
enclosure inside (319 × 314 × 314) and the raw H2C bed (325 × 320 × 320).
Zero solid collisions.

The cold core sits front-left on the floor; the compressor shroud and the
source-select + bag-circuit trays fill the back-bottom strip; the condenser,
SeaFlo, two pump cases, and the bib-gate + nozzle-gate trays form a second
layer above the cold core. Layout is first-fit-decreasing on bounding-box
bricks; reflects future.md subsystem inventory, not its faucet-up cabinet
geometry.

## Regenerate

`tools/cad-venv/bin/python hardware/device-assembly/device_assembly.py`
→ `device-assembly.step`. Placement constants live at the top of `build()`
in `device_assembly.py`.

## Placeholder dimensions

- **Condenser + fan**: 178 × 151 × 56 mm. The 56 is calipered (fan + finstack
  airflow-axis depth combined); the 178 × 151 face matches two dimensions of
  the compressor envelope (where they share back/side flush against the same
  shroud plane).
- **SeaFlo 22-series diaphragm pump**: 75 × 60 × 175 mm, body only, no
  mounting brackets.
