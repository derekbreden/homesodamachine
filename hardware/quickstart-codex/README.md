# Home Soda Machine quick start

One 19 × 13 inch landscape sheet with seven illustrated steps, from mounting the faucet
to filling both flavors and pouring the first glass. Print at 100% on 13 × 19 inch paper.

This is the owner quick start published on [Drawings](https://homesodamachine.com/drawings).

The [On tap identity](/brand/README.md) matches the [install guide](../install-guide/README.md):
a cobalt masthead with the ice-blue faucet and orange drop, navy headings, cobalt step numbers,
ice-blue callouts and orange accents. The artwork in `art/brand/` contains the approved print marks.
Illustrations sit on white paper with uniform 0.6 pt slate contours (`#46515b`). Instruction
arrows use coral with white outlines; tubes and connectors use their physical colors.

Step 6 shows the Big Blue enclosure display. Select a flavor in the left rail, open **Fill**,
put the bottle in the funnel, then tap **Start filling**. `art/fill-screen.svg` and its PNG
are fixed snapshots of the install guide's screen illustration. The same seven step numbers
appear in both documents, and the braided-hose link opens install guide pages 9-11.

The power-connection illustration uses the white On tap mark on the black nameplate.
`tools/quickstart-codex/brand_scenes.py` renders that mark in the frozen scene, preserving
the physical lettering and ratings. The manufacturing CAD in
`hardware/printed-parts/enclosure/nameplate/nameplate.py` still carries the glass mark.

The PDF, cover, fonts and artwork are committed snapshots. The manual authoring scripts
are in `tools/quickstart-codex/`, outside the hardware build. The quick start, install guide
and weld rotator guide are the source material for this edition.

## Compose and review

From the repository root:

```sh
tools/cad-venv/bin/python tools/quickstart-codex/build.py
pdftoppm -scale-to 1900 -singlefile -png hardware/quickstart-codex/quick-start-codex.pdf hardware/quickstart-codex/out/review
```

The composer writes the PDF, cover, document metadata and a copy in `output/pdf/`. `out/` holds
page renders, contours and text-box measurements. Review the full sheet and its small action
cues at reading size before publishing.
