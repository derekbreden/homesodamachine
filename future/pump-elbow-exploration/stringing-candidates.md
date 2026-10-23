# TPU stringing candidates

**Status: the deposited-path Siraya pair is accepted on Mark2 with no strings
reported and seal seeming as good as before.**
The [current trial](prints/2026-10-22-deposited-links-siraya85a-mark2/README.md)
prints native wall and fin paths through turns and uses straight material-contained
chords between those paths. Its emitted review covers every free attachment span,
including a conservative case that ignores extrusion runs shorter than 1 mm as
attachments. It adds 1.21% deposition on existing inner-wall paths, with no part
retractions, Z hops or photo trips. Mark2 accepted task 1365546966 with clear
Siraya Tech TPU 85A; allow about 2 hours / 8.55 g. The
[physical result](prints/2026-10-22-deposited-links-siraya85a-mark2/physical-result.json)
records Derek's report: “That worked very well. I see no strings, and seal seems
as good as before.” Acceptance belongs to this combined geometry, material and
processed-path recipe; the seal comparison is qualitative.

The vertical center-web Bambu pair retains dense bore and exterior-to-fin stringing. The
[tested trial](prints/2026-10-16-vertical-center-web-tpu85a-mark1/README.md) connects
both elbows and each elbow's legs with tapered cutaway fins. The joining web
stays in a vertical center plane from the bed to its top. Both standalone
and paired versions have one connected island at all 184 layer section planes.
The print record includes firsthand related work and emitted travel checks
against model sections that retain every opening.
The [0.4 mm lap's physical record](prints/2026-10-16-departure-lap040-normal-lift-tpu85a-mark1/physical-result.json)
reports persistent threads with a possible small reduction in thickness. The
[0.2 mm lap's physical record](prints/2026-10-15-departure-lap-tpu85a-mark1/physical-result.json)
reports no improvement and insufficient apparent clearance.
Related options below remain candidates. The
[two-object trial](prints/2026-10-14-compact-two-siraya85a-overhang10-engineering-z000-mark1/README.md)
is their baseline; its finished result is pending. A strand across a bore sits
in the water path and in the tube socket.

## Deposited path and free strands

The [finned pair's physical record](prints/2026-10-16-vertical-center-web-tpu85a-mark1/physical-result.json)
shows persistent stringing. A nonextruding travel that turns above a wall does
not make a deposited attachment at the turn. Its free strand can straighten
between attachment points and span the bore or exterior gap that the nozzle
went around. The [command review](prints/2026-10-16-vertical-center-web-tpu85a-mark1/free-strand-review.json)
contains a layer-49 example: zero nozzle travel outside the model, with a
3.98 mm potential taut span across a bore.

The anchoring mechanism requires a continuous deposited path through the
connection or a reliable new attachment before changing direction. The
[deposited-path trial](prints/2026-10-22-deposited-links-siraya85a-mark2/README.md)
splices the existing paths into layer tours, printing through the turns. Its
free transfers and potential taut spans are straight and contained within
material. Its finished Mark2 pair has no visible strings reported. One connected
model and travel-wall avoidance alone do not establish attachment; the accepted
result belongs to the complete deposited-path Siraya recipe.

## Departure lap

At each point where the nozzle leaves an elbow:

1. Stop extruding and retract standing still (`G1 E-1 F600` in Bambu 85A).
2. Rise vertically 0.4 mm above the printed layer.
3. Travel once around a wall loop of that elbow without extruding, ending at
   the loop entry point, then return to the native departure XY.
4. Continue native travel at 0.4 mm clearance, lower, unretract and print.

The proposed effect is that ooze hanging from the tip touches down on the wall
top, where the next layer can cover it, leaving less for the crossing. Derek's
experience: "When the ooze is wiped longer the stringing is less."

The launched two-object job has 184 departures to the other elbow, over an
unavoidable gap of 12.3 mm on average; 184 timelapse photo trips, one at each
layer change; and 59 crossings between the two legs of each elbow.

Settings to choose for a trial:

- **Height.** The 0.4 mm lap trial runs above the layer. Layers are 0.12 mm.
  At 0.1 mm the nozzle runs lower than it
  prints the next layer and brushes high spots. At 0.2 mm only ooze hanging at
  least 0.2 mm touches down; at 0.4 mm the proposed contact needs at least
  0.4 mm of hanging material. Actual contact and string reduction are physical
  observations.
- **Speed.** A slower lap leaves the TPU more time to ooze onto the wall
  before the crossing.
- **Loop.** The wall just inside the outer wall buries the deposit away from
  the exterior. On the outer wall, a deposit can leave a bump outside.

The assessment is the finished article: strands between the elbows, at wall
starts and across the bores, compared with the baseline job.

### Inserting it

A post-processor runs between the offline slice and `tools/bambu_print.py`.
[`departure_lap.py`](departure_lap.py) prepares the wall-lap files by hand;
its [print record](prints/2026-10-16-departure-lap040-normal-lift-tpu85a-mark1/README.md)
specifies the emitted path, thin-rim fallbacks, full-height wall connectors
and return to the native departure point.
It rewrites `Metadata/plate_1.gcode` in the native `.gcode.3mf` and its
`plate_1.gcode.md5`, which the sender checks. It inserts moves only; every
extrusion line stays as Bambu wrote it. In the launched job, all 368 object
blocks open with travel, lower and unretract and close with a standing
retraction, so every departure offers the same insertion point.

Before sending, a check confirms that the extrusion lines are unchanged and in
order, that each extrusion runs at its layer's Z, that the lap runs at its set
height and each crossing at the hop height, and that the checksum matches.

Bambu Studio's command-line slicer does not run post-processing scripts, and by
default it refuses a project that lists one
([BambuStudio.cpp](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/BambuStudio.cpp#L1950-L1960)).
The app runs them after slicing and redraws its preview from the rewritten
G-code ([BackgroundSlicingProcess.cpp](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/slic3r/GUI/BackgroundSlicingProcess.cpp#L827-L880)).

### Stock settings near it

- **Wipe while retracting** is off in the Siraya profile. Bambu's wipe moves at
  print height, in contact with the bead, only along the path just extruded,
  and makes 95% of the retraction during the move. Its length is capped at
  that path's length
  ([wipe](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode.cpp#L434-L510),
  [retract](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode.cpp#L7923-L7954)).
  It laps a loop only when an elbow's layer ends on one. In the launched job
  the outer wall ends 52 of the 368 elbow-layers; the rest end on an
  inner-wall piece or infill.
- **Z hop height** is one value for every lifted travel. Bambu's own TPU
  profiles set 0.4 or 0.6 mm where they set it. With Avoid crossing wall on,
  some travel already follows walls; a lower hop brings those stretches down
  but adds no lap.

## Related options measured on the same jobs

[`travel_survey.py`](travel_survey.py) measures the commanded travel in the
printed single and the launched pair:

| | Printed single (Avoid crossing wall off) | Launched pair (on) |
| --- | --- | --- |
| Travels over a bore, per elbow | 492 (3.0 m) | 15 (26 mm) |
| Crossings between the legs, per elbow | 59 | 59 |
| Crossings between elbows | none | 184 within layers, 183 at layer changes |
| Timelapse photo stops | 184 | 184 |

- **Avoid crossing wall** keeps travel off the bores. The single with reported
  internal stringing had it off; the pair's finished result tests it.
- **Timelapse.** At each layer change the H2C template's `M9711` moves the head
  to the photo position, (262, 162) on every layer of the pair
  ([GCode.cpp](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode.cpp#L4476-L4483)).
  The next travel returns about 110 mm on average from there, and 61 of those
  returns cross a bore. Timelapse off removes the trips. Farthest point
  timelapse takes the photo without the trip, pausing the nozzle on the outer
  wall ([GCode.cpp](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode.cpp#L7456-L7483)).
- **Print sequence By object** prints one elbow completely, then the other, so
  no travel crosses between them. The 22.16 mm elbow is under the H2C's
  47.4 mm rod clearance; spacing follows the slicer's clearance check.

These are commanded paths. Whether a strand forms is a physical result.
