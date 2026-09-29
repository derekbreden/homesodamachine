# Sourcing requests — hand-tool-as-press

Amazon candidates for the coordinator's Prime-confirmation pass. No amazon.com
page was fetched. Where an ASIN appears, it came from general web search
results or from the repo's ledger, and was not opened. Items already in
[`../../context/sourcing-requests.md`](../../context/sourcing-requests.md)
(JST WC-110, Engineer PA-09, load cell + HX711, SO-101) are not repeated,
except where a different capability matters.

| Item | Idea | Capability that matters | Search terms / lead |
|---|---|---|---|
| iCrimp / IWISS SN-2549 ratcheting crimper (a machine copy) | a1, a2, a3 | Same SN frame as the bench tool; lower-jaw M4 screw; release lug on the pawl | `iCrimp SN-2549`. Derek's ledger ASIN B01N4L8QMW [repo `tools.md`]. Non-Amazon: icrimptools.com $20.99; TH3D $17.99 |
| SN-series replacement jaw set, "2549" profile | a4 (die pieces), spares for a1–a3 | Genuine SN-2549 profile; both die pieces; screws included | `SN-2549 replacement jaws`, `SN series replacement crimping jaw set 2549`. Leads from search: B0GXVSKMS7, B0GJ523YNW. Non-Amazon: icrimptools.com $4.99–9.99 |
| NEMA 17 external linear stepper, Tr8×2 lead screw, 48 mm stack | a1 pusher, a3 module, a5 | 2 mm lead (not 8 mm); external nut; ~0.4 N·m; 100–300 mm screw | `nema 17 external linear stepper Tr8x2`. Lead from search: B07GSR5Y43 (STEPPERONLINE) |
| 5840-31ZY worm gearmotor, 12 V, ~10 rpm | a1 winch branch, a4 eccentric drive | Self-locking worm; 8 mm D-shaft; 10 rpm variant (high ratio) | `5840-31ZY 12V 10rpm worm gear motor`. Leads: B0BCQK4RWZ, B0B7BRX2MS. Non-Amazon: nfpshop.com $18.50 |
| Bar or S-type load cell, 25–50 kg, with HX711 | a1 grip force | Range past ~250 N at the grip; M4/M5 mounting | `load cell 50kg bar HX711`, `S type load cell 50kg HX711` |
| Button compression load cell, 500 kg (5 kN) | a4 die force | ≤ ~20 mm diameter, compression button, 5 kN | `button load cell 500kg compression miniature`. Lead from search: B01M3UABJT |
| Disc spring (Belleville washer) assortment, ~20–25 mm OD, 1–1.25 mm thick | a4 overtravel stack | Spring steel; sizes stackable to ~3.5 kN preload | `belleville disc spring washer assortment 20mm`, `disc spring 25mm x 1.25` |
| 8 mm ground linear shafts (~100 mm) with LM8UU or bronze bushings | a4 ram guide | Hardened, ground 8 mm; bushing play small | `8mm linear rod 100mm LM8UU`, `8mm bronze bushing oilite` |
| 2.54 mm male pin header strip | a1 post option, a3 post column | Square 0.64 mm pins, pullable | `2.54mm male pin header strip 40 pin` |
| Spring steel shim / feeler gauge stock, 0.2–0.4 mm | a1 flap blade (all ideas) | Hardened spring steel; cuttable into a slotted blade | `feeler gauge stock 0.3mm spring steel`, `shim stock spring steel 0.3mm` |
| Hobby servos, 20–25 kg·cm, metal gear | a2 flap, fork, pin; a3 flap; cutter squeezer | Metal gear; standard size; 5–7 V | `25kg servo metal gear` |
| MGN12 linear rail + carriage, 150–250 mm, with GT2 belt kit | a2 carriage (purpose-built route) | Preloaded carriage; three axes' worth | `MGN12 linear rail 200mm carriage`, `GT2 belt pulley kit nema 17` |
| Open-frame diode-laser engraver frame (gantry over a fixed bed) | a3 gantry | Belt X–Y over a fixed work area; head payload ~0.5–1 kg; G-code controller | `laser engraver frame kit`, `diode laser engraver 400x400` (the laser itself is not used) |
| AS5600 magnetic angle sensor board | a4 shaft angle, optional a1 handle angle | I²C; magnet included | `AS5600 magnetic encoder module`. Non-Amazon: Adafruit STEMMA QT board (~€7.50 at Opencircuit) |
| Push-in PCB terminal block, 5–10 position (or Wago 221-415 per conductor, already in the BOM) | all: far-end electrode block | Accepts stripped 22 AWG; lever or push-in release | `push in terminal block 5 position pcb`, `wago 221-415` |
| Dyneema cord, ~1–2 mm | a1 winch branch | Low stretch; ≥ 1 kN break | `dyneema cord 1.5mm` |
| Digital hanging luggage scale, ~50 kg, 10 g resolution, with hook | a6 pull jig; grip-force measurement on the SN-2549 | Reads 20–40 N (2–4 kg) to ~0.1 N; peak hold | `digital luggage scale 50kg`, `hanging scale 110lb peak hold` |
| Polyimide (Kapton) tape, 25–50 µm, narrow roll | a1, a6 insulated blade | Thin, heat-proof, adheres to steel; 0.025–0.05 mm total thickness | `kapton tape 1/4 inch`, `polyimide tape 6mm` |
| Feeler gauge set with separate leaves down to 0.10 mm (or 0.10 mm shim roll) | a1, a6 blade; a6 pull plate (0.30 mm) | Hardened spring-steel leaves 0.10–0.30 mm, individually removable | `feeler gauge set 0.02-1.00mm 32 blade`, `0.1mm spring steel shim` |
| Spring steel strip ~1.0 mm × 10–12 mm (1095 or 65Mn) | a6 pull-limit leaf | Hardened spring temper; cut to 40 mm | `1095 spring steel strip 1mm`, `65Mn spring steel sheet 1mm` |
| 608 bearings (10-pack) | a6 treadle pulley (carries the AS5600 magnet) | Standard 8 × 22 × 7 | `608 bearing 10 pack` |
| Compression spring assortment | a6 treadle return and two-stage step | Light and medium rates, 6–12 mm OD | `compression spring assortment` |
| S-type load cell 50 kg with HX711 (already listed as "bar or S-type") | a6 cord line, a1 winch | Threaded ends for an in-line cord | `S type load cell 50kg HX711 M6` |
| 5 mm LEDs (amber, green) and an active buzzer | a6 far-end box | 3.3 V drive from an ESP32 | `5mm LED assortment`, `active buzzer 3.3V` |
| 20 kg bar load cell with HX711 | a2d housing press, a3 housing slide | 20 kg bar, M4/M5 holes | `20kg load cell HX711` |
| O1 or D2 ground flat stock, ~5 × 10 mm section | a4b lower arm | Hardenable tool steel, ground to size | `O1 ground flat stock 3/16 x 3/8`, `tool steel flat bar 5mm x 10mm` |

