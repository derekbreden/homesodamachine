# Sourcing: trials

Observed 2026-09-28 (Lincoln, NE delivery address on the Amazon pages). Amazon: only Prime listings, found with the Prime filter on the search page; each entry says how Prime was confirmed on the product page (Prime badge in the buy box, or "FREE delivery" line with the badge). Sales evidence is what the listing itself shows: review count, "bought in past month", Best Sellers Rank. A representative listing is not a recommendation; nothing was ordered or contacted. Prices and delivery dates move daily.

Every part below serves a specific trials idea; ids in brackets.

## Load cells and amplifier: the dock as a scale [trials-02-dock-reset]

- **2-set 5 kg load cell + HX711 ADC module kit** (bar cell, 24-bit amplifier, sold for DIY kitchen scales). Amazon, ASIN B09K7G3477, https://www.amazon.com/dp/B09K7G3477. $9.99 for 2 sets. Prime confirmed: Prime badge in the buy box; ships from Amazon; "FREE delivery Tomorrow, September 29". Sales: 100+ bought in past month, 4.0 stars (24 ratings), rank #32,499 in Industrial & Scientific, first available Oct 25, 2021. Three cells per dock means two of these kits' cells; the dock idea assumes a resolution of a few grams and that a bar cell stays repeatable under a kinematic seat: both unchecked.
- **SparkFun HX711 load cell amplifier breakout.** Amazon, ASIN B079LVMC6X, https://www.amazon.com/dp/B079LVMC6X. $11.50. Prime badge in the buy box; ships from Amazon. Sales: 100+ bought in past month, 4.6 stars (75 ratings), #5 in Industrial Scale & Balance Parts. A better-documented amplifier for the same cells.
- Unchecked: the noise floor and long-term drift of these cells on a printed dock; the scene uses 5 to 10 g as a placeholder.

## Kinematic seats and puck hardware [trials-01-puck-swap, trials-02-dock-reset]

- **6 mm chrome steel bearing balls, G25 (100 pcs).** Amazon, ASIN B07DKSN46T, https://www.amazon.com/dp/B07DKSN46T. $11.45. Prime badge in the buy box. Sales: 4.6 stars (387 ratings), rank #648 in Deep-Groove Ball Bearings. The three balls under each puck. (G25 is a sphericity grade of about 0.6 micrometres; the listing says so, not checked.)
- **3 mm x 30 mm stainless dowel pins, 50 pcs.** Amazon, ASIN B0DWSNNRV8, https://www.amazon.com/dp/B0DWSNNRV8. $6.99. Prime listing (appeared under the Prime filter; product page not opened). Sales: 200+ bought in past month, 4.6 stars (116 ratings). Two per seat make the V. Stainless is softer than a hardened dowel; wear is untested.
- **10 x 3 mm round magnets, 100 pcs.** Amazon, ASIN B0FDQJ3WR6, https://www.amazon.com/dp/B0FDQJ3WR6. $10.79. Prime badge in the buy box. Sales: 2K+ bought in past month, 4.3 stars (337 ratings), #10 in Rare Earth Magnets. Preload magnets and the puck's index magnet. Pull force per magnet is not stated on the listing (unchecked); the calc uses an illustrative 30 N total.
- **A3144 Hall effect sensor, 20 pcs.** Amazon, ASIN B0CZ6QXMZ2, https://www.amazon.com/dp/B0CZ6QXMZ2. $6.99. Prime listing (search filter; page not opened). Sales: 200+ bought in past month, 4.5 stars (81 ratings). The index-pulse sensor on the rotator base.
- **NTAG213 NFC stickers, 25 mm.** Amazon, ASIN B0C5MPDYT8, https://www.amazon.com/dp/B0C5MPDYT8. $12.99. Prime badge in the buy box; "FREE delivery Wednesday, September 30". Sales: 100+ bought in past month, 4.5 stars (208 ratings). 144 bytes: room for an ID and a pointer, not the map itself (the map lives in software, keyed by the ID).
- **HiLetgo PN532 NFC RFID module V3 kit.** Amazon, ASIN B01I1J17LC, https://www.amazon.com/dp/B01I1J17LC. $8.99. Prime badge in the buy box. Sales: 200+ bought in past month, 4.3 stars (214 ratings), #81 in Single Board Computers. The tag reader at the stand.
- Unchecked: reading a tag near a spinning steel tube; mounting the reader at the stand avoids it.

## Industrial zero-point clamping as a borrowed toolchanger [trials-07-toolchange-swap, trials-01-puck-swap]

