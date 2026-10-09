# Sourcing — eyes

Observed 2026-09-28 (Lincoln, NE 68520 delivery address as shown by the browser). Amazon: Prime listings only; every Amazon entry below was opened on its product page and the buy box showed the Prime badge and a "FREE delivery" line with a date. Search results were reached with the "All Prime" delivery filter. Sales volume is the "bought in past month" figure and review count shown on the page; a listing existing is not evidence of volume. Nothing was ordered and no vendor was contacted. Prices and delivery move daily.

Purpose: representative purchasable parts for the eyes ideas. Not a shopping list.

## Cameras and light

**Arducam 100 fps mono global-shutter USB camera, OV9281, M12 lens** (used by eyes-01, eyes-03, eyes-06)
- Amazon ASIN B096M5DKY6. $49.99. In stock; FREE delivery Tomorrow (Sep 29), or Wed Sep 30 with other items. Prime: Prime badge in the buy box.
- 4.4 stars, 35 reviews, "100+ bought in past month". Volume evidence is modest.
- Why it matters: a global shutter, monochrome, UVC device with an M12 lens mount, so the lens (field of view, focus distance) can be swapped. Mono suits a red-dot camera behind a red filter. No rolling-shutter smear on a moving gun. Minimum focus distance depends on the M12 lens, **unchecked**.
- Alternatives seen in the same search: Arducam 120 fps 130° mono $31.99 (14 reviews, "50+ bought"); a Raspberry Pi OV9281 module $30.00 (23 reviews, "50+ bought").

**Logitech HD Pro Webcam C920** (used by eyes-03, eyes-02b as the "cheap fixed eye")
- Amazon ASIN B006JH8T3S. $67.39. In stock; FREE delivery Tomorrow (Sep 29). Prime: Prime badge in the buy box.
- 4.6 stars, 32,759 reviews, "500+ bought in past month". The strongest volume evidence in this file. Autofocus, 1080p, fixed wide lens; whether its close-focus range and lens suit a tag cube at 250-500 mm is **unchecked**.

**Endoscope camera with light, 1920P borescope, semi-rigid cable** (used by eyes-02b ideas: a small eye dipped over the rim; eyes-10)
- Amazon ASIN B0C4V5LWWL. $25.99. In stock; FREE delivery Tomorrow (Sep 29). Prime: Prime badge in the buy box.
- 4.3 stars, 7,785 reviews, "6K+ bought in past month". Very high volume.
- Diameter, focus range and field of view of the probe head were not read; whether it fits beside the gun in the canyon is **unchecked**.

**520 nm green line-laser module, focusable, 16 mm, 5 V with adapter** (used by eyes-01: the line laser on the shell)
- Amazon ASIN B0D4YRDKXN. $29.98. In stock; FREE delivery Wed Sep 30. Prime: Prime badge in the buy box.
- 4.4 stars, 40 reviews, "100+ bought in past month". Related green line modules in the same search show "800+ bought" and "1K+ bought" (listed as Halloween projectors): the parts are common.
- Laser class, fan angle and line width on this listing were not read: **unchecked**. Some sibling listings state Class 1 or Class 3R. A line laser next to a 700 W laser needs its own eye-safety look; not assessed.

**650 nm filters**: the Prime results for "650nm bandpass filter" were mostly 650 nm **IR-cut** filters (block above 650 nm), which is the opposite of what a red-dot camera wants. A light-red band-pass filter (BP635, 30.5 mm) was $130. A 665 nm IR-pass filter, 52 mm, was $70. Not opened. Whether a suitable narrow 650 nm band-pass exists at hobby prices is **unresolved**. Note that an IR-pass filter would also pass the 1080 nm process light.

## Motion, tilt, heat, sound

**HiLetgo 3 pcs GY-521 MPU-6050 (6-axis IMU)** (used by eyes-11)
- Amazon ASIN B00LP25V1A. $11.79. In stock; FREE delivery Tomorrow (Sep 29). Prime: Prime badge in the buy box.
- 4.6 stars, 800 reviews, "600+ bought in past month", "Best Sellers Rank #1 in Acceleration Sensors" shown on the page. Very high volume.
- A MEMS accelerometer and gyro board: tilt against gravity for two axes, no absolute heading. Accuracy of the tilt in the presence of the gun's vibration motor is **unchecked**.

