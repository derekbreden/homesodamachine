---
title: Back-top's raised nameplate field joins the wall in the print
lede: The field no longer floats 0.4 mm off the wall in back-top's print mesh, so the STL is one body that trial preparation accepts.
date: 2026-10-25T05:44:27-05:00
commit: 07b8fcacb6589f5c2569deefee1e1779e738b533
model: printed-parts/enclosure/enclosure/enclosure.step
---
The rear-face fluting cut a 0.4 mm margin sheet that took the root off the 2.2 mm-proud nameplate field, so back-top's STL was two bodies. Back-top now uses the step back-bottom's raised letters already use: the print solid leaves the field out, a plain land covers its footprint, and the field joins back 0.1 mm into the wall after fluting.

Only back-top's print mesh and the payload cut from it change. Its STEP and every other piece come out byte for byte as before. The new STL is one watertight body.
