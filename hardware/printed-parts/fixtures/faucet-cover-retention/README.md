# Faucet cover retention trials

This directory retains the six complete Sculpted display covers from the
recorded Mark2 trial. Each bezel carries its letter A–F. They fit the tip
identified by `printed_tip_stl_sha256` in [the retained manifest](retained-artifacts.json).
Their geometry and fit readings refer to that printed tip, not to the current
production faucet.

| Cover | Inward preload per wing | Tab height | Print orientation |
|---|---:|---:|---|
| A | 1.00 mm | 3.00 mm | Bezel on the bed |
| B | 1.25 mm | 3.00 mm | Bezel on the bed |
| C | 1.00 mm | 3.00 mm | Bezel up |
| D | 1.25 mm | 3.00 mm | Bezel up |
| E | 1.00 mm | 3.10 mm | Bezel up |
| F | 1.25 mm | 3.10 mm | Bezel up |

The trial's reference faucet print uses 0.75 mm preload and 3.00 mm tabs, with the bezel
on the bed. A/C and B/D share their geometry apart from the identification
letter; their print orientation differs. C/E and D/F differ in tab height.
The taller CAD tabs occupy more of the existing recess, leaving 0.05 mm below its
retaining shoulder. At the retained 0.24 mm layer height, both CAD tab heights
finish on the same printed layer: local N6.38. E/F therefore serve as repeat
specimens for C/D in this print, rather than a resolved tab-height comparison.
All six keep the same radial engagement and tab length.

Preload is the free wing's inward displacement at the reference tab's upper
edge. The nominal seated covers keep the display aperture and outer shape.
The 0.25 mm letter recess leaves 1.05 mm of bezel material.

## Fit and handling

Remove supports before installing the display. A/B have supported retaining
faces; C–F print those faces upward and place support contact under the bezel.
Clean that underside so it does not bear on the display glass. Spread the
plastic wings by hand to load the display.

Hold the cover and display together 8.5 mm above the final seat, measured normal
to the glass. Slide them onto the existing tip from the outlet, then lower them
until the feet and tabs are seated. The complete aperture and four display feet
retain their reference locations. Compare retention after seating and after
several removals, identifying each result by its bezel letter.

[The print project](faucet-cover-retention-petgf.3mf) contains all six covers on
one plate. [Print settings and support readings](faucet-cover-retention-petgf.md)
describe the retained slice. [Geometry](trial-geometry.json) records each trial
and its source hashes; [fit readings](fit-check.json) measure the saved covers
against the recorded tip and display. [Physical results](print-log.md) identify
the printed samples and observations.

## Retained artifacts

`retained-artifacts.zip` holds the exact six STEP/STL/viewer-payload triplets
and `trial-geometry.json`. The build target restores those bytes at their
existing paths. `retained-artifacts.json` pins every archive member, the print
project, and the retained fit, slice, support, readiness and lint records.
The integrity checker leaves all reports unchanged and does not evaluate fit
against current production CAD.

The original CAD, geometry-check and print-preparation recipes, including
their production dependencies, are held at Git commit
`fa5c2dcb40b2cfd278c07ad571996ec0827b25b3`. That commit matches every source hash
in `trial-geometry.json`. Use a separate checkout of that commit to inspect or
run those recipes. The retained archive supplies the exact published bytes;
new experiments receive new identifiers rather than replacing A–F.

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-cover-retention/cover_retention_trial.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-cover-retention/check_geometry.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-cover-retention/prepare_print_project.py
```

The first command restores the retained outputs. The second verifies their
integrity and the saved records. The third verifies and names the existing
3MF for a reprint; it does not rebuild the project or invoke a slicer.
