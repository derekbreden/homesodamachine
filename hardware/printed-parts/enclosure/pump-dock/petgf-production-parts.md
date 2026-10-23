# PET-GF pump-dock production parts

The dock's one PET-GF part is the factory's tube setting jig (`enclosure-pump-tube-setting-jig`). The tee wall, its collet plate and the magnet slots are front-top's own material, and the pump tees are purchased.

The tube setting jig prints alone on the `factory-tools` plate, as exported, with the shared [petgf.3mf](../../petgf.3mf): 0.20 mm first layers and 0.24 mm body layers, ordinary/auxiliary cooling off, localized overhang/bridge cooling at 70% above the 50% unsupported threshold, and the shared Tree (auto)/Default support decisions.

Manual offline preparation, without starting a printer:

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py factory-tools --slice --review
```

Bind any production project and emitted paths to the current manufacturing mesh. No native project or print is bound to the jig.
