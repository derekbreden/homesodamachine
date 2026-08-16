---
title: Two machines
start: 2026-07-26
end: 2026-08-01
kind: week
lede: The hardware tree was forked into a second, taller and narrower appliance, and the stripped-down Lite edition was deleted.
---

On 26 July the whole hardware tree — 955 files — was copied into a second edition. By the end of the week the two had genuinely diverged: 290 files differ, 128 of them source, with about 13,600 lines added and 6,400 removed.

The new machine is a different silhouette. Its cold core is rotated a quarter turn so its short axis runs across the cabinet, which buys a tall column of space above and in front of it. It carries its own full set of printed enclosure pieces, its own valve manifold — five identical two-valve trays where the original has four differently-shaped ones — and its own generator scripts.

{{fig:two-machines}}

The Lite edition was deleted on 27 July: 57 files, an enclosure, electronics trays, a funnel and a silicone funnel mould, preserved under a tag. It was the stripped build — a transparent printed cabinet around the existing counter prototype, paired with a resold external carbonator.

The repository, the viewer and the tooling all learned what an edition is. A single list of machines now feeds the dev server and the 3D viewer's routing, with an edition selector in the interface. Beside it, a static checker walks every edition's scripts and fails on any file path that escapes its own machine's tree — both trees contain the same filenames, so a stray path reports the wrong machine's numbers.

On the original machine, the cold core came down onto the floor. The screws holding its bottom foam cap sit in counterbores now, so the core stands flat and the printed ring it used to stand on is gone. Appliance depth dropped from about 387 mm to 369 mm. The CO2 line was rerouted to stay low and enter the core's own front face rather than crossing the service bay, and the power block's AC hub, one relay and the ground-lug stack got real mounting positions.

A printed shop-floor card deck for tool stations was built over 26–27 July: 13 letter-size station cards — drill press, band saw, laser welder, hydro test, tube bench, braze bench, vacuum and charge, crimp, solder, electrical test, plastic fittings, pour and cure, printers — each rendered and collected into a printable PDF, with a photograph of every tool.

Two candidate reservoir filaments were retired. The flavor reservoirs now print in ordinary translucent PETG: a filled grey filament cannot show fill level through the wall, and a resin certificate covers the pellet rather than the finished print.

Nothing was bought or delivered this week. Six June deliveries were recorded as received — the vacuum degassing chamber, the convection oven, the platinum silicone kit, pigment, mould release and clear acrylic sealer — opening a casting and moulding category on the tools ledger.
