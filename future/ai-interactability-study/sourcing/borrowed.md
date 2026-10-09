# Sourcing: borrowed

Observed 2026-09-28 (Lincoln 68520 delivery address shown by Amazon). Amazon entries are Prime listings only: each search used the Prime filter (`rh=p_85:2470955011`), and each product page was opened to confirm the Prime logo icon and the Prime delivery message in the buy box ("Two-Day", "Tomorrow", or "FREE delivery ..."). No non-Prime listing is recorded. Nothing was ordered and no vendor was contacted.

"Bought in past month" is Amazon's own label ("100+", "4K+"); review counts are the listing's rating count. Both are listing counts, not unit sales. Where a listing has few ratings the row says so.

## What the sourcing changed in the ideas

- Monitor-arm gas springs are rated for a minimum load (the top-selling one: 4.4 lb, 2 kg). A gun and printed shell that weigh less than that sit below the arm's range. The encoded-arm scene's mass and balance sliders start at 0.5 kg for this reason; a lighter spring (lamp arm, balancer) or ballast is the route. [borrowed-03]
- The desktop CNC found on Prime has a 40 mm Z travel (11.2 x 7.1 x 1.6 in working area). The gimbal-on-gantry scene's compensation needs 100 to 200 mm of Z at a 200 mm pivot distance. A stock hobby CNC is a donor for the electronics and the language (G-code, probe input), not for the frame. [borrowed-02]
- The magnetic encoder that is cheapest and easiest to get (AS5600, $8 for three) has a datasheet INL of +/-1 degree maximum. That, not its 12-bit resolution, is what decides whether it can be a joint sensor. [borrowed-03]
- Hollow-shaft gimbal motors with an on-board AS5600 and a SimpleFOC driver are on Prime for about $35 (a kit): the candidate ring-drive donor and a way to get an angle sensor on every ring for one price. [borrowed-01, borrowed-02]

## Entries

### 12 in lazy susan bearing (ring-bearing donor)
- What: "12 Inch Lazy Susan Hardware Heavy Duty Metal Rotating Hardware Turntable Bearing Ring 300 mm ... Base Only" (TamBee). ASIN B01L8EHD6K.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B01L8EHD6K
- Price: $22.99. Delivery: "FREE delivery Tomorrow, September 29" (order within 3 min), or Wed Sep 30.
- Sales evidence: 4.6 stars, 2,611 ratings, "200+ bought in past month".
- Prime: Prime logo icon on the product page; buy box shows "Tomorrow / FREE delivery".
- Also seen: Shepherd Hardware 9549 12-inch lazy susan, ASIN B00004YOKA, $12.99, 4.5 stars, 2,471 ratings, "100+ bought in past month", FREE delivery Fri Oct 2, Prime logo on the page; the page says zinc coated ball bearings sandwiched between plates.
- Relevance: idea borrowed-01 (rings round empty axes). Unchecked: the bore diameter, thickness and runout of either listing; the yaw ring in the scene has a bore radius of about 60 mm, smaller than a 12 in ring. The printed 165 mm ball race of the rotator [repo] is the alternative at the sizes the scene uses.

### Hollow-shaft gimbal motor kit with encoder
- What: "2804 Brushless Gimbal Motor Kit with AS5600 Encoder and SimpleFOC Driver". ASIN B0FXKN9YMJ.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B0FXKN9YMJ
- Price: $34.88. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.1 stars, 16 ratings, "50+ bought in past month" (small volume).
- Prime: Prime logo icon on the page; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Also seen in the same Prime-filtered search (search page only): a 2804 hollow-shaft motor with AS5600 at $24.99 (11 ratings) and a 4015 hollow-shaft motor with an MT6701 encoder at $39.89 (9 ratings).
- Relevance: borrowed-01 ring drives, borrowed-02 gimbal axes. Unchecked: torque, bore, whether it can hold a gun's cantilever; a 2804 is a small gimbal motor.

