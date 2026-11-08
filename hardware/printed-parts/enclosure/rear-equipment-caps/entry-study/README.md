# Regulator entry comparison

The comparison pairs the standard pointed regulator cover with a cover whose
free tips extend farther along the installed Z axis. Both lead-ins retain the
same lateral position and reach. The taller cover's spring walls, roots,
retaining faces and fitted hardware bearings retain the standard geometry.
Each cover has a complete matching receiver, including its axial stops and
enclosure roof stock.

The standard receiver is cropped from the production back-top solid. The
taller cover's receiver extends only the same flank pockets upward into the
roof stock. [geometry.json](geometry.json) records the tip dimensions, retained
lower profiles, seated overlaps, ramp angles and roof stock. The [physical result](../prints/2026-11-07-ceiling-down-mark2/physical-result.json)
records Derek's acceptance of the longer tips. The saved articles and geometry
record identify this completed comparison; the production generator makes the
approved lead-in on the rear caps.

The `regulator-entry-comparison` recipe in
[pieces.json](../../trial-preparation/pieces.json) prints both receiver-and-cover
pairs on Mark2. The receivers retain
back-top's ceiling-down layer direction and print without cavity supports. The caps stand
on their production axial ends and use their ordinary production layer
schedule. The receiver catches bridge between their complete end shoulders. The articles
provide time away from each cover between layers, measured from the emitted
paths separately for each article. The plate has no priming tower and uses
traditional timelapse. Temperatures and localized cooling follow the
production PET-GF recipe.

The [prepared plate](prepared-print.json) records the native slice, cooling
interval and submission state.
