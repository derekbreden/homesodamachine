# Sourcing — machine-that-learns

Observed 2026-09-28 in Derek's Chrome (delivery to Lincoln 68520). Every Amazon
entry below was opened as a product page and showed a Prime badge unless marked
"search level" (Prime-filtered search result only, product page not opened).
Review counts and "bought" lines are per listing and are thin evidence on their
own; where a whole commodity family matters more than one listing, the note
says so.

## Motion

- **SFU1605 ball-screw stage, 100 mm stroke, with NEMA 17** — the X (and later Y/Z) axis in A and B; the knob-first axis unit.
  - Source: https://www.amazon.com/dp/B0BLVNDSZZ (Yeebyee) · Observed: 2026-09-28 · Price: $69.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Today 5 PM - 10 PM"; "Only 11 left in stock"
  - Volume/interchangeability evidence: 1 review on this ASIN, but the same stage (SFU1605, 5 mm lead, square rails, 265 mm long, NEMA 17) appears as at least six other Prime listings at $54–74 (B09NVYST2Z, B085SXDS2B, B0BP6WT5QK, B085STFFM7, B09GY88PZ7, B0FD2V6B1H) — a commodity DIY-CNC part sold by many vendors.
  - Observation vs estimate: price, stock, delivery, listing specs (±0.03 mm repeatability, 30 kg horizontal / 15 kg vertical) observed; real repeatability and carriage tilt stiffness not verified.

- **Double-rail SFU1605 cross-slide stage, 100 mm stroke, 150 mm wide (RATTMMOTOR ZBX150)** — the stage that carries the whole rotator in A.
  - Source: https://www.amazon.com/dp/B09PTN7C2D · Observed: 2026-09-28 · Price: $130.80 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "Only 15 left in stock"
  - Volume/interchangeability evidence: 15 reviews; the same class (two 20 mm square rails + SFU1605) is sold under several names.
  - Observation vs estimate: listing claims 120 kg horizontal, 50 kg vertical, motor mount but no motor; stated accuracy 0.03 mm. Height of the stage not recorded (sketches assume ~65 mm).

- **Manual SFU1605 stage with handwheel revolution counter and lock (YRJM)** — the no-motor X/Z for the watch-first nest; the counter is a readable manual DRO; the handwheel end can later take a motor.
  - Source: https://www.amazon.com/dp/B0H4YSV1VH · Observed: 2026-09-28 · Price: $85.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Friday, October 2"; "Only 4 left in stock"
  - Volume/interchangeability evidence: new listing, no reviews shown; weak. The motorised equivalents above are the fallback.
  - Observation vs estimate: listing claims ±0.03 mm repeatability, 50 kg horizontal / 30 kg vertical, locking handle.

- **NEMA 17 with integrated 100 mm Tr8×8 lead screw** — hexapod leg (C) and belt-linked Z screws (A).
  - Source: https://www.amazon.com/dp/B07YQRCHW7 · Observed: 2026-09-28 · Price: $22.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Wednesday, September 30"; "Only 3 left in stock"
  - Volume/interchangeability evidence: 9 reviews here; the same part (42 mm, Tr8×8, brass nut, "Prusa Z axis") appears as several other Prime listings (B0FHHY3JKX $23.19, B0FHHVJPHD $20.87, 5-pack B0FHHWSKNP $62.79) — a standard 3D-printer Z motor.
  - Observation vs estimate: listing specs observed; axial play of the motor bearings (matters for C) is not stated.

- **Dual-shaft NEMA 17 (STEPPERONLINE 1.68 A, 45 N·cm)** — every knob-first axis in B: motor on one shaft end, hand knob on the other.
  - Source: https://www.amazon.com/dp/B00W98YK5M · Observed: 2026-09-28 · Price: $20.38 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "Only 20 left in stock"
  - Volume/interchangeability evidence: 18 reviews on this ASIN; STEPPERONLINE's single-shaft NEMA 17 (B00PNEQKC0, $14.99) shows "300+ bought in past month" in search; dual-shaft NEMA 17 is sold by several brands (search level).
  - Observation vs estimate: observed.

