# Faucet print artifacts

The two retained faucet plate archives require regeneration from current meshes with infill-only reinforcement before printing. Their archived readings retain their identified geometry and process scope. See the [current Industrial preparation](../industrial/prints/2026-10-11-infill-only-reinforcement-review/README.md).

The [complete Industrial selection](../industrial/selected-print.json)
contains the base, shared tip, display cover, counter plate and side-down
lever. It uses 0.20 mm first bed layers, 0.24 mm normal layers and 0.12 mm
on the two selected base shoulder bands. The base has one continuous
six-wall solid foot with Arachne and 15% infill/wall overlap. The cover's
wings extend 0.50 mm. The shared tip has a smooth common tube/ribbon passage,
a 70° male plug mating with the base socket, and an unsealed Ø4 mm overflow
drip hole. The [current geometry reading](../vent-qualification/simple-drip-check.json)
and each job's native checks describe their specific scope.

The selected job is authorized for Mark2. Its launch receipt records the one
foreground transaction and exact acceptance separately; preparation tools
do not launch a printer.
The separate above-counter gasket and donor thimble have their own TPU
recipes. The current faucet needs no drain bungs or perimeter insertion tool.

The files in this directory preserve native plates for the two-bung sealed
cavity, with their exact source, archive and G-code hashes. Those artifacts
remain readable; their readiness and containment claims belong to that
identified geometry. They do not establish readiness for the unsealed
shared tip or the extended Industrial cover.

| Retained plate | Native archive |
| --- | --- |
| Sculpted rigid faucet | [Archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/vent-print-readiness/faucet-black-z018-h2c/faucet-black-z018-h2c.gcode.3mf) |
| Industrial rigid faucet | [Archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/vent-print-readiness/faucet-industrial-black-z018-h2c/faucet-industrial-black-z018-h2c.gcode.3mf) |
| Sculpted bungs and counter gasket | [Archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/vent-print-readiness/vent-bungs-tpu85a-h2c/vent-bungs-tpu85a-h2c.gcode.3mf) |
| Industrial bungs and counter gasket | [Archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/vent-print-readiness/vent-bungs-industrial-tpu85a-h2c/vent-bungs-industrial-tpu85a-h2c.gcode.3mf) |
| Perimeter insertion tool | [Archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/vent-print-readiness/vent-seal-tool-petgf-z018-h2c/vent-seal-tool-petgf-z018-h2c.gcode.3mf) |

Physical observations remain beside the parts and in the
[mechanical qualification index](../../../mechanical-qualification/README.md).
Commanded support paths and CAD access do not establish easy physical
cleanup, fit, strength or lifetime.
