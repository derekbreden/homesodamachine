# Nameplate receiver with 0.45 mm wing Y clearance

Mark2 accepted task **1296653642** at 2026-09-30T16:45:40.747148+00:00.
The native estimate is **43 min 4 sec**, **20.07 g** at the saved profile density.
Use the existing flat 3.36 mm nameplate from task 1294806669.

The [physical reference](../2026-09-30-nameplate-body-x035-receiver-mark2-v8/physical-result.json)
records sideways movement with bowing throughout that movement, and wings that
feel tight in Y. This receiver tests additional space above both wings.

| Interface | Nominal dimension |
|---|---:|
| Wing thickness | 1.68 mm |
| Slot opening in Y | 2.13 mm |
| Gap above the seated wing | 0.45 mm |
| Flat retaining-lip stock | 1.23 mm |
| Body X gap on each side | 0.35 mm |
| Wing-tip X gap at center / full body float | 0.45 / 0.10 mm |
| Ordinary / print-down Z end gap | 0.15 / 0.40 mm |
| Plate-back and wing-underside seating datum | Y=0 |
| Minimum overlap / flat bearing at full X float | 1.70 / 0.80 mm |

[Exact solid comparison](geometry-delta.json) confines the 22.9125 mm³ removal to
the wing-slot retaining faces and their entry bevels. Each roof and bevel moves
0.15 mm in Y; the bevel width and slope stay fixed. The X/Z openings, seating
floor, external stock and existing nameplate are unchanged. All six pure-axis
travel limits and capture beyond them pass, along with the ideal 101-position
insertion envelope. These checks do not establish printed force or retention.

[Native verification](verification.json) measures 468 sections across both flat
bearings: a 2.13 mm slot and 1.23 mm retaining stock are present in the emitted
bead envelopes. No support bead enters either slot or entry bevel. One shared
PET-GF tree rises from the bed to its labelled interface after 41.28 mm. The
receiver uses its enclosure orientation, a 0.20 mm first layer, 0.24 mm above,
saved speeds and wall order, and 0.40 XY / 0.45 top Z / 0.30 bottom Z support gaps.
Support and interface are black. Physical support removal remains a bench check.

[Published artifacts](published-artifacts.json) match the live STEP and viewer
payload. [Geometry lint](geometry-lint.log) has no unanswered findings. The
[launch receipt](launch.json) binds the reviewed archive, left black PET-GF on
Mark2's 0.4 mm nozzle, requested +0.04 mm bed trim (emitted +0.02 mm on textured
PEI), ordinary startup options including Auto nozzle offset, the user's clear
bed report, and more than three minutes after H2C's start.
[Postlaunch](postlaunch.json) confirms the matching task RUNNING without errors.

Physical result: Pending same-nameplate Y play, relaxed flatness, insertion and shake-retention assessment.
