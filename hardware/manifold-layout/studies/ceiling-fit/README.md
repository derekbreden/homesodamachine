# Water header, ceiling pockets and first neighbours

The pump inlet TPU elbow is clocked **27.5° below horizontal**. V-K and the entire
rigid header translate **1.469 mm downward** and **0.725 mm toward the back wall**.
Their rotations are preserved: valves remain vertical, the water run stays
straight and the fitting turns remain square. The pump, corrected rear foot and
carbonator discharge group retain their poses.

The lower pump-side elbow has **1.494 mm clearance above the plain cold-core
cap**; V-A's outlet elbow has **1.639 mm**. The nominal clocking limit is about
**2.856 mm of lowering** from the 25° reference, where the pump-side elbow reaches
the cap. Keeping 1 mm of cap clearance permits about 1.927 mm. These limits
describe the reference meshes, not manufacturing tolerance. The selected pose
does not use all of that room. [`lowering-limits.json`](lowering-limits.json)
records the evaluated cases.

## Ceiling

The current-size enclosure retains its exterior roof at **Z355**. Its ideal
9 mm ceiling starts at Z346; two plain rectangular recesses open upward to a
common flat roof at **Z352**, leaving **3 mm of solid ceiling** above both.
The highest ASSE surface is at **Z350.876**, leaving **1.124 mm** above it;
the regulator has 2.124 mm to its pocket roof.

| Recess | X span | Y span | Depth |
|---|---:|---:|---:|
| ASSE and both TPU cuffs | 26–49 mm | 328–397 mm | 6 mm |
| Regulator | −40–−15 mm | 270–336 mm | 6 mm |

The footprints enclose triangle surfaces above Z345, including exact triangle-edge
crossings at that height, with 1 mm added in X/Y and dimensions rounded outward.
Surfaces below that threshold clear the ordinary underside by at least 1 mm.
The recesses remove 19,422 mm³ from this rear ceiling segment. Its native export
is one valid solid. This establishes the requested geometric stock; it is not
a load-capacity or print-acceptance result.

[`ceiling-plan.json`](ceiling-plan.json) drives [`ceiling.py`](ceiling.py).
The segment begins at Y244, behind the current funnel/frame. The forward roof
and funnel interface are outside this ceiling model.

## First surrounding components

- **Rear water bulkhead:** its inboard mouth is aligned with the ASSE at
  X37.25, Z334.376. A straight tube spans **32.125 mm between mouths**, with
  15 mm modeled insertion in the TPU and an estimated 12.7 mm in the bulkhead.
  The 9 mm rear wall has a 17.44 mm through-hole. An estimated 20 mm AF × 4 mm
  retention nut seats on the inner face; the reference barrel leaves 2.29 mm
  before the far socket shoulder. The nut models occupied space, not measured
  threads or retention capacity.
- **Populated main PCB:** stands beside the pump in the +X aft corridor,
  3 mm above the cap. Its complete component/connector and THT-tail model spans
  X71.15–92.25, Y352–442.816 and Z256.4–329.2. Four straight Ø10 mm standoffs
  reach the board's existing M3 mounting holes on their 78 × 66.3 mm pattern.
  Boss length is 8.25 mm; the Ø4 mm blind pilots are 6 mm deep. The modeled tails
  have 6.25 mm to the wall and at least 0.477 mm to the wall/posts. The populated
  board clears V-K by 2.410 mm and the pump by 17.055 mm.
- **Current funnel and frame:** retain their installed reference poses forward
  of the water group, making that occupied space visible. Their capacity and
  planned enlargement are outside this study.

The PCB standoff locations derive from `PCBA_TURN`, the native board underside
and the existing MH1–MH4 coordinates in
[`pcba_tray.py`](../../../printed-parts/electronics/pcba-tray/pcba_tray.py).
[`pcb-terminals.json`](pcb-terminals.json) moves the nominal electrical connector
datums with the board so later wire routes can use the same pose.

## Model scope and reproduction

This is an implementation study separate from the production appliance pack.
It uses current enclosure size, plain 9 mm walls, the current cap height Z253.4,
and a cropped plain core block for display. Native ceiling, wall, bore and PCB
standoff solids are in [`parts/`](parts/). Existing shell cuts, mounts and other
equipment are omitted. The remaining electronics, WAGOs, gas circuit and complete
installed wire/tube routes are not placed here.

The manual mesh check finds no unrelated-body intersections among the selected
plumbing, ceiling and contextual components. Intended fitting interfaces, board
seating faces, the funnel/frame interface and wall corner faces are identified
in the mate records. The separate PCB-tail query checks the material behind the
board against the wall and posts. These are reference-geometry checks.

[`context-sources.json`](context-sources.json) binds the frozen component snapshots
to the installed assembly mesh and generator sources. That upstream pointer
marks source reproduction of the assembly payload as unproven; this study retains
the artifact identity and that evidence limit. [`context.json`](context.json)
records poses. The native wall generator is
[`context_hardware.py`](context_hardware.py); no production module is imported
by either native context generator.

From the repository root:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/ceiling-fit/study.py --plan-only
PYTHONPATH=. tmp/takeover/cadq "Water ceiling" -- tools/cad-venv/bin/python \
  hardware/manifold-layout/studies/ceiling-fit/ceiling.py \
  --plan hardware/manifold-layout/studies/ceiling-fit/ceiling-plan.json \
  --out hardware/manifold-layout/studies/ceiling-fit/parts/ceiling
PYTHONPATH=. tmp/takeover/cadq "Water wall context" -- tools/cad-venv/bin/python \
  hardware/manifold-layout/studies/ceiling-fit/context_hardware.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/ceiling-fit/study.py --check
```

Checks run on demand. The study adds no production build dependency or automatic
gate. Production enclosure geometry and its generated assembly remain unchanged.
