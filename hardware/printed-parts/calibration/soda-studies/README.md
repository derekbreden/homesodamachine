# The Pour V5 · Corner

The Pour is a **42.5 × 34.4 × 32.4 mm** reference object for selected printing
mechanisms in the home soda machine. Its crown carries the display facet and
transitions outside and a supported ceiling inside. Rounded edges, a fluted
flank, a teardrop opening and one captive slide complete the object. Nine
readings cover surface finish, local fit and support release.

[Explore the model](https://homesodamachine.com/3d#step:printed-parts%2Fcalibration%2Fsoda-studies%2Fthe-pour.step)
· [Editable Bambu Studio project](prints/the-pour-v5-petgf.3mf)
· [Download the print kit](https://github.com/derekbreden/homesodamachine/releases/download/the-pour-v5/print-kit.zip)

![The Pour](the-pour.step.png)

The prepared editable PET-GF project uses Mark2's left 0.4 mm nozzle, a
0.20 mm first layer, uniform 0.24 mm model layers and six walls. The native
estimate is **1 h 3 min and 25.29 g**, including supports.
[Print preparation](print-preparation.json) records the recipe and native slice.
The Corner is unprinted.

Print complete objects to compare recipes. Each object uses one uniform model
layer height after its first layer, one support recipe and one fixed
slide configuration. Change one chosen variable between prints and keep the
other geometry and settings fixed. Import the supplied meshes at 100% scale;
the prepared project retains their shared print-in-place arrangement.

The [feature guide](feature-guide.md) connects each reading to a setting to try
on the next complete print. The blank [reference card](reference-card.csv)
records one object's recipe and nine observations. Keep the material, lot,
date and recipe with the physical object, and compare corresponding faces under
the same light. Write a recipe ID with a marker on an existing inside side-wall
flat and use the same ID on the card.

Layer, material and support settings are edited in the single project. The
geometry generator's `--xy-air` and `--z-air` options set the slide's running and
release clearances for a whole build. `prepare_reference.py --slice` prepares the
current geometry with its one recipe in the repository's normal CAD runtime.

Physical release, movement and surface quality remain unmeasured. Confirm a
selected recipe on the relevant complete machine part; production loads,
sealing, retention and service life require their own evidence.
