# Home Soda Machine quick start

One 19 × 13 inch landscape sheet with seven illustrated steps, from mounting the faucet
to filling both flavors and pouring the first glass. Print at 100% on 13 × 19 inch paper.

This is the owner quick start published on [Drawings](https://homesodamachine.com/drawings).

The [On tap identity](/brand/README.md) matches the [install guide](../install-guide/README.md):
a cobalt masthead with the ice-blue faucet and orange drop, navy headings, cobalt step numbers,
ice-blue callouts and orange accents. The artwork in `art/brand/` contains the approved print marks.
Illustrations sit on white paper with uniform 0.6 pt slate contours (`#46515b`). Instruction
arrows use coral with white outlines; tubes and connectors use their physical colors.

The first-pour glass is filled with rounded ice cubes from the base to just above the cola.
Their pale faces, blue-gray shading and partial transparency remain visible at the sheet's
illustration size. The cola's near surfaces use 82% opacity over a dark-brown interior, revealing
the submerged cube faces. Step 7 calls for a glass filled with ice.
`tools/quickstart-codex/ice_scene.py` models the cubes in the frozen faucet-and-glass scene;
the PNG is shared as a snapshot with the install guide.

Step 6 shows the Big Blue Fill screen inside the machine display's frame and on the machine.
Select a flavor in the left rail, open **Fill**, put the bottle in the funnel, then tap
**Start filling**. The concentrate bottle has a rounded PET body, tapered shoulders, an open
ribbed neck, dark liquid and a wrapped COLA concentrate label. `tools/quickstart-codex/fill_scene.py` renders
the bottle and both display views from the frozen scene. `art/fill-screen.svg` and its PNG
supply the interface texture; `art/fill-screen-framed.png` is the framed close-up.
The cover shares the enclosure's matte black PET-GF appearance. Both Fill views use the same
exposure, and the complete frame has an uninterrupted outline.
The same seven step numbers appear in both documents, and the braided-hose link opens
install guide pages 9-11. The leak band closes the water and cylinder supplies and links to
the connection checks on page 23.

The rear illustrations draw the nameplate from `enclosure-assembly.step`: the white On tap
mark, HOME SODA MACHINE and the unit's QR code on the black plate.
`hardware/install-guide/_install_art.py the-back-face` renders step 3's back face.
`tools/quickstart-codex/scenes.py power` rebuilds the power and rear-connection snapshots from
the assembly, and `tools/quickstart-codex/insertion_actions.py power-ready` draws step 5 with
the cord drawn back. The manufacturing CAD in
`hardware/printed-parts/enclosure/nameplate/nameplate.py` reads the same `brand/mark.svg` master.

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