### DJI RS 4 Pro handheld gimbal
- What: "DJI RS 4 Pro, Gimbal Stabilizer for DSLR & Cinema Cameras". ASIN B0CS6J2648.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B0CS6J2648
- Price: $869.00. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.3 stars, 532 ratings, "100+ bought in past month".
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Payload: the listing and search snippets give 4.5 kg. Not checked against DJI's own spec page (search results only).
- DJI RS SDK: https://www.dji.com/rs-sdk (fetched 2026-09-28) lists RS 5, RS 4, RS 4 Pro and RS 3 Pro as supported and features "set gimbal position", "control gimbal rotation", "get motor and attitude information"; no licence requirement stated on that page. A search summary says the protocol is CAN at 1 Mbps and that CAN can be bridged to a PC with a CAN-USB adapter; that was not confirmed on the DJI page (unchecked).
- Relevance: borrowed-02. Unchecked: whether the gimbal can hold 0.05 degrees with a cantilevered 250 mm load, or hold a pose unpowered.

### Genmitsu 3018-PROVer V2 desktop CNC
- What: "Genmitsu 3018-PROVer V2 CNC Milling Machine for Beginners ... 11.2'' x 7.1'' x 1.6'' Working Area". ASIN B0CMTJ6CZC.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B0CMTJ6CZC
- Price: $269.00. Delivery: "FREE delivery Friday, October 2"; "Only 11 left in stock".
- Sales evidence: 4.0 stars, 75 ratings, no "bought" label on this page. A SainSmart 3018 listing in the same search shows 1,286 ratings (not opened).
- Prime: Prime logo icon on the page; buy box "FREE delivery Friday, October 2".
- GRBL probing: search results (Grbl project, Marlin docs) describe G38.2 as a straight probe that stops when the probe input closes. Not tested on this machine.
- Relevance: borrowed-02 (G-code as the language; the probe input as a touch channel). The 40 mm Z travel is too small for the scene's gantry.

### Gas-spring monitor arm (weight-carrying donor)
- What: "HUANUO FlowLift Single Monitor Mount, 13 to 32 Inch Monitor Arm ... Fits 4.4 to 19.8 lbs". ASIN B07T3KCQ94.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B07T3KCQ94
- Price: $35.99. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.6 stars, 16,507 ratings, "4K+ bought in past month" (the highest volume of anything in this file).
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Also seen (search page): ErGear single arm $26.99, 9,010 ratings, "8K+ bought"; Amazon Basics arm $25.49, 1,327 ratings, "500+ bought".
- Relevance: borrowed-03. Rated load 4.4 to 19.8 lb: below the gun's likely weight range? Gun mass is unknown [unknown]. Unchecked: joint play, and whether its joints can take an encoder.

### AS5600 magnetic encoder modules
- What: "UMLIFE 3pcs AS5600 Magnetic Encoder High Precision Sensor Module, 12bit, I2C, PWM, Voltage Output, Non-Contact, 23x23mm". ASIN B094F8H591.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B094F8H591
- Price: $7.99 for three. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.4 stars, 70 ratings, "100+ bought in past month".
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Datasheet (ams AS5600 v1-06, a Seeed-hosted copy, read 2026-09-28): resolution 12 bit; system INL "+/-1 degree" maximum over 360 degrees with no magnet displacement and no zero programming; RMS output noise 0.015 degrees (slow filter, 2.2 ms) to 0.043 degrees (fast filter, 0.286 ms). A search summary quoted a "0.5 degree typical" figure, which does not appear in the datasheet table read here (unchecked).
- Relevance: borrowed-03 (joint sensors), borrowed-01 (ring encoders).

### USB to RS-232 adapter (FTDI)
- What: "USB to RS232, USB Serial Adapter with FTDI Chipset, USB 2.0 to Male DB9 Serial Cable ... 6ft". ASIN B0759HSLP1.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B0759HSLP1
- Price: $12.99. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.6 stars, 2,066 ratings, "2K+ bought in past month".
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Relevance: borrowed-06. The X1 Pro's RS232 port is a DB9 with pins 2 (RXD), 3 (TXD) and 5 (GND) documented and nothing about a protocol [manual p. 16]. Whether a male or female DB9 is needed is not checked.

