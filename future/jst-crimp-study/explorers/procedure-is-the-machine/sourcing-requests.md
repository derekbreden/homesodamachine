# Sourcing requests: procedure-is-the-machine

Amazon candidates for the coordinator's Prime-confirmation pass. No amazon.com
page was fetched and no Chrome tool was used. Items already on the context list
([`../../context/sourcing-requests.md`](../../context/sourcing-requests.md)) are
not repeated here, though these ideas use them:
- OTP XH side-feed applicator (for its anvil and punch);
- load cell with HX711;
- crimp-height micrometer;
- small vibratory bowl (loose-contact branch);
- JST WC-110.

Non-Amazon sources observed on 2026-09-28 are at the foot.

| Item | Idea(s) | Capability that matters | Search terms |
|---|---|---|---|
| Lazy-susan ball-bearing turntable, 300–400 mm (12–16 in) | p1b | Flat, low wobble under ~5 kg; mounting holes; full-circle rotation | `lazy susan bearing 12 inch aluminum`, `turntable bearing 16 inch heavy duty` |
| Hardened steel dowel pin assortment, 3–8 mm, h6/m6 | p1, p1b, p5 | Ground, hardened; lengths 10–30 mm; to press into printed nests as cassette locators | `dowel pin assortment hardened steel metric`, `304 stainless dowel pin kit 3mm 4mm 5mm 6mm` |
| Chrome steel balls, 6–8 mm, G25 or better | p1, p1b | For three-ball / V-groove (Maxwell) cassette mounts | `chrome steel bearing balls 6mm G25`, `8mm steel balls precision` |
| Neodymium disc magnets 10 × 3 mm | p1, p1b | Hold cassettes in nests; ~1–2 kg pull | `neodymium disc magnets 10x3mm` |
| Music wire / spring steel wire, 0.6–0.65 mm (0.025 in) | p1 comb | Straight lengths to press into printed comb blocks at 2.5 mm pitch | `music wire 0.025 inch`, `K&S music wire assortment` |
| NEMA 17 stepper with integrated T8 lead screw, 2 mm lead, 100–300 mm | p1 slides, p2, p3 guillotine and y slide | Fine lead (2 mm) for force and resolution; anti-backlash nut | `nema 17 lead screw stepper T8 2mm lead`, `nema17 linear actuator T8x2 anti backlash nut` |
| MGN9 or MGN12 linear rail with carriage, 150–300 mm | p1, p2, p3 | Low-play carriage for the cassette slide and tool slides | `MGN12H linear rail 300mm`, `MGN9 rail carriage 200mm` |
| NEMA 17 worm-gear stepper, 30:1 or 50:1 | p5 camshaft | Self-locking worm; output shaft ≥8 mm; rated output torque ≥3 N·m | `nema 17 worm gear stepper 30:1`, `worm gearbox stepper motor 50:1 nema17` |
| Needle roller bearings (e.g. HK1010, HK1210) and 608 bearings | p5 eccentric and followers | Dynamic rating ≥5 kN for the eccentric; followers light duty | `HK1010 needle bearing`, `608 bearing 10 pack` |
| Small 12 V push-pull solenoids, 5–10 mm stroke | p5 skip (optional), p2 turret detent | 12 V, a few newtons, holding type | `12V push pull solenoid 10mm stroke JF-0530B` |
| Spring ball plungers, M6–M8 | p1b carousel detent | Threaded body, adjustable preload | `spring plunger ball M8`, `ball plunger set M6 M8` |
| GT2 belt (open, 6 mm) and 20T pulleys, plus flat/timing belt for ribbon feed | p1b rim drive, p3/p3b belt feed | Long open belt for a rim drive; a pair of flat belts for the ribbon feed | `GT2 belt 10m 6mm 20T pulley`, `rubber flat belt feeder` |
| IR break-beam sensor pair or slotted optical switch | p3 tip stop, p4 funnel stop | 3–5 V logic, small emitter, beam ≤2 mm | `IR break beam sensor 3mm LED`, `slotted optical switch module` |
| Rotary encoder with measuring wheel (e.g. 600 P/R optical + 20 mm wheel) | p3 loom length | Wheel rides on ribbon; ≥100 counts per 10 mm | `600 p/r rotary encoder measuring wheel`, `optical encoder wheel length measurement` |
| Single-edge razor blades | p1 trim, p1b/p3 web splitter | Thin (0.2–0.25 mm), sharp, stack at 1.7 mm pitch | `single edge razor blades 100 pack` |
| Capsule slip ring, 6–12 circuits | p3, p3b | Alternative to Adafruit 736; ≥5 circuits; ≤2 A | `capsule slip ring 6 wire 12mm`, `slip ring 12 wire 2A` |
| LED ring light or dome light for a USB camera, 60–80 mm | p1, p1b, p4 inspection | Diffuse, even light on a crimp at 50–100 mm working distance | `LED ring light 60mm microscope`, `dome light machine vision small` |
| Microswitch assortment with roller levers | p1 cassette ID, p5 cam switches and end stop | Small (e.g. 12 × 6 mm), roller lever | `micro limit switch roller lever assortment` |