- **XinDian Quick Zero Point plate D52-D** (20CrMnTi steel, 120 x 120 x 27 mm, four pull studs, 52 x 52 mm pattern). Amazon, ASIN B0CL27T69R, https://www.amazon.com/dp/B0CL27T69R. $295.00. Prime badge in the buy box; ships from Amazon; "FREE delivery Thursday, October 1". Listing claims: 0.005 mm repeatability, 20 kN clamping force, 35 N&middot;m locking torque, "10,000+ cycles" (seller claims, unchecked). Weight 7.15 lb. Sales evidence: **thin**: 3 ratings (5.0), rank #139,905 in Industrial & Scientific. It shows the product class exists at retail with next-day availability; one listing with three reviews is not evidence of volume. Whether a 52 mm module carries a 1.5 kg gun on a 250 mm lever with an umbilical pulling is a moment-capacity question the listing does not answer; the manual version needs a hand or a wrench to release, a pneumatic one needs air.
- **Open-source printer toolchangers, as a lighter class.** StealthChanger (DraftShift): https://github.com/DraftShift/StealthChanger. Observed 2026-09-28: 1.2k stars, 129 forks; kits are sold commercially (LDO Motion). Bushings, pins and N52 6 x 3 mm magnets; the README describes a very light design for printer toolheads. Toolheads are a few hundred grams (assumption, not found on the page). Useful as the ecosystem for a docking gantry; not sized for a gun.
- Not sourced: hobby servo latches, pneumatic robot tool changers (quote-only class).

## Cameras for the judge [trials-03-dot-touch-probe, trials-04-seam-map-replay, trials-05-artefact-ladder]

- **OBSBOT Tiny 2 Lite 4K PTZ webcam.** Amazon, ASIN B0CZ6XY78Y, https://www.amazon.com/dp/B0CZ6XY78Y. $119.00. Prime badge in the buy box; "FREE delivery Tomorrow, September 29". Sales: 1K+ bought in past month, 4.3 stars (2,015 ratings), rank #22 in Webcams. A software-pointable camera in Derek's "couple PTZ cameras" sense; whether its control is open enough for a script is unchecked.
- **Arducam 100 fps mono global-shutter USB camera (OV9281, UVC, M12 lens).** Amazon, ASIN B096M5DKY6, https://www.amazon.com/dp/B096M5DKY6. $49.99. Prime badge in the buy box. Sales: 100+ bought in past month, 4.4 stars (35 ratings), rank #110 in Webcams. A fixed, sharp, no-rolling-shutter camera for the dot and its blink; monochrome helps with a red dot plus a red bandpass filter (not sourced).
- Unchecked: how a 0.3 mW red dot looks in either camera on polished 316L under bench light.

## Red dot for the mule [trials-06-mule-gun]

- **HiLetgo 10 pcs 5 V 650 nm 5 mW red dot laser head, 6 mm.** Amazon, ASIN B071FT9HSV, https://www.amazon.com/dp/B071FT9HSV. $6.79. Prime badge in the buy box; ships from Amazon. Sales: 200+ bought in past month, 4.3 stars (760 ratings), #2 in Diode Lasers. Focus-adjustable small modules; on/off by a GPIO. 5 mW is class 3R (more than the real dot's 0.3 mW **[manual p.12]**): the mule needs a dimmer module or a resistor; eye safety is Derek's call.
- **Red dot laser module with TTL modulation, 650 nm, class IIIa.** Amazon, ASIN B0DQXYQTWS, https://www.amazon.com/dp/B0DQXYQTWS. $58.59. Prime badge in the buy box. Sales: **thin**: 1 rating, rank #98,401. Shown only to establish that a modulated (blinkable) module exists.
- **BNO085 9-axis IMU breakout (GY-BNO085 class).** Amazon, ASIN B0CDGZMLPP, https://www.amazon.com/dp/B0CDGZMLPP. $20.49. Prime badge in the buy box; "FREE delivery Tomorrow, September 29". Sales: 100+ bought in past month, 4.7 stars (24 ratings), #3 in Acceleration Sensors, first available Aug 2, 2023. On-chip fusion gives pitch and roll from gravity; yaw from the magnetometer is doubtful near a motor and a steel bench (the scene treats yaw as blind).

## Hand-driven axes with readout [trials-12-encoded-manual-axes]

- **Digital linear scale 0-150 mm (DRO scale).** Amazon, ASIN B089ZSG84J, https://www.amazon.com/dp/B089ZSG84J. $26.99. Prime badge in the buy box. Sales: 50+ bought in past month, 4.3 stars (207 ratings), #43 in Digital Calipers. Caliper-style scale; a serial output for logging is unchecked.
- **SEMY60-class 60 x 60 mm micrometer XY stage.** Amazon, ASIN B07QW8MCVY, https://www.amazon.com/dp/B07QW8MCVY. $116.58. Prime listing (search filter; page not opened). Sales: **thin**: 2 ratings. Shows hand-micrometer stages exist at retail; far too small to carry the rotator (a few kilograms), so this is for a gun-side follower or fine adjustment only.
- Unsourced: a tube-side X stage that carries the rotator (trials-04 branch). Left open.