### Spring tool balancer
- What: "QWORK Spring Balancer, 2 Pack 3.3 lbs - 6.6 lbs Bearing Retractable Tool Fixture Holder for Assembly-line". ASIN B0BTCXLZB8.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B0BTCXLZB8
- Price: $18.97 for two. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 3.8 stars, 29 ratings, "50+ bought in past month" (thin evidence).
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Also seen (search page only): a 1.1 to 3.3 lb two-pack at $16.97 (34 ratings) and a 3 to 5 kg PATIKIL unit at $21.19 (2 ratings).
- Relevance: the ceiling-carry branch (notebook B10). Unchecked: travel, cable stiffness, lock.

### Monochrome global-shutter USB camera
- What: "Arducam 100fps Mono Global Shutter USB Camera, 720P OV9281 UVC Webcam Module with Low Distortion M12 Lens". ASIN B096M5DKY6.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B096M5DKY6
- Price: $49.99. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.4 stars, 35 ratings, "100+ bought in past month".
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Relevance: borrowed-05 (a small mono camera for a centroid). Unchecked: sensitivity to a 630 to 670 nm 0.3 mW dot under welding light, and whether an M12 lens can be aimed into the corner.

### Manual cross-slide table and digital scale (DRO stack donors)
- Cross-slide: "Compound Slide Table, MYSWEETY Worktable Milling Working Cross Table ... X-Y". ASIN B07GXH3HWZ, https://www.amazon.com/dp/B07GXH3HWZ, $59.99, 4.1 stars, 1,068 ratings, no "bought" label, FREE delivery Fri Oct 2, "Only 15 left in stock". Prime logo icon on the page.
- Digital scale: "Digital LCD Linear 0-150mm/0-6inch Accurate Digital Readout Lathe Scale for Milling Machines". ASIN B089ZSG84J, https://www.amazon.com/dp/B089ZSG84J, $26.99, 4.3 stars, 207 ratings, "50+ bought in past month", Two-Day Wed Sep 30. Prime logo icon on the page. The same search shows 5-micron optical DRO kits at about $60 with 3 to 4 ratings each (not opened).
- Relevance: the manual-stack-with-scales idea (notebook B5). Unchecked: resolution and output of the LCD scale (no data port checked).

### 6-DoF hand controller
- What: "3DConnexion 3DX-700059 Spacemouse Compact 3D Mouse". ASIN B079V4PXYD.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B079V4PXYD
- Price: $171.00. Delivery: Wed Sep 30 (Two-Day).
- Sales evidence: 4.7 stars, 1,044 ratings, "200+ bought in past month".
- Prime: Prime logo icon; buy box "Two-Day / FREE delivery Wednesday, September 30".
- Relevance: setup jogging and demonstration recording (notebook B11/B12). Unchecked: driver route on macOS.

### LeRobot SO-101 arm kit (leader-follower donor)
- What: "SO-101 Follower Arm Electronics Kit with 12V Feetech STS3215 Servos". ASIN B0GH35175P.
- Vendor / URL: Amazon, https://www.amazon.com/dp/B0GH35175P
- Price: $184.99. Delivery: FREE delivery Fri Oct 2; "Only 1 left in stock".
- Sales evidence: 1 rating. Essentially none.
- Prime: Prime logo icon on the page; buy box "FREE delivery Friday, October 2".
- Other sources (search summaries only, unchecked on the vendor pages): SO-ARM101 dual-arm kits from about $220 (standard) or $240 (pro) at Seeed and on AliExpress, printed parts extra (about $35); six Feetech STS3215 servos rated 30 kg-cm each; natively supported by Hugging Face LeRobot. CNX Software article: https://www.cnx-software.com/2025/05/02/so-arm101-open-source-dual-robotic-arm-kit-works-with-hugging-faces-lerobot/
- Relevance: notebook B11 (a leader arm as a hand controller; the follower is far too small for the gun).

## Not sourced (and why)

