# Sourcing — one-knob-one-parameter

All observations 2026-09-28, through Derek's Chrome (Amazon delivery to Lincoln
68520). Amazon entries are Prime listings only; each was opened (or fetched) and
its Prime delivery signal confirmed before recording. "Search list" means the
figure came from the Prime-filtered results page rather than the product page.

## Rotary axes (the knobs that turn about the dot)

- **4-inch horizontal/vertical rotary table, HHIP 3906-2304** — the couch
  rotation (horizontal, under the rotator) and the hole-axis rotation (vertical
  mount beside the tube) in `ideas/isocentric-couch-and-gantry.md`; the yaw
  table in `ideas/c-arm-on-the-gun.md`. Worm drive, graduated dial, table lock
  and a stiff cast-iron bearing in one bought part.
  - Source: https://www.amazon.com/dp/B093CCXNVX · Observed: 2026-09-28 · Price: $159.80 · Prime: yes
  - Stock/delivery signal: "Only 1 left in stock"; "FREE delivery Thursday, October 1"
  - Specs on page: table Ø110 mm, horizontal height 80 mm, vertical overall height 152 mm, centre height 86 mm, 280 mm long with handle, 19.8 lb.
  - Volume/interchangeability evidence: only 2 reviews on this listing. The evidence is the category: the Prime-filtered search for 4-inch H/V rotary tables returned ≥10 Prime listings from different sellers (HHIP, Vertex, VEVOR, several unbranded), $99–$469. It is a standard machinist accessory with a common form (4 T-slots, MT2 centre bore, H/V mounting).
  - Observation vs estimate: price, stock, delivery and dimensions observed. Worm ratio for this listing not shown on the page.

- **4-inch rotary table, unbranded (36:1)** — same role; the cheapest Prime example and the one whose page states the reduction.
  - Source: https://www.amazon.com/dp/B0BYJBYM8V · Observed: 2026-09-28 · Price: $99.00 · Prime: yes
  - Stock/delivery signal: "Only 5 left in stock"; "FREE delivery Wednesday, September 30"
  - Specs on page: 36:1, handwheel graduated in 10-arc-minute divisions, rim in 5-minute increments, handwheel zeroable, vertical centre height about 51 mm.
  - Volume/interchangeability evidence: as above (category, many sellers). No review count shown.
  - Observation vs estimate: observed. 36:1 means 10° per handwheel turn; reading to ~0.05° by interpolation is my estimate.

## Linear axes and stops

- **Micrometer head, 0–25 mm, 0.01 mm, ratchet thimble** — the stop and readout for couch X, gantry standoff and (in the cartridge idea) any linear trim. The carriage is held against the spindle by gravity or a spring, so the micrometer is both the knob and the stop.
  - Source: https://www.amazon.com/dp/B07VHMYCGD · Observed: 2026-09-28 · Price: $15.99 · Prime: yes
  - Stock/delivery signal: "Only 4 left in stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: 8 reviews on this listing. Micrometer heads are a standardised instrument (plain thimble, 12 mm or 3/8 in stem clamp); the same search showed Prime listings from Dasqua ($28.44) and Mitutoyo 150-801 ($100.00), so the part does not depend on one seller.
  - Observation vs estimate: observed; the Mitutoyo and Dasqua prices are from the search list.

- **MGN12H linear rail, 250 mm, with preloaded carriage** — couch X slide, standoff rail, gantry Z guide.
  - Source: https://www.amazon.com/dp/B0BYV8SYPG · Observed: 2026-09-28 · Price: $17.99 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: 71 reviews; MGN12 is the dominant miniature-rail profile in the 3D-printer ecosystem, sold by many vendors in interchangeable form.
  - Observation vs estimate: observed. "Blocks are pre-loaded" is the listing's claim.