**BNO080/BNO085 nine-axis module** (used by eyes-11)
- Amazon ASIN B0CDGZMLPP. $20.49. In stock; FREE delivery Tomorrow (Sep 29). Prime: Prime badge in the buy box.
- 4.7 stars, 24 reviews, "100+ bought in past month", "#3 in Acceleration Sensors". Sensor-fusion output on the chip; magnetometer heading near a stepper motor and a steel bench is **unchecked** and probably poor.

**Waveshare MLX90640 thermal imaging camera, 32 x 24, 55° field of view** (used by eyes-10 and the thermal branch of eyes-09: seeing the seam through the tube wall)
- Amazon ASIN B07ZKK8QWY. $68.99. "Only 3 left in stock". FREE delivery Friday Oct 2. Prime: Prime badge in the buy box.
- 4.5 stars, 10 reviews, no "bought" figure. Rank #184 in Thermal Imagers. Low volume. 768 pixels: on a 127 mm tube a pixel is several millimetres. Frame rate and the response to a 316L surface (emissivity) are **unchecked**.

**Piezo contact-microphone pickups, 2 pcs** (used by eyes-11: a sound channel on the tube or the gun)
- Amazon ASIN B07795XHLH. $13.99. Prime badge seen in the Prime-filtered search result card; the product page itself was **not opened** for this one.
- 4.1 stars, 959 reviews, "50+ bought in past month". Sold for instruments; whether it hears the keyhole or the wobble motor is **unchecked**.

## Proximity chips (not on Prime)

No Prime listing was found for an FDC1004 or LDC1612 breakout in this pass. Other vendors, read from their own pages:

**Seeed Studio Grove 2-Channel Inductive Sensor (LDC1612)** (used by eyes-04, the eddy-current option)
- seeedstudio.com/Grove-2-Channel-Inductive-Sensor-LDC1612.html. $16.40. "In stock", China warehouse shown. Read 2026-09-28. Also listed by RS Components (UK, £14.89 excl. VAT, 21 in stock at the time of the search result) and other resellers.
- The chip is a TI LDC1612: 28-bit, 2 channels, 1 kHz to 10 MHz sensor frequency, metal-proximity detection (TI product page, read 2026-09-28). Whether the board's included coil suits a 5 mm sensing window near the nozzle is **unchecked**; the board page does not say.
- Sales volume: none observed.

**ProtoCentral FDC1004 capacitance-to-digital breakout, v2 with Qwiic** (used by eyes-04, the capacitive option)
- protocentral.com/product/protocentral-fdc1004-capacitance-sensor-breakout-board/. Priced in Indian rupees on that page (₹1,695); the page shows it on back-order, shipping in 7-10 days; free worldwide shipping over $200. Read 2026-09-28. Also sold through Tindie.
- Chip: 4 channels, 0.5 fF resolution, ±15 pF range, up to 400 S/s (TI product page and the vendor page). USD price and US delivery time: **unchecked**.
- Sales volume: none observed.

## Not bought, not sourced

