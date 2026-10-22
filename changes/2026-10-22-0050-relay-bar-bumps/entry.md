---
title: Relay 2's lower mounting bar is flat under its inserts
lede: The two 0.25 mm bumps on the underside of the bar that holds relay 2's lower screws are gone. The bar keeps one flat face, as the flat pads beside it do.
date: 2026-10-22T00:50:14-05:00
commit: 6b6daf0d8b39493d0b737287bd8e5b85550756bf
model: printed-parts/enclosure/enclosure/enclosure-back-top.step
---
Each M3 insert's bore on back-top's right wall is cut 0.25 mm taller on its supported side, and the 8 mm boss around it was grown the same 0.25 mm to keep a complete 2 mm ring. Relay 2's two lower holes share one bar, which already holds that whole 8 mm boss, so on the bar the growth added only a 0.25 mm crescent below its flat underside, one under each hole.

The bar now keeps its flat faces, as the stations inside the flat pads already did: 1.75 mm of plastic under each hole, where the insert needs at least 1.6 mm. Nothing else on the piece moved.

The geometry lint's new `bump` class reads this kind of defect: a patch rising off a flat face by under a millimeter and coming back down to it on both sides. It found these two on back-top and none elsewhere on the piece.

Derek: “I'm far less concerned about the 2 mm thick walls, and far more concerned about those bumps. When I speak of slivers and defects, it is those bumps, on the edge I indicated in the screenshot, that I am seeing.”
