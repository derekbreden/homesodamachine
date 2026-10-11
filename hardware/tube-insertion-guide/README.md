# Tube insertion jig build guide

Letter pages with one CAD view per assembly or operating action. The guide covers the
printed T handle, bench press, cap-support puck, sleeve fitting and sleeved-tube insertion.
The [fixture](../printed-parts/fixtures/tube-insertion/README.md) is bench tooling.

The attached faucet lever remains down at unpressed rest while the sleeve is fitted and
the sleeved tube enters the bare Touch-Flo. The TPU thimble goes onto the square-cut LLDPE
tube outside the donor and reaches its annular cap before the sleeved end enters the
metal port. The [operator observations](../printed-parts/faucet/lever-replica/assembly-observations.json)
and [faucet procedure](../assembly/faucet-and-umbilical.md) establish that sequence.

The later shell insertion belongs to the [faucet assembly guide](../faucet-assembly-guide/README.md).
Its faucet lever flips up for entry, the shell pushes it forward as the donor seats, and
the lever snaps down to unpressed rest. The shell prevents the seated lever from reaching
the flipped-up entry pose.

## Files

| File | Purpose |
| --- | --- |
| `NN-name.html` | Authored pages in numbered order. |
| `style.css` | The Letter page system, following the weld-rotator guide. |
| `art/*.png` | Rendered fixture CAD and wet-path sections. |
| `tube-insertion-guide.pdf` | The bound guide. |
| `tube-insertion-guide.cover.png` | Cover thumbnail for the drawings shelf. |
| `tube-insertion-guide.pdf.json` | Drawings shelf metadata. |
| `out/` | Ignored page renders and temporary STEP scenes. |
| `../../output/pdf/tube-insertion-guide.pdf` | Identical delivery copy. |
| `../../output/pdf/tube-insertion-guide.sources.json` | Manual source, artwork and print-project hash receipt. |

Coral identifies the part or fastener added or moved on the current page; existing
printed structure stays black. Brass identifies threaded metal nuts. Blue identifies
alignment tools or marks. Screws float off their holes along the axes on which they enter.
The existing thimble and accepted faucet lever retain their source geometry. A pictured
section opens the actual shapes to show the tube end and cap; it is not a dimensional
drawing of elastic deformation.

The fixture is an unprinted prototype. The donor/lever sequence comes from the linked
physical observations. CAD renders establish the depicted geometry, not insertion force,
tube grip, seating performance or fixture endurance. During ordinary assembly, the guide
uses actual port depth and two tube marks to set travel without assuming the donor's
nominal port floor. The press provides up to 20 mm of guided travel. For a measured port deeper than
20 mm, the T handle starts the sleeved tube by the excess depth before the ram engages.

The two F liners are thick finished half-channel blocks with 28 mm contact length and
3.375 mm minimum backing. Their manufacturing print pose puts the tube axis vertically,
on an 8 x 20 mm footprint. Rotate each finished block into its rigid jaw pocket for use;
the gripping shape is already present in the print.

## Manual regeneration

```bash
tools/cad-venv/bin/python tools/tube-insertion-guide/insertion_art.py
tools/cad-venv/bin/python tools/tube-insertion-guide/build.py
```

The art script accepts individual scene names; `--list` lists them. The binder renders
the HTML pages, checks the authored page bounds and joins the leaves in numbered order, then writes the delivery copy and source receipt.
These scripts run by hand. No build target, hook, graph entry or recurring verification
step invokes them. The HTML, artwork, PDF, cover and metadata are committed artifacts.