## What the printing route already covers

- Printed zoo tubes, the corner coupon, pucks and the dock are printed on the existing Bambu printers **[Derek]**; the notch tube is a band-saw job on scrap tube **[repo]**. Nothing to source beyond fasteners.

## Not sourced (kept unresolved)

- The X1 Pro's RS232 protocol and DB25 pin map (the manual pages available here give the RS232 pins and no protocol) **[manual p.16]**.
- A ChArUco board printed at true scale: printing plus a flat glass or aluminium plate; not looked up.

---

## Wave 2 additions (observed 2026-09-29, Lincoln, NE delivery address)

Amazon, Prime only: each search below used the Prime refinement on the search page (results listed under "All Prime"); product pages were not opened, so Prime is confirmed by the filter and the "FREE delivery" line on the result card, not by a buy-box badge. Nothing was ordered. Sales evidence is what the result card shows. Each entry names the idea it serves.

### Pan/tilt and micro servos for a steerable pointer [trials-18-steerable-mule]

- **Mini Pan-Tilt Kit Camera Platform, assembled with micro servos** (FPV mount). $13.99. 4.1 stars (33 ratings), "100+ bought in past month", FREE delivery Fri Oct 2. A second card, **Mini Pan/Tilt Camera Platform Anti-Vibration Mount with 2 servos**, $13.99, 3.2 stars (210 ratings), FREE delivery Tomorrow Sep 30. Both are the class of thing borrowed-10 names; either is a bracket plus two 9 g servos. Resolution and lash unchecked.
- **2 Sets Pan Tilt Servo Mount Bracket for MG996R / S3003**. $13.99. 4.5 stars (343 ratings), "100+ bought in past month", FREE delivery Today 5 PM to 10 PM. Larger servos, brackets only.
- **MG90S 9 g metal-gear micro servo, pack of 4** ("2.0 kg.cm torque" in the title). $13.88. 4.5 stars (794 ratings), "900+ bought in past month", Best Seller badge on the card, FREE delivery Tomorrow Sep 30. **SG90 4-pack**: $7.98, 4.4 stars (1.7K ratings), "400+ bought in past month". Servo deadband and lash on these parts are not stated on any card (unchecked); the scene uses 0.2 degrees of lash as a slider.
- **ELEGOO 5 sets 28BYJ-48 geared stepper with ULN2003 board**. $14.99. 831 ratings, "400+ bought in past month", FREE delivery Today 5 PM to 10 PM. Its usual figure of 4096 half-steps per turn (0.088 degrees) is from general knowledge, unchecked, as is the backlash of its gear train; a stepper is the way to a step finer than a hobby servo's. Second card: HiLetgo 5 pcs, $14.59, 193 ratings, "50+ bought in past month".

### Dimmer red laser modules and a nose steering element [trials-18-steerable-mule, trials-06-mule-gun]

