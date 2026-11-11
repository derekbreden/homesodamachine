# Reading what a slice commands

Run by hand. Nothing here is a hook, gate or build step.

These tools read the G-code inside a Bambu Studio `.gcode.3mf`, the moves the printer will be
sent, and answer questions about a whole part rather than a chosen window of it.

| Question | Tool |
|---|---|
| Where does the main exterior seam sit, over the part's whole height? | `hsm-gcode seams` |
| What speed is commanded at this place on the outer wall, layer by layer? | `hsm-gcode speeds` |
| Show the commanded walls with seam markers or speed colours | `hsm-gcode view seams` or `hsm-gcode view speed` |
| Watch consecutive layers deposit under the moving head and bed | `hsm-gcode view playback` |

```bash
hsm-gcode seams SLICE.gcode.3mf PRINT.json --part industrial-shell-base --project PROJECT.3mf
```

```bash
hsm-gcode speeds SLICE.gcode.3mf --layers FIRST-LAST --at leftmost
```

```bash
hsm-gcode view speed "A=FIRST.gcode.3mf" "B=SECOND.gcode.3mf" --mark-layers FIRST-LAST --at leftmost --view left --title "Elbow lip speeds" --out PAGE.html
```

```bash
hsm-gcode view playback SLICE.gcode.3mf --layers FIRST-LAST --title "Print motion" --out PAGE.html
```

Playback runs continuously across the selected layers, with a timeline, playback speed and
print, nozzle-following and whole-printer cameras. It draws the emitted deposition paths,
moves the bed and its deposited material opposite commanded Z, and keeps the head in the
gantry plane. `--bed-model` accepts the binary build-plate STL from the printer's profile;
the remaining H2C hardware is a simplified reference model. Start at the first layer when
the view needs all previously deposited material.

Its motion planner reads commanded axis speed limits, acceleration, instantaneous junction
speed limits and feed overrides. Forward and reverse lookahead passes join consecutive moves;
each move accelerates, cruises and brakes. Timing is estimated: firmware actions, thermal
waits, compensation, input shaping and interventions during the print are outside the study.
This is an on-demand view of a slice and starts no printer operation.

`PRINT.json` is the `*.print.json` a preparer writes beside its project. It supplies the part's
identify ID and its pose on the plate, so seams are measured in the part's own CAD frame.
`--csv` retains each seam reading and `--json` saves the summary. The speed command's
`--json` retains its layer readings. A plain `.gcode` file is also accepted.

`view seams` accepts `--compare "label=SLICE:PRINT.json"` to overlay another slice in the
selected part's frame, `--project` to show its seam-enforcer paint and `--frame-z` to focus
the view. Both view commands write an HTML page at `--out`. Keep pages in a scratch run
and inspect them when the current question needs a picture.

## Reading rules

[`gcode.rs`](../hsm/inspection/src/gcode.rs) holds them, and every command reads through it.
The rich run reader shares the native print preparation's word lexer and archive reader.
Ordinary bead and support reviews use their existing deposited-road representation.

- A run is one continuous extrusion path of a layer and object. A travel, a retraction, a layer
  change, an object change or a feature outside the set ends it.
- Feed-only commands, acceleration changes and the switch between "Outer wall" and "Overhang wall"
  happen mid-perimeter, so they do not end a run.
- A nonnegative E-word move continues the commanded wall path even when Bambu rounds its
  extrusion to `E0`. Scarf ramps and tails can carry that rounded value. Travels carry no
  E word; numerical E-less hops within the decoder's tolerance continue the current run.
- Feed is modal. A move carries the last F before it, so a wall setting does not fix every wall
  move's speed. Overhang speeds and the cooling slowdown replace it on the moves they cover, and
  those moves can still be labelled "Outer wall".
- Bambu extrudes holes counter-clockwise too. A layer's exterior is its largest-area loop.
- A loop's first point is its seam start, the bottom of a scarf ramp. Its last point is the end
  of the scarf overlap.
- A place is found by geometry on each layer: a crossing of the part's CAD centre plane, an
  extreme point, or the point nearest a plate X,Y. It is never a guess at which run is which.
- Layer numbering follows Bambu Studio's layer slider.
- Enforcer paint is read from the selected part's mesh member, using that part's
  pose. Other painted parts in a project are not mixed into its paint geometry.

The largest-loop profile includes pedestal, plug and terminal contours when they
are that layer's exterior. An offset on those contours is not a verdict about
the exposed main-body seam. The faucet's
[feature-aware reading](../../hardware/printed-parts/faucet/industrial/seam-placement/rear-center-v2/README.md)
retains every exterior run and distinguishes those features from its rear show
surfaces.

## Recorded readings

The faucet's [shared-reader profiles and CSVs](https://github.com/derekbreden/homesodamachine/tree/f0d1e837bdaa383ecb435e62b88c9e1d6d1cf180/hardware/printed-parts/faucet/industrial/seam-placement/rear-center-v2/shared-reader)
retain the complete-height loop readings, selected-part paint checks and numerical scarf
connectors. The pump elbow's [emitted-command record](https://github.com/derekbreden/homesodamachine/blob/f0d1e837bdaa383ecb435e62b88c9e1d6d1cf180/future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/emitted-command-review.json)
binds its reviewed slice and speed reader. Use these records for a focused manual comparison
when changing the decoder.
