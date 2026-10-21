---
title: Installed wires follow the available passages and grooves
lede: All 103 conductors have proposed routes. The internal sensor leads share one passage into the foam cavity, and cartridge wires follow the existing paired grooves.
date: 2026-10-21T04:44:27-05:00
commit: 8fabece862cba7cecac6d640ec7aab3b87dbb5bf
model: manifold-layout/enclosure-assembly.step
---
The main foam cavity has a shared Ø7.5 mm cable passage through the cap cup
and lid, west of the pump. It carries the three temperature-bus feeds, three
carbonator-reed feeds and carbonator earth. Each reservoir reed column uses
its own existing passage.

Five conductors turn together through each reservoir passage, then separate
into four signal lanes and a continuous common beside the reeds. The
temperature bus also keeps a shared section between probes. Its feeds
continue through the first probe's splice row without doubling back.

The four cartridge leads dress upward from the pogo tails and follow the
existing grooves in pairs. Their joint insulation follows the wire bends.
The cartridge's printed geometry is unchanged. The flow-sensor leads rise
together in the existing gap beside the regulator. Other wire paths clear
the installed tubes and fittings.

The [manual routing review](https://github.com/derekbreden/homesodamachine/blob/main/hardware/wiring/installed/routing-review.json)
records 103 valid single-solid wires and 22 valid connector/insulation bodies,
matching native installed positions and separate shared-bundle cores. The
[exact contact follow-up](https://github.com/derekbreden/homesodamachine/blob/main/hardware/wiring/installed/contact-review.json)
finds no overlap outside the remaining mesh witnesses' local electrical
endpoints. Terminal estimates, physical dressing and enclosure closing
motions retain their stated scope in the wiring model.

Derek: “Please proceed resolve all things you can where the solutions are obvious and simple and result in simple things. If you need to bring me in, please give me 3D visuals to understand what you are talking about.”
