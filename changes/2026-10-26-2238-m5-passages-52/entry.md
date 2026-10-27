---
title: Printed M5 pass-throughs use the selected Ø5.2 mm fit
lede: The four enclosure quadrants share the Ø5.2 mm passage selected from the printed screw samples. The printed shop fixtures use the same fit.
date: 2026-10-26T22:38:55-05:00
commit: 5104eaa42
model: manifold-layout/enclosure-assembly.step
---
The shared printed M5 pass-through diameter is **5.2 mm**. It applies to the enclosure's four screw-bearing quadrants and the tube-insertion and weld-rotator fixtures. The enclosure's mating planes, screw positions and installed pump-retainer pose stay fixed.

Derek's physical samples establish the selected fit: the 12 mm bearing passed the screw by pushing; the 40 mm bearing sometimes needed turning to pass a resistant section. The 5.1 mm sample needed turning throughout. The [physical result](https://github.com/derekbreden/homesodamachine/blob/main/hardware/print-tests/m5-seam-bearing/physical-result.json) records his accepted fit and variability.

The section shows the upper west passage around a nominal Ø5 mm screw envelope. The tighter passage adds plastic around the screw; the envelope depicts clearance, not individual thread contact. [Native part checks](https://github.com/derekbreden/homesodamachine/blob/main/hardware/printed-parts/enclosure/enclosure/m5-pass-fit-review.json) verify valid solids with added material confined to the passage and entry reliefs. [Assembly checks](https://github.com/derekbreden/homesodamachine/blob/main/hardware/printed-parts/enclosure/enclosure/m5-pass-fit-aggregate-review.json) verify the four replacements and preserve the other installed geometry.
