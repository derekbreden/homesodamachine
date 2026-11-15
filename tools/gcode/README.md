# Reading what a slice commands

Run by hand. Nothing here is a hook, gate or build step.

`hsm-gcode` runs the build last installed, so after an edit to its source, build it and install
it again with `hsm-run --install-tools "$PWD" tools/hsm/target/release/hsm-gcode`.

These tools read the G-code inside a Bambu Studio `.gcode.3mf`, the moves the printer will be
sent, and answer questions about a whole part rather than a chosen window of it.

| Question | Tool |
|---|---|
| Where does the main exterior seam sit, over the part's whole height? | `hsm-gcode seams` |
| What speed is commanded at this place on the outer wall, layer by layer? | `hsm-gcode speeds` |
| Show the commanded walls with seam markers or speed colours | `hsm-gcode view seams` or `hsm-gcode view speed` |
| Watch consecutive layers deposit under the moving head and bed | `hsm-gcode view playback` |
| Did a change to a print stage change what prints? | `hsm-gcode compare` |
| Is a re-prepared project, sliced archive or output folder the one before it, by value? | [`hsm-project compare`](../hsm/inspection/README.md#print-projects) |
| How fast, with how much part fan and how much plastic is one part laid at each height, on several plates? | `hsm-gcode laying` |
| What does one plate command differently from another, apart from where its beads lie? | `hsm-gcode recipe` |
| Could the head hit plastic it laid earlier: a low travel, a drop onto a part, a wait over a part? | `hsm-gcode harm` |

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
hsm-gcode compare BEFORE.gcode.3mf AFTER.gcode.3mf
```

```bash
hsm-gcode laying "A=FIRST.gcode.3mf" "B=SECOND.gcode.3mf" --object ID [--step MM] [--walls [--outside]]
hsm-gcode recipe FIRST.gcode.3mf SECOND.gcode.3mf
hsm-gcode harm SLICE.gcode.3mf [--object ID] [--above MM]
```

`laying` reads one object, by its id on the plate, in height bands of its moves' end Z. Each
band gives the length laid, the share laid with the part fan on, the length in each commanded
speed band with the fan off and on, the slow laying under the fan, the mean speed and the
plastic per millimetre, plate by plate. `--walls` keeps the outer and overhang walls, and
`--outside` the walls beyond the middle of each layer's wall radii.

`recipe` lists, by part and feature, the length laid at each feed, part-fan level, nozzle
temperature and acceleration where the two plates differ. It then lists the printer-side
commands, retractions, lifts and travels whose counts differ, the heating commands, and the
moves that follow the same path under other settings.

`harm` keeps the tallest bead top laid so far in every cell of the plate. It samples each
travel between beads against it, leaving out the ends where the travel leaves and reaches a
bead. It reports the travels whose nozzle tip comes within a tenth of a millimetre of earlier
plastic or passes below its top, the drops that end close above plastic, and the waits over
it. `--object` and `--above` keep the travels at one object and height.

`compare` reads two slices or G-code files. For each feature it reports the bead length
each lays, the plastic, and how much of each one's bead length lies on the other's beads of
that feature. It then lists the layers that differ and the longest stretches only one slice
lays. Beads are matched where they lie, so sloped and warped courses compare as level ones
do. `--tolerance` sets how close counts as on; `--json` writes every group.

```bash
hsm-gcode view playback SLICE.gcode.3mf --layers FIRST-LAST --title "Print motion" --out PAGE.html
hsm-gcode view playback SLICE.gcode.3mf --layers all --inline --title "Whole plate" --out PAGE.html
```

Playback runs continuously across the selected layers, with a timeline, playback speed and
print, nozzle-following and whole-printer cameras. The Print and Whole printer cameras stay
fixed relative to the frame during playback and scrubbing. The head moves in XY at gantry
height as the bed and deposited paths move opposite commanded Z. Follow nozzle tracks the
head in XY. `--bed-model` accepts the binary build-plate STL from the printer's profile.
The remaining H2C hardware is a simplified reference model. Start at the first layer when
the view needs all previously deposited material.

`--inline` packs sampled head motion and simplified bead paths for the chat visualization
reader. It uses the shared website player and the same motion planner as the detailed view.
For a custom playback, frame the bed's travel when setting the camera preset, then keep the
camera and orbit target fixed as playback advances. Larger plates can select a consecutive
range with `--layers` to fit the inline limit.

`--inline --data` writes the sampled playback data for a [website Print view](../../print-playbacks/README.md).

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
the view. View commands write an HTML page at `--out`. Keep pages in a scratch run
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
