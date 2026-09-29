# Sourcing requests — force-and-form

These are Amazon candidates for the coordinator's Prime-confirmation pass in
Derek's signed-in Chrome.
- **Nothing here was fetched from amazon.com.** Where an ASIN appears, it
  showed up in a general web-search result and was not opened.
- **Non-Amazon evidence** gathered on 2026-09-28 is given where it exists, so
  that each route stands even if no Prime listing does.
- **Items already on the context list** ([`../../context/sourcing-requests.md`](../../context/sourcing-requests.md))
  are referenced, not repeated: the OTP side-feed XH applicator, the JST
  WC-110, the Engineer PA-09, the 50 kg load cell with HX711, and the crimp
  height micrometer.

| # | Item | Idea(s) | Capability that matters | Search terms | Non-Amazon evidence (2026-09-28) |
|---|---|---|---|---|---|
| 1 | iCrimp / IWISS SN-2549 ratcheting crimper, a second unit | f1, f4 | The same XH nest Derek uses today; replaceable jaws | `iCrimp SN-2549`, `IWISS SN-2549 ratcheting crimper` | $20.99 at icrimptools.com; wire-EDM jaws |
| 2 | SN-2549 replacement jaw set, jaws only | f3 (die route a) | The XH jaw pair on its own, to bolt into a linear die set | `IWISS SN-2549 replacement jaws`, `SN series crimping pliers jaws`. A brand page, amazon.com/clp/B0C3XFJQR3 ("Crimping tool pliers jaws SN-48B SN-02C …"), appeared in search | $9.99 per jaw set at icrimptools.com; two screws, 2.5 mm hex |
| 3 | 12 V linear actuator, 300–1,500 N, ≥50 mm stroke, potentiometer feedback | f1, f2b | Thrust ≥300 N held at low speed; position feedback. For f2b a lower rating (300–500 N) is wanted so it cannot crush the stop | `linear actuator 1500N 50mm potentiometer feedback 12V`, `12V linear actuator position feedback 500N`. ASINs seen in search: B0FLCBKKCH, B07N3SDHXQ, B0C2VL6977 | Progressive Automations PA-14P (pot feedback); price not observed |
| 4 | Button (spoke) compression load cell, 500 kg–1 t | f2, f3, f4 | 5–10 kN full scale; flat button or spoke form under an anvil; mV/V output for an HX711 | `button load cell 1000kg`, `miniature compression load cell 500kg`, `spoke load cell 1t`. A FEGIANCHE button 500/1000 kg brand page (amazon.com/clp/B0DGCKFW94) appeared in search | ATO miniature tension/compression cells to 500 kg, $172.49 (a different, threaded form) |
| 5 | Compression load cell, 5 t | f5 | ~50 kN full scale under a cassette; tolerates the shop press being watched | `5 ton compression load cell`, `50kN button load cell` | — |
| 6 | NEMA 23 stepper with NMRV030 30:1 worm gearbox | f2 | Self-locking; ≥10 N·m output; NEMA 23 input; hollow output with torque arm | `STEPPERONLINE NMRV030 worm gearbox Nema 23 30:1`. ASINs seen in search: B09WYFZYSJ (50:1), B09WCZ947T (5:1) | StepperOnline 23HS30-2804S-RVS30-G30, C$76.69, 200 in stock, ships in 24 h, 20 N·m permissible, 65 % efficiency |
| 7 | Arbor press, 1 t, and a 2–3 t press with ≥175 mm maximum opening | f2b, f5 | Maximum opening height, which decides whether a mini-applicator fits; ram size; leverage | `arbor press 1 ton`, `arbor press 3 ton max height`. ASINs seen in search: B00NOHYTPI, B006ZBCCWC | Harbor Freight Central Machinery #59766: $79.99, 20:1, 2,000 lb, 5-1/2 in maximum height (too short for an applicator) |
| 8 | Digital indicator, 0.001 mm resolution, with a data output | f3, f4 | 0.001 mm resolution; data port (USB, or a documented serial or SPC-like protocol) an ESP32 can read; 10–12.7 mm travel | `digital indicator 0.001mm data output`, `0.001mm electronic indicator USB` | Mitutoyo ID-C with SPC output: $451–668 at gauge dealers. TouchDRO reads Mitutoyo SPC and iGaging/Shahe on an ESP32 |
| 9 | AS5600 magnetic angle sensor board | f2 | 12-bit crank angle over I²C | `AS5600 magnetic encoder module` | — |
| 10 | NEMA 17 stepper with integrated lead screw, 2 mm lead | f3, f4 | ~300 N thrust at a 2 mm lead; 50–100 mm screw | `nema 17 lead screw stepper T8 2mm lead`, `nema17 linear stepper lead screw 100mm` | — |
| 11 | High-torque digital servo, 25–60 kg·cm | f3 (knee option), pawl, pilot pin and shear levers | Torque at stall; metal gears | `60kg servo digital metal gear`, `DS3225 servo` | — |
| 12 | Desktop CNC frame kit ("3018" class) as an XYZ gantry | f4 | XYZ travel ≥150 × 100 × 40 mm; lead-screw axes; stiff enough to position ±0.1 mm | `3018 CNC router kit`, `Genmitsu 3018` | — |
| 13 | Ground shaft Ø10 h6 with flanged bronze bushings, or die-set guide post and bushing sets | f3, f4, f5 | Shaft h6; bushing clearance ≤0.02 mm | `10mm h6 linear shaft`, `oilite bronze flange bushing 10mm`, `die set guide post bushing` | Misumi sells ball guide-post sets; price not observed |
| 14 | Linear rail HGR15 with carriage | f2 (ram guide) | Preloaded carriage; 100–150 mm rail | `HGR15 linear rail HGH15CA` | — |
| 15 | Pillow-block bearings, 15–20 mm bore | f2 (crankshaft) | Carries 3 kN at 2 rpm | `pillow block bearing 15mm`, `UCP202 pillow block` | — |
| 16 | Die springs, 10–16 mm OD assortment | f5 | Holds the upper shoe open; low force | `die spring assortment 10mm` | — |
| 17 | Air cylinder, 32 mm bore, with a 24 V 5/2 solenoid valve and flow controls | f3 (drive option) | ~500 N at 90 psi; meter-out flow control for a slow stroke | `SC32 air cylinder 25 stroke`, `5/2 solenoid valve 24V 1/4`, `pneumatic flow control valve 1/4` | — |
| 18 | Hardened dowel pins, 6 mm | f3, f4 (knee pins) | Hardened and ground | `6mm dowel pins hardened` | — |
| 19 | Small USB endoscope-style camera | f4 (head camera) | Close focus at 10–30 mm; UVC | `USB endoscope camera close focus UVC` | The ELP 16MP UVC camera is on hand for fixed views [repo] |