- **MKS SERVO42D closed-loop NEMA 17 driver, RS485/Modbus** — mounts on the back of a NEMA 17; reads shaft angle with a magnetic encoder, so a hand-turned knob is still recorded; takes step/dir or serial absolute-position commands (hexapod legs, knob-first axes).
  - Source: https://www.amazon.com/dp/B0CNG7T5ZJ · Observed: 2026-09-28 · Price: $25.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: 14 reviews here; weak alone. Same family in Prime search: CAN version B0CNG7ZKSZ $25.99, SERVO42C B09MTXGVMZ $37.69, BIGTREETECH S42C B09LHFS2HF $39.99, NEMA 23 SERVO57C/57D $26–29 — two brands, several generations.
  - Observation vs estimate: listing bullets (pulse or RS485 Modbus-RTU, absolute/relative position modes, limit-switch homing) observed. Whether the encoder can be read with the coils disabled while the knob is turned is **not verified** — the knob-first idea depends on it.

- **BIGTREETECH Octopus Pro V1.1 (H723), 8 stepper sockets, Klipper** — one controller for X/Y/Z/arc/roll and, through step/dir, the rotator's existing DM542T.
  - Source: https://www.amazon.com/dp/B0BM3BFZ35 · Observed: 2026-09-28 · Price: $64.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: "50+ bought in past month", 42 reviews; Octopus V1.1 variants also on Prime ($53.99); BTT Pi host board $43.99 (search level).
  - Observation vs estimate: observed. Klipper/Moonraker as the control API is from my knowledge of that ecosystem, not verified here.

- **PGFUN harmonic drive with NEMA 17, 30:1, 2 arcmin** — an option for a zero-backlash arc/roll/trunnion drive.
  - Source: https://www.amazon.com/dp/B0F8ZTL7GF · Observed: 2026-09-28 · Price: $109.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Today"; "Only 1 left in stock"
  - Volume/interchangeability evidence: 2 reviews; weak. Other Prime harmonic-drive listings at $99.99–139.99 (B0CMZGCX3Z, B0GF87W2KK, B0BQ3S5V6J) and a STEPPERONLINE 100:1 planetary B0BPGP3B5N at $45 (search level). Printed worm + sector remains the default.
  - Observation vs estimate: observed.

- **PGN UCP205-16 pillow blocks (2-pack)** — trunnion bearings for A's tilt branch.
  - Source: https://www.amazon.com/dp/B07MWGF35D · Observed: 2026-09-28 · Price: $20.25 · Prime: yes
  - Stock/delivery signal: "FREE delivery Today 5 PM - 10 PM on qualifying orders over $25"; "In Stock"
  - Volume/interchangeability evidence: "100+ bought in past month", 1,191 reviews; UCP205 is a universal standard housing.
  - Observation vs estimate: observed. Self-aligning inserts have radial play that a precision trunnion would have to preload; not assessed.

- **uxcell SI5T/K (PHSA5) M5 female rod ends, 4-pack** — hexapod joints.
  - Source: https://www.amazon.com/dp/B0C7MZMYMF · Observed: 2026-09-28 · Price: $9.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: 66 reviews; SI5T/K is a standard size sold by several brands (two more Prime listings at $6.99–8.99, search level).
  - Observation vs estimate: observed; joint play not stated.

- **MGN12H 300 mm rails** — search level only: at least eight Prime listings at $17.59–49.35. A standard 3D-printer rail; not opened.

- **V-groove POM wheels with eccentric spacers** — arc carriage in B. Search level: several Prime kits at $9.99–18.99, one "50+ bought in past month" (B08B4JDB67). Standard Creality/V-slot wheel.

- **12 mm G25 chrome-steel balls** — the three balls of the kinematic seat on the gun shell. Search level: uxcell 30 pc B0FDW258DF $7.69; 50 pc B0CRGGR7CD $11.99.

## Angles by hand

