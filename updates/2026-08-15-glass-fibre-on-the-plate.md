---
title: A build system, and glass fibre on the plate
start: 2026-08-09
end: 2026-08-15
kind: week
thumb: panel
lede: The flavor manifold was absorbed into the enclosure shell itself, and the first enclosure panel went on the printer in glass-filled PET.
---

The flavor pack's carriers stopped being parts. The separate flavor module, three valve-tray variants and the two-piece pump case are all deleted. Eight solenoids now stand on two valve panels and both pumps on two pump trays, printed as the front-top enclosure piece's own material, wall to wall — nothing ships under a valve and nothing is billed for one. A service procedure followed: the whole flavor manifold lifts out on the front-top as one body across eight parted joints, with the carbonator still full and pressurised.

{{fig:manifold-absorbed}}

![The front-top piece on 15 August, carrying both valve panels and both pump trays in its own material.](/update-images/2026-08-15-front-top.png)

Capacitive sensing was cut out of the machine on 10 August, one day after its controller, two printed sleeves and a four-wire loom were named as placed. No firmware ever read it — flow is the meter, level is the reeds, and dose is a counted volume. The I²C header stays as the bus star point. Per-unit parts cost moved from $1,285.61 to $1,282.14.

Both assembly models went from failing their own checks to passing. The packed appliance read seven failures at the start of the week and 96 of 96 gates green at the end, over a larger machine — 83 bodies against 77, 67 ports against 60. Eight rendered sub-assembly scenes were born beside it, each a posed subset that no single model file contains. The port-inventory register, 68 promised joints drawn as coloured discs in the 3D viewer, was retired once every row read ok.

The CAD tree got a build system on 13 August: 99 build actions, with the dependency graph learned by watching each generator run and recording every repository file it opens, including the solids loaded below Python where no hook reaches. A comment-stripped source copy is what actions declare, so writing a comment reruns one action rather than ninety-five.

The purchase ledger became machine-checkable. It went from five columns with order numbers and dates buried in prose to eight, with order number, ordered and delivered as their own fields, joined to a committed record of the actual orders and an audit procedure. It immediately found the ten controller carrier boards sitting at on-order for six weeks when they had arrived on 3 July.

The enclosure's front-top panel went on the printer in glass-filled PET on 15 August — 290 °C nozzle, 100 °C bed, 50 °C chamber, fan off, 5 mm³/s — with every geometric and profile setting identical to the PETG version, so the material is the only difference. It was still running that evening, six hours in, with a clean wall surface.

Arrived this week: a diamond nozzle and 3 kg of glass-filled PET on the 11th, zip ties on the 11th, M5 heat-set inserts, screws and fender washers for the compressor floor on the 14th, and two filament storage boxes on the 15th, a 3 kg spool being too large to turn in the existing dryer. The whole rear-wall CO2 chain was ordered in one tube size on the 11th.

The ten assembled controller boards ordered on 3 August shipped on the 12th and reached the Omaha sort facility on the 15th.

The daily feed that ran from 7 March to 28 June was removed from the site, recoverable under a tag. In its place the site carries a build tree: one unit's assembly as a drill-down read off the build order, the procedures, their step headings and the cards.