- Goniometer cradles, pano heads, geared photo heads, moving-head stage lights, wiper motors and window regulators: named in the notebook as donors; none was needed to decide anything yet. No prices claimed.
- Autoguiding software (PHD2): its manual pages could not be retrieved in this session, so the calibration procedure in borrowed-05 is described from general practice, not from a checked page (unchecked).

---

# Wave 2 (observed 2026-09-29, Derek's signed-in Chrome, delivering to Lincoln 68520, my own tab, closed)

Same rules as above. Every Amazon search used the Prime filter (`rh=p_85:2470955011`). "Product page" below means the page was fetched in my tab and the buy box shows the Prime icon or a Prime delivery line ("Two-Day", "Tomorrow", "FREE delivery ... for Prime members"); "search card" means the entry was seen only on a Prime-filtered results card and the page was not opened. Ratings counts and "bought in past month" are Amazon's labels. Prices are single observations. Nothing was ordered and no vendor was contacted. Specifications marked **search** are search-engine summaries of a maker or forum page and are unchecked against the page. This wave was looking for what bought hardware would realise Derek's examples (loops, cords, bungee; balanced arms and their payload ranges; gantry rails, drawer slides, sit-stand frames; PTZ cameras) and for ordinary robot arms and other multi-axis positioners with a software interface.

## What the sourcing changed in the ideas

- **The payload floor of monitor arms is a selection problem, not a wall.** Prime listings cover 0.25 kg to 9 kg with next-day or two-day delivery: a microphone boom rated 0.25 to 1.2 kg (RØDE PSA1+), a scissor-spring boom rated 1.5 kg (InnoGear, 24,099 ratings, "2K+ bought"), a gas-spring mic arm rated 3 kg (Elgato Wave Mic Arm Pro) and the 2 kg-and-up monitor arms already in `sourcing/freedom.md`. What decides it is weighing the parts to about 0.1 kg. [borrowed-14]
- **The camera-stabiliser sled is a product for freedom-08's plumb bob:** a three-axis ball-bearing gimbal, fine-tune balance knobs and a bottom weight. It is sold up to 3.5 kg for $178. Fluid video heads (a rotary viscous damper with stepped drag, a 5 kg rating, $57 to $99) are on Prime, and none of their listings states a damping value. [borrowed-15]
- **No Prime desktop arm carries the gun.** The desktop arms found are rated 0.25 to 0.5 kg. A collaborative arm that states 3 kg and +-0.02 mm is a maker product, not a Prime listing. A telescope mount rated 5 kg with a two-rotation, 0.625 arcsecond step is on Prime for $525. [borrowed-17]
- **There is no ready-made hexapod on Prime.** The miniature laser-alignment hexapods are quote products; the parts for a small one (six mini linear rails with motors, rod ends) are on Prime. [borrowed-13]

## Balanced arms, balancers, sleds, dampers

**RØDE PSA1+ boom arm with spring damping** (product page)
- Amazon, https://www.amazon.com/dp/B09JBVR5B4, $112.00, "Two-Day FREE delivery Thursday, October 1", In Stock, ships from Amazon.
- Volume: 2,701 ratings, "1K+ bought in past month". Prime icon in the buy box.
- Rated: "holds microphones from 0.25 kg to 1.2 kg including shock mounts"; clamps to desks up to 70 mm thick; internal spring damping. A window that starts at 0.25 kg and stops at 1.2 kg. [borrowed-14]

**InnoGear boom arm, scissor spring** (product page)
- Amazon, https://www.amazon.com/dp/B01L3LL95O, $19.99, "FREE delivery Today 5 PM - 10 PM on qualifying orders over $25".
- Volume: 24,099 ratings, "2K+ bought in past month" (the highest sales evidence of anything in this file). Prime icon in the buy box.
- Rated: "load-bearing capacity of 3.3 lb / 1.5 kg" (listing bullet); item weight 1.35 lb. The same family appears at 3.3 to 4.4 lb on other InnoGear listings (search cards). [borrowed-14]

**Elgato Wave Mic Arm Pro, gas spring** (product page)
- Amazon, https://www.amazon.com/dp/B0DGQMDKH3, $179.99, "Tomorrow", ships from Amazon.
- Volume: 371 ratings, "100+ bought in past month". Prime icon.
- Rated: "supports up to 3 kg / 6.6 lbs, including accessories"; gas-spring suspension; clamp for desks to 60 mm. A floor is not stated. [borrowed-14]

