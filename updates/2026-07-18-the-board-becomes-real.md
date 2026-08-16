---
title: The board becomes real
start: 2026-06-21
end: 2026-07-18
kind: period
lede: Ten controller boards were ordered and the design behind them retired the next day, and a paste-layer defect was found two days before the assembled boards were paid for.
---

## One board, two designs

On 27 June ten through-hole carrier boards went into production at a board house — the project's first PCB fab run, $122.71 delivered. They arrived on 3 July.

On 28 June the design that produced them was deleted. Its replacement is a fully machine-assembled board built from bare silicon rather than plug-in modules: microcontroller, two I/O expanders, two driver arrays, real-time clock, two pump H-bridges, two switching regulators and a USB-C programming block, on six copper layers, with gerbers, assembly bill of materials and pick-and-place files generated on every build.

Routing six layers with through-hole vias meant changing the routing engine. The project now maintains forks of several upstream circuit-design packages on its own branch, pinned by commit, one of them carrying an autorouter that emits through-hole vias natively. An experiment letting the router use all six layers freely was committed on 29 June and reverted on 1 July as not manufacturable.

## Two audits

The board was audited against itself twice, on 11 and 13 July.

The second audit found that the exported solder-paste layer covered only rectangular pads: 148 of 330 surface-mount lead pads had no paste opening at all. A stencil cut from that file would have placed nine integrated circuits onto bare, paste-free pads. It was fixed in the project's own fork of the gerber exporter, with an automated coverage check added behind it.

The board also gained protection that does not depend on software being correct — reverse-polarity protection on the 12 V inlet, a surge clamp, a buzzer flyback diode, hardened flow-sensor and display-cable inputs, and a gas-leak-to-compressor interlock built from a logic gate, so the compressor cannot run when the gas sensor trips. A broken wire, an unpowered controller, or unprogrammed firmware all leave the compressor off.

On 15 July ten assembled boards were ordered: four layers, black mask, gold plating, epoxy-filled vias, $702.00 all in.

## Two subsystems cut

Bag-in-box syrup input was removed on 15 July. Each flavor reservoir formerly filled two ways — a hopper on top or a commercial syrup-bag adapter on the back panel. It is now hopper-only. The valve manifold went from twelve solenoids to ten, and the printed bag-gate tray was deleted.

The Colder CO2 quick-disconnect went the same day, $43.84 per unit removed; a push-to-connect fitting already in the build becomes the sole CO2 inlet.

A pocketable demo that runs the board and clicks a valve from an iPhone's USB-C port was built, landed on the main branch, and was then backed out and shelved. Its clearance floor came out at 0.137 mm against the board's own 0.14 mm baseline. The fab's minimum is 0.127 mm.

## The casting bench

A silicone casting bench was bought and stood up: a 5-gallon stainless vacuum degassing chamber, a 30-quart convection oven for post-cure, food-contact platinum silicone, pigment, mold release and mixing cups. Two mold part-sets were modelled and four mold prints logged — one failed outright when auto-generated supports toppled mid-print, two completed, and the halves fit with too much clearance.

## The first scorecard

The enclosure gained machine-checked requirements measuring whether every component is correctly positioned, whether every hose and wire connector has a real location on the part, and whether parts are real geometry rather than placeholder boxes.

Its first run on 17 July found that the sealed refrigerant loop — compressor to condenser to evaporator and back — existed in no topology file at all, so it had been silently absent from the completeness count. It also flagged that the compressor's rotation points both refrigerant stubs at neither of the things they must connect to, and that only 4 mm of clearance sits behind the condenser.

## Toward metal

The period closes pointing at the pressure vessel. On 18 July a swivel-blade deburrer, a cobalt countersink set and abrasive weld-prep pads were bought — all for deburring, chamfering and surface-prepping the 316L vessel.

The board has never been powered. The pin assignments are provisional until tested, several protection circuits depend on polarities nobody has measured, and the shipping firmware still targets the old prototype's motor driver: two pins agree with the new board and twelve conflict.