- **XYZ manual stage 40 × 40 mm, LD40-LM (Oumefar)** — the wire-tip position (lead, height, lateral) on the roll body, independent of the gun's standoff.
  - Source: https://www.amazon.com/dp/B08J2G7QY3 · Observed: 2026-09-28 · Price: $116.59 · Prime: yes
  - Stock/delivery signal: "Only 1 left in stock"; "FREE delivery Wednesday, September 30"
  - Specs on page: X/Y ±6.5 mm, Z 10 mm, 0.01 mm micrometers, cross-roller, 0.44 kg, 2 kg load.
  - Volume/interchangeability evidence: the LD40-LM is a generic optics-stage pattern; the Prime search returned five LD40-LM-type listings from different sellers ($94.99–$189.99).
  - Observation vs estimate: observed.

## Roll bearing (must pass the gun nose-first; see the isocentric idea)

- **6816-2RS thin-section bearing, 80 × 100 × 10 mm (uxcell)** — a preloaded pair carries the roll body around the grip axis; the 80 mm bore is sized so the gun can pass through nose-first with its captive umbilical (a closed ring cannot be threaded over the cable).
  - Source: https://www.amazon.com/dp/B07RQ4RXDR · Observed: 2026-09-28 · Price: $14.59 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: "50+ bought in past month", 90 reviews; ISO 618xx series, four other Prime sellers in the same search ($11.99–$16.69).
  - Observation vs estimate: observed. Whether 80 mm clears the real gun needs the scan.

- **6812-2RS, 60 × 78 × 10 mm, 2 pcs (uxcell)** — the smaller alternative if the bearing only has to surround the cable bundle behind the grip.
  - Source: https://www.amazon.com/dp/B082PSBTLP · Observed: 2026-09-28 · Price: $14.39 (2 pcs) · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Today 5 PM – 10 PM on qualifying orders over $25"
  - Volume/interchangeability evidence: "50+ bought in past month", 177 reviews; ISO series.
  - Observation vs estimate: observed.

- **32011 tapered roller bearing cone and cup** — a stiffer back-to-back preloaded pair (55 mm bore) where the bearing only surrounds the cable bundle.
  - Source: https://www.amazon.com/dp/B0DZNL4HHT · Observed: 2026-09-28 · Price: $16.89 · Prime: yes
  - Stock/delivery signal: "Only 3 left in stock"; "FREE delivery Thursday, October 1"
  - Volume/interchangeability evidence: 36 reviews; ISO 32011 is a standard tapered-roller size.
  - Observation vs estimate: observed. Crossed-roller bearings did not surface in the Prime-filtered search.

- **Worm gear set, module 1, 40:1 (uxcell)** — the roll drive. Its steel worm could also drive a larger printed module-1 sector on the roll body. It self-locks and has a zeroable dial on the worm shaft.
  - Source: https://www.amazon.com/dp/B0G4WLD1T9 · Observed: 2026-09-28 · Price: $23.99 · Prime: yes
  - Stock/delivery signal: "Only 7 left in stock"; "FREE delivery Thursday, October 1"
  - Volume/interchangeability evidence: 3 reviews; module-1 worms are standard, and uxcell lists the same family in 20:1–40:1 and module 0.5–1.5.
  - Observation vs estimate: observed. Whether a printed wheel meshes well with this worm is my assumption.

## Reading and recording

- **AS5600 magnetic angle encoder modules, 3 pcs (UMLIFE)** — a logged angle for every rotary knob (on a handwheel shaft, with turn counting) so the station writes its own record.
  - Source: https://www.amazon.com/dp/B094F8H591 · Observed: 2026-09-28 · Price: $7.99 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: "100+ bought in past month", 70 reviews; at least seven other Prime AS5600 listings in the same search.
  - Observation vs estimate: observed.