**FIFINE CS1 scissor boom arm** (product page)
- Amazon, https://www.amazon.com/dp/B09BQQTLC8, $19.99, "Tomorrow". 1,846 ratings, "1K+ bought in past month". Prime icon. Item weight 1.1 lb; the payload was not read. Also seen on Prime search cards: MAONO BA20 (title: max load 1 KG, $24.99, 480 ratings), NEEWER MS006 (max load 3.3 lb, $20.99, 235 ratings), "Upgraded Mic Arm, 1.8 KG" ($24.99, 29 ratings).

**Tigon TW-1R spring balancer, 0.5 to 1.5 kg** (product page, re-observed)
- Amazon, https://www.amazon.com/dp/B07Z6R1KP3, $39.00, "Tomorrow". 69 ratings. Prime icon. Item weight 13.4 oz; "Maximum Weight Capacity 3.3 pounds". Also in `sourcing/freedom.md`. In borrowed-16 it is the source of a near-constant downward pull (5 to 15 N).

**FLYCAM HD-3000 handheld stabiliser (sled)** (product page)
- Amazon, https://www.amazon.com/dp/B00O5ZSAC6, $178.00, "Tomorrow". 362 ratings. Prime icon.
- Listing: "for DSLR cameras up to 3.5 kg / 7.7 lb"; "Micro-Balance system with fine-tuning knobs adjusts your camera front-to-back and side-to-side"; "Internal 3-axis gimbal with ball bearings"; item weight 8.8 lb (with weights). It is freedom-08's gimbal above the centre of mass, its trim, and a bottom weight in one product. Also seen (search cards, Prime filter): Zeadio handheld stabilising handle ($17.98, 4,610 ratings, "400+ bought"), a Wondalu 40 cm steadicam ($39.99, 177 ratings). [borrowed-15]
- Drop-time practice (a properly balanced sled drops in 2 to 3 seconds; the pendulum period is the balance) is from search results on Steadicam operator documentation: unchecked against a manual.

**Fluid video heads** (product pages)
- SIRUI VA-5 fluid head, https://www.amazon.com/dp/B00KS5QE02, $99.00, "Tomorrow", 230 ratings, Prime icon.
- V504 video tripod fluid head with quick-release plate, https://www.amazon.com/dp/B09V4X6XK7, $56.99, "Tomorrow", 100 ratings, "50+ bought in past month", Prime icon. Listing: max load 11 lb / 5 kg, tilt +90 / -50 degrees, pan 360 degrees. Also on search cards: Manfrotto video head with flat base ($229.95, 2.1K ratings, "50+ bought"), Benro S6 PRO with 6-step counterbalance ($264.95, 56 ratings), K10 Pro with adjustable pan drag ($69.99, 49 ratings).
- What none of the listings states: the damping in N*m*s/rad. Drag is set in steps (Sachtler: 0 to 7; SmallRig: 4 steps). Search results give no torque values: unchecked, a spring scale on the handle at a known speed would measure it. [borrowed-15]

**Locking gas spring and chair gas lift** (one product page, two search cards)
- Bansbach B-locking gas spring 28 in (715 mm), force 135 N, https://www.amazon.com/dp/B019XFR1B8, $71.57, "FREE delivery Friday, October 2", Prime icon; listing: "rigidly lock in both directions". Ratings not shown.
- Office chair gas lift cylinders (Prime search cards): Omyoffice 5.5 in class 4, $22.99, 2.2K ratings, "800+ bought"; a 5 in cylinder, $25.99, 7.7K ratings, "100+ bought". Not opened. A pneumatic column that holds any height under load and releases with a pin. [borrowed-18]

## Gantry parts, lifts, slides, loops (Derek's table-opening and suspension examples)

