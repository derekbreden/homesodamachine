# Reading what a slice commands

Run by hand. Nothing here is a hook, gate or build step.

These tools read the G-code inside a Bambu Studio `.gcode.3mf`, the moves the printer will be
sent, and answer questions about a whole part rather than a chosen window of it.

| Question | Tool |
|---|---|
| Where does the main exterior seam sit, over the part's whole height? | `seams.py` |
| What speed is commanded at this place on the outer wall, layer by layer? | `speeds.py` |
| Show it, the way Bambu Studio's slice preview does | `view.py seams` or `view.py speed`, published as an Artifact |

```bash
tools/cad-venv/bin/python tools/gcode/seams.py SLICE.gcode.3mf PRINT.json --part industrial-shell-base --project PROJECT.3mf
```

```bash
python3 tools/gcode/speeds.py SLICE.gcode.3mf --layers 26-33 --at leftmost
```

```bash
tools/cad-venv/bin/python tools/gcode/view.py speed "A=FIRST.gcode.3mf" "B=SECOND.gcode.3mf" --mark-layers 26-33 --at leftmost --view left --title "Elbow lip speeds" --out PAGE.html
```

`PRINT.json` is the `*.print.json` a preparer writes beside its project. It supplies the part's
identify ID and its pose on the plate, so seams are measured in the part's own CAD frame. Pages
go in a scratchpad. Look at one with `node tools/viz/shot.mjs PAGE.html PAGE.png` before
publishing it.

## Reading rules

[`toolpaths.py`](toolpaths.py) holds them, and every tool here reads through it.

- A run is one continuous extrusion path of a layer and object. A travel, a retraction, a layer
  change, an object change or a feature outside the set ends it.
- Feed-only lines (`G1 F876`), `M204` and the switch between "Outer wall" and "Overhang wall"
  happen mid-perimeter, so they do not end a run.
- A zero-E connector no longer than 0.02 mm, with at most 0.002 mm Z movement,
  continues the wall run. Bambu emits a 0.001 mm connector at some scarf ramp
  boundaries; splitting there falsely labels the ramp's end as another seam.
- Feed is modal. A move carries the last F before it, so a wall setting does not fix every wall
  move's speed. Overhang speeds and the cooling slowdown replace it on the moves they cover, and
  those moves can still be labelled "Outer wall".
- Bambu extrudes holes counter-clockwise too. A layer's exterior is its largest-area loop.
- A loop's first point is its seam start, the bottom of a scarf ramp. Its last point is the end
  of the scarf overlap.
- A place is found by geometry on each layer: a crossing of the part's CAD X = 0 plane, an
  extreme point, or the point nearest a plate X,Y. It is never a guess at which run is which.
- Layers are numbered from 1, as Bambu Studio's layer slider numbers them.
- Enforcer paint is read from the selected part's mesh member, using that part's
  pose. Other painted parts in a project are not mixed into its paint geometry.

The largest-loop profile includes pedestal, plug and terminal contours when they
are that layer's exterior. An offset on those contours is not a verdict about
the exposed main-body seam. The faucet's
[feature-aware reading](../../hardware/printed-parts/faucet/industrial/seam-placement/rear-center-v2/README.md)
retains every exterior run and distinguishes those features from its rear show
surfaces.

## Known readings

To check a change to the reader, run it against these slices and compare:

| Slice | Reading |
|---|---|
| `hardware/printed-parts/faucet/industrial/prints/2026-10-13-rear-seam-base-only-mark2` | Base seam −1.955 mm at print Z 13.64 (layers 1–64 past 1 mm); +1.556 mm at print Z 61.64 (layers 425–473); 0.45 mm or less above print Z 70 |
| `hardware/printed-parts/faucet/industrial/prints/2026-10-13-a2-back-mark2` | Base seam 12.278 mm at print Z 163.16 |
| `hardware/printed-parts/faucet/industrial/prints/2026-10-13-complete-rear-seam-base-tip-mark2` | Base exterior loop at most 0.543 mm over the complete height; the zero-E connector at print Z64.64 remains inside its rear-starting scarf run |
| `future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-engineering-z000-mark1` | Leftmost lip, layers 26–33: 14.60–17.60 mm/s |
| `future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1` | Leftmost lip, layers 26–33: 15.83–21.80 mm/s; the rest of each loop 10.0 mm/s |
| `future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1` | Leftmost lip, layers 26–33: 10.00 mm/s |
