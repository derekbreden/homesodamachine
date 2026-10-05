# Gun positioner guide tools

The [finished shop guide](../../hardware/gun-positioner-guide/README.md) is a
Letter PDF with individual HTML leaves, actual-CAD assembly views and a separate
book of 1:1 drilling templates.

`author.py` creates the operation leaves and their source manifest. `art.py`
selects named instances from the governing mechanics, camera and controller
mount assemblies; `clamp_art.py` renders the complete clamp hardware and metal
preparation detail. Wiring and measurement figures use vector SVG;
`schematic_detail.py` places the voltage-divider branch clear of its pin label. `templates.py`
projects the source plate outlines and hole coordinates onto overlapping Letter
tiles. Formed-angle face drawings retain their three-dimensional assembly notes.

`build.py` verifies current source hashes, every used image and the template
revision before rendering and binding one Letter PDF page per HTML leaf. It adds
chapter and operation bookmarks, the cover and drawings-shelf metadata.
`qa.py --render` renders both final PDFs through Poppler and checks page count,
Letter size, vector titles, fonts and source binding. Inspect every contact sheet
and the critical full-page operations before running `qa.py --record`.

Run the complete sequence in the hardware guide README after all governing
source files are frozen. Generated review images remain in its ignored `out/`
directory; the PDFs, artwork, HTML leaves and hash receipts are delivery assets.
Document checks do not establish received fit, load capacity or measured motion.

The reviewer finds `pdftoppm` on the command path or in the bundled desktop
runtime. Set `GP_PDFTOPPM` to its executable path when using another installation.
`qa.py --render --layout-only` supports an interim layout inspection while
governing inputs are changing; those renders cannot record final acceptance.