**Creality Ender-3 V3 SE printer** (product page)
- Amazon, https://www.amazon.com/dp/B0F8J78BN1, $219.00, "FREE delivery Monday, October 5 for Prime members" (the Prime icon was not detected in the buy box; the delivery line names Prime). 2,153 ratings, "500+ bought in past month". Listing: dual Z lead screws, CR Touch auto-levelling. XYZ Cartesian, G-code. Payload of its carriages not stated. Step of a GT2 20-tooth belt at 1/16 microstepping is 0.0125 mm; belt elasticity 50 to 100 micrometres per a search summary (unchecked). [borrowed-17]

**Genmitsu PROVerXL 4030 CNC router** (product page)
- Amazon, https://www.amazon.com/dp/B08L6314MW, $659.00, "Tomorrow", 525 ratings, Prime icon. GRBL-class G-code. Z travel and spindle-mount size not read (unchecked).

**MGN12 300 mm linear rail with preloaded carriage** (product page)
- Amazon, https://www.amazon.com/dp/B07ZVFFXQZ, $20.49, "FREE delivery Sunday, October 4 for Prime members", 615 ratings. "Blocks are pre-loaded", rubber end stops. 2020 T-slot extrusion, 4 x 300 mm: $17.99, 984 ratings, "100+ bought" (search card).

**100 mm mini linear rail, T6x1 lead screw, NEMA 11** (product page, also in `sourcing/freedom.md`)
- https://www.amazon.com/dp/B087NMQWQL, $54.80, "Two-Day", 34 ratings, Prime icon. 5 micrometres per full step [derived]. The six axes of a small hexapod, or of a vernier. [borrowed-13]

**Rod end bearings, M5, 4 pack** (search card): https://www.amazon.com/dp/B0C7MZMYMF, $9.99, 66 ratings. Linear actuator, 100 mm stroke, 96 N (search card): Justech, $26.99, 12 ratings. Play of a cheap rod end is not stated on either.

**VIVO dual-motor sit-stand desk frame** (product page)
- Amazon, https://www.amazon.com/dp/B08P7WL7SJ, $199.99, "FREE delivery Thursday, October 1", 1,209 ratings, "50+ bought in past month", Prime icon. "Solid 220 lbs support". Also on search cards: HUANUO frame $169.99 (225 ratings, "100+ bought"), ErGear $169.99 (601 ratings, "300+ bought"). Height resolution, presets and leg skew are not on the listing.

**FivePears 20 in ball-bearing drawer slides, pair** (product page)
- https://www.amazon.com/dp/B0BX9BKLC8, $19.79, "Tomorrow", 157 ratings, Prime icon. "150 Lb Load Capacity". Side play is not stated.

**LOKMAN 2 in rubber-cushioned stainless cable clamps, 20 pack** (product page)
- https://www.amazon.com/dp/B01ISZLJBM, $17.99, "FREE delivery Today 5 PM - 10 PM on qualifying orders over $25", 6,185 ratings, "100+ bought in past month", Prime icon. Inside diameter 2 in, 6.5 mm screw hole: an openable rubber-lined loop with the friction set by the screw. Also: pegboard hooks, 2 in, 50 pack, $13.99, 344 ratings, "500+ bought" (search card).

## Positioners with a software interface (ordinary arms, mounts, cameras, hexapod)

**Sky-Watcher AZ-GTi alt-az GoTo mount** (product page)
- Amazon, https://www.amazon.com/dp/B07F9WF45J, $525.00, "Tomorrow", "Only 11 left in stock", 117 ratings, Prime icon. Listing: "11-pound payload capacity", Wi-Fi, app controlled, "Freedom Find dual encoders ... manual slewing without losing alignment", 8.6 lb.
- Search summaries (unchecked): 2,073,600 counts per revolution on the motor axes (0.625 arcsecond); auxiliary encoders 1,068 counts per revolution; Wi-Fi on UDP port 11880 with an open SynScan command set, a pure-Python driver and an INDI driver. Backlash and periodic error are not on the listing.
- Sky-Watcher Star Adventurer GTi head kit (product page): https://www.amazon.com/dp/B0BCCL38JQ, $579.00, "Tomorrow", 85 ratings, Prime icon; item weight 15.18 lb; payload not read. [borrowed-17]

