# Back-top and cold-core lid before the full print

The two Mark1 jobs use black Fiberon PET-GF15 on textured PEI. The new back-top slice includes the shortened rear ledges and the insert mouths that open square to the 45° seats. The existing lid download matches its current production mesh and emitted G-code. The five-way WAGO belongs to MAN-B in the front top. Its accepted opening is 8.10 × 30.20 mm, short side first, with 8.70 mm of insertion depth. [Back-top seat measurements](enclosure/prints/2026-11-27-back-top-square-seats-mark1/funnel-seat-toolpaths.json) · [Cold-core lid print plan](../cold-core/foam-cap/prints/2026-11-27-lid-fitted-wago-mark1/print-plan.json) · [Five-way bench result](../../print-tests/wago-pocket-support/prints/2026-11-27-fit-d-mark2/physical-result.json)

## Harness routing

The installed model shows five flexible leads passing through printed plastic along part of their routes. The table gives local movements that cleared the neighboring equipment and tubes in the model while holding the terminals fixed. The production illustration still shows the original routes. Correct it before using it to guide assembly, and allow slack for the meter cover to come off. The model check covers rigid obstacles. Lead-to-lead dressing and bend strain need the physical harness. [Wiring route and assembly](../../wiring/README.md#routing-and-assembly)

| Location | Leads in the model | Route that clears the printed part |
| --- | --- | --- |
| Back-top flow meter | J4‑IO25, J4‑V5 and flow GND enter the receiver floor and the cap. | Raise these three leads 2 mm near machine Y400. |
| Lid, V‑B return clip | J4‑IO25 and J4‑V5 cross the solid clip root for about 13 mm each. | Dress the pair 6 mm aft around the root. |
| Lid, DC1 and J1 | DC1‑V12 and J1 common each catch the lid locally. | Shift the DC1 bend 1 mm aft and the J1 bend 1 mm down. |

## Lid closure and frame seating

Use the November 21 HSM-0018 shell with this lid. Its ten M5 insert axes match all ten lid holes. The nearest October shell stations miss by 2.1 to 30.5 mm. On the current lid, each emitted shank opening clears 5.17 mm, and an 80 mm driver shaft clears all ten paths on the bare lid. Tighten the lid to its shell before installing equipment. Seal the lid perimeter and penetrations in the existing assembly order. [Lid measurements](../cold-core/foam-cap/prints/2026-11-27-lid-fitted-wago-mark1/preprint-review.json) · [Matching shell](../cold-core/foam-shell/prints/2026-11-21-shell-production-mark2/print-plan.json) · [Closure sequence](../../assembly/cold-core.md#7-close-and-populate-the-top-lid)

With both rear frame seats just touching, the nominal clearance above the lid’s V‑B wall is 0.038 mm. The bare lid can travel 0.149 mm toward its shell rim, clear of the installed core components. Seating it by 0.04 mm clears the wall even when the front of the frame comes down onto its ledge. Seating it fully gives about 0.19 mm at the rear-seat position. Check where the frame bears after tightening the lid. If the V‑B wall takes load, give the underside of the removable frame local clearance there. Both rear M3 × 12 screws have a clear approach from above, and the heads clear the silicone by 1.12 mm. [Frame and lid contact location](https://homesodamachine.com/3d#step:manifold-layout%2Fenclosure-assembly.step?find=solid%3A%20cold-core%2Ffoam-cap-lid-top%0Aclick%3A%20x%3D29.110%20y%3D231.067%20z%3D299.650)

## Retention and service

Each of the six back-top and four lid WAGO roofs has a single removable tree rooted in its own pocket. The crown clears its pocket mouth by at least 0.48 mm on the withdrawal path in the two print files. With the funnel and its frame removed, all three west-wall connectors have a rigid-body exit past their neighbors. Withdraw the disconnected housing 24 mm inboard, move it forward to the foremost pocket, and lift through the roof opening. Hand access and the dressing of disconnected leads depend on the assembled machine. [Back-top pocket measurements](enclosure/prints/2026-11-27-back-top-square-seats-mark1/wago-fit-toolpaths.json) · [Lid pocket measurements](../cold-core/foam-cap/prints/2026-11-27-lid-fitted-wago-mark1/wago-fit-toolpaths.json)

The water regulator’s revised saddle fit very well in the hand trial. Pisco and ASSE were accepted for this print. The remaining retention checks are the Digiten flow-meter cover on the full shell after support cleanup, and the carbonator pump on its production lid with the motor running. The PET-GF lid toolpaths support both pump guides throughout their first shoulder courses. A bench check can establish whether the meter latches securely and the pump stays seated under vibration. [Rear equipment fit history](rear-equipment-caps/production-fit.json) · [Water regulator hand fit](../../print-tests/equipment-snap-pairs/prints/2026-11-26-mark1-firm-regulator/physical-result.json) · [Pump retainer](../cold-core/foam-cap/pump-snap-fit.json)

The lower RiteAV jack catch has the longest exposed perimeter span in the back top, 14.09 mm. Both ends land on the cheeks, and Derek previously fitted and accepted the purchased jack in this catch. The vent edge bridges 8.64 mm with both ends supported by the previous layer. Inspect the catch for sag before seating the jack and the vent for clearance before mating the rear halves. Both rear label channels print free of supports. [Finished back-top print check](enclosure/prints/2026-11-27-back-top-square-seats-mark1/print-check.md)

Installed clearances were measured on assembly mesh `e933bfb74cabc3269b5e08a39bd6d9f9ab15bfb004d0abaa34f5944076b06089`. Nominal seating, rigid travel and commanded extrusion describe different stages of assembly. The first full build supplies the physical fit and operating observations.
