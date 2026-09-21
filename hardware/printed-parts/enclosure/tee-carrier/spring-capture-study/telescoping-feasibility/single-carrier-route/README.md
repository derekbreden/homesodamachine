# Continuous carrier and underside assembly

A single continuous carrier fits the frozen enclosure in its working positions. **It cannot follow the tested straight insertion paths through the unchanged front-top.** A bounded virtual bottom opening admits the carrier and its preloaded springs, but transferring the removed guide stock directly onto front-bottom blocks the existing shell-closing slide.

Eliminating the centre joint is credible only with an intentional guide-closure arrangement. One broad stationary keeper attached to front-top before the shell closes is a simpler architecture to investigate than interlocking spring guards. It would leave an uninterrupted moving beam, while adding a fixed support connection that must carry the lower guide loads. That keeper is a concept, not a designed or qualified part.

This is a read-only native study against front-top SHA-256 `63471e1fa49233b281b6334ec3ef82c73a3abe8c635eb537c4f38e2a2e6e5508` and the matching frozen carrier. Its provisional tee branch datum is 20.07 mm. The measured tee placement requires rebase. **No production source, coupon, slice or print is released.**

## Reference geometry and barriers

The continuous reference blank replaces only the joint strip, X−9.18..8.07, with the uninterrupted web and shelf described by `_carrier_blank`. The nearest tie cut starts at |X|9.43 and the nearest tee trough at |X|11.32; neither is altered. Native geometry outside the centre strip is retained. The reference is one valid solid, spanning X±107.5, Y89.71..130.86 and Z167.174..229.119 mm. Its centre has no lap, screws or insert holes.

It has zero modeled overlap with the fixed front-top at release, connected and the 4.65 mm aft stop. The obstruction is access to those positions:

| Route reading | Actual native result |
|---|---|
| Straight rise from below at the aft stop | Only 0.25 mm clearance below the final position; at −0.30 mm, 18.978 mm³ intersects the fixed floor at Z166.874..166.924. |
| Same route at −1 mm | 334.707 mm³ intersects the floor, side sills and fore shoulder, spanning Z166.174..180.800. |
| Carrier entirely below the loose top, −70 mm | Clear, but the intervening rise is blocked. Front-bottom is already absent from the check. |
| Centred rear approach, Y offset4.90 mm | 4.500 mm³ intersects both upper aft shoulders at Y116.51..116.76, Z226.119..229.119. |
| Centred rear staging at offset38.55 mm | 5056.547 mm³ intersects the side walls/shoulders. The independent inboard shifts used by two halves are unavailable to one rigid blank. |
| Existing elevated rear approach, +70 mm Z | The full-width ends intersect the side walls above the service openings. |

The fixed floor is carried by `_tee_carrier_fixed_features` and shaped by `_tee_carrier_clearances`. The service slots and upper aft stops are cut by `_tee_carrier_service_slots`. The low fore shoulder comes from `_tee_carrier_fore_guide`. The side sill lies in the existing Z-seam storey, **Z160..174.8**; the fore shoulder reaches **Z180.8**. These are substantial bearing and seam surfaces, not incidental printing artifacts.

The probes do not exhaust arbitrary rotations and coupled six-axis paths. They establish why the existing straight rear route and a direct rise from the open underside do not accept the continuous blank.

## Bounded bottom opening

`bottom_opening.py` encloses the complete vertical travel with component prisms, verifies that the continuous closed-cup carrier is wholly within those bounds, and opens only the lower fixed stock that blocks the rise. The cut is confined to **Z159.9..180.801**, preserving the upper aft stop and top guide. It includes space for the two held springs and temporary pushers.

- The entire **70 mm upward carrier sweep** is clear.
- Both spring and temporary-pusher sweeps are clear. Each spring is held at **12.15 mm** in its closed moving cup, using the same flat pusher envelope as the closed-cup study.
- The front-top remains one valid solid.
- The opening removes **10,861.463 mm³** of stock, in **nine disconnected regions**, spanning X±107.5, Y94.11..135.76 and Z160..180.8.
- The upper aft stop/top bearing loses **zero material**. The lower bearing floor, side sill/seam stock and the aft portion of the fore shoulder lose material in the entry footprints.

