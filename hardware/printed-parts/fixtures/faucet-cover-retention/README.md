# Faucet cover retention trials

Six complete Sculpted display covers fit the existing faucet tip and display.
Each bezel carries its letter A–F. The tip's recesses, display supports and
dispense face stay in the printed faucet.

| Cover | Inward preload per wing | Tab height | Print orientation |
|---|---:|---:|---|
| A | 1.00 mm | 3.00 mm | Bezel on the bed |
| B | 1.25 mm | 3.00 mm | Bezel on the bed |
| C | 1.00 mm | 3.00 mm | Bezel up |
| D | 1.25 mm | 3.00 mm | Bezel up |
| E | 1.00 mm | 3.10 mm | Bezel up |
| F | 1.25 mm | 3.10 mm | Bezel up |

The successful faucet print uses 0.75 mm preload and 3.00 mm tabs, with the bezel
on the bed. A/C and B/D share their geometry apart from the identification
letter; their print orientation differs. C/E and D/F differ in tab height.
The taller tabs occupy more of the existing recess, leaving 0.05 mm below its
retaining shoulder. All six keep the same radial engagement and tab length.

Preload is the free wing's inward displacement at the production tab's upper
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
retain their production locations. Compare retention after seating and after
several removals, identifying each result by its bezel letter.

[The print project](faucet-cover-retention-petgf.3mf) contains all six covers on
one plate. [Print settings and support readings](faucet-cover-retention-petgf.md)
describe the retained slice. [Geometry](trial-geometry.json) records each trial
and its source hashes; [fit readings](fit-check.json) measure the saved covers
against the existing tip and display.

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-cover-retention/cover_retention_trial.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-cover-retention/check_geometry.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/faucet-cover-retention/prepare_print_project.py
```