- **Klein Tools 935DAG digital level and angle gauge** — a gravity reading of the hole angle and roll body and a check of each cartridge's as-printed angles. It has a magnetic base, so it sits on a steel pad fixed to the part it reads.
  - Source: https://www.amazon.com/dp/B07ZWW3BW5 · Observed: 2026-09-28 · Price: $32.97 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: "5K+ bought in past month", 16,508 reviews.
  - Observation vs estimate: observed. Resolution is not stated in the captured text (commonly 0.1°, which is my assumption).

## Kinematic seats (cartridges, shell interface)

- **1/4 in G25 chrome steel balls, 100 pack (BC Precision)** — the three balls under each pose block and on the shell.
  - Source: https://www.amazon.com/dp/B007B2AIZ2 · Observed: 2026-09-28 · Price: $6.95 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: "100+ bought in past month", 296 reviews; G25 AISI 52100 is a commodity grade.
  - Observation vs estimate: observed.

- **6 mm × 40 mm precision-ground dowel pins, 24 pcs** — the pin pairs that form the V-seats.
  - Source: https://www.amazon.com/dp/B0GS1B62Y1 · Observed: 2026-09-28 · Price: $6.49 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Today 5 PM – 10 PM on qualifying orders over $25"
  - Volume/interchangeability evidence: 19 reviews; dowel pins are a standard part sold by many vendors.
  - Observation vs estimate: observed; "precision ground" and stainless are the listing's claims.

## Umbilical support

- **Spring balancer 0.5–1.5 kg (MECCANIXITY)** — hangs the umbilical so its pull on the roll body stays about constant between settings.
  - Source: https://www.amazon.com/dp/B09F61YQNL · Observed: 2026-09-28 · Price: $20.29 · Prime: yes
  - Stock/delivery signal: "Only 13 left in stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: 41 reviews; the same search showed three more Prime balancers in the 0.5–1.5 kg class, including a QWORK 2-pack at $16.97 marked "50+ bought in past month" (search list).
  - Observation vs estimate: observed. The umbilical's weight per metre is unknown.

## Custom flat parts

- **SendCutSend laser/waterjet-cut plate** — an R 300 aluminium arc for the C-arm, gantry arm plates and the couch plate, if printed parts prove too compliant.
  - Source: https://sendcutsend.com/ · Observed: 2026-09-28 · Price: instant online quote (not quoted here) · Prime: NA
  - Stock/delivery signal: site states "delivered in as little as 24 hours"; rush and overnight options; "175+ materials in stock".
  - Volume/interchangeability evidence: the site lists 6061-T6 in 12 thicknesses (.040–.750 in) and MIC-6 cast tooling plate (.250–.500 in), and claims 100,000+ customers. Any DXF-driven cutter could make the same part.
  - Observation vs estimate: site claims observed. No part was quoted.

## Wave 3 — knob-wired suspension

Wire rope (1/16 in 7x7 stainless, B07Z373ND9) and M4 turnbuckles (B0D6FLB7KH)
are in carry-and-locate's sourcing and were not re-observed here. So were the
spring balancers above and SFU1605 stages (machine-that-learns).

- **Tr8×2 lead screw, 100 mm, with brass nut** — the anchor slide for each angle wire in `ideas/knob-wired-suspension.md`: 2 mm per turn, a 100-division dial reads 0.02 mm (0.005–0.017° of angle). Wire tension always loads the nut the same way.
  - Source: https://www.amazon.com/dp/B092YV88MB · Observed: 2026-09-28 · Price: $7.49 · Prime: yes
  - Stock/delivery signal: "Only 2 left in stock"; "FREE delivery Tomorrow, September 29"
  - Volume/interchangeability evidence: 185 reviews; Tr8 lead screws are the standard 3D-printer Z part, and the same search showed five other Prime Tr8 listings (Tr8×2, Tr8×4, Tr8×8; $7.30–$13.59).
  - Observation vs estimate: observed.

