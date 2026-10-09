# Sourcing: use (the day of use)

Observed 2026-09-28 (the pages showed "Deliver to Lincoln 68520"; delivery dates below are the ones shown that day). Nothing was ordered, added to a cart, or sent to a vendor. One browser tab, mine, was opened and closed.

**How Prime was confirmed, for every Amazon entry.** Searches were run with Amazon's Prime filter (`rh=p_85:2470955011`) and only result cards carrying Amazon's Prime badge (the `a-icon-prime` element) were read. Each entry below was then opened on its product page, where the Prime badge sits beside the price and in the buy box (page check `#priceBadging_feature_div` / `#buybox` contains `a-icon-prime`), and the delivery line is quoted. Where the page says "FREE delivery for Prime members" that wording is quoted. No non-Prime listing is recorded.

**Sales evidence** is what the page shows and nothing else: rating count, "bought in past month" where present. A listing's existence is not evidence of volume. The ecosystems these parts come from (3D-printer motion parts, camera accessories, furniture hardware) are large, but that is a statement about the class, not something these pages prove.

Which idea each entry serves is named in the last field. Prices are the price on the page that day.

## Motion for the swing head (use-02-swing-head)

### NEMA 17 stepper with integrated T8 lead screw, 200 mm
- YEJMKJ Nema 17 Stepper Motor TR8x8 200mm with T8 Lead Screw, 42x48 mm, 0.55 Nm, 1.7 A. Amazon, `https://www.amazon.com/dp/B0FHHW532B`.
- **$25.59**, "FREE delivery for Prime members", Sunday October 4; the search card said "Only 1 left in stock".
- Sales evidence: none (rating 5.0 with 0 reviews). This class, a printer Z-axis motor with a lead screw, is routinely sold in 200 to 400 mm lengths at similar prices; another card in the same search (300 mm integrated screw, $24.99) showed 26 ratings.
- Prime: badge and quoted delivery line as above.
- Serves: the plunge (a short stroke along the barrel axis) if it is a stepper; the rotator's DM542T/ESP32 stack [repo] or a small driver could run it. A 46 mm stroke is a fraction of a 200 mm screw.

### 12 V linear actuator with built-in limit switch and self-locking, 50 mm stroke
- Justech 330 LBS / 1500 N, 2 inch / 50 mm, 12 V, with bracket, "Built-in Limit Switch, Self-Locking". Amazon, `https://www.amazon.com/dp/B0F5Q1HXSX`.
- **$29.99**, "FREE delivery for Prime members", Saturday October 3.
- Sales evidence: 4.4 stars, 230 reviews, "#1 Top Rated" tag in a search list, "100+ viewed in past month" (views, not sales).
- Prime: badge and quoted delivery line as above.
- Serves: a plunge or swing that only needs two end positions, since the seat sets the position. **The force is the problem:** 1500 N is far above what a retract should be allowed to push (a fused 0.76 mm wire holds about 270 N [derived from a spec-sheet tensile figure], the rotator is backdrivable). It would need a series force limit or a smaller actuator. Smaller 30 to 100 N mini actuators with limit switches appeared in the same search (listed at $20 to $32); their Prime status was not confirmed, so they are not recorded as sources.

### Planetary-geared NEMA 17, 27:1
- STEPPERONLINE 27:1 Planetary Gearbox High Torque Nema 17 Stepper Motor. Amazon, `https://www.amazon.com/dp/B00QEUZ9EM`.
- **$41.91**, "FREE delivery Wednesday, September 30. Order within 9 mins".
- Sales evidence: 4.5 stars, 36 ratings; none for volume. Same vendor as the rotator's motor and driver [repo `hardware/assembly/weld-rotation-rig.md`], which keeps parts and drivers familiar. Other ratios (5:1, 20:1, 51:1) listed in the same search at $24 to $45.
- Prime: badge and delivery line as above.
- Serves: the swing drive (belt or gear to the arm hub). The seat, not the drive, sets position, so gearbox backlash is not a positioning error.

### Lazy Susan bearing, 6 inch, 500 lb
- 6" Lazy Susan Turntable 500 LBS Steel Ball Bearing, low profile. Amazon, `https://www.amazon.com/dp/B08N52SVXF`.
- **$6.95**, "FREE delivery Friday, October 2".
- Sales evidence: 4.6 stars, 1,112 ratings, "300+ bought in past month".
- Prime: badge beside the price; delivery line quoted.
- Serves: the swing bearing. Its slop is irrelevant if a kinematic seat locates the gun; its stiffness against the cantilever moment of the arm (unknown gun mass) is not checked.

### Precision balls, 6 mm G25
- Breezliy 200 pieces 6 mm precision steel bearing balls G25 (304 stainless). Amazon, `https://www.amazon.com/dp/B09JLRTQFF`.
- **$7.99**, "FREE delivery Wednesday, September 30. Order within 8 mins".
- Sales evidence: 4.7 stars, 1,865 ratings, "100+ bought in past month".
- Prime: badge beside the price.
- Serves: the three seat balls. 304 stainless is softer than chrome steel; a chrome-steel G25 100-pack ($6.65, 101 ratings) was in the same search but was not opened on its product page, so it is not recorded as a source. Hardened inserts in printed pockets are the obvious form.