**PTZ cameras** (product pages)
- NexiGo conference-room PTZ, 10x, USB: https://www.amazon.com/dp/B0DQCFX9WN, $242.99, ships from Amazon (delivery "Today 5 PM - 10 PM"), 5,521 ratings, Prime icon. "Pan rotation of -170 to +170 degrees, tilt range -30 to +90", 10 presets by IR remote.
- TONGVEO PTZ, 20x, HDMI and USB: https://www.amazon.com/dp/B0C2Q2HV8Q, $299.00, "Tomorrow", 359 ratings, Prime icon. "Up to 350 degrees pan and 180 degrees tilt", 255 presets, AI tracking.
- The control protocol (VISCA, ONVIF, UVC) is not on either listing: unchecked. Also on search cards: OBSBOT Tail Air ($474 to $510, 192 ratings), PTZOptics (several, $1,349 to $2,699, few ratings), Jennov PoE PTZ ($179.97, 59 ratings).

**Desktop arms** (product pages and search cards)
- wlkata Mirobot professional kit: https://www.amazon.com/dp/B094FRPJ16, $2,050.00, "FREE delivery Sunday, October 4 for Prime members", "Only 2 left in stock", 5 ratings. Search summary: payload 0.25 kg standard (0.4 kg maximum), reach 315 mm, repeatability 0.2 mm; the MiroMAX models 1 kg, 450 mm, +-0.05 mm (maker pages, not Amazon listings).
- reBot B601-DM assembled arm kit (LeRobot SO-ARM101 class, Python SDK, ROS): https://www.amazon.com/dp/B0H2TWVFSW, $1,899.00, "Tomorrow", Prime icon. SO-ARM101 kit (Hiwonder), search card: $459.99, 4 ratings, "50+ bought". Search summary: payload 0.5 kg; joint servos 12 bit (0.088 degree per count, 0.4 mm at 250 mm).
- Not Amazon listings, maker or reseller pages found by search: uFactory Lite 6 (0.6 kg payload, 440 mm reach, +-0.5 mm, $3,299 at a reseller) and Fairino FR3 (3 kg, 622 mm, +-0.02 mm, $6,799 in the US, full software access included, per reseller pages). Neither was ordered or contacted; no lead time was observed.

**Hexapod for optics and laser alignment**: Physik Instrumente H-811 miniature hexapod; search summary of the maker's pages: +-17 mm and +-21 degrees, position and centre of rotation defined in software, a free simulation tool. Priced by quote (not observed). LinuxCNC ships generic hexapod kinematics (genhexkins), per its repository. Hangprinter (RepRapFirmware kinematics with spool build-up and flex compensation for cable robots), per its documentation via search. [borrowed-13, borrowed-16]

## Haptic knob references (search results, not Amazon listings)

- SmartKnob: an open-source haptic input knob with software-defined endstops and virtual detents (a BLDC gimbal motor with a hollow shaft and a magnetic encoder; nearly every off-the-shelf gimbal motor tested cogs moderately to severely). GitHub: scottbez1/smartknob. SimpleFOC documents haptic and steer-by-wire examples (docs.simplefoc.com/haptics_examples). A 2804 motor with an AS5600 encoder is listed by DFRobot and Makerbase as 0.087 degree accuracy; no torque figure was found. The Prime kit found in wave 1 (2804 hollow-shaft motor with AS5600 and SimpleFOC driver, $34.88, 16 ratings, "50+ bought", ASIN B0FXKN9YMJ) is the parts route. [borrowed-19]

## What was not sourced

- A hollow-shaft rotary joint or a through-hole ball for the fibre at the pivot (borrowed-15 round 4), a fibre bend restrictor, an eddy-current damper, and any load cell better than the HX711 set already in `sourcing/freedom.md`.
- The mass of the mini linear rail with motor (borrowed-14 uses 0.3 kg each as an illustrative number; the listing states no weight) and the mass of any fluid head.
- Drag or damping values for any fluid head; rated torques for any mount or arm; backlash of any rod end or telescope mount.