Non-Amazon sources, observed 2026-09-28:
- **Creality Ender-3 V3 SE**, $199 at store.creality.com. It is the a2
  secondhand-printer-frame route.
- **SparkFun TAL220 10 kg bar load cell**, $12.95, in stock. It covers the a2
  proof pull; a1's grip needs a larger range.
- **JLCPCB 304 stainless stencil**, from $3 (100 × 100 mm), "most stencil orders
  are shipped within 24 hours" [source: jlcpcb.com/pcb-stencil, fetched
  2026-09-28]. Thickness options were not listed on the page or on the
  capabilities page [assumption: 0.10–0.20 mm, the common SMT range]. It serves
  a6's keyhole, the a1/a6 blade blanks, a2c's pusher blade and a2d's squaring
  comb.
- **B*n*B-XH-A headers** for i5's nest and a2d's optional wired header:
  B4B-XH-A 171,802 at Newark, B9B-XH-A 44,226 at Digi-Key [source: findchips,
  via into-the-housing].

## Wave 3

Where the 2026-09-28 Prime pass left this explorer's earlier rows
([`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md)):
- **Confirmed on Prime and now cited in the idea files:** SN-2549 ($22.29,
  B01N4L8QMW); Engineer PA-09 ($38.99, B002AVVO7K); NEMA 17 Tr8×2 external nut
  ($27.78, B07TB7FPPP) and integrated anti-backlash ($27.99, B094CRRSRQ);
  Greartisan 40 kg·cm self-locking worm ($26.99, B07YBXB4N7); 500 kg button cell
  ($74.99, B0GZZRQC6Y); 8 mm case-hardened rods ($6.99, B09RVS4PXZ); AS5600
  ($7.99, B094F8H591); Dyneema ($17.95, B07BKQLFRB); Wago 221-415 ($28.00,
  B0107SYYGU); feeler set ($8.99, B08GLN7K1R); 1095 shim assortment ($53.39,
  B00065V062); DS3218MG servo ($14.99, B076CNKQX4); MGN12 rail ($20.49,
  B07ZVFFXQZ); LONGER Ray5 ($268.99, B0G13BBN9L); header strips ($7.99,
  B01MQ48T2V); DITR-0105 indicator ($52.99, B07888LX1R); NEMA 23 10:1 planetary
  ($48, B0BPGMZ5LM); iCrimp IWS-0723K with a 2549 die ($46.59, B09CP8RV94).
- **No Prime listing:** SN-2549 jaw set alone; spring steel strip 1.0 mm (the
  0.8 mm shim serves a6's leaf); heavy disc springs (only a light stainless
  assortment).
- **Not reached by the pass:** polyimide tape, digital luggage scale, 20 kg bar
  cell, LEDs and buzzer (generic).

| Item | Serves | Capability that matters | Search terms |
|---|---|---|---|
| Plug pin gauges 1.53–1.75 mm in 0.01 mm steps (or a 0.061–0.250 in set) | a6b (the snap's grip against the ribbon's measured jacket OD); change-the-question c6 | The Prime-confirmed Accusize set stops at 1.52 mm (0.060 in); a no-go pin has to sit ~0.05–0.08 mm under the measured jacket OD (1.6–1.8 mm) | `plug pin gauge set 0.061-0.250`, `pin gauge 1.6mm 1.65mm`, `minus pin gage set 0.061` |
| Light compression springs, ~1–3 N at 1–2 mm, 3–5 mm OD | a6b and a6c: the flag seat's sprung rear guide and front ledge | Soft enough that the punch seats the contact before the wings curl (tens of N); small enough to hide in a printed clip. The Prime $6.99 assortment (B0BVTDP29W) does not state wire sizes | `mini compression spring assortment 3mm OD`, `small compression springs 0.3mm wire` |
| Heavy-series disc springs (DIN 2093 class), 20–25 mm OD, ~1–1.25 mm thick, stackable to ~3.5 kN preload | a4, a4b, a4c, a4d: the force cap under the lower die | Spring steel, a load table per disc; the Prime Belleville row is light stainless with no load stated | `din 2093 disc spring 25mm`, `belleville spring heavy duty 20mm 1.25mm`, `disc spring washer 25x12.2x1.5` |
| RS232 data cable for a Clockwise DITR-0105 indicator (DTCR-01) or a USB SPC cable that fits it | a4, a4c: the re-touch reading into the station MCU | The cable is not on Prime; any cable that brings the indicator's reading to a serial port, or the camera reads the display | `clockwise tools dtcr-01`, `digital indicator rs232 usb cable spc` |
| Polyimide (Kapton) tape, 25–50 µm, 6–12 mm wide | a1, a6: the insulated blade's front face | Thin; adheres to spring steel; ≤ 0.05 mm total | `kapton tape 1/4 inch`, `polyimide tape 6mm` |
| Digital hanging luggage scale, 50 kg, peak hold | a6: the pull jig's simple form; grip force on the SN-2549 | Reads 20–40 N to ~0.1 N; peak hold | `digital luggage scale 50kg peak hold` |
| 20 kg bar load cell with HX711 | a4c and a6c: station T's forming-force cell under the nest (33–132 N); a2d's housing press | 20 kg range (the Prime 5 kg pair tops out at 49 N) | `20kg load cell HX711`, `bar load cell 20kg` |
