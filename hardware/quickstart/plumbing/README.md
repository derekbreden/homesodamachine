# Older-home braided-hose plumbing study

These assets support the separate installer path for a 3/8-inch braided faucet hose and threaded
angle-stop tee. They are not pages or build dependencies of the modern push-fit Quick Start.

`plumbing_scenes.py` generates four registered under-sink installation scenes:

- `plumbing-valve-on` — the original braided faucet supply is connected directly to the open
  quarter-turn cold-water stop.
- `plumbing-valve-off` — the same scene with the lever rotated 90 degrees across the flow path.
- `plumbing-pre-tee` — the stop is closed and bare; the faucet connector, tee, and white appliance
  branch are separated with visible air at every mating face.
- `plumbing-tee-installed` — the tee is seated between the stop and faucet supply, with its white
  1/4-inch appliance branch connected at the side port.

All objects are modeled solids. There are no instruction arrows or text inside the CAD.

## Generate

From the repository root:

```sh
tools/cad-venv/bin/python hardware/quickstart/plumbing/plumbing_scenes.py --render
```

This command regenerates only these four STEP scenes and their `.step.mesh` payloads under
`hardware/quickstart/plumbing/out/`, then writes the four final PNGs under
`hardware/quickstart/plumbing/art/`. Use `--out-dir` and `--art-dir` to override them separately.

## Registered frame

- World `+X`: installer right.
- World `+Y`: away from the wall and into the cabinet.
- World `+Z`: up.
- Finished wall face: `Y = 0`.
- Valve outlet seating face: `(0, 50, 145)` mm.
- Installed tee bottom: `(0, 50, 132)` mm.

Use the same literal viewport for every state:

```text
camera direction  (1.05, 1.70, 0.62)
target            (10, 53, 160) mm
up                (0, 0, 1)
orthographic span 105 mm half-height
output            2000 x 1100 px
ground / fog      off
```

The wall slab is identical in all four STEP files and provides the same source bounds; the explicit
viewport fixes the scale and registration pixel-for-pixel.