- **Economical red dot laser module, 650 nm, Class 2, under 1 mW, with APC driver, 2.6 to 6 V.** $15.99. 3.9 stars (79 ratings), FREE delivery Tomorrow Sep 30. This is the nearest listing to the real dot's 0.3 mW **[manual p.12]**; the 5 mW listings already in this file are brighter. Whether the listed power is what the module emits is unchecked. Eye safety of an unattended pointer stays Derek's call.
- **650 nm red dot diode module, adjustable focus, 5 mW, 3 to 5 V** (Amazon's Choice card): $11.89, 4.2 stars (39 ratings), delivery Today 5 PM to 10 PM. **UMLIFE 5 pcs 650 nm 5 mW laser head**: $14.99, 4.5 stars (30 ratings), "50+ bought in past month".
- **Laser Galvo 20Kpps galvanometer scanning set with show card** (stage laser-light class): $109.99. 3.9 stars (25 ratings), FREE delivery Fri Oct 2, "Only 13 left in stock". The nose mirror of trials-18 could be a galvo mirror. **Sales evidence: thin** (25 ratings, no bought-in-past-month text); it shows the class exists at retail. Mirror size, pointing accuracy and whether a bare galvo mounts inside a 5 mm nose are all unchecked.
- A small first-surface mirror was searched and not recorded: the results page was too large for the reading tool. Unchecked.

### Higher-resolution magnetic encoders for the arm calibration [trials-19-fixed-point-cal]

- **AS5047P encoder module, 14 bit, SPI/ABZ/PWM**: $11.99, 5.0 stars (5 ratings). **AS5048A 14 bit PWM/SPI** modules: $13.88 (3.3 stars, 6 ratings), $14.99 (3.4 stars, 4 ratings), $14.24 (5.0 stars, 2 ratings). **Sales evidence: thin** (single-digit ratings; no bought-in-past-month text); they show a 14-bit magnetic module exists with Prime delivery. For comparison the 12-bit route in borrowed's sourcing, **WWZMDiB 4 pcs AS5600**: $9.99, 4.4 stars (41 ratings), "100+ bought in past month". The calc (calc/arm_touch_cal.py) says the 12-bit code alone leaves 0.28 mm at this arm's lever arms and 14 bit about 0.10 mm; a listed part's real linearity is unchecked.

---

## Wave 3 additions (observed 2026-09-29, Lincoln, NE delivery address)

Amazon, Prime only: each search used the Prime refinement on the search page (results under "All Prime"); product pages were not opened, so Prime is confirmed by the filter and the "FREE delivery" line on the result card. Nothing was ordered. Sales evidence is what the card shows. Each entry names the idea it serves.

### A camera with a trigger input, so the axis or the rotator can trigger the exposure [trials-23-frame-clock]

- **USB2.0 UVC camera module, global shutter mono OV9281, 720p 120 fps, "with UVC driver, external trigger, strobe"** (title text). $35.99. 4.0 stars (48 ratings), FREE delivery Tomorrow Sep 30. The title claims an external trigger and a strobe output; whether the trigger pad is accessible, its timing against the exposure, and whether the UVC stream carries a frame counter are all unchecked. It is the same sensor as the listed 100 fps Arducam UVC camera in the wave 1 entry, which does not state a trigger.
- **GS camera module for Raspberry Pi, IMX296 mono global shutter 1456 x 1088, 60 fps, "external trigger support"**. $43.00. 4.3 stars (20 ratings), FREE delivery Sat Oct 3, only 6 in stock. A Raspberry Pi host, not a USB webcam; the trigger route is the point.
- Others on the same results page without a stated trigger: ELP AR0234 global-shutter USB cameras with 90 fps at 1080p ($78.99 to $91.80, 18 to 36 ratings), an Arducam 120 fps mono module with a 130 degree M12 lens ($31.99, 14 ratings, "50+ bought in past month"), an Arducam OV2311 2 MP module ($98.99, 10 ratings). **Sales evidence is thin to modest** (tens of ratings); the listing text is the only source for trigger support.

### A red bandpass filter for a monochrome camera [trials-23-frame-clock, trials-03]

- **Light Red Bandpass Filter for Machine Vision, BP Series, BP635-25.5** (a 635 nm band; the red dot is 630 to 670 nm **[manual p.12]**). $121.00. 5.0 stars (13 ratings), Small Business, FREE delivery Fri Oct 2. **BP635-30.5** the same class, $130.00, no ratings shown, FREE delivery Fri Oct 2, 14 left. Sales evidence: thin. A band that suits a 650 nm module is a guess from the listing name; bandwidth and transmission are unchecked.
- The many "650nm" listings on the same page are **IR-cut (low-pass) filters** for a camera's sensor (for example 6.5 mm x 1 mm M12 AR-IR cut, $8.99, 62 ratings), not bandpass filters: they block infrared and pass visible light, which does not help isolate a red dot. Noted so that nobody buys one for this.

### A Gray-coded slate for a wide camera's view [trials-23-frame-clock]

- **74HC595 shift register breakout, 2 pcs**: $9.88, 5.0 stars (2 ratings), FREE delivery Tomorrow. **SN74HC595N DIP-16**: $7.99, 4.8 stars (62 ratings), FREE delivery Thu Oct 1; a 20-piece pack $8.49, 4.9 stars (27 ratings). **4 pcs 3-24 V 8-bit LED indicator module, common cathode, blue and red LED bar graph**: $9.88, 1 rating, Overnight. Eight LEDs and a shift register are the whole slate; the rotator's ESP32 (already on the rotator **[repo]**) drives them from its step counter. Sales evidence: commodity parts (dozens of ratings); nothing here is scarce.

### Not sourced

- A low-distortion M12 lens as a separate part: the Arducam listing in the wave 1 entry already ships one ("Low Distortion M12 Lens" in its title); its measured distortion is unchecked and is a calibration item (`trials-22-reference-pucks`).
- The printed board, the coupon, the notch and twin pucks: printed or sawn from scrap on the tools Derek has **[Derek]**, **[repo]**. The clear acrylic tube is in `sourcing/datum.md`.
