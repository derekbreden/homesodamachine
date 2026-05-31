# Quad-stack assembly — 3 source-selection cells stacked

Three [quad-trays](../quad-tray/README.md), each holding its 4 Beduan valves
and 2 Y-dividers, stacked one `stack_pitch` (63 mm) apart. A flat
`cq.Assembly` of pre-positioned solids, exported as one multi-solid STEP.

## Contents

- 3 trays (floor + 2 side walls) at Z = 0, 63, 126. Each floor rests on the
  wall tops below, 3.4 mm over the 56.6 mm valve coils.
- 12 valves (4/tray) and 6 dividers (2/tray) in the cradle/gap positions.
- 21 solids. STEP colors: tray tan, valves dark, dividers blue; the in-repo
  `/3d` viewer renders all gray.

Envelope **210 (X) × 80 (Y) × 189 (Z) mm**.

## Files

- `quad_stack_assembly.py` → `quad-stack-assembly.step`
- `drawings/engineering-drawings/quad-stack-iso.py` → `quad-stack-iso.svg`
  (CadQuery HLR isometric — visible edges solid, hidden dashed)

```
tools/cad-venv/bin/python quad_stack_assembly.py
tools/cad-venv/bin/python drawings/engineering-drawings/quad-stack-iso.py
```
