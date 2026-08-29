# Home Soda Machine installation quick start

Five single-sided landscape 11 x 17 inch sheets publish together as `quick-start.pdf` on
`/drawings`. The guide is a visual installation sequence:

1. mount the complete factory faucet assembly;
2. close the under-sink cold-water valve;
3. release the existing 1/4-inch plastic tube from its push fitting;
4. add one black push-fit tee with the supplied short tube;
5. connect the five tubes and RJ11 signal lead to the appliance rear panel.

This edition follows the modern-home installation path: an existing 1/4-inch plastic cold-water
line and push fitting under the sink. The installer releases one tube, adds one tee and one short
piece of supplied tube, reconnects the original line, and pushes the new white branch into the
third port. The white branch continues through the supplied filter before it reaches the appliance
`TAP` inlet. No threaded fitting is opened during this path.

## Faucet mount

Four registered model states show one physical story: lower the complete factory assembly through
the prepared opening, seat it, slide the open under-counter plate around the attached tubes, and
hand-tighten the retained nut. The exact same 220 x 72 mm countertop window appears in every
state. It is long on the plate's slide axis and narrow across the real under-sink working space.
The retracted plate stays visibly clear of the washer and nut before it moves.

## Cold-water connection

`plumbing/modern/render_modern_tee.py` models the complete push-fit sequence in one continuous
under-sink coordinate frame. The wide camera shows the same valve and connected plastic line open
and closed. The macro camera then shows the existing fitting's collet pressed, the original tube
withdrawn, the supplied short tube seated, the tee seated on that tube, the original tube
reconnected, and the filtered white branch seated in the third port.

The existing fitting uses the repository's measured John Guest PP0408W union geometry, including
its 1.335 mm collet travel and 16 mm tube insertion. The customer-facing PP0208E tee is built from
John Guest's published 1/4-inch dimensions: 39.0 mm run span, 19.5 mm port reach, 15.7 mm insertion
depth, 16.3 mm maximum body diameter, and 4.3 mm bore. Long tubes continue through the common crop;
no arbitrary remote tube end is shown. Every connector and tube is a CAD solid.

`plumbing/plumbing_scenes.py` retains the separate older-home braided-hose study assets. They are
not pages or dependencies of this modern push-fit guide.

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

# Modern under-sink shutoff, release, and tee sequence.
tools/cad-venv/bin/python hardware/quickstart/plumbing/modern/render_modern_tee.py

# Five rendered sheets and the bound PDF.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The PDF is 17 x 11 inches with five pages. Review every page at actual size, at quarter scale, and
in grayscale. The three text levels are the page title, scene caption, and one supporting line;
modeled geometry carries connector identity, valve state, fitting pose, and tube routing.