## Added in wave 2

| # | Item | Idea(s) | Capability that matters | Search terms | Non-Amazon evidence (2026-09-28) |
|---|---|---|---|---|---|
| 20 | OTP-style "XH2.54" crimping knife set (conductor and insulation crimpers, anvils) sold without the applicator | f3 route d, f4, f6, f7 | Separate conductor and insulation blades; which XH contact it is tooled for; blade dimensions and mounting | `XH2.54 crimping knife applicator blade`, `OTP applicator crimper anvil XH`, `terminal applicator knife set 2.5mm` | Listing titles on eBay (376757376428) and AliExpress (3256803331644772) via terminal-supply; prices not read. An OTP-standard applicator's tooling pack is 19 mm wide with CH/IH wedge adjustment [crimpapplicator.com KS-EM40R] |
| 21 | HSS parting blade, 1/16 in (1.6 mm) wide, T-type | f7 (anvil blades) | Hardened, ground width near 1.59 mm at the top edge; flat top edge | `HSS parting blade 1/16`, `cut off blade high speed steel 1/16 x 1/2` | — |
| 22 | Precision ground O1 flat stock, 1/16 in (1.5875 mm) thick, or 1.5 mm gauge plate | f7 (anvils stood on edge), f5b (gang anvil block) | Thickness tolerance about ±0.0005 in; hardenable | `O1 ground flat stock 1/16`, `gauge plate 1.5mm O1` | — |
| 23 | Feeler gauge set, individual leaves 0.2–0.4 mm | f1, f3, f6 (neck blade), hand-tool-as-press a1 | Hardened spring steel of ground thickness, cut to a blade | `feeler gauge set metric blades` | — |
| 24 | Disc springs (Belleville washers) 10–16 mm OD | f7 (pusher preload so the cartridge's stop takes the surplus) | Stackable to ~3–4 kN at a few tenths of a mm | `belleville disc spring washer assortment` | — |
| 25 | LED backlight / light pad, small | f6 (silhouette of the insulation crimp), sees-and-learns v1/v5 | Even white backlight a few cm across | `LED light pad A5`, `LED backlight panel 5V small` | — |
| 26 | Hardened dowel pins 2 mm | f6 (bend pin) | Smooth, hard pin to bend the conductor over | `2mm dowel pin hardened` | — |
| 27 | Miniature two-post die set | f7 (cartridge body), f5b | Two guide posts with bushings, small footprint | `mini die set two post`, `small punch die set guide post` | Misumi sells guide-post sets; price not observed |

Non-Amazon routes seen in wave 2: SendCutSend laser-cuts mild steel, 4130,
AR500 (3.02–12.7 mm), 1095 high-carbon (3.18 and 4.75 mm, supplied annealed,
hardens after cutting to Rc 65) and CPM MagnaCut (3.94 mm, 60–63 HRC after heat
treatment), ±0.005 in, 2–4 days, instant online quote; no heat-treat service
listed [source: sendcutsend.com materials pages, 2026-09-28].

## Wave 3

Items for the combinations in
[`../../exchange/force-and-form--on--procedure-is-the-machine-w3.md`](../../exchange/force-and-form--on--procedure-is-the-machine-w3.md).
Rows already Prime-confirmed in [`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md)
are not repeated: music wire 0.025 in (tip comb), 1095 blue-tempered shim
(laminated fin), feeler gauges, NEMA 17 Tr8×2 steppers, 500 kg button load cell,
0.001 mm indicator, A5 light pad, MGN9 rail, CQRobot kit, header strips, and the
Greartisan 12 V self-locking worm gearmotor.

| # | Item | Idea(s) | Capability that matters | Search terms | Non-Amazon evidence (2026-09-28) |
|---|---|---|---|---|---|
| 28 | Precision ground O1 or A2 flat stock, 0.075 in (1.905 mm) thick × 1/2 in | FP1 (the fin's insulation step, paired with #22's 1/16 in or 1.5 mm for the conductor step), FP2 | Ground thickness ±0.0005 in class; hardenable; short lengths | `O1 ground flat stock .075`, `precision ground flat stock 0.075 x 1/2`, `A2 ground flat stock 5/64` | — |
| 29 | Heavy-series disc springs, 20–31.5 mm OD, rated 2–5 kN each (DIN 2093 class) | p5 as written (the preloaded stack), for comparison with a plain compliant rod | Rated load per disc stated; carbon spring steel, not the light stainless assortment already confirmed | `DIN 2093 disc spring 25mm`, `belleville spring heavy duty 31.5mm` | — |

Added in the final pass, for f9b, f10, f1 and f6 as they stand. Rows #21, #22,
#26 and #28 above did not appear in the Prime table and remain unconfirmed; #27
(two-post die set) had no Prime listing.

| # | Item | Idea(s) | Capability that matters | Search terms | Non-Amazon evidence (2026-09-28) |
|---|---|---|---|---|---|
| 30 | Data cable for the Clockwise DITR-0105 indicator (DTCR-01), or a 0.001 mm indicator with a USB output | f3, f6, f7, f9b, f10 (re-touch height) | Reads the Prime-confirmed DITR-0105's RS232 port on a Mac or ESP32; or USB HID/serial output directly | `Clockwise Tools DTCR-01`, `digital indicator 0.001mm USB output`, `digital indicator RS232 cable` | The DITR-0105 itself is Prime-confirmed at $52.99; its cable had no Prime listing |
| 31 | Mold ejector pins, 1.0–1.5 mm, hardened, straight | f9b (lifts the box out of the keyed nest), f5b (pockets) | Hardened, ground diameter; 50–100 mm long to cut down | `ejector pin 1mm`, `mold ejector pin set 1.0 1.5`, `core pin hardened 1.5mm` | — |
| 32 | 2 mm hardened pin or carbide rod for the bend-and-look pin | f6, f9b | Hard, smooth, 2.0 mm diameter; a pin gauge serves too (the Accusize set is Prime-confirmed but tops out at 1.52 mm) | `2mm carbide rod`, `2mm drill blank`, `2mm hardened steel pin` | — |
| 33 | Precision ground gauge plate or O1 flat stock, 1.5 mm and 0.075 in (restates #22 and #28 in other terms) | f7 anvils, f10's fin, f5b's anvil block | Ground thickness ±0.0005 in class; hardenable | `gauge plate 1.5mm ground`, `ground flat stock 1.5 mm tool steel`, `O1 precision ground flat stock` | — |
| 34 | Spring-loaded toggle or cam lever with an adjustable steel stop (for the tack comb's stop) | f9b, f9 (tack lever) | Repeatable end position; 0.1–0.7 kN; the POWERTEC 305CM push-pull clamp is already confirmed as the lever | `toggle clamp adjustable stop`, `cam lever clamp steel` | — |