### 2020 T-slot extrusion, 1000 mm
- 4pcs 1000mm T Slot 2020 Aluminum Extrusion, Black. Amazon, `https://www.amazon.com/dp/B0CLGYBHHN`.
- **$39.99**, "FREE delivery Wednesday, September 30".
- Sales evidence: 4.6 stars, 190 ratings.
- Prime: badge beside the price.
- Serves: the post and mast; this is the standard printer-frame stock. A tall cantilever from 2020 section will flex; stiffness is not analysed.

## Presetting and instrumented manual axes (use-03-preset-cartridge, coach idea)

### Digital dial indicator, 0.001 mm
- Neoteck 12.7 mm / 0.5" Digital Dial Indicator, 0.001 mm / 0.00005" resolution, 4-digit LCD. Amazon, `https://www.amazon.com/dp/B07DFLTTQ1`.
- **$37.99**, "FREE delivery Wednesday, September 30. Order within 10 mins".
- Sales evidence: 4.4 stars, 1,373 ratings.
- Prime: badge beside the price and in the buy box.
- **No data port is listed.** Reading it from software means either the caliper-style clock/data pads under the case (widely documented for calipers: 24-bit packets; the vendor's own protocol for this indicator is unchecked), or a camera on the LCD. The rig already owns a Neoteck indicator with a magnetic base [repo `hardware/ledger/tools.md`].

### Neoteck 1" / 0.01 mm indicator (same brand)
- Neoteck 1"/25.4mm Digital Dial Indicator 0.0005"/0.01mm. Amazon, `https://www.amazon.com/dp/B01JYCVHLK`.
- **$23.99**, "FREE delivery Wednesday, September 30. Order within 8 mins".
- Sales evidence: 4.4 stars, 1,373 ratings, "200+ bought in past month".
- Prime: badge beside the price.

### Data cable for a Digimatic-port indicator
- Mitutoyo 905338 Digimatic Cable, 40 in, straight. Amazon, `https://www.amazon.com/dp/B002SG7PPW`.
- **$58.67**, "FREE delivery Friday, October 2. Order within 8 mins".
- Sales evidence: 4.7 stars, 23 ratings.
- Prime: badge beside the price.
- Serves: the route with a real data output. Mitutoyo Digimatic indicators with the SPC port were listed at about $551 on search cards (not opened, price not confirmed on a product page). The SPC protocol reports whatever is on the display and has open Arduino and ESP32 readers (see "Other vendors and documents").

### Linear scale with 5 micron resolution (DRO)
- TOAUTO Digital Readout 2 Axis 3 Axis DRO Display Linear Scale 150mm 6" 5um. Amazon, `https://www.amazon.com/dp/B09DGFTGTY`.
- **$72.99**, "FREE delivery Wednesday, September 30".
- Sales evidence: 4.0 stars, 9 ratings.
- Prime: badge beside the price.
- Serves: an instrumented manual axis (a scale on a hand-driven slide). Whether the scale can be read directly (TTL quadrature is typical for such scales) without the supplied display is unchecked.

### Magnetic rotary encoder, 12 bit
- UMLIFE 3pcs AS5600 Magnetic Encoder module, 12 bit, I2C/PWM. Amazon, `https://www.amazon.com/dp/B094F8H591`.
- **$7.99** for three, "FREE delivery Wednesday, September 30. Order within 9 mins".
- Sales evidence: 4.4 stars, 70 ratings, "100+ bought in past month".
- Prime: badge beside the price.
- Serves: a digital scale on a hand knob (with an M3 x 0.5 screw, 12 bits is 0.12 micrometres of travel per count in principle; accuracy is far worse and unchecked).

### Manual XYZ micrometer stage, 60 mm
- XYZ 3 Axis Manual Linear Stage 60x60mm Trimming Bearing Tuning Platform. Amazon, `https://www.amazon.com/dp/B07D7NM2WF`.
- **$130.00**, "FREE delivery Wednesday, September 30".
- Sales evidence: 3.8 stars, 19 ratings. Others in the search: 40 mm stages at $95 to $134, and one at $469.99.
- Prime: badge beside the price.
- Serves: a hand-set fine axis for the coach idea. Whether such a stage can carry a gun (mass unknown) is not established.

### Friction / magic arm
- SMALLRIG 9.8 Inches Magic Arm Clamp Kit with 1/4" and 3/8" threaded holes. Amazon, `https://www.amazon.com/dp/B087T4T8D5`.
- **$19.99**, "FREE delivery Wednesday, September 30. Order within 9 mins".
- Sales evidence: 4.6 stars, 2,975 ratings, "3K+ bought in past month".
- Prime: badge beside the price.
- Serves: the locking arm in the coach idea. **Payload is a camera-class figure, not a gun**; the X1 Pro gun mass is [unknown]. An 11-inch arm and a clamp on a T-slot post are the same class at $26 to $36 (NEEWER, SMALLRIG; 400+ bought in past month on some).

## Cameras and logging (recorder and dry-run observation)

### UVC camera module, 1080p
- Arducam 30fps@1080P HDR USB Camera Module, 78 degree, autofocus, UVC. Amazon, `https://www.amazon.com/dp/B0FX47YSJQ`.
- **$19.99**, "FREE delivery Wednesday, September 30. Order within 9 mins".
- Sales evidence: 4.0 stars, 22 ratings, "100+ bought in past month".
- Prime: badge beside the price.
- Serves: the recorder and the dot camera in several scenes. Whether the red dot survives the weld's brightness (a narrow-band filter, exposure) is not tested.

## Other vendors and documents

Found through web search on 2026-09-28; only the search summaries were read, the pages themselves were not fetched, so treat the specifics as unchecked.

- Mitutoyo Digimatic (SPC) data port: no interactive control, it reports the display; open Arduino and ESP32 readers exist, the ESP32 reading the 1.5 V signal on its ADC. `https://github.com/tlbruns/Digimatic`, `https://github.com/Roger-random/mitutoyo`, `https://github.com/MGX3D/EspDRO`.
- Cheap calipers and LCD scales: a 24-bit clock/data packet, about 1.2 V logic, widely read with an ESP32. `https://github.com/sorinbotirla/esp32-digital-caliper`, `https://hackaday.com/2019/07/04/hacked-calipers-make-automated-measurements-a-breeze/`.
- Kinematic coupling repeatability: a well-made three-groove coupling with hardened balls repeats to well under 2 micrometres per the search summaries; sphericity error transfers directly. `http://pergatory.mit.edu/kinematiccouplings/documents/theses/hart_thesis/chapter2.pdf`.
- ER316L 0.030 in wire: about 86 to 88 ksi (593 to 607 MPa) is the deposited weld metal figure on spec sheets (`https://www.weldwire.net/wp-content/uploads/2013/08/ER316L.pdf`); the spool wire's own tensile strength was not checked. Used only to estimate that a fused wire holds hundreds of newtons (0.456 mm^2 x ~590 MPa = about 270 N).

## Things looked for and not found or not recorded

- Any Prime-listed digital dial indicator under $100 that lists a data output: none found; the sub-$100 indicators list an LCD only.
- The X1 Pro's RS232 and DB25 protocols: not documented in the manual [manual p.16]; nothing was searched from a vendor, and no vendor was contacted.

## Wave 2 additions: an index pulse and an absolute angle (use-16, use-17, notes on travel-02 and travel-06)

Observed 2026-09-29 (delivery lines are those shown that day). Nothing was ordered, added to a cart, or sent to a vendor. One browser tab, mine, was opened and closed. Prime was confirmed as above (Prime filter in the search, badge on the card, badge and delivery line re-checked on the product page for the two entries recorded). Other cards in the same searches carried the Prime badge and are not recorded as sources because they were not opened.

### Hall-effect sensor module (A3144 / 3144E), 5 pack
- HiLetgo 5pcs Hall Effect Magnetic Sensor Module 3144E A3144, DC 5V. Amazon, `https://www.amazon.com/dp/B01NBE2XIR`.
- **$5.99**, "FREE delivery Thursday, October 1".
- Sales evidence: 4.5 stars, 135 ratings, "100+ bought in past month". The search also listed a 20-piece bare-sensor pack at $6.99 (81 ratings, "200+ bought in past month", not opened).
- Prime: badge beside the price and quoted delivery line on the product page.
- Serves: a once-per-revolution index pulse on the rotator's turntable (a magnet in the turntable, the sensor on the base). The written sequence already returns the table to an index mark by eye; a pulse gives a software-run dry lap and weld lap the same zero. The replay tolerance is about 10 degrees for a 22 micron error on a 0.125 mm sinusoid (`explorers/use/calc/w2_angle_key.mjs`), so a hall pulse is far more than enough. Used in the notes on travel-02.

### AS5600 magnetic angle encoder module (already recorded above, re-checked)
- The UMLIFE 3-pack recorded under the presetting entries (`https://www.amazon.com/dp/B094F8H591`) was re-opened on 2026-09-29: **$7.99**, "FREE delivery Tomorrow, September 30", 4.4 stars, 70 ratings, "100+ bought in past month", Prime badge beside the price. A 4-pack at $9.99 (41 ratings, "100+ bought in past month") was also listed on a Prime-filtered card and not opened.
- Serves (new in wave 2): an absolute angle on a hand-turned presetter turntable (use-17) or on a printed arc or yoke pivot (use-16): 12 bits is 0.088 degrees per count, coarse for a stop but adequate to say which screw is at the driver. Not a probe and not a stop.

### Still not found (unchanged from wave 1)
- A Prime-listed indicator or probe with a documented data output that can serve as travel-06's probe; the caliper-style clock-and-data-pad route is documented by open-source readers and remains unchecked here.
