# Sourcing: datum

Observed 2026-09-28 (the page date) in the signed-in Chrome, one tab of my own, closed afterwards. Nothing was ordered, nothing was added to a cart, no vendor was contacted. **Amazon: Prime listings only.** Every Amazon search below used the Prime delivery filter (`rh=p_85%3A2470955011` in the URL); where I opened a product page, "Prime confirmed" means a Prime badge image in the buy box together with a "FREE delivery" line. Where I only saw the search card, the entry says so. Prices and delivery are as observed on that date and change.

The sourcing serves the ideas in `explorers/datum/ideas/`; it is representative, not a shopping list. "Sales evidence" is what the page showed (rating counts, "bought in past month", rank); a listing's existence is not evidence of volume.

## Touch and contact sensing (datum-07-touch-off, datum-03-rim-crown plunger, datum-04-corner-follower)

**Creality CR Touch auto-leveling probe (3D-printer bed probe).**
- Vendor: Amazon, listing by Creality. URL: https://www.amazon.com/dp/B0995H2X92
- Price $34.99 (list $39.00). Delivery: FREE delivery Tomorrow, Sep 29. Prime confirmed on the product page (Prime badge image in the buy box, FREE delivery line).
- Sales evidence: 1.7K ratings (1,787), 4.4 stars, "200+ bought in past month", Best Sellers Rank #128 in 3D Printer Accessories.
- Relevance: a switch-type probe with a retracting pin, sold in large volume for bed levelling. The 3DTouch/BLTouch-class parts advertise +/-0.005 mm repeatability on their own listing (one lower-priced alternative in the same results: "Upgraded 3D Touch V3.2 BL-Touch replacement", $23.74, 241 ratings, "50+ bought in past month", claims +/-0.005 mm accuracy: seller's claim, unchecked). Fit to a gun shell, pin length, contact force and behaviour on 316L: **unchecked**.

**Ruby-ball CMM stylus, M2 thread, 1 mm ball.**
- Vendor: Amazon third-party sellers. Search: https://www.amazon.com/s?k=ruby+ball+tip+stylus+M2+thread+touch+probe+CMM&rh=p_85%3A2470955011
- Prices $20.90 to $26.99 for 1 mm ball, 10 to 27 mm stems (e.g. "Cmm Touch Probe Stylus M2 Thread 1mm Diameter Ruby Ball Tip Stainless Steel Stem 20mm Long", $26.99). Delivery text FREE delivery (Prime filter); product page not opened, so Prime not separately confirmed on a product page.
- Sales evidence: **weak**: two to eight ratings per listing, none showing "bought in past month". A niche part.
- Relevance: a rigid dedicated stylus tip for the touch-off. Thread on the X1 Pro nozzle seat and stem length: **unknown** (nozzle interface not documented; manual p. 17 only names the copper nozzle and graduated tube).

## Linear motion for a fine axis (datum-02-seam-signature, datum-03-rim-crown Z stage, datum-07-touch-off)

**Mini linear stage with lead screw and NEMA 11 stepper, 100 mm travel.**
- Vendor: Amazon third-party sellers; the first card was "Befenybay 100mm Mini Linear Rail Guide Lead Screw T6x1 with NEMA11 Motor". Search: https://www.amazon.com/s?k=mini+linear+stage+stepper+lead+screw+NEMA+11+100mm+travel&rh=p_85%3A2470955011 (the card's product ASIN I did not open myself; the same title appears in another explorer's tab as B087NMQWQL, unverified by me).
- Price $54.80 (five near-identical cards $48.64 to $59.89). Delivery FREE delivery Fri, Oct 2 on the first card; Prime badge reported on the cards by the page reader, product page not opened.
- Sales evidence: 34 ratings on the first card, 25 on another; no "bought in past month" shown. Moderate.
- Relevance: a T6x1 screw (1 mm per turn) on a 200-step motor is far finer than the 0.01 mm the fine axis wants, and the travel is much more than the few tenths of a millimetre needed; stiffness under a gun and backlash are **unchecked**.

## Cameras and tags (datum-05-fiducial-collar)

**Arducam 100fps mono global-shutter USB camera, 720P OV9281, M12 low-distortion lens.**
- Vendor: Amazon, Arducam. URL: https://www.amazon.com/dp/B096M5DKY6
- Price $49.99. Delivery FREE delivery Tomorrow. Prime confirmed on the product page (Prime badge image in the buy box).
- Sales evidence: 35 ratings, 4.4 stars, "100+ bought in past month", Best Sellers Rank #110 in Webcams. A cheaper sibling ("Arducam 120fps mono global shutter USB camera module, 800P", $31.99, 14 ratings, "50+ bought in past month") and a Raspberry Pi variant ($30.00, 23 ratings) appeared in the same results.
- Relevance: a global-shutter mono sensor avoids rolling-shutter smear on a turning ring of tags. Whether its 1280 x 800 (or 1280 x 720) field and M12 lens are enough at 60 to 100 mm is **modelled only** in the scene (calc/tag_lever.py); glare on polished steel and fume are unchecked.
- Tags: printed square tags from an open detection library (AprilTag / OpenCV ArUco); nothing to buy; **unchecked** that a small camera on the shell can see them under welding light.

## Eddy-current sensing through the wall (datum-06-eddy-through-wall)

**Grove 2-channel inductive sensor module, TI LDC1612 (Seeed Studio).**
- Vendor: not Amazon Prime. My Amazon Prime search for an LDC1612 module returned unrelated current-loop converters, so there is no Prime route seen. Seen through a web search on 2026-09-28: Digi-Key lists Seeed part 101020599 at $16.40; RS Components UK lists it at GBP 14.89 ex VAT. Stock at that moment was **not checked** and no page was opened beyond the search snippets.
- Sales evidence: none observed. The chip is a stock TI part with an evaluation board (LDC1612EVM on Digi-Key) and a Seeed wiki page; that is availability, not volume.
- Relevance: an inductance-to-digital converter for a small coil is the kind of front end the toy model assumes. Its usable frequency range against a 6 mm coil on 316L behind a 1.65 mm wall, and the coil itself, are **unchecked**; a bench test decides (see the idea file).

**Commodity inductive proximity switch, LJ12A3-4-Z/BX (M12, 4 mm rated range, NPN).**
- Vendor: Amazon, Heschen. URL: https://www.amazon.com/dp/B071ZQ6VV6
- Price $6.99. Delivery FREE delivery Wed, Sep 30 (search card). Prime confirmed on the product page (Prime badge images in the buy box).
- Sales evidence: 386 ratings, 4.6 stars; other sellers' listings of the same model number appear with 8 to 39 ratings.
- Relevance: the cheapest possible probe that a plain eddy sensor responds to steel through air at a couple of millimetres. It is a switch and a ~mm-scale device, not a 6 mm-coil profile sensor; whether it sees 316L (a low-permeability, higher-resistivity steel) through a wall step, at what frequency, is **unchecked**.

## Position and load parts (datum-04-corner-follower, datum-03-rim-crown)

**Linear Hall-effect sensors, SS49E / 49E (TO-92), for a spring feeler with a magnet.**
- Vendor: Amazon third-party sellers. Search: https://www.amazon.com/s?k=SS49E+linear+hall+effect+sensor+module&rh=p_85%3A2470955011
- Price $7.99 for 20 pieces (first card). Delivery: FREE delivery (Prime filter); product page not opened.
- Sales evidence: 86 ratings, 4.5 stars, "100+ bought in past month" on the first card.
- Relevance: an analogue Hall sensor with a small magnet on a spring arm reads a few millimetres of feeler deflection; resolution to a hundredth of a millimetre depends on magnet, geometry, ADC and noise, **unchecked**.

**6 in lazy Susan ball-bearing turntable, steel, 500 lb rated.**
- Vendor: Amazon third-party sellers and Woodpeckers. Search: https://www.amazon.com/s?k=lazy+susan+turntable+bearing+6+inch+ball+bearing&rh=p_85%3A2470955011
- Price $6.95 for one (1.1K ratings, 4.6 stars, "300+ bought in past month", FREE delivery Fri, Oct 2); Woodpeckers five-pack $28.27 (3.1K ratings). A 12 in version with 1,000 lb rating is $26.09 (3.1K ratings). Prime filter with FREE delivery on the cards; product pages not opened.
- Relevance: an off-the-shelf ball turntable for the crown's rotating interface. The ball circle of a 6 in plate is smaller than the tube's 5 in OD plus the ring, and a square plate has no central opening, so it is not a drop-in; the printed 36-ball race already made for the rotator [repo] is the alternative. **Unchecked:** ball circle diameter, opening, side stiffness.

## Clear twin for ground truth (idea 10 in the notebook; no scene)

**Clear cast-acrylic round tube, 125 mm ID x 130 mm OD (5 in ID), 6 in long.**
- Vendor: Amazon third-party sellers. Search: https://www.amazon.com/s?k=clear+acrylic+tube+5+inch+OD+cast+acrylic+round+tube&rh=p_85%3A2470955011
- Price $15.99 for 6 in (76 ratings, 4.6 stars); $22.79 (49), $25.99 (140) for 10 and 12 in. FREE delivery text under the Prime filter; product page not opened.
- Relevance: the bore is 125 mm against the steel tube's 123.70 mm and the wall 2.5 mm against 1.65 mm, so a printed plate seated in it does not reproduce the real corner exactly; a twin machined or turned to 123.7 mm bore would. **Unchecked**: whether acrylic survives even the red dot's 0.3 mW (it does; it would not survive a laser pulse), and the refraction of a 2.5 mm wall for a side camera.

## Not looked up, on purpose

Ball bearings, PP or steel balls, elastic cord, printed rings, counterweights (lead or steel plate), clips, GT2 belts and gears: ordinary items the study already owns or can print. The gun scan and printed shell are established capabilities [Derek].

---

# Wave 2 additions (observed 2026-09-29, the page date)

Same method as above: Chrome, one tab of my own, closed afterwards; nothing ordered or added to a cart; every Amazon search used the Prime delivery filter (`rh=p_85%3A2470955011`); the search cards were read by script from the same-origin result pages, and one product page was opened (Prime confirmed there by the buy-box badge and a FREE delivery line). Where a card only is listed, Prime is the filter's, not separately confirmed on a product page. The sourcing serves `datum-14` (indicator log, touches), `datum-17` (the twin), `datum-18` (the flush ring), `datum-19` (camera lens).

## Digital indicators (datum-14 turn-in-the-nest test, datum-02 indicator log, datum-16 nothing)

**Neoteck 25.4 mm / 1 in digital dial indicator, 0.001 mm resolution.**
- Amazon listing by Neoteck. URL: https://www.amazon.com/dp/B0F5X2PJ53. Price $38.99. FREE delivery Today 5 PM - 10 PM or Tomorrow, Sep 30. Prime confirmed on the product page.
- Sales evidence: 1,374 ratings, 4.4 stars; no "bought in past month" line on the page. A 12.7 mm sibling (B07DFLTTQ1, $37.99) shows 1.3K ratings; a Neoteck indicator-and-magnetic-base set (B0935Y9FWB, $54.99, 887 ratings, "100+ bought in past month") is the same family as the 0.0005 in indicator the rig doc already uses `[repo tools.md]`.
- What it is not: none of the LCD indicators on the first result page states a data output (the listing bullets mention the 4 digit LCD, mm and inch switch and zero setting, and nothing about a port); the one with a data port seen there is a Mitutoyo Digimatic (543-700B-02, $551.00, Prime card, not opened). So logging the existing indicator against table angle needs either a camera on the LCD, a serial-output indicator, or a different sensor (a linear Hall sensor with a magnet on a spring probe, wave 1). **Unchecked:** any indicator's data interface.

## Clear twin (datum-17, datum-10)

**Clear acrylic round tube, 125 mm ID x 130 mm OD (5 in ID, 5 1/8 in OD), 6 in and 14 in.**
- Amazon third-party sellers. 6 in: https://www.amazon.com/dp/B0CYHCLTN1, $15.99, 76 ratings, 4.6 stars; MECCANIXITY 14 in: https://www.amazon.com/dp/B0B9BYJ395, $31.89, 67 ratings, 4.4 stars. Prime filter on the cards; product pages not opened.
- No listing in the first results has the steel tube's bore (123.70 mm) or wall (1.65 mm); the nearest are 125 mm ID. So the twin's plate is printed at Ø125 or the tube is bored; the geometry of a corner seen from outside is the same either way.

## Flat ring around the table hole (datum-18)

**6061 aluminium sheet, 1/4 in, 12 x 12 in (and 6 x 12, 8 x 12).**
- Amazon third-party sellers. Cards: B0BF214Q57 ($32.99, 639 ratings, 4.6 stars, "50+ bought in past month"); the 6 x 12 in and 8 x 12 in sizes of the same listing show "100+ bought in past month" ($20.99, $23.99). FREE delivery text under the Prime filter; product pages not opened.
- Relevance: a flat aluminium plate set flush round the hole as the surface the probe touches (a machined ring would be flatter). Flatness of this sheet stock is **unchecked** and is the number that decides the flush mode.

## Camera lens (datum-19)

**Arducam M12 low-distortion lens kit, and generic M12 CCTV lenses.**
- Arducam M12 lens kit (B07NW8VR71): $59.99, 16 ratings, 3.6 stars; Arducam M12 lens set for USB cameras (B096V2NP2T): $99.99, 5 ratings; a fixed 6 mm 5 MP M12 CCTV lens (B0DPJX9N28): $7.99, 2 ratings. Prime filter on the cards; pages not opened.
- Sales evidence is thin for every lens seen (2 to 21 ratings; none shows "bought in past month"). Distortion figures are not stated on the cards. The plate-as-target fit assumes a calibrated lens: a chessboard calibration of any of these would be needed and is **unchecked**.

---

# Wave 3 additions (observed 2026-09-29, the page date)

Same method: Chrome, one tab of my own (the first tab I opened was closed by another session's clean-up, so I opened a second and closed it at the end); every Amazon search used the Prime delivery filter (`rh=p_85%3A2470955011`); result cards were read by script from same-origin fetches of the search pages, and four product pages were fetched the same way and read for a Prime badge and a free-delivery line (marked "product page"). Where only a card was read, Prime is the filter's. Nothing was ordered or added to a cart. The sourcing serves `datum-22` (feet, port pins), `datum-23` (roller, wheel, preload, contact) and the bench measurements the new ideas ask for. It is representative, not a shopping list; a listing's existence is not evidence of volume.

## Feet, pins and hardware for the setting ring (datum-22)

**304 stainless set screws, metric assortment (M3 to M8).** Hapric 485 pcs, 14 sizes (B0CZRDS1CB): $9.99, 4.8 stars, 106 ratings, "100+ bought in past month"; product page: Prime badge, FREE delivery Tomorrow, Sep 30. Also on the cards: a 1220-piece M3 to M6 hex socket kit (B0FG2964F5, $22.99, 2.3K ratings, "1K+ bought in past month"). Relevance: the depth-stop feet are M3 or M4 set screws set with a depth gauge (foot length tolerance +-0.02 is the scene's figure; the screws' own length and tip finish are **unchecked**, and set screws are cut for a cup point, so a ball or a ground tip may need a lapped screw).

**Quick-release ball-lock pins, 5/16 in (8 mm), 2.17 in long.** 2 pcs (B07N1JYDJG): $6.99, 4.6 stars, 191 ratings, "100+ bought in past month"; product page: Prime badge, FREE delivery Tomorrow. Relevance: the nearest ordinary part to the plug's pins. A ball-lock pin is a spring ball holding a pin in a hole, not the quarter-turn T-head drawn in the scene, and 8 mm passes the port pilot (11.13 mm) with room to spare. A wing-toggle or T-head pin was not found in the first results; a printed or turned T-head is drawn instead. **Unchecked:** whether a pin of this class centres a cone collar in the 82 degree countersink to the 0.05 mm the scene asks; a turned collar would.

## Roller, wheel and preload for the wall clip (datum-23)

**MR105ZZ miniature ball bearings, 5 x 10 x 4 mm.** uxcell 10 pcs (B0DP7FYPDV): $7.55, 5.0 stars, 9 ratings; MR105ZZ ABEC-5 (B0FMK2MR3C): $6.99, 6 ratings; uxcell 20 pcs (B075CMP2HF): $14.69, 4.6 stars, 28 ratings. Cards only. Sales evidence: **weak** (no "bought in past month"). Relevance: the roller is a bearing outer race, 10 mm OD (the scene draws 5 mm; the calc used 2.5 mm radius, and a 10 mm roller would not fit the 6 to 10 mm gap beside the wire). A 5 mm roller would be a smaller bearing (MR85ZZ class, not searched). **Unchecked:** the outer race on a 1.65 mm 316L bore under 8 N.

**Ball transfer units, mini.** "Mini Ball Transfer Bearing Unit" 12 pcs (B0C6GTSW65): $8.49, 4.1 stars, 10 ratings; 1/3 in nylon-ball table conveyor unit (B07VGGVXMH): $9.99, 4.5 stars, 56 ratings; 5/8 in carbon-steel units, 30 pcs (B0CLNKC87G): $25.99, 76 ratings. Cards only. Relevance: the rim wheel (a 6 mm ball carrying 0 to 15 N, 0.01 of it as drag along the seam). Sales evidence weak; ball material and finish on a 316L rim **unchecked**.

**Ball-nose spring plungers, M6, stainless.** 4 pcs (B0DCSHBQY4): $16.89, 4.8 stars, 9 ratings; 2 pcs (B0DBM4GKJ4): $12.79, 3.4 stars, 6 ratings. Cards only. Relevance: the pad arm's preload (8 N in the scene). Plungers of this class are light springs (the travel sourcing recorded a 12 N end-force class); the spring rate and end force are **unstated** on the cards, and the preload wants a spring that stays within 2 to 20 N over the wall's thickness spread.

## Switches for the seat check (datum-22, datum-23)

**Micro limit switches, SPDT.** HiLetgo 10 pcs KW12-3 (B07X142VGC): $5.99, 4.7 stars, 724 ratings, "1K+ bought in past month"; product page: Prime badge, FREE delivery Tomorrow. Also 9 to 30 piece roller-lever packs ($5.99 to $7.99, 11 to 19 ratings). Relevance: the flange switch and the three foot switches (proposed) are switch-class parts in real volume; the actuation force and repeatability (a switch closes to a few hundredths of a millimetre, not to 0.005) are **unstated**, and a foot switch on a plug arm is a switch, not the foot itself.

**A3144 hall-effect sensors (OH3144, AH3144E), 20 pcs.** (B0CZ6QXMZ2): $6.99, 4.5 stars, 81 ratings, "200+ bought in past month"; product page: Prime badge, FREE delivery Tomorrow. Also a 10 pc pack (B0CFLNZK9M, $8.59, "100+ bought"). Relevance: a magnet-and-hall pair per foot is the alternative to a switch, and the pad-arm sensor of `datum-23`; it is a digital latch, so it gives contact and no analogue reading. **Unchecked:** sensing distance against the magnet on a 316L plate 10 mm from a tack.

## For Derek's bench measurements (datum-21, datum-22)

**iGaging Absolute Origin 0 to 6 in digital caliper, IP54, stainless.** (B00KDUD67G): $53.59, 4.7 stars, 662 ratings, "300+ bought in past month"; card only. Relevance: the caliper Derek already owns is the tool for outside diameter at eight positions and for depth from the rim; this is the class. Its data output and resolution are not stated on the card; not needed for the survey.

## Not looked up, on purpose

Feeler gauges, a surface plate, ball micrometers for wall thickness (Derek's own tools or a measurement, not a part), printed rings, ball bearings for the crown race, PTFE-faced skids and elastic cord: ordinary items or already recorded above. A steel or ceramic roller of 5 mm OD and a turned T-head with a cone collar are custom parts; nothing on a Prime listing was found for them.