- **1/8 in (M3) stainless wire-rope thimbles, 50 pcs (YAMASO)** — keep the wire's end geometry fixed where it hooks into a printed V-notch, so the effective length repeats after unhooking for lift-off.
  - Source: https://www.amazon.com/dp/B0B2VJC6PR · Observed: 2026-09-28 · Price: $6.99 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Today 5 PM – 10 PM on qualifying orders over $25"
  - Volume/interchangeability evidence: "100+ bought in past month", 348 reviews; a rigging commodity.
  - Observation vs estimate: observed. Whether a thimble in a V-notch repeats to hundredths of a millimetre is unmeasured.

- **SUS301 constant-force spring, 2.09 lb (~9.3 N), 36 in extended** — a preload whose force does not change as the angle knobs move the attachment (branch W-C).
  - Source: https://www.amazon.com/dp/B0F446L2VW · Observed: 2026-09-28 · Price: $39.99 · Prime: yes
  - Stock/delivery signal: "In Stock"; "FREE delivery Today 5 PM – 10 PM"
  - Volume/interchangeability evidence: weak. No reviews shown; the same seller lists a family of loads ($33.99–$39.99). The spring balancers (0.5–1.5 kg class, several Prime sellers, "50+ bought") are the volume alternative.
  - Observation vs estimate: observed.

## Wave 4 — flexure trim head

- **Precision Brand 1095 spring-steel shim assortment, blue tempered (AMS 5122), 0.005–0.020 in** — the leaves of the load-carrying flexure stages (`ideas/flexure-trim-head.md`), clamped in PET-GF blocks: no creep, 10–25× the out-of-plane stiffness of printed leaves.
  - Source: https://www.amazon.com/dp/B00065V062 · Observed: 2026-09-28 · Price: $53.39 · Prime: yes
  - Stock/delivery signal: "Only 2 left in stock"; "FREE delivery Thursday, October 1"
  - Volume/interchangeability evidence: 48 reviews; blue-tempered 1095 shim is a standard stock form (AMS 5122). The same search showed other Prime 1095 assortments (B0B5H47G6D $28.92, 0.004–0.03 in, delivery tomorrow; B0B511LHFB $29.98) and 304 stainless strips (uxcell B0DQ8DZFRV, 0.2 mm, $9.99).
  - Observation vs estimate: observed; the allowable-stress figure used in `flexures.py` (400 MPa) is my estimate.

- **Bambu Lab PETG Basic filament** — printed leaves in light-duty stages (levers, rider, wire anchors).
  - Source: https://us.store.bambulab.com/products/petg-basic · Observed: 2026-09-28 · Price: $9.79/roll at 10+ rolls · Prime: NA
  - Stock/delivery signal: store page, in the catalogue.
  - Volume/interchangeability evidence: Bambu's standard line; Derek's printers are Bambu.
  - Observation vs estimate: bending strength XY 75 MPa, Z 56 MPa observed on the page. Flexural modulus XY 1,670 MPa is the value the repo already cites (`hardware/printed-parts/cold-core/magnetic-float/petg-shell.md`); Tg ~80 °C per the repo. Creep and CTE are my estimates.

- **Polymaker Fiberon PET-GF15 TDS** — the stiff, heat-stable block material Derek already prints.
  - Source: https://polymaker.com/wp-content/uploads/lana-downloads/TDS_FIBERON_PET-GF15_v2.0_2026-02-02.pdf (linked from the product page) · Observed: 2026-09-28 · Price: NA · Prime: NA
  - Stock/delivery signal: NA (the project's existing material).
  - Volume/interchangeability evidence: the project's standard fixture material.
  - Observation vs estimate: the link was observed but the PDF text could not be read in the browser. The modulus (~3.5 GPa), allowable stress and CTE (~35e-6/K) used in `flexures.py` are my estimates, to be replaced by the TDS values.

- Digital indicator with RS232 output (0.01 mm), for logging A and S stage positions: see workspace-as-structure's sourcing (B09XN5FXTR, $23.99); not re-observed here.