- **K&F Concept GD-3W PRO 3-way geared tripod head** — B2 branch: three worm-driven, graduated, lockable rotations in one purchased part, 6 kg rated.
  - Source: https://www.amazon.com/dp/B0F6YLMRCY · Observed: 2026-09-28 · Price: $159.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: "100+ bought in past month", 81 reviews. Other Prime geared heads: NEEWER TH15 $146.99 ("50+ bought"), K&F B0BTD7K2W8 $188.98 ("50+"), Benro GD3WH $249.94, Manfrotto MHXPRO-3WG $219.00 — a mature photographic category.
  - Observation vs estimate: listing claims 0.1° micro-adjustment and three angle scales; stiffness under a cable pull and backlash in the worms are unknown.

## Observation

- **ELP 16MP autofocus USB camera, IMX298, 68° lens** — the joint camera (one on hand; a second as the station camera).
  - Source: https://www.amazon.com/dp/B0BX6DSQ6C · Observed: 2026-09-28 · Price: $72.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Wednesday, September 30"; "Only 5 left in stock"
  - Volume/interchangeability evidence: 20 reviews; already acquired once (ledger). ELP sells many UVC variants; any UVC camera fits the same software.
  - Observation vs estimate: observed.

- **Tiffen 52 mm Red 25 filter** — in front of the joint camera (in a printed hood) to pass the 630–670 nm reference beam and suppress room light; the camera's own IR-cut filter supplies the upper edge.
  - Source: https://www.amazon.com/dp/B00004ZCA0 · Observed: 2026-09-28 · Price: $16.95 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: "50+ bought in past month", 568 reviews.
  - Observation vs estimate: observed. Narrow 650 nm bandpass filters did not show up usefully under Prime (only IR-cut and 850/940 nm parts); a Thorlabs/Edmund 650 nm bandpass is the step up, not checked.

- **Oxlasers 650 nm adjustable cross-line module** — optional structured-light stripe across the joint (seam profile) independent of the gun's own reference beam.
  - Source: https://www.amazon.com/dp/B0D8DVR3FQ · Observed: 2026-09-28 · Price: $39.00 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: "50+ bought in past month", 26 reviews; several other Prime 650 nm line modules at $9.95–32.88 (search level).
  - Observation vs estimate: observed.

- **HiLetgo AS5600 magnetic angle encoder, 2-pack with magnets** — reads hand-set angles (geared-head knobs, pose-block hinge, nest micrometers) into the log.
  - Source: https://www.amazon.com/dp/B09KGWC1PT · Observed: 2026-09-28 · Price: $7.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Today 5 PM - 10 PM on qualifying orders over $25"; "In Stock"
  - Volume/interchangeability evidence: "50+ bought in past month"; other Prime AS5600 listings with "100+ bought" (B0CM3C8KFT) and "50+" (B097QNG1CN) at search level.
  - Observation vs estimate: observed. 12-bit = 0.09° per count on the shaft it reads.

## Already on hand (ledger), used as-is

- Revopoint MINI 2 scanner and spray (shell from a scan); two H2C printers; ESP32-DevKitC boards; NEMA 23 + DM542T in the rotator; Neoteck test indicator; Hgnova D18 × 2 mm protective lenses (15-pack) — a spare makes a sacrificial spatter window for the joint camera.

## Added in wave 2

- **iGaging Absolute Origin 0–6 in digital caliper with SPC/USB output port** — the scale of the D-s stylus (exchange with carry-and-locate): a commodity linear encoder at 0.01 mm whose data port can be read by a microcontroller.
  - Source: https://www.amazon.com/dp/B00INL0BTS · Observed: 2026-09-28 · Price: $47.77 · Prime: yes
  - Stock/delivery signal: "FREE delivery Today 5 PM - 10 PM"; "In Stock"
  - Volume/interchangeability evidence: "900+ bought in past month", 1,886 reviews; sister listings B00KDUD67G ("300+"), 0–8 in B00K3PZVKG ("50+").
  - Observation vs estimate: listing observed. Reading the SPC clock/data port with an ESP32 is a widely described hack, not verified here; update rate not known.

