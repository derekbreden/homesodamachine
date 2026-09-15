# Home Soda Machine quick start

One 19 × 13 inch landscape sheet with seven illustrated steps, from mounting the faucet
to filling both flavors and pouring the first glass. Print at 100% on 13 × 19 inch paper.

The illustrations sit on white paper with uniform 0.6 pt slate contours (`#46515b`).
This is the owner quick start published on [Drawings](https://homesodamachine.com/drawings).

The header uses the [On tap identity](/brand/README.md): a cobalt faucet and orange drop
beside the navy title. The artwork in `art/brand/` is a snapshot of the approved print mark.
Instruction arrows and connector colors retain their functional colors.

The power-connection illustration uses the white On tap mark on the black nameplate.
`tools/quickstart-codex/brand_scenes.py` renders that mark in the frozen scene, preserving
the physical lettering and ratings. The manufacturing CAD in
`hardware/printed-parts/enclosure/nameplate/nameplate.py` still carries the glass mark.

The PDF, cover, fonts and artwork are committed snapshots. The manual authoring scripts
are in `tools/quickstart-codex/`, outside the hardware build. The quick start, install guide
and weld rotator guide are the source material for this edition.