## Non-Amazon sources observed (2026-09-28)

| Item | Source | Price | Stock signal | Serves |
|---|---|---|---|---|
| Slip ring with flange, 22 mm, 6 × 26 AWG, 2 A, 300 rpm | [Adafruit 736](https://www.adafruit.com/product/736) | $14.95 (10+: $13.46) | In stock | p3, p3b |
| Pogo pins P75-H2, 1.0 mm body, crown head, 10 pack | [Adafruit 2429](https://www.adafruit.com/product/2429) | $4.95 | In stock | p3 test through the housing face |
| BTT SKR Pico V1.0, RP2040, 4 × TMC2209, Klipper | [biqu.equipment](https://biqu.equipment/products/btt-skr-pico-v1-0) | $39.85 (sale from $55.68) | In stock | every arrangement's motion control |
| NEMA 17 with 38 cm Tr8×8 lead screw, 1.7 A | [Pololu 2690](https://www.pololu.com/product/2690) | $158.78 | "Active and preferred", backorders allowed | slides (shows the class; Amazon is where these are cheap) |
| Dobot MG400 desktop arm, 4-DOF, ±0.05 mm repeatability, 500 g payload | [Pololu 5400](https://www.pololu.com/product/5400) | $3,495 | Backorders allowed | an alternative carrier for p1's cassettes (not developed) |
| 240 Series wiper DC gear motor, 40 N·m, 65:1 planetary | [AmEquipment](https://www.amequipment.com/shop/240-series-dc-gear-motor/) | $172.65 | Two-week lead time | p5 alternative drive (not self-locking as stated) |
| SXH-001T-P0.6 in 100 / 500 / 1,000 lots | Digi-Key via [xh-facts §6](../../context/xh-facts.md) | $0.047 / $0.042 / $0.040 | 3,100 / 2,500 / 5,000 | contacts on strip for every arrangement |

## Added in wave 2 (exchange on borrowed-machines)

Amazon, Prime to be confirmed. No amazon.com page was fetched.

| Item | Idea(s) | Capability that matters | Search terms |
|---|---|---|---|
| Disc springs (Belleville washers), DIN 2093, ~20–31.5 mm OD, stackable | over-travel stack in the rod of b1b's crank and p5's eccentric (exchange C1) | Stack preloadable to ~4 kN with ~0.3–0.5 mm travel above preload; hardened spring steel | `DIN 2093 disc spring 25mm`, `belleville washer assortment spring steel` |
| Compression springs, ~150–450 N rated, 10–20 mm free length | spring link between actuator and hand-tool handle (exchange, b2 Break 1) | Rate and preload settable with a nut; fits a clevis | `heavy compression spring 20mm od assortment`, `die spring 16mm` |
| DC motor H-bridge with current sense (BTS7960 class) | b2 actuator control, stall detection | ≥10 A, current-sense outputs readable by an ESP32 | `BTS7960 motor driver current sense` |
| 12 V linear actuator, ~500 N, ~15 mm/s, 50 mm, pot feedback | faster b2 cycle (exchange, b2 Break 3) | ≥ 1.5× the largest handle force; feedback pot | `linear actuator 500N 15mm/s feedback 50mm` |
| Polyimide (Kapton) tape, 25–50 µm | insulating the box face of the b2 blade electrode | Thin, adhesive, withstands pressure | `kapton tape 1 mil` |
| 455 nm diode laser module, 5–10 W optical, standalone with driver | in-pose scoring at a bench or spool clamp (exchange, b4 Break 3) | Fixed-focus or adjustable; TTL/PWM input; sold as a module, not a whole engraver | `10W laser module 455nm engraver head replacement`, `5.5W laser module TTL PWM` |
| Laser safety window acrylic/panel for 445–455 nm, OD4+ | enclosure for the station laser | Rated for 445–455 nm | `laser safety acrylic 450nm OD4` |
| Stainless shim stock, 0.2–0.3 mm | valley tines for picking one of touching split conductors (exchange, b1 Break 3) | Flat, cuttable, blunt-edged tines | `stainless shim stock 0.2mm assortment` |

## Added in wave 2 (p6, p1c, p4b, p5b, p7)

Amazon, Prime to be confirmed. No amazon.com page was fetched and no Chrome
tool was used. Items already listed above are not repeated: dowel pins, balls,
magnets, music wire, NEMA 17 T8 lead screw, MGN rails, worm stepper, needle and
608 bearings, solenoids, GT2 belt, IR break-beam, encoder wheel, razor blades,
slip ring, ring light, microswitches, disc springs, compression springs,
stainless shim.

| Item | Idea(s) | Capability that matters | Search terms |
|---|---|---|---|
| ESP32 dev board (DevKitC class), 2–3 pack | p6 stage-0 test board; p4b; p5b stepper and load cell | ≥20 GPIO for a 9-post header plus LEDs; USB serial to the Mac | `ESP32 DevKitC 38 pin`, `ESP32-WROOM-32 development board 3 pack` |
| JST XH 2.54 mm male header, straight THT, 4/5/6/7/9 pin (B4B–B9B-XH-A or compatible) | p6 test board; p4b insertion nest; p1 bench C | Genuine B*B-XH-A preferred; a clone must mate the kit housings | `JST XH 2.54 male header straight 9 pin`, `B9B-XH-A header` |
| 2020 aluminium extrusion, 1 m, with T-nuts and end caps | p6 length rail and stage-4 puller | Straight to ±0.5 mm over 700 mm; takes printed pegs and a GT2 carriage | `2020 aluminum extrusion 1000mm t slot`, `2020 t nut m4 100 pcs` |
| 40-pin male pin headers, 2.54 mm, 0.64 mm square | p6 stage-2 and p1c post revolver; p5b post wheel | Square 0.64 mm posts, gold or tin; to cut into single posts | `2.54mm male pin header 40 pin breakable 0.64` |
| Momentary foot switch (pedal) | p6 stage 1; p4b | Momentary, cable with bare ends, low-voltage contact | `momentary foot pedal switch` |
| Metal-gear micro servo (MG90S) and standard servo (MG996R) | lift finger (p1c, p6), clamps and revolvers (p4b), post wheel (p6) | Metal gears; MG996R ~1 N·m for the lift finger | `MG90S metal gear servo 4 pack`, `MG996R servo` |
| LED backlight panel, small (≤100 × 100 mm), 5–12 V | camera silhouette of bare strands (p1c, p6 stage 2, p7) | Even diffuse white; small enough to sit under a station | `LED backlight panel 5V small`, `LED light pad A6` |
| Spring steel feeler gauge set with 0.30 mm leaves | flap blade in the contact's neck (p1c, p4b, p5b, p6) | Hardened leaves 0.25–0.35 mm; cuttable to a 2–3 mm blade | `feeler gauge set 0.02-1.00mm stainless` |
| Cam follower / track roller bearing, 16 mm OD | p5b squeeze-lobe follower | Needle or ball track roller on a stud; ≥1 kN dynamic rating | `cam follower bearing 16mm KR16`, `track roller bearing 16mm` |
| NEMA 17 stepper with 50:1 worm gearbox | p5b shaft | Self-locking; ≥4 N·m output; 8–10 mm output shaft | `nema 17 worm gear stepper 50:1` |
| Precision ground steel flat stock, 3–6 mm, small | p7 blade stops and the plate under the channel floor | Ground flat to ~0.01 mm; drillable on the WEN | `precision ground flat stock 1/8 inch O1`, `ground steel plate small` |

The spool rewind in p6 uses a tool already on the bench (the HOTO electric screwdriver or the drill press chuck turning a printed hub adapter); nothing is bought for it.

## Wave 3

Amazon, Prime to be confirmed. No amazon.com page was fetched and no Chrome
tool was used. Rows already confirmed in
[`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md) are cited
there and not repeated. The first four rows were requested earlier and do not
appear in that file, neither confirmed nor as "no Prime listing found".

| Item | Idea(s) | Capability that matters | Search terms |
|---|---|---|---|
| ESP32 dev board (DevKitC class), 2–3 pack | p6 test board; p4b; p5c controller | ≥20 GPIO for a 9-post header plus LEDs; USB serial to the Mac | `ESP32 DevKitC 38 pin`, `ESP32-WROOM-32 development board 3 pack` |
| 2020 aluminium extrusion, 1 m, with T-nuts | p6 length rail and puller; p3 | Straight to ±0.5 mm over 700 mm; takes printed pegs and a GT2 carriage | `2020 aluminum extrusion 1000mm t slot`, `2020 t nut m4 100 pcs` |
| Cam follower / track roller on a stud, 16 mm OD | p5b squeeze lobe; p5c knee lobe | Needle or ball track roller, ≥1 kN dynamic rating | `cam follower bearing 16mm KR16`, `track roller bearing 16mm stud` |
| Precision ground flat stock (gauge plate), 1/16 in (1.59 mm) and 5/64–3/32 in, O1 or A2, short lengths | p1d and p5c fin; p1 and p5 B-drop fin; p7 blade stops | Ground to ±0.013 mm in thickness; hardenable; the fin is its thickness stood on edge (1.45 mm and 1.88 mm steps, lapped or stoned from the nearest size) | `precision ground flat stock O1 1/16 inch`, `gauge plate 1.5mm tool steel`, `ground flat stock 3/32 O1` |
| DIN 2093 disc springs, series A, 25 × 12.2 × 1.5 mm, heavy duty (not the light stainless assortment) | p5 optional rod spring | ~2.9 kN at 75 % of 0.55 mm travel; hardened spring steel; 2–4 pieces | `DIN 2093 disc spring 25x12.2x1.5`, `belleville spring 25mm heavy duty` |
| Die springs, 16–20 mm OD, medium or heavy load, 25–40 mm long | p5b spring link (~275 N preload) | Rate that reaches ~275–350 N within its travel; ground ends | `die spring 20mm OD heavy load`, `die spring 16mm medium load` |
| Knurled or serrated steel strip, 3–6 mm wide, or small serrated gripper pads | p7 slug pads | Fine teeth or diamond knurl that bite a silicone jacket without squeezing it hard | `knurled steel strip`, `serrated jaw pads small`, `diamond knurled flat bar` |
| Hardened steel pins, 3–4 mm diameter, ground (h6), 10–20 mm long | p1d and p5c knee links | Hardened and ground; press-fit into drilled plate | `hardened dowel pin 3mm x 16mm`, `ground dowel pins 4mm hardened` |
