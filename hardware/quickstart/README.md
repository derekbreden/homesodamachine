# Home Soda Machine installation quick start

Five single-sided landscape 11 x 17 inch sheets publish together as `quick-start.pdf` on
`/drawings`. The guide is a visual installation sequence:

1. mount the complete factory faucet assembly;
2. close the under-sink cold-water valve;
3. add the brass tee where the home has a 3/8-inch braided faucet hose;
4. add the black push-fit tee where the home has an existing 1/4-inch plastic line;
5. connect the five tubes and RJ11 signal lead to the appliance rear panel.

The two tee sheets are alternatives. The installer uses only the sheet that matches the existing
cold-water connection. In either path, the new white tube continues through the supplied filter
before it reaches the appliance `TAP` inlet.

## Faucet mount

Four registered model states show one physical story: lower the complete factory assembly through
the prepared opening, seat it, slide the open under-counter plate around the attached tubes, and
hand-tighten the retained nut. The exact same 220 x 72 mm countertop window appears in every
state. It is long on the plate's slide axis and narrow across the real under-sink working space.
The retracted plate stays visibly clear of the washer and nut before it moves.

## Cold-water connection

`plumbing/plumbing_scenes.py` models the common 3/8-inch braided-hose installation as four states
in one coordinate frame: valve open, valve closed, hose removed with the tee and new branch staged,
and tee installed with both lines connected. The finished wall, copper stub, escutcheon, valve,
braided hose, brass compression fittings, and white 1/4-inch branch are CAD solids. One fixed
2000 x 1100 orthographic viewport keeps invariant geometry registered in every state.

`plumbing/modern/render_modern_tee.py` models the alternative existing-1/4-inch-line installation.
The checked-in PP0208E reference solid sits between two square-cut ends, and the new white branch
occupies its third port. Before and connected states share one 2000 x 1100 orthographic viewport.

## Appliance rear connections

The rear sheet contains exactly two registered states: all six customer leads clear of the rear
face, and all six fully seated. The five tube collars are production solids. Each 30 mm collar
starts 47.5 mm behind its insertion tip and ends 77.5 mm behind it. The routed ends of every tube
and the RJ11 ribbon continue out of the common crop, so the connected state contains no visible
loose distal ends.

The physical endpoint rule is:

- red `CO2` supply to `CO2`;
- filtered white tap-water supply to `TAP`;
- blue faucet tail to `SODA`;
- both black faucet tails to the two `FLAVOR` ports;
- RJ11 plug to the signal jack.

## Build

From the repository root:

```sh
# Faucet and appliance-rear CAD artwork.
tools/cad-venv/bin/python hardware/quickstart/quickstart_art.py

# Both under-sink tee alternatives.
tools/cad-venv/bin/python hardware/quickstart/plumbing/plumbing_scenes.py
tools/cad-venv/bin/python hardware/quickstart/plumbing/modern/render_modern_tee.py

# Five rendered sheets and the bound PDF.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The PDF is 17 x 11 inches with five pages. Review every page at actual size, at quarter scale, and
in grayscale. The three text levels are the page title, scene caption, and one supporting line;
modeled geometry carries connector identity, valve state, fitting pose, and tube routing.
