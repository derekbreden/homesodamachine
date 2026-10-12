# Reading The Pour V5

The Pour is a compact reference for the machine's finish, supported surfaces and
sliding fit. The Corner's crown carries the display surface outside and the
supported ceiling inside. Its standing round also carries the contour seam;
the two flanks carry the teardrop opening and flute fade. One object carries
nine selected readings at one recipe.

Print complete objects to compare recipes. Change one chosen variable between
prints and identify each object with its recipe, material and date. Keep the
geometry and other settings fixed. A clearance comparison changes the gate's
single clearance value between builds. Layer-height comparisons use one model
layer height throughout each object, after the same 0.20 mm first layer.

## Read the object

| Feature | Read | Setting or geometry to try on the next complete print |
|---|---|---|
| Expanding R6 edge | Inspect the rear lower edge for loose outward roads, droop and a rough transition into the standing wall. This round begins on the bed. | Layer height, outer-wall speed, cooling or flow; retain the native tangent fill while comparing print settings. |
| Inward/top R6 edge | Turn the crown's side roll under raking light; feel the steps with a fingernail. | Model layer height. |
| Standing R6 edge | Inspect a rear standing corner's layer lines, waviness and consistency with its adjoining flat. | Outer-wall speed or material; model layer height also changes the visible striation. |
| Display facet and transitions | Compare the sloped flat, R12 front turn, R18 roof turn and R6 side blend under one light. | Model layer height, top-surface settings or material. The retained native facet is 30 degrees from horizontal. |
| One gate slide | Record whether it releases, whether movement is smooth and whether the play feels acceptable. | One gate-clearance value. Keep its release procedure and print orientation the same. |
| Supported flat ceiling | View the 12 × 6 mm flat inside the crown through the rear opening with support attached, then after removal. Separate residue, droop and damage to roof strands from removal effort. | One support-top distance, or one interface setting in a separate comparison. Read the emitted gap from the native slice. |
| Teardrop opening | Inspect the left flank's nominal Ø11 opening for roof finish, clear diameter and loose strands. The circular body is retained below a 36-degree roof. | Layer height, bridge speed or cooling. |
| Contour seam | Under raking light and by fingernail, record a ridge, groove, open gap or clean closure at the left rear standing corner. | One seam-gap or scarf setting per complete print; keep the seam on the same contour. |
| Fluted-to-flat fade | Compare the flute field, its fade and the adjoining flat under the same light. | Material or layer height. |

The gate has 10 mm of nominal travel, 0.25 mm XY air per face, and 0.48 mm lower
and upper Z release gaps in CAD. The prepared native slice emits both Z gaps at
0.48 mm and lateral road air at 0.245–0.250 mm. Its requested 0.45 mm support-top
distance emits a 0.48 mm gap beneath the crown. The
[native reading](prints/the-pour-v5-petgf.print.json) records these planned paths;
record physical measurements separately.

Read the ceiling with support attached first. Remove all automatic supports
before assessing the slide, including roots and branches in the open end-travel
pockets and unused space beside the handle. The rear opening reaches the crown
underside and handle. Read the ceiling again after cleanup.

The gate is a local fit reference. Print-in-place release does not qualify the
machine's separately assembled service joints. If it does not release, record
that result; forceful break-in can deform the fit and change later readings.

## Retained geometry

The three round readings retain R6 sections in expanding, inward and standing
orientations. The display crown retains the production R12 front turn,
30-degree facet and R18 roof turn, shortened to a 12 mm flat facet. The supported
reading is the underside of that same crown. The opening uses the production
Ø11/36-degree teardrop profile. The fluted flank retains the production 5 mm
pitch, 4 mm groove width, 1.2 mm depth and 5 mm fades.

The 42.5 mm width comprises the 36.5 mm gate bay and two 3 mm walls. The crown's
25.392 mm run, a 6 mm ceiling viewing land and 3 mm rear wall set the 34.392 mm
depth. Its 18.804 mm rise sits above the 10.4 mm gate lip with a chosen 3 mm
front viewing reveal; rounding onto the 0.20/0.24 mm layer phase sets the
32.36 mm height. The front reveal is for viewing. The 12 × 6 mm ceiling patch,
20 × 15 mm flute field and viewing allowances are design choices, with
[exact geometry recorded here](geometry.json).

The [accepted tee-carrier print](../../enclosure/tee-carrier/physical-acceptance.json)
supports the expanding R6 tangent profile on that source part. The
[PET-GF interface experiment](../../../print-tests/petgf-interface-edges/README.md)
selected a 0.48 mm planned gap for clean release with preserved roof strands;
its underside strands still felt loose. The
[flute evidence](../../cadlib/flute-evidence/README.md) compares texture and flat
appearance on full-size enclosure faces. These results apply to their recorded
prints. The Corner's small viewing patches remain unprinted.

## Compare complete prints

Use one [reference card](reference-card.csv) per object. Its recipe row applies
to all nine reading rows; observation and measurement fields are blank.
Write its recipe ID with a marker on an existing inside side-wall flat.

Edit layer-height, material and support settings in the single
[project](prints/the-pour-v5-petgf.3mf). Change geometric slide clearance between
builds with `reference.py --xy-air` or `reference.py --z-air`, then prepare that
geometry with `prepare_reference.py --slice`. Change one chosen variable and
keep the remaining geometry and settings fixed.

Set objects side by side with the same face toward the same light. Handle both
before selecting a setting. Record the actual recipe and observations against
each object's identity; nominal CAD gaps and requested support distances do not
substitute for deposited geometry or a physical result.

For a material comparison, keep the recipe and geometry fixed and identify the
material and lot. For a layer-height comparison, keep the material and other
settings fixed. For a support comparison, record the last support-top extrusion
and the first ceiling layer's lower plane: their difference is the planned gap.

This object is a finish and local-fit reference. It does not establish the full
machine's load capacity, seal performance, retention force or service life.
Short paths and the compact body's cooling time also differ from complete machine
parts. Confirm a selected recipe on the relevant complete part before changing
production settings.

[Model](https://homesodamachine.com/3d#step:printed-parts%2Fcalibration%2Fsoda-studies%2Fthe-pour.step)
· [Editable project](prints/the-pour-v5-petgf.3mf)
· [Print kit](https://github.com/derekbreden/homesodamachine/releases/download/the-pour-v5/print-kit.zip)
