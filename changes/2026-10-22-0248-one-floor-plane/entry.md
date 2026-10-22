---
title: The enclosure floor is one plane
lede: The cold core's 0.35 mm floor allowance is now the whole floor's level, not a pocket in the core's outline, so no step runs round the core on front-bottom or back-bottom.
date: 2026-10-22T02:48:44-05:00
commit: c4da6ef81e1eef0ab1293bc25980f4e918da3bc8
model: printed-parts/enclosure/enclosure/enclosure-back-bottom.step
---
The core rests on the floor and slides over it to its seat, so the face it bears on carries the running allowance and the cavity-floor transition, 0.25 mm plus 0.10 mm. That allowance was cut as a pocket in the core's rounded outline, which left the rest of the floor 0.35 mm higher: a step across front-bottom's floor ahead of the core, and a strip standing proud along both walls of back-bottom.

The whole floor now stands at that level, 0.35 mm under the pack's z = 0, over a 5.65 mm slab whose underside is unchanged. The core pocket starts on the floor and cuts nothing from it, and the compressor plate's relief in the front wall runs down to the floor rather than leaving a sill. Everything standing on the floor reaches the new plane.

Derek: “I don't mind decreasing or increasing by 0.35 millimeters anywhere. What I mind is introducing steps and edges.”
