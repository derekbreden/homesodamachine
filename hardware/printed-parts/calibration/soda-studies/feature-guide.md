# Reading The Pour V4

The Pour is a compact reference for the machine's finish, supported surfaces and
sliding fit. Its arch, crown and moving gate carry the features being read. One
object carries nine selected readings at one recipe.

Print complete objects to compare recipes. Change one chosen variable between
prints and identify each object with its recipe, material and date. Keep the
geometry and other settings fixed. A clearance comparison changes the gate's
single clearance value between builds. Layer-height comparisons use one model
layer height throughout each object, after the same 0.20 mm first layer.

## Read the object

| Feature | Read | Setting or geometry to try on the next complete print |
|---|---|---|
| Expanding R6 edge | Inspect the jamb feet and the arch's upper rim for loose roads, droop and a rough outward transition. The feet begin on the bed; the upper rim begins beside a supported ceiling. | Layer height, outer-wall speed, cooling or flow; retain the native tangent fill while comparing print settings. |
| Inward/top R6 edge | Turn the crown's side roll under raking light; feel the steps with a fingernail. | Model layer height. |
| Standing R6 edge | Inspect a rear standing corner's layer lines, waviness and consistency with its adjoining flat. | Outer-wall speed or material; model layer height also changes the visible striation. |
| Display facet and transitions | Compare the sloped flat, R12 front turn, R18 roof turn and R6 side blend under one light. | Model layer height, top-surface settings or material. The retained native facet is 30 degrees from horizontal. |
| One gate slide | Record whether it releases, whether movement is smooth and whether the play feels acceptable. | One gate-clearance value. Keep its release procedure and print orientation the same. |
| Supported flat ceiling | View through the rear opening with support attached, then after removal. Separate residue, droop and damage to roof strands from removal effort. | One support-top distance, or one interface setting in a separate comparison. Read the emitted gap from the native slice. |
| Teardrop opening | Inspect the nominal Ø11 opening's crown, clear diameter and any loose strands. The nominal circular body is retained below a 36-degree roof. | Layer height, bridge speed or cooling. |
| Contour seam | Under raking light and by fingernail, record a ridge, groove, open gap or clean closure at the left rear standing corner. | One seam-gap or scarf setting per complete print; keep the seam on the same contour. |
| Fluted-to-flat fade | Compare the flute field, its fade and the adjoining flat under the same light. | Material or layer height. |

The gate has 10 mm of nominal travel, 0.25 mm XY air per face, and 0.48 mm lower
and upper Z release gaps in CAD. Record actual deposited gaps with the recipe.
Remove the ceiling supports and their roots from the open end-travel pockets
through the arch opening before assessing the slide. Read the ceiling with its
support attached first, then after cleanup.

The gate is a local fit reference. Print-in-place release does not qualify the
machine's separately assembled service joints. If it does not release, record
that result; forceful break-in can deform the fit and change later readings.

## Compare complete prints

Use one [reference card](reference-card.csv) per object. Its recipe row applies
to all nine reading rows; observation and measurement fields are blank.
Write its recipe ID with a marker on an existing inside side-wall flat.

Edit layer-height, material and support settings in the single
[project](prints/the-pour-v4-petgf.3mf). Change geometric slide clearance between
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
· [Editable project](prints/the-pour-v4-petgf.3mf)
· [Print kit](https://github.com/derekbreden/homesodamachine/releases/download/the-pour-v4/print-kit.zip)
