# TPU stringing candidates

**Status: departure-lap trial submitted; physical result pending.** The
[Mark1 Bambu 85A trial](prints/2026-10-15-departure-lap-tpu85a-mark1/README.md)
implements a 0.2 mm high, 10 mm/s wall lap at all 368 object departures, with
full-height connectors and the native extrusion/travel commands retained.
Related options below remain candidates. The
[two-object trial](prints/2026-10-14-compact-two-siraya85a-overhang10-engineering-z000-mark1/README.md)
is their baseline; its finished result is pending. A strand across a bore sits
in the water path and in the tube socket.

## Departure lap

At each point where the nozzle leaves an elbow:

1. Stop extruding and retract standing still, as now (`G1 E-.8 F1800`).
2. Rise 0.1–0.2 mm above the layer instead of the 0.4 mm hop.
3. Travel once around a wall loop of that elbow without extruding, ending at
   the loop point nearest the next destination.
4. Rise to the 0.4 mm hop, travel, lower, unretract and print.

Ooze hanging from the tip touches down on the wall top, where the next layer
covers it, and the nozzle reaches the crossing carrying less. Derek's
experience: "When the ooze is wiped longer the stringing is less."

The launched two-object job has 184 departures to the other elbow, over an
unavoidable gap of 12.3 mm on average; 184 timelapse photo trips, one at each
layer change; and 59 crossings between the two legs of each elbow.

Settings to choose for a trial:

- **Height.** Layers are 0.12 mm. At 0.1 mm the nozzle runs lower than it
  prints the next layer and brushes high spots. At 0.2 mm only ooze hanging at
  least 0.2 mm touches down.
- **Speed.** A slower lap leaves the TPU more time to ooze onto the wall
  before the crossing.
- **Loop.** The wall just inside the outer wall buries the deposit away from
  the exterior. On the outer wall, a deposit can leave a bump outside.

The assessment is the finished article: strands between the elbows, at wall
starts and across the bores, compared with the baseline job.

### Inserting it

A post-processor runs between the offline slice and `tools/bambu_print.py`.
[`departure_lap.py`](departure_lap.py) prepares the selected trial by hand;
its [print record](prints/2026-10-15-departure-lap-tpu85a-mark1/README.md)
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