- AprilTag or ArUco tags: printed on the existing printers; nothing to buy. Whether a printed cube survives near a laser head is **unchecked** (eyes-03).
- Cameras' M12 lenses, ring lights, small posts and camera mounts: not sought.
- A 316L half-tube for the sectioned phantom (eyes-07) would be sawn from the same 5 in tube stock the project already buys (OnlineMetals #12498, [repo] pressure-vessel.md); not re-priced here.
- Non-Amazon retail for a digital indicator with data output and for small XY trim stages: not sought this wave (eyes-01's trim stage is drawn generically).

## Wave 2 additions (observed 2026-09-29; Amazon Prime only)

Search pages were reached with the "All Prime" filter (`rh=p_85:2470955011`). Where an entry says "product page opened", the page carried the Prime logo element beside the buy box; where it says "search card only", only the Prime-filtered result card was read. Nothing was ordered or contacted. Delivery dates are the day's promise.

**NexiGo 10X optical zoom PTZ conference camera, USB output, IR remote** (used by eyes-16: Derek's "couple PTZ cameras controllable by software")
- Amazon ASIN B0DQCFX9WN. $242.99. Product page opened; Prime logo present; "FREE delivery Today 5 PM - 10 PM" (Lincoln 68520), ships from Amazon.
- 4.4 stars, 5,521 ratings. No "bought in past month" figure on the page. Volume evidence is the rating count: real.
- Spec text on the page: pan +/-170 degrees, tilt -30 to +90 degrees, pan speed 2.7 to 47 degrees per second, 255 presets over RS232, VISCA over RS232/RS485/IP for multi-camera control, 1080p. That is a software-commandable pointing device.
- **Not on the page:** any pan or tilt repeatability, zoom scale repeatability, or resolution of the pan/tilt steps. These decide whether the aim can be part of a measurement (eyes-16 assumes it cannot). **Unchecked.**
- Same search, all Prime: NUROUM V403 5X $199.99 (4.3 stars); Tenveo 20X $299 (4.2); Monoprice 3X $261.32 (3.4 stars); TONGVEO 20X $299 (4.2); TONGVEO 3X. Roughly $200 to $300 for a VISCA-class unit.

**Digital LCD linear scale, 0 to 150 mm, resolution 0.01 mm** (used by eyes-14: scales on the outside end of the wall-port rod)
- Amazon ASIN B089ZSG84J. $26.99. Product page opened; Prime logo present; FREE delivery Tomorrow, Sep 30.
- 4.3 stars, 207 ratings, "50+ bought in past month".
- Page text: resolution 0.01 mm (0.0005 in), accuracy +/-0.06 mm. It is an LCD readout scale of the calipers-and-lathe-DRO kind: **no data output was stated**, so software would read it by camera or through a tapped data port. Accuracy is 6 times the 0.01 mm noise figure the scene assumes; accuracy is a bias that a one-off calibration can remove, noise it cannot.
- Better-specified relatives seen in the same search: TOAUTO 5 micrometre optical scale with a 2- or 3-axis DRO display, 150 mm, $72.99 (9 ratings); a 0 to 300 mm magnetic scale $39.99 (55 ratings). Low volume on the optical ones.

**Load cell plus HX711 amplifier** (used by eyes-14: force at the tail actuators)
- Search card only. "2 Sets Digital Load Cell Weight Sensor + HX711 ADC Module", ASIN B09K7G3477, $9.99, 4.0 stars, 25 ratings, "100+ bought in past month". SparkFun HX711 Load Cell Amplifier, ASIN B079LVMC6X, $11.50, 4.6 stars, 75 ratings, "100+ bought in past month". NOYITO 1/5/10/20 kg cell plus HX711 kit $6.79 (14 ratings).
- Cells are bar-type 1 to 20 kg parts sold for kitchen-scale projects. The scene assumes 0.1 N (10 g) noise at about 6 N: **unchecked**, and a bar cell inline in a tail actuator would need a mounting the listing does not show.

**Aluminium round tube for the wall-port rod** (used by eyes-14: how stiff a rod is)
- 6061 aluminium tubing 1-1/2 in (38 mm) OD, 0.12 in (3 mm) wall, 12 in, ASIN B0BNQ4T5LJ, $15.19, 4.2 stars, 114 ratings, delivery Tomorrow, Sep 30 (search card only). A 24 in intercooler pipe of 1.5 in OD is also Prime at $32.66.
- The scene's default rod is 20 mm OD with a 2 mm wall; this listing's tube is 38 mm with a 3 mm wall, about 15 times stiffer in bending than the default. The point of eyes-14 is that this choice matters more than the ball's play; the parts exist at hardware prices with next-day delivery.

**Still unresolved:** a narrow red band-pass filter at hobby prices for a camera that must see a 0.3 mW dot beside a 1080 nm process (wave-1 gap); not searched again this wave.

## Wave 3 additions (observed 2026-09-29; Amazon Prime only)

Reached with the "All Prime" filter (`rh=p_85:2470955011`), my own Chrome tab (closed). "Product page opened" means the buy box carried the Prime logo, "Ships from Amazon" or the fulfilment line, and the delivery promise was read from the page; "search card only" means only the Prime-filtered result card was read (price, stars, ratings count, "bought" figure, delivery line). Nothing was ordered or contacted. For the feedback-layer ideas (eyes-17, eyes-18) and the second fan of eyes-01.

**Green cross-hair laser module, 520 nm, with adapter and holder** (eyes-01 wave 3: a second fan at 90 degrees resolves all five observable pose numbers, `calc/line-laser-pose.mjs`)
- Amazon ASIN B0BJ6YM9TB, "520nm Green Cross Line Light Cross Hair Locator Marker for Screen Printing Heat Press Machine Alignment Placement (+AC-DC adapter+Holder)", sold by Laserland, ships from Amazon. $35.00. Product page opened; Prime logo in the buy box; "FREE delivery Tomorrow, September 30" (overnight also offered), In Stock.
- 4.1 stars, 78 ratings; no "bought in past month" figure on the page. Sibling listings in the same search: 16 mm module cross $26.85 (7 ratings, two-day), a 22 mm 5 V cross $29.99 (1 rating), Class 1 industrial cross-hair modules (VLM-520-29 LPA, $42.99, 8 ratings) with a stated 7 to 10 V APC driver. Related green line modules from the wave 1 entry show 100+ to 1K+ bought.
- Not on the page: fan angle, line width, laser class, whether the two fans are orthogonal to a stated tolerance (a cross-hair from a hobby module is not calibrated: the fan angles are then two more calibration unknowns). **Unchecked.** A 700 W laser stands next to it, and eye safety of a second visible laser near the operator has not been assessed.

**WS2812B 8-LED addressable stick, 10 pack** (eyes-17: the light bar on the shell)
- Amazon ASIN B0BWH95XSH, DIYmall "10PCS 8 RGB LED Stick 8 X WS2812B 5050", DC 4 to 7 V, single-wire. $18.99 for ten ($1.90 each). Product page opened; Prime logo in the buy box; "FREE delivery Tomorrow, September 30"; In Stock.
- 4.8 stars, 35 ratings, "100+ bought in past month". Cheaper and thinner-evidence siblings on the same search: $14.99 (43 ratings, 4.4 stars), $6.97 (14 ratings, 3.8 stars), $16.99 (4 ratings).
- Not on the page: brightness in candela (WS2812B: a few hundred mcd per colour at full drive, from the chip's public datasheet, unchecked here), whether a bar reads against the bead's glow with a welding shield or laser safety glasses on. **Unresolved, and it decides the light bar** (question for Derek: which eyewear, and does it pass a green and an amber LED?).

**Push-pull solenoid, 12 V, 10 mm stroke** (eyes-17 brake: a solenoid pulling a printed pad onto a rail; power-off = pad released)
- Amazon ASIN B07MJJB12M, Heschen HS-0530B, "1.7 A, 5 N max force, 10 mm stroke, initial force 0.5 N, push-pull, open frame". $7.99. Product page opened; Prime logo in the buy box; ships from Amazon; "FREE delivery Tomorrow, September 30".
- 4.1 stars, 383 ratings, "50+ bought in past month". Same search: $12.99 (4 N, 5.0 stars, few ratings), $13.89 (25 N, 4.2), $14.89 (uxcell 15 N), $13.99 (20 N, 4.4). A bigger 15 to 25 N unit costs about $14.
- The 5 N is the force at the closed end of the stroke, a solenoid's number; through a 2:1 to 5:1 printed lever it becomes a clamp force at a pad, minus friction. What a pad on an anodised or stainless rail holds is **unmeasured**. A holding (sticky) solenoid would hold without power: not wanted, the design needs power-off to release.
- Also on the search: spring-applied electromagnetic brakes are Prime but priced as industrial parts (24 V 25 N-m brake $211, integrated closed-loop steppers with brakes $46 to $233). No magnetic-particle brake or small friction clutch at hobby price was found on Prime; a printed pinch with a solenoid or servo is the cheap route, a bought brake the expensive one.

**Haptic motor driver DRV2605L breakout** (eyes-17: a vibration cue with named effects and a library; hand or grip)
- Search cards only: ASIN B083G1MCYZ $11.81, 4.3 stars, delivery Tomorrow; SparkFun PID 14538 (B01MTF2BLH) $24.07, 4.0 stars; a 2-pack $16.07 (3.4 stars). No "bought" figures; ratings counts not captured. Volume evidence: **thin** (the chip is common, the listings are not high volume).
- 10 mm flat coin ERM vibration motors: ASIN B07Q1ZV4MJ, 20 pieces, $12.99, 4.7 stars, "100+ bought in past month", delivery Tomorrow (search card only); other packs $5.99 to $12.99. The laser head already contains a vibration motor (**[manual]** p. 20); whether the grip can tell a second buzz from it is unknown.

**Miniature linear rail with carriage** (eyes-17: the cross-slide the hand pushes through; the coach loop's fine stage without knobs)
- ASIN B0D54LNVKX, uxcell MGN9 100 mm rail with MGN9C carriage, $9.99, 4.5 stars, delivery Tomorrow (search card only). Others: MGN9H 100 mm $12.09 (two-day/Sat), 2-pack $19.99, TEN-HIGH $19.00 (3.7 stars). Printer-class parts; what they state is a size and a load, never a stiction number, which a brake-and-release design needs.

**Not searched:** a red band-pass for the dot camera (still open from wave 1); any projector that puts a guide onto the plate (the line laser of eyes-01 is the projector in the drawn design); a small OLED (an 0.96 in SSD1306 is a commodity part; not sourced).