- **FoMaKo K20UH 4K PTZ camera, 20× optical zoom, USB 3.0/HDMI/NDI** — representative of Derek's "PTZ cameras controllable by software": zoom lets the camera sit ~1 m from the spatter and still see the corner at ~15–20 µm per pixel (estimate from a 1/2.8 in sensor and a 20× lens; minimum focus distance at full zoom not known).
  - Source: https://www.amazon.com/dp/B0DK1BXJWY · Observed: 2026-09-28 · Price: $449.00 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: "100+ bought in past month", 176 reviews; a crowded category (TONGVEO, Tenveo, PTZOptics 20× units at $299–1,349 in the same Prime search).
  - Observation vs estimate: listing observed (8.42 MP 1/2.8 in CMOS, 20× optical). Control protocol (VISCA/UVC PTZ) and close-focus behaviour not verified.

## Added in wave 3 (idea E, table-opening station)

- **Tr8×2 single-start lead screws, 300 mm, with brass nut** — the four shelf screws (workspace-as-structure's belt-linked layout) and the self-locking legs of C-p. Search level only (Prime-filtered results, product pages not opened): B07R38L317 $8.99, B08JLV1NF1 $11.99/2; anti-backlash T8×2 nuts B07T2N7FB7 $9.99/2. A standard 3D-printer Z part.
- **Closed-loop GT2 6 mm belt** — ties the four shelf screws to one motor. Search level only: 1100 mm closed loops, 5-pack $24.99 (B0CZDMMBB2); longer closed loops were scarce under Prime, so the post spacing may have to fit an available length, or the shelf gets four motors with Klipper's multi-Z levelling instead.
- Parts reused from other explorers' sourcing, not re-observed here: the RS232 0.01 mm digital indicator (workspace-as-structure, B09XN5FXTR, $23.99) as E-h2's plunger readout; carry-and-locate's QWORK balancer, V-rollers, MG90S servo; the Farwind 150 N gas strut and Tr8×2 integrated-screw NEMA 17 in C-p (carry-and-locate's exchange).

## Added in wave 4 (idea F, the wire path; cart-station exchange)

- **SwitchBot Bot button pusher (Bluetooth)** — presses the wire feeder's own Wire Feed / Wire Retract buttons for stick-out resets, with no wiring into the feeder (idea F). An MG90S servo finger on the ESP32 is the wired alternative.
  - Source: https://www.amazon.com/dp/B07B7NXV4R · Observed: 2026-09-28 · Price: $25.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Today 5 PM - 10 PM"; "In Stock"
  - Volume/interchangeability evidence: "700+ bought in past month", 28,482 reviews; Fingerbot-class pushers from MOES and others at $27.99–39.99 with "100+–200+ bought" (search level).
  - Observation vs estimate: listing observed. Whether its push force and stroke suit the feeder's buttons is unknown (the feeder's buttons have not been seen); host control over Bluetooth relies on open-source libraries, not verified.

- **Teslong 5 MP USB auto-focus endoscope** — the wire camera beside the gun's wire bracket (idea F): stick-out, tip aim and touch-off in the gun's own frame.
  - Source: https://www.amazon.com/dp/B07HVT2XZL · Observed: 2026-09-28 · Price: $49.99 · Prime: yes
  - Stock/delivery signal: "FREE delivery Tomorrow, September 29"; "In Stock"
  - Volume/interchangeability evidence: "50+ bought in past month", 388 reviews; fixed-focus 5.5 mm 1080p endoscopes at $19.99–26.98 with "100+" to "4K+ bought in past month" (search level).
  - Observation vs estimate: listing observed (auto-focus, USB). Probe diameter of this model, close-focus distance and UVC behaviour on the host not verified.

- **Wire straightener, 20-wheel stainless, 0.020–0.079 in** — reduces the cast of the 0.030 in ER316L before the conduit (idea F). Search level only: B0H8XK8C4C, $55.99 (Prime-filtered result, page not opened). Most Prime "wire straighteners" are 3-roller jewellery tools; industrial roller straighteners are the category to look in further.

- **100 k NTC thermistors (printer-standard)** — module and air temperatures for the cart-station drift model, read by the Octopus Pro's thermistor inputs. Not observed; a standard 3D-printer part.