The nine removed regions are a record of required clearance, not nine proposed parts. They cannot be exported as an adequate keeper without joining and supporting them. A keeper must restore the lower bearing planes, the fore travel constraint, the side-slot restraint and the affected Z-seam load path. One valid remaining solid does not establish adequate rigidity.

The end cups themselves remain simple: the full Ø6.57 moving bore is closed laterally, and the existing fixed cup is 2 mm deep. No spring-ID guide or retained loading plug is used. The open middle span is still **6.40..11.05 mm**. Holding two springs while lifting one carrier, controlled pusher release and real spring stability remain physical questions. Geometric clearance does not establish that this paired loading is easier than loading the halves separately.

## Why direct closure by front-bottom fails

The top shell closes by sliding in Y. Putting the removed stock on front-bottom holds it stationary while front-top and its carrier approach. Native checks find collisions before the final position:

| Top-shell Y shift from home | Carrier / transferred stock | Opened front-top / transferred stock |
|---:|---:|---:|
| −10 mm | 48.375 mm³ | 5506.308 mm³ |
| −5 mm | 3.225 mm³ | 2898.558 mm³ |
| −1 mm | 0 | 604.638 mm³ |
| 0 | 0 | 0 |

The carrier contact at −10 mm is the fore shoulder, X±101..104.5, Y94.11..95.61, Z175.3..180.8. The shell contacts are within the Z160..174.8 seam storey. Clear final mating surfaces do not establish an assembly route.

Keeping a broad keeper with front-top during shell closure would carry those surfaces together and avoid this particular transfer conflict. Its attachment, connecting stock, support access and relation to the existing bottom rail remain undesigned. If front-bottom supplies final capture, the keeper would still need a way to stay correctly seated during the closing slide.

## Parts, motions and stiffness implications

| Architecture | Carrier-related parts and assembly | Consequence |
|---|---|---|
| Two substantial carrier halves with a simple snap joint | Two moving pieces; load each spring, seat each half, join across the centre. | Retains an interface in the moving load path. Full-width bending and engagement length must be measured; the old joint is not prescribed for reuse. |
| One carrier, guide stock moved directly to front-bottom | One moving piece; lift it from below, then close the lower shell. | The tested shell slide collides. This arrangement is not viable with the unchanged closing route. |
| One carrier plus one broad keeper attached to front-top | One moving piece and one fixed keeper; preload/lift the carrier, seat the keeper, withdraw loading tools, then close the shell. | Removes the centre interface from the moving beam. Adds a fixed support connection that needs broad engagement and a complete load path. A connected keeper and its access are not yet modeled. |

The physical joint feedback distinguishes secure seating from unwanted bending/bowing. It does not provide a load, a unique bending axis or numerical stiffness. A continuous beam removes joint play as one possible contributor, but it can still bend through insufficient section depth or short engagement. A new design needs a full-width comparison under the same hand loading, including unequal-hand operation, after the lower guides and any keeper are installed. A latch-only coupon cannot answer that question.

The preferred next architectural comparison is the continuous moving beam with one broad stationary closure versus two broad moving halves with a simple long-engagement joint. Neither should inherit the old small keys or joint solely because a coupon stayed assembled. The faucet display cover supplies the physical example for substantial walls and simple snapping; it is not quantitative strength evidence for either carrier arrangement.

## Reproduction

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/single-carrier-route/probe.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/single-carrier-route/bottom_opening.py
```

`checks.json` records the intact-wall route barriers and a conservative opening diagnostic. Its diagnostic XY allowance can touch nominal stops and is not an implementation proposal. `bottom-opening-checks.json` records the bounded opening, continuous entry sweeps and failed shell-closure witnesses. STEP files are native inspection artifacts only. All inputs and results are included in the parent study's digest manifest.
