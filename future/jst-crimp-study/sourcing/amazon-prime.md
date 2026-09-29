# Amazon Prime listings for the study's Amazon candidates

Observed **2026-09-28** in Derek's signed-in Chrome. Delivery estimates are the
ones Amazon showed for the account's default address on that day (Mon Sep 28;
"next day" is Tue Sep 29). Searches used Amazon's Prime filter. Every listing
in a table's Listing and Link columns was opened, and had the Prime badge
beside the price on its own product page. A few further listings are named in
a Caveat cell and marked "(search result)": they carried the Prime badge in the
Prime-filtered results, but their product pages were not opened. Prices are for
the variant named, as shown that day.

**Volume signal** here means only what the page itself showed: the ratings
count, an "N+ bought in past month" line, the Amazon's Choice badge, and any
low-stock line ("only N left"). A brand name or a listing existing is not
counted. A listing is called **thin** when it has fewer than about 50 ratings
and no bought-in-past-month line.

This pass covers the rows in [`../context/sourcing-requests.md`](../context/sourcing-requests.md)
and every `explorers/*/sourcing-requests.md`, deduplicated. The "Serves" column
uses these explorer codes with each explorer's own idea ids:

| Code | Explorer |
|---|---|
| ctx | context prior-art pass (§ = [`prior-art.md`](../context/prior-art.md) section) |
| BM | [borrowed-machines](../explorers/borrowed-machines/summary.md) |
| CQ | [change-the-question](../explorers/change-the-question/summary.md) |
| FF | [force-and-form](../explorers/force-and-form/summary.md) |
| HT | [hand-tool-as-press](../explorers/hand-tool-as-press/summary.md) |
| IH | [into-the-housing](../explorers/into-the-housing/summary.md) |
| SL | [machine-that-sees-and-learns](../explorers/machine-that-sees-and-learns/summary.md) |
| PM | [procedure-is-the-machine](../explorers/procedure-is-the-machine/summary.md) |
| RP | [ribbon-as-pallet](../explorers/ribbon-as-pallet/summary.md) |
| TS | [terminal-supply](../explorers/terminal-supply/summary.md) |

"(ref)" means the explorer uses the item but pointed to another list for it.

## Crimp and press

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Terminal crimp press, 1.5–2 t, 110 V, OTP applicators | ctx §4; BM b1; RP (ref) | no Prime listing found on 2026-09-28 | | | | | | | |
| OTP side-feed applicator for XH chain contacts | ctx §3–4; BM b1, b1b, b3; FF f2 (ref); IH i1; PM p1 (ref); RP (ref); TS a1 (ref) | no Prime listing found on 2026-09-28 | | | | | | | |
| OTP XH crimper and anvil blade set | TS a2, a3b, a4, a4b, a5 | no Prime listing found on 2026-09-28 | | | | | | | |
| JST WC-110 | ctx §3; FF f1b (ref); HT (ref); SL (ref); PM (ref) | no Prime listing found on 2026-09-28 | | | | | | | |
| Engineer PA-09 | ctx §4; FF (ref); HT (ref); IH i1 | ENGINEER PA-09 Micro Connector Crimping Pliers, 175 mm, Made in Japan | https://www.amazon.com/dp/B002AVVO7K | $38.99 | yes | next day (Sep 29) | 4.5 stars, 1,719 ratings; 200+ bought in past month; Amazon's Choice; only 18 left | Genuine Engineer: page says AWG #32–#20, die widths 1.0, 1.4, 1.6 and 1.9 mm, S55C steel, made in Japan (confirmed) | |
| iCrimp SN-2549 ratcheting crimper (a second unit) | BM b2; FF f1, f4; HT a1, a2, a3; RP a2, a2b, a2d | iCrimp SN-2549 for JST ZH 1.5, PH 2.0, XH 2.5, VH 3.96, JWPS 4.0, Dupont 2.54, AWG 28–18 | https://www.amazon.com/dp/B01N4L8QMW | $22.29 | yes | overnight (Sep 29) | 4.5 stars, 532 ratings; 100+ bought in past month; Amazon's Choice; in stock | XH nest (title lists XH 2.5 mm); open barrel AWG 28–18 (confirmed). Jaw screws and pawl detail not on page | A second iCrimp listing, "SN-2549 JST Dupont Crimping Tool, AWG 28-18", https://www.amazon.com/dp/B01N1RFZZ4, $22.29, 194 ratings, 50+ bought in past month (search result) |
| SN-2549 replacement jaw set, sold alone | FF f3; HT a4 | no Prime listing found on 2026-09-28 | | | | | | | |
| SN-series interchangeable-jaw set that includes the 2549 die | BM b2; FF f3 and HT a4 (as a jaw source) | iCrimp IWS-0723K 7-piece ratchet crimping tool set, AWG 28–10 | https://www.amazon.com/dp/B09CP8RV94 | $46.59 | yes | Wed Sep 30 | 4.3 stars, 9 ratings (thin) | Page lists five interchangeable dies: 2549 (JST/Dupont open barrel), 06WF, 02C, 06, 48B (confirmed). Whether a die carries its own pivot is not stated | The only Prime route to a loose 2549 die found; it comes in a frame |
| Pneumatic bench crimper with interchangeable dies | ctx §4 | Pneumatic crimping tool AM-10, 14 die sets, foot pedal | https://www.amazon.com/dp/B0B8T9X2DK | $159.00 | yes | Fri Oct 2 | 3.6 stars, 14 ratings (thin); only 7 left | Die change and pedal operation (confirmed). An open-barrel XH die is not listed | Dies shown are for lugs and insulated terminals. A sibling "Am-10 Pneumatic Terminal Crimping Machine", https://www.amazon.com/dp/B0DMW2GM9C, $179.99, 3 ratings, 1.3 t, double-acting cylinder, 15 die sets, 13 lb, only 5 left |
| Electric bench crimper with dies | ctx §4 | Electric terminal crimping machine, 7 die sets, pedal, counter | https://www.amazon.com/dp/B0FHDRR22T | $899.00 | yes | Wed Sep 30 | 1.0 star, 1 rating (thin); only 3 left | Changeable dies, foot pedal, counter (confirmed). Open-barrel XH die not listed | Accepting OTP applicators is not stated |
| Arbor press, 1 t | FF f2b; TS a1, a2, a4, a5 | VEVOR 1 Ton Manual Arbor Press (AP-1), 5.9 in maximum height | https://www.amazon.com/dp/B0CGJ4QT17 | $61.90 | yes | Fri Oct 2 | 4.3 stars, 281 ratings; 300+ bought in past month; Amazon's Choice | Page spec: maximum working stroke/opening 150 mm (5.9 in); throat depth 81 mm (3.2 in); ram bore 10 mm; plate 90 mm; ram length 225 mm; 23 lb (confirmed) | Handwheel version https://www.amazon.com/dp/B0CGJ33KWN, $76.90, 126 ratings, 100+ bought in past month (search result) |
| Arbor press, 3 t, opening ≥175 mm | FF f2b, f5 | VEVOR 3 Ton Manual Arbor Press (AP-3), 12.2 in maximum height | https://www.amazon.com/dp/B0CGJ4PRMQ | $255.90 | yes | Fri Oct 2 | 3.9 stars, 28 ratings (thin) | Page spec: maximum stroke/opening 310 mm (12.2 in); throat 130 mm (5.1 in); ram bore 12 mm; plate 166 mm; 86 lb (confirmed) | |
| Arbor press, 3 t, ratchet | FF f2b, f5 | VEVOR 3 Ton Ratchet Type Arbor Press (PR-3) | https://www.amazon.com/dp/B0CGHXCQ1P | $262.14 | yes | Fri Oct 2 | 3.6 stars, 44 ratings; 50+ bought in past month | Page spec: stroke/opening 310 mm; throat 130 mm; ram bore 12 mm (0.5 in); plate 166 mm; 99 lb (confirmed) | |
| Two-post guided die set, ~100 × 60 mm shoe | RP a2b | no Prime listing found on 2026-09-28 | | | | | | | |
| Air-over-hydraulic bottle jack, 12 t | RP a2b | BIG RED TA91206 Torin pneumatic air hydraulic bottle jack, 12 t | https://www.amazon.com/dp/B00026Z3HM | $136.04 | yes | Wed Sep 30 | 4.5 stars, 290 ratings; Amazon's Choice; only 9 left (more on the way) | Air input 100–175 psi and manual pump; lift range 10-1/4 to 20-1/16 in (confirmed) | It is a lifting jack. Fit into the VEVOR 12 t press frame and its return springs is not stated |
| Push-pull toggle clamp, GH-305 class | BM b1b, b2; CQ c1b | POWERTEC 2-pack push-pull toggle clamp, 305CM, 500 lb | https://www.amazon.com/dp/B0D227VW2B | $18.25 | yes | overnight (Sep 29) | 4.7 stars, 605 ratings; 50+ bought in past month; Amazon's Choice | 500 lb hold (confirmed). Plunger stroke not stated on the page | |
| Disc springs (Belleville washers) | HT a4; TS a1, a2 | Hilitchi 215-piece M3–M12 304 stainless Belleville washer assortment | https://www.amazon.com/dp/B07CSQDS7F | $14.99 | yes | next day (Sep 29) | 4.4 stars, 68 ratings; 50+ bought in past month; Amazon's Choice | Sizes M3–M12 (confirmed). Load per washer not stated | Stainless, light duty. A heavy-series stack for 3–4 kN preload is not shown |
| Die springs | FF f5 | Glarks 50-piece 8 mm OD × 20 mm light-load die springs | https://www.amazon.com/dp/B081DSZTV6 | $16.95 | yes | Wed Sep 30 | 4.3 stars, 70 ratings; Amazon's Choice; only 17 left | Light load, 8 mm OD (confirmed) | 10–16 mm OD assortment not found; 20 × 10 × 25 mm pairs appeared in search |
| Precision flush cutter to motorise (Hakko CHP-170) | TS a2 | Hakko CHP-170 Micro Soft Wire Cutter, pack of 2 | https://www.amazon.com/dp/B0765LT5JG | $22.91 | yes | overnight (Sep 29) | 4.7 stars, 24,508 ratings; 500+ bought in past month | Genuine Hakko CHP-170 (confirmed) | |

## Contacts and housings

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| JST XH connector kit, housings plus loose contacts (CQRobot, as on the bench) | every explorer (the contacts on hand) | CQRobot JST XH 2.54 mm pitch connector kit; variants 2P through 9P | https://www.amazon.com/dp/B0731NHS9R | $10.99 (2P/3P/4P set); 4P $7.99, 5P $8.29, 6P $8.69, 7P $8.99, 5P/6P/7P set $10.99 | yes | next day (Sep 29) for most variants | 4.6 stars, 167 ratings; Amazon's Choice | 2P/3P/4P set: 30 each of B2B/B3B/B4B-XH-A headers and housings, 280 open-barrel crimp contacts (confirmed). Each size variant showed Prime delivery | JST genuineness is not claimed on the page |
| XH contacts on carrier strip (reel) | PM (every arrangement, strip-fed); TS (strip-fed ideas) | no Prime listing found on 2026-09-28 | | | | | | | |
| JST-XH balance extension leads, 22 AWG silicone | CQ c2 | elechawk JST-XH 4S (XH-5) balance extension, 200 mm, 22 AWG silicone, 5 pieces | https://www.amazon.com/dp/B07Q29TG24 | $8.99 | yes | overnight (Sep 29) | 4.7 stars, 376 ratings; 50+ bought in past month; Amazon's Choice | 22 AWG silicone, JST-XH (confirmed); "separate insulation", so wires are not bonded flat | Only 200 mm in this family; 3S and 6S siblings at https://www.amazon.com/dp/B07PX37XX5 (513 ratings) and https://www.amazon.com/dp/B08L5WCH82 (154 ratings) appeared in search |
| JST-XH balance extension, 8S (XH-9), 22 AWG | CQ c2 | 10-piece JST-XH 8S balance lead extension, 30 cm, 22 AWG | https://www.amazon.com/dp/B08L36NDVX | $13.99 | yes | overnight (Sep 29) | 4.3 stars, 32 ratings; Amazon's Choice | 30 cm length, 22 AWG, 9-pin XH (confirmed) | 500–600 mm at 22 AWG not found |
| Pre-crimped single XH wires, 22 AWG silicone | CQ c2 | elechawk XH 2.54 connector kit with 22 AWG pre-crimped silicone cables, 2–6 pin housings | https://www.amazon.com/dp/B0CM315RFP | $16.99 | yes | overnight (Sep 29) | 4.6 stars, 95 ratings; 100+ bought in past month; Amazon's Choice | 22 AWG silicone, contact crimped on one end, 6 colours × 15 (confirmed) | Wire length is not stated on the page; not black-only |
| XH-mating IDC housing, 2.5 mm pitch | CQ c4 | no Prime listing found on 2026-09-28 | | | | | | | |
| JST XH contact extraction tool | CQ c2 | JRready ACTCRH7A13 pin removal kit, XH2.54PRO and HY2.0PRO tips with push rod | https://www.amazon.com/dp/B0H25W39YS | $34.00 | yes | next day (Sep 29) | 5.0 stars, 1 rating (thin); only 18 left | Tip for JST XH/XH2.54 terminals with push rod (confirmed) | |
| 2.54 mm male pin headers, 40-pin strips | HT a1, a3; TS a4 | 20-piece 2.54 mm 40-pin male and female header strips | https://www.amazon.com/dp/B01MQ48T2V | $7.99 | yes | overnight (Sep 29) | 4.6 stars, 441 ratings; 500+ bought in past month; Amazon's Choice | 2.54 mm single row (confirmed). Pin cross-section (0.64 mm square) not stated | |
| Extra-long male pin headers, ≥20 mm | TS a4b, a5 | uxcell 30-piece 2.54 mm 40-pin headers, 25 mm pin length | https://www.amazon.com/dp/B07DK4BDHK | $15.49 | yes | Fri Oct 2 | 4.7 stars, 76 ratings; only 8 left | 25 mm pin length (confirmed). Pin cross-section not stated | |
| Push-in terminal (Wago 221-415) | HT (far-end electrode block, all ideas) | Wago 221-415 Lever-Nuts, 5-conductor, 25 pack | https://www.amazon.com/dp/B0107SYYGU | $28.00 | yes | Wed Sep 30 | 4.9 stars, 6,963 ratings; 50+ bought in past month; only 6 left | Genuine Wago 221-415 (confirmed) | 50-pack https://www.amazon.com/dp/B01M6Y2UEK, $40.45, 833 ratings, 600+ bought in past month (search result) |
| P75 pogo pins, 100 pack | PM p3; RP a6 | MEETOOT 100-piece P75-E2 spring test probes | https://www.amazon.com/dp/B099F1DRYJ | $6.49 | yes | Wed Sep 30 | 4.7 stars, 21 ratings; 50+ bought in past month; Amazon's Choice | Page: 1.3 mm conical head, 1.02 mm tube, 2.50 mm full stroke, 100 g, 3 A (confirmed) | Conical E2 head, not the crown H2 head. Crown-head P75 and matching receptacles: no Prime listing found on 2026-09-28 |

## Motion and drive

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| 12 V linear actuator, 50 mm, potentiometer feedback | BM b2; FF f1, f2b | Progressive Automations PA-01-POT 12 V mini linear actuator, 2 in stroke, 169 lb | https://www.amazon.com/dp/B0G7DD9QWQ | $155.39 | yes | Fri Oct 2 | no ratings shown (thin); only 8 left | Built-in potentiometer feedback; 169 lb (≈750 N); 2 in stroke (confirmed) | Below the 1,000–1,500 N wanted for BM b2; inside the 300–500 N band wanted for FF f2b |
| 12 V linear actuator, 1,500 N, 50 mm, limit switches | BM b2; RP a2 | Justech 330 lb/1500 N, 2 in/50 mm, 12 V, with bracket | https://www.amazon.com/dp/B0F5Q1HXSX | $29.99 | yes | Thu Oct 1 | 4.4 stars, 230 ratings; Amazon's Choice; only 10 left | Page: 1,500 N push, 1,200 N pull, 50 mm stroke, 7 mm/s loaded, 2.5 A, built-in limit switches, self-locking (confirmed) | No position feedback |
| NEMA 17 with integrated T8×2 lead screw, anti-backlash nut | BM b1; CQ c1b; FF f3, f4; IH i1, i2, i3; PM p1, p2, p3; RP a1, a4, a6; TS a2, a2c, a4 | Iverntech 42HD6039-05 NEMA 17 42×48 with integrated 240 mm Tr8×2 lead screw | https://www.amazon.com/dp/B094CRRSRQ | $27.99 | yes | Thu Oct 1 | 4.1 stars, 21 ratings (thin) | 2 mm lead, single start; 500 mN·m; anti-backlash nut included (confirmed) | |
| NEMA 17 external linear stepper, Tr8×2, external nut | HT a1, a3, a5; RP a1, a4, a6 | MybotOnline 310 mm Tr8×2 NEMA 17 integrated linear stepper with external brass nut | https://www.amazon.com/dp/B07TB7FPPP | $27.78 | yes | Fri Oct 2 | 4.6 stars, 5 ratings (thin); only 9 left | 2 mm lead; 42 N·cm; 1.5 A; free-running brass nut (confirmed) | Nut is not anti-backlash |
| NEMA 23 planetary gearbox, 10:1 and 20:1 | BM b1b | STEPPERONLINE planetary gearbox 10:1, 15 arc-min, for 6.35 mm shaft NEMA 23 | https://www.amazon.com/dp/B0BPGMZ5LM | $48.00 (5:1, 10:1, 20:1 and 50:1 variants all $48) | yes | Wed Sep 30 | 4.4 stars, 4 ratings (thin); only 3 left | 10:1 page: 96 % efficiency; max permissible torque 10 N·m; momentary 20 N·m (confirmed). Derek's shaft size decides the variant | 10 N·m permissible is half the ≥20 N·m wanted; the 20:1 variant's rating was not read. 10 mm-shaft version https://www.amazon.com/dp/B0BPHJVPTH (search result) |
| NEMA 17 planetary geared stepper | BM b3 | STEPPERONLINE 17HS19-1684S-PG27, NEMA 17 with 26.85:1 planetary gearbox | https://www.amazon.com/dp/B00QEUZ9EM | $41.91 | yes | next day (Sep 29) | 4.5 stars, 36 ratings; only 1 left | Max permissible torque 3 N·m, momentary 5 N·m; backlash ≤1° (confirmed) | 3 N·m is just under the 3.5 N·m asked |
| NEMA 23 stepper with 30:1 worm gearbox | FF f2 | Heechoo worm-gear NEMA 23 stepper, 3.5 A, 30:1 | https://www.amazon.com/dp/B07XFRL9GP | $120.00 | yes | Thu Oct 1 | 4.3 stars, 15 ratings (thin); only 10 left | 30:1 worm; motor holding torque 1.3 N·m (confirmed). Output torque and self-locking not stated | |
| NMRV030 worm gearbox for NEMA 23 | FF f2 | CNCTOPBAOS NMRV030-40 worm gear reducer, 40:1 | https://www.amazon.com/dp/B09HGS2SSG | $38.99 | yes | next day (Sep 29) | 5.0 stars, 8 ratings (thin); only 12 left | 40:1, 60 mm flange, 11 mm input bore, 14 mm output shaft (confirmed) | 11 mm bore does not take a 6.35 or 8 mm motor shaft without a sleeve |
| NEMA 17 worm-gear stepper, 30:1–50:1 | PM p5 | no Prime listing found on 2026-09-28 | | | | | | | |
| 12 V self-locking worm gearmotor, ~10 rpm (5840-31ZY class) | HT a1, a4 | Greartisan DC 12 V 10 rpm 40 kg·cm, 8 mm double shaft, self-locking worm gear motor | https://www.amazon.com/dp/B07YBXB4N7 | $26.99 | yes | next day (Sep 29) | 4.2 stars, 40 ratings | Self-locking; 10 rpm; 8 mm shaft; 40 kg·cm (confirmed) | Double-shaft worm body rather than the 5840-31ZY outline |
| 12 V wiper-type gearmotor | BM b1b | BEMONOC high-torque PMDC right-angle gear motor, 12 V, 50 rpm | https://www.amazon.com/dp/B01GJ4VPH2 | $46.88 | yes | Fri Oct 2 | 4.5 stars, 117 ratings; Amazon's Choice; only 20 left | Rated torque 6 N·m, 30 W, 100 % duty (confirmed) | No park switch stated; 6 N·m rated, stall not stated (≥12 N·m stall was wanted) |
| N20 gear motor with encoder | BM b2, b3 | 2-piece DC 12 V 200 rpm N20 worm gear motor with encoder | https://www.amazon.com/dp/B0D9V62J3W | $27.99 | yes | overnight (Sep 29) | no ratings (thin) | 7 PPR Hall encoder (confirmed) | The N20 encoder listings seen were all unrated |
| 28BYJ-48 with ULN2003, 5-pack | TS a2, a4, a4b, a5 | ELEGOO 5 sets 28BYJ-48 with ULN2003 driver boards | https://www.amazon.com/dp/B01CP18J4A | $14.99 | yes | overnight (Sep 29) | 4.6 stars, 831 ratings; 400+ bought in past month; Amazon's Choice | 5 V geared stepper with driver (confirmed) | |
| Micro servo, metal gear (MG90S) | BM b1, b2; IH i1, i2, i4; SL v1, v6 | Miuzei MG90S 9 g metal gear micro servo, 4 pack | https://www.amazon.com/dp/B0CP98TZJ2 | $13.88 | yes | next day (Sep 29) | 4.5 stars, 794 ratings; 900+ bought in past month; Amazon's Choice | Metal gear; 2.0 kg·cm (confirmed) | |
| Standard servo, MG996R, 4 pack | RP a1; TS a2, a2b, a3 | Deegoo-FPV MG996R 55 g metal gear digital servos, 4 pack | https://www.amazon.com/dp/B07MFK266B | $18.99 | yes | overnight (Sep 29) | 4.5 stars, 1,346 ratings; 300+ bought in past month; Amazon's Choice | Metal gear, standard size (confirmed). Stall torque not in the bullets read | |
| Servo, 20–25 kg·cm (DS3218) | BM b2; HT a2, a3; SL v1, v3; RP a1 | DS3218MG 20 kg digital servo, full metal gear, 270° | https://www.amazon.com/dp/B076CNKQX4 | $14.99 | yes | Wed Sep 30 | 4.5 stars, 5,306 ratings; 100+ bought in past month; Amazon's Choice | Up to 21.5 kg·cm at 6.8 V; metal gears (confirmed) | |
| Servo, 25–60 kg·cm | FF f3 | ZOSKAY DS3235 35 kg coreless servo, stainless steel gear | https://www.amazon.com/dp/B07S9XZYN2 | $27.99 | yes | overnight (Sep 29) | 4.5 stars, 1,755 ratings; 100+ bought in past month; Amazon's Choice | 35 kg class, stainless steel gears (confirmed) | 60 kg class did not surface in the Prime search |
| MGN12 rail with MGN12H carriage | BM b1; CQ c1; HT a2; PM p1, p2, p3; RP a1 | MGN12 300 mm linear rail with MGN12H stainless carriage | https://www.amazon.com/dp/B07ZVFFXQZ | $20.49 | yes | Thu Oct 1 | 4.2 stars, 615 ratings; Amazon's Choice; only 9 left | Preloaded MGN12H carriage (confirmed) | |
| MGN9 rail with MGN9H carriage | CQ c1; IH i1, i2, i3, i5; PM p1, p2, p3 | 200 mm MGN9 rail with 1 MGN9H stainless carriage | https://www.amazon.com/dp/B0DY4LGPS5 | $16.12 | yes | Wed Sep 30 | 4.2 stars, 34 ratings; Amazon's Choice | Pre-loaded carriage (confirmed) | |
| HGR15 rail with HGH15CA carriage | FF f2 | 2 × HGR15 400 mm rails with 4 × HGH15CA carriages | https://www.amazon.com/dp/B0C4DG3HLR | $48.99 | yes | Wed Sep 30 | 4.3 stars, 40 ratings | HGH15CA blocks (confirmed). Preload class not stated | Sold as a 400 mm pair; a single 100–150 mm rail did not surface |
| Ball screw, SFU1204, short | CQ c1 | SFU1204 ball screw, 200 mm, with metal nut | https://www.amazon.com/dp/B07XXSL3CC | $35.99 | yes | Thu Oct 1 | 4.3 stars, 24 ratings; Amazon's Choice; only 4 left | 12 mm, 4 mm lead, 200 mm (confirmed) | End supports not included |
| Ball screw kit, SFU1605 with BK12/BF12 | TS a1 | CHUANGNENG SFU1605 450 mm with BK/BF12 supports, nut housing and coupler | https://www.amazon.com/dp/B089DGRFY9 | $41.59 | yes | Wed Sep 30 | 4.6 stars, 63 ratings; Amazon's Choice; only 9 left | 5 mm lead, BK12/BF12, nut housing (confirmed) | Accuracy class not stated |
| GT2 pulleys (and belt) | HT a2; PM p1b, p3, p3b | WINSINN GT2 20-tooth pulley, 6 mm bore, 6 mm belt, 5 pack | https://www.amazon.com/dp/B07CXR7SFL | $5.99 | yes | overnight (Sep 29) | 4.7 stars, 980 ratings; 50+ bought in past month; Amazon's Choice | 20T, 6 mm belt width (confirmed) | Open belt not opened (generic) |
| Pillow block bearings, 20 mm (UCP204) | BM b1b; FF f2 | XIKE UCP204 pillow block bearing, 20 mm, 2 pack | https://www.amazon.com/dp/B09T5NFMGZ | $26.99 | yes | Wed Sep 30 | 4.2 stars, 234 ratings | 20 mm bore, self-aligning (confirmed). Load rating not read | |
| Needle roller bearings, HK1010 | PM p5 | uxcell HK1010 drawn cup needle bearings, 5 pack | https://www.amazon.com/dp/B07GCBXRQN | $7.79 | yes | Thu Oct 1 | 4.5 stars, 162 ratings; only 4 left | 10 × 14 × 10 mm (confirmed). Dynamic rating not stated | |
| Ground shaft, 8 mm | HT a4 | 2 × 8 × 100 mm case-hardened chrome linear rod, h8 | https://www.amazon.com/dp/B09RVS4PXZ | $6.99 | yes | next day (Sep 29) | 4.7 stars, 567 ratings; Amazon's Choice; only 11 left | Case hardened (confirmed) | h8 tolerance, not h6 |
| Ground shaft, 10 mm | FF f3, f4, f5 | 4 × 10 × 300 mm case-hardened chrome linear rods | https://www.amazon.com/dp/B0D2312R72 | $17.99 | yes | next day (Sep 29) | 4.8 stars, 279 ratings; only 6 left | Case hardened (confirmed). Tolerance not in title | The 10 mm rods seen elsewhere were listed as h8 |
| Flanged bronze bushings, 10 mm | FF f3, f4, f5 | uxcell 10 × 12 × 10 mm flange sleeve bearings, sintered bronze, 10 pack | https://www.amazon.com/dp/B0GCH3THWM | $11.99 | yes | Wed Sep 30 | 4.6 stars, 29 ratings (thin) | 10 mm bore (confirmed). Running clearance not stated | |
| Ground steel rod, 3 mm | IH i3 | no Prime listing found on 2026-09-28 | | | | | | | |
| Lazy-susan turntable bearing, 12 in | PM p1b | 12 in (300 mm) lazy susan turntable bearing | https://www.amazon.com/dp/B01L8EHD6K | $22.99 | yes | overnight (Sep 29) | 4.6 stars, 2,611 ratings; 200+ bought in past month | 300 mm full rotation (confirmed). Wobble not stated | |
| Dyneema cord, 1–2 mm | HT a1 | emma kites hollow UHMWPE braided cord, 1.3/1.6/2 mm | https://www.amazon.com/dp/B07BKQLFRB | $17.95 | yes | Wed Sep 30 | 4.7 stars, 608 ratings; 50+ bought in past month; Amazon's Choice | UHMWPE, 520–1,000 lb by size (confirmed) | |
| Capsule slip ring, 6 circuits | PM p3, p3b | 12.5 mm capsule slip ring, 6 wires × 2 A, 300 rpm | https://www.amazon.com/dp/B07H2SRMXP | $9.99 | yes | overnight (Sep 29) | 4.5 stars, 136 ratings; 50+ bought in past month; Amazon's Choice | 6 circuits, 2 A (confirmed) | |
| Capsule slip ring, 12 circuits | PM p3, p3b | Taidacent 12-wire 2 A slip ring, 12.5 mm OD | https://www.amazon.com/dp/B07Y9P8N3Y | $19.99 | yes | overnight (Sep 29) | 4.0 stars, 6 ratings (thin); only 5 left | 12 circuits, 2 A (confirmed) | |
| Spring ball plungers, M8 | PM p1b | uxcell M8 × 16 mm ball point spring set screws, 304 stainless, 8 pieces | https://www.amazon.com/dp/B099JXP155 | $7.79 | yes | overnight (Sep 29) | 4.8 stars, 25 ratings (thin); only 3 left | Threaded M8 hex-socket ball plunger (confirmed). Preload not stated | Carbon-steel 10-piece M8 set https://www.amazon.com/dp/B07PRFPF8N, $11.99, 4 ratings, only 5 left |
| Controller, BTT SKR Pico | BM b1, b3; PM (motion control for every arrangement) | BIGTREETECH SKR PICO V1.0, 4 × TMC2209 UART | https://www.amazon.com/dp/B09MYKL9MP | $35.99 | yes | Wed Sep 30 | 4.0 stars, 74 ratings; Amazon's Choice | Four TMC2209 drivers (confirmed) | |
| Controller, MKS DLC32 | BM b1, b3 | MKS DLC32 V2.1 ESP32 GRBL 3-axis board with TS24 touch display | https://www.amazon.com/dp/B0GY43P1CL | $38.50 | yes | Fri Oct 2 | 3.5 stars, 6 ratings (thin); 50+ bought in past month; only 16 left | ESP32, GRBL, Wi-Fi, SD (confirmed). Driver count not stated beyond "3 axis" | |
| Momentary foot switch, dry contact | BM b2 | TEMCo CN0002 aluminum foot switch, SPDT NO/NC, 10 A | https://www.amazon.com/dp/B00EF98MRU | $13.76 | yes | Wed Sep 30 | 4.2 stars, 24 ratings; Amazon's Choice | Bare 37 in 3-conductor cord: white common, black NC, red NO (confirmed) | |
| Air cylinder, 63 mm bore × 50 mm | BM b1b | BAOMAIN SC63×50 pneumatic air cylinder | https://www.amazon.com/dp/B0788NFXFV | $33.49 | yes | Fri Oct 2 | 4.4 stars, 13 ratings (thin) | 63 mm bore, 50 mm stroke (confirmed) | |
| Air cylinder, 32 mm bore × 25 mm | FF f3 | TAILONZ SC32×25 double-acting cylinder | https://www.amazon.com/dp/B092HJ3341 | $20.99 | yes | Wed Sep 30 | 4.6 stars, 272 ratings; Amazon's Choice; only 14 left | 32 mm bore, double acting (confirmed) | |
| 5/2 solenoid valve, 24 V DC, 1/4 | BM b1b; FF f3 | TAILONZ 4V210-08 1/4 NPT 24 V DC 5/2 single-coil pilot valve | https://www.amazon.com/dp/B07SGDDKL1 | $16.99 | yes | overnight (Sep 29) | 4.5 stars, 188 ratings; 50+ bought in past month; Amazon's Choice | 24 V DC coil, 5/2 (confirmed) | |
| Flow control valves, 1/4 | BM b1b; FF f3 | TAILONZ SCF-1/4 push-to-connect flow control, 5 pieces | https://www.amazon.com/dp/B085NRHHSJ | $14.99 | yes | next day (Sep 29) | 4.5 stars, 415 ratings; 50+ bought in past month; Amazon's Choice | Adjustable flow control (confirmed) | Meter-out depends on fitting orientation; not stated |
| Push-pull solenoid, 12 V, 10 mm | SL v4; PM p2, p5 | Heschen HS-0530B 12 V push-pull solenoid, 10 mm stroke | https://www.amazon.com/dp/B07MJJB12M | $7.99 | yes | next day (Sep 29) | 4.1 stars, 383 ratings; 50+ bought in past month; Amazon's Choice | 10 mm stroke; 5 N max, 0.5 N initial; 1.7 A (confirmed) | Holding type not stated |
| Coin vibration motors, 10 mm, 3 V | RP a2c; TS a3 | 20-piece 10 × 3 mm 3 V coin vibration motors | https://www.amazon.com/dp/B07Q1ZV4MJ | $12.99 | yes | next day (Sep 29) | 4.7 stars, 307 ratings; 200+ bought in past month; Amazon's Choice | 10 mm, 3 V (confirmed) | |

## Sensing and vision

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Bar load cell with HX711, 5–10 kg | ctx §6; BM b1; HT a2 (proof pull); IH i3; PM p1; RP (ref); SL (ref); TS (ref) | ShangHJ 2 sets 5 kg bar load cell with HX711 | https://www.amazon.com/dp/B09K7G3477 | $9.99 | yes | overnight (Sep 29) | 4.0 stars, 24 ratings; 100+ bought in past month; Amazon's Choice | Bar cell plus HX711 board (confirmed) | 10 kg, 4-set version https://www.amazon.com/dp/B09VYVRQD5, $15.99, 11 ratings (search result) |
| S-type load cell, 50 kg class | ctx §6; FF f1; HT a1 | S-type beam load cell, 50/100/300/2000 kg; 100 kg variant | https://www.amazon.com/dp/B077YHNNCP | $37.71 | yes | Wed Sep 30 | 4.4 stars, 16 ratings (thin); only 20 left | Tension and compression S-beam (confirmed) | 50 kg variant's Prime status not checked; no amplifier included |
| Button compression load cell, 500 kg | FF f2, f3, f4; HT a4 | Micro button load cell, flush diaphragm, IP66, ±0.5 % FS, 0–500 kg variant | https://www.amazon.com/dp/B0GZZRQC6Y | $74.99 | yes | Thu Oct 1 | no ratings (thin); only 6 left | Compression button, 500 kg (confirmed) | 1 t button: none surfaced |
| Button load cell, Φ20 × 12 mm | HT a4 | Mini button load cell Φ20 × 12 mm, 0.2 %, 3 m cable; 0–200 kg variant | https://www.amazon.com/dp/B0DGFS22T3 | $49.99 | yes | Wed Sep 30 | no ratings (thin); only 12 left | Φ20 mm body (confirmed); variants to 500 kg listed | The 500 kg variant's Prime status was not checked |
| Compression load cell, 5 t | FF f5 | Bellows compression load cell 0–5 t with 5-digit indicator, peak hold, two relay outputs | https://www.amazon.com/dp/B0DY7JJ7ZV | $129.00 | yes | Thu Oct 1 | 3.9 stars, 3 ratings (thin); only 2 left | 5 t compression with indicator and peak hold (confirmed) | Raw mV/V access for an HX711 not stated |
| Foil strain gauges, BF350 | BM b1b, b3 | Icstation 4-piece BF350 350 Ω foil strain gauges | https://www.amazon.com/dp/B0CNJTY2F3 | $6.99 | yes | next day (Sep 29) | 4.0 stars, 4 ratings (thin) | 350 Ω foil (confirmed) | |
| HX711 amplifier board | BM b1b, b3 | SparkFun Load Cell Amplifier HX711 | https://www.amazon.com/dp/B079LVMC6X | $11.50 | yes | next day (Sep 29) | 4.6 stars, 75 ratings; 100+ bought in past month; Amazon's Choice | Separate analog and digital supplies (confirmed) | 80 Hz rate selection not stated in the bullets read |
| Point micrometer | ctx §6; PM (ref); SL (ref) | Shars 303-2307 0–1 in micrometer, 30° point, 0.0001 in, ratchet | https://www.amazon.com/dp/B082QWT3ST | $61.95 | yes | Thu Oct 1 | 4.9 stars, 13 ratings (thin); only 9 left | Point on both faces; 0.0001 in graduation; 0.00016 in accuracy (confirmed) | Not a point-and-blade crimp micrometer |
| Blade micrometer | ctx §6; PM (ref); SL (ref) | Shars 303-2202 0–1 in blade micrometer | https://www.amazon.com/dp/B082T4MWRM | $98.75 | yes | Wed Sep 30 | 4.9 stars, 14 ratings (thin); only 7 left | Blade on both anvil and spindle; 0.0001 in graduation (confirmed) | Not a point-and-blade crimp micrometer |
| Crimp-height micrometer (point spindle with blade anvil) | ctx §6; PM (ref); SL (ref) | no Prime listing found on 2026-09-28 | | | | | | | |
| Digital indicator, 0.001 mm, data output | FF f3, f4; SL v3 | Clockwise Tools DITR-0105 digital indicator, 0–1 in, 0.001 mm | https://www.amazon.com/dp/B07888LX1R | $52.99 | yes | next day (Sep 29) | 4.6 stars, 67 ratings; Amazon's Choice | RS232 data port (confirmed); needs the DTCR-01 cable, not included | DTCR-01 cable: no Prime listing found on 2026-09-28 |
| AS5600 magnetic angle sensor | FF f2; HT a1, a4; IH i5 | UMLIFE 3-piece AS5600 12-bit magnetic encoder boards | https://www.amazon.com/dp/B094F8H591 | $7.99 | yes | next day (Sep 29) | 4.4 stars, 70 ratings; 100+ bought in past month | 12-bit; I²C, PWM and analog outputs (confirmed) | Magnet inclusion not stated in the bullets read |
| Linear Hall sensor, SS49E | IH i4 | ALLECIN 20-piece 49E/SS49E linear Hall sensors, TO-92S | https://www.amazon.com/dp/B0CZ6RL4B2 | $7.99 | yes | Wed Sep 30 | 4.5 stars, 86 ratings; 100+ bought in past month; Amazon's Choice | Linear (analog) Hall (confirmed) | |
| Micro limit switches, roller lever | IH i3b, i5; PM p1, p5 | HiLetgo 10-piece KW12-3 micro limit switch with roller lever, SPDT | https://www.amazon.com/dp/B07X142VGC | $5.99 | yes | overnight (Sep 29) | 4.7 stars, 724 ratings; 1K+ bought in past month; Amazon's Choice | Roller lever, SPDT (confirmed). Operating force not stated | |
| IR break-beam pair, 3 mm | PM p3, p4 | IR break beam sensor, 3 mm LEDs, split through-beam module | https://www.amazon.com/dp/B0DXT9H7VR | $9.99 | yes | Thu Oct 1 | no ratings (thin) | 3 mm LEDs, through-beam (confirmed) | |
| Slotted optical switch module | PM p3, p4 | 10-piece IR slotted optocoupler modules | https://www.amazon.com/dp/B0CHDRF497 | $9.99 | yes | next day (Sep 29) | 4.4 stars, 29 ratings; 50+ bought in past month; Amazon's Choice | Slotted photo-interrupter module (confirmed). Slot width not read | |
| Rotary encoder with measuring wheel | PM p3 | CALT GHW38 600 PPR encoder with 300 mm rubber wheel and spring bracket | https://www.amazon.com/dp/B07H29BBLK | $81.00 | yes | Wed Sep 30 | 4.8 stars, 5 ratings (thin) | 600 PPR, wheel and bracket (confirmed) | 600 counts per 300 mm is 20 counts per 10 mm, short of the 100 wanted. Bare 600 P/R encoder https://www.amazon.com/dp/B07MX1SYXB, $18.99, 77 ratings, 50+ bought in past month, Amazon's Choice (6 mm shaft) |
| 16 MP USB camera, M12 lens mount | SL v1, v5 | MMlove 16 MP IMX298 USB camera module with M12 1.95 mm fisheye | https://www.amazon.com/dp/B0C54VCKZV | $69.99 | yes | Wed Sep 30 | 4.6 stars, 16 ratings (thin) | IMX298; M12 lens; MJPEG 4656 × 3496 at 10 fps, 2048 × 1536 at 30 fps (confirmed). UVC plug and play | ELP 16 MP 118° board https://www.amazon.com/dp/B0C289GYVZ, $74.99, 39 ratings, Amazon's Choice; lens mount not stated in the text read |
| M12 board lens, 12 mm | SL v1, v5 | 12 mm board lens, CCTV | https://www.amazon.com/dp/B07CZ49BMK | $9.99 | yes | Wed Sep 30 | 4.5 stars, 12 ratings (thin) | 12 mm focal length (confirmed) | 16 mm uxcell https://www.amazon.com/dp/B07JZ1X8S4, $13.40, 7 ratings (search result) |
| Clip-on macro lens | SL v1, v5 | NEEWER Basics LS-69 15× macro phone lens with 37 mm clamp | https://www.amazon.com/dp/B0FKSKTLQX | $24.99 | yes | next day (Sep 29) | 4.3 stars, 87 ratings; 100+ bought in past month; Amazon's Choice; only 14 left | 15×; working distance 2–4 cm (confirmed) | Fit over the ELP's small lens not verified |
| Close-focus USB camera (microscope) | FF f4; IH i3, i4 | Plugable USB digital microscope 250×, 2 MP, flexible arm stand | https://www.amazon.com/dp/B00XNYXQHE | $59.95 | yes | next day (Sep 29) | 4.2 stars, 6,580 ratings; 200+ bought in past month | Uses a standard webcam chipset and driver (confirmed) | Larger than a board camera for a moving hand |
| First-surface mirror | SL v1, v5 | Front surface mirror, 100 × 100 × 3 mm | https://www.amazon.com/dp/B0GW4WT69F | $20.90 | yes | Wed Sep 30 | no ratings (thin) | First-surface (confirmed) | Needs cutting to 25–50 mm |
| LED light pad, A5, USB | SL v4, v4b, v5 | XIAOSTAR A5 light box, USB, adjustable brightness | https://www.amazon.com/dp/B08QJ2JMHZ | $16.99 | yes | next day (Sep 29) | 4.4 stars, 4,700 ratings; 50+ bought in past month; Amazon's Choice | A5, dimmable, USB (confirmed) | |
| Opal (white diffusing) acrylic, 3 mm | SL v1, v4 | Lesnlok 8 × 12 in translucent white acrylic, 3 mm, one side matte, 2 pack | https://www.amazon.com/dp/B0G4JJSFCS | $11.98 | yes | overnight (Sep 29) | 4.6 stars, 341 ratings; 100+ bought in past month | 73 % transmittance, 3 mm (confirmed) | |
| WS2812B ring, 16 LEDs | SL v1 | 5-piece 16-bit WS2812B RGB LED rings | https://www.amazon.com/dp/B0B2D5QXG5 | $18.99 | yes | next day (Sep 29) | 4.6 stars, 40 ratings; 50+ bought in past month; Amazon's Choice | Individually addressable, 16 LEDs (confirmed) | |
| LED ring light, 60–80 mm | PM p1, p1b, p4 | AmScope LED-144W-ZK 144-LED ring light | https://www.amazon.com/dp/B00JZJO7YC | $35.99 | yes | next day (Sep 29) | 4.6 stars, 664 ratings; 100+ bought in past month; Amazon's Choice | 62.5 mm inside, 92.5 mm outside; 6000 K; 110–240 V (confirmed) | Mains-powered controller |
| Line laser module, 650 nm, focusable | SL v6 | 650 nm dot/line/cross focusable module, 13 × 42 mm, with adapter and heatsink | https://www.amazon.com/dp/B01KNQ5RBC | $42.00 | yes | overnight (Sep 29) | 3.8 stars, 73 ratings | <5 mW, 3–5.5 V, line option (confirmed) | Which shape ships depends on the variant chosen |
| Precision pin gauges, 0.28–1.52 mm | SL v1, v5; TS a2, a2b, a2c (1.45 mm pilots) | Accusize 50-piece plug pin gage set, 0.011–0.060 in, class ZZ plus | https://www.amazon.com/dp/B00JOLCSF6 | $45.58 | yes | next day (Sep 29) | 4.6 stars, 167 ratings; Amazon's Choice | 60–62 HRC; 0.001 in steps; covers 0.057 in = 1.448 mm (confirmed) | |
| Drill blanks near 1.45 mm | TS a2, a2b, a2c | no Prime listing found on 2026-09-28 | | | | | | | |
| Mini diaphragm vacuum pump, 12 V | SL v4, v4b | 12 V 12 W micro diaphragm vacuum pump, −75 kPa, 12 L/min | https://www.amazon.com/dp/B08RCRJH9M | $26.99 | yes | next day (Sep 29) | 4.4 stars, 74 ratings; Amazon's Choice | −75 kPa (confirmed) | |
| 12 V 2-way normally closed valve | SL v4, v4b | Beduan 2-way NC 12 V air solenoid valve, 1/4 NPT | https://www.amazon.com/dp/B07N2LGFYS | $9.99 | yes | overnight (Sep 29) | 4.4 stars, 432 ratings; 200+ bought in past month | NC, 12 V (confirmed) | 1/4 NPT body is large for a pick-up line |
| Vacuum pressure sensor module (XGZP6847 class) | SL v4, v4b | no Prime listing found on 2026-09-28 | | | | | | | |
| Pick-and-place nozzle, Juki 500 series | SL v4, v4b | Mxfans tungsten steel SMT nozzle 503 for JUKI 2000 series | https://www.amazon.com/dp/B07DWYRM2F | $14.99 | yes | Thu Oct 1 | no ratings (thin); only 6 left | Juki 503 type (confirmed) | |
| Plastic optical fibre, 1 mm | TS a5 | AZIMOM PMMA end-glow fibre, 1 mm, 50 m | https://www.amazon.com/dp/B07W979RH3 | $10.89 | yes | Wed Sep 30 | 4.6 stars, 477 ratings; 50+ bought in past month | 1 mm PMMA (confirmed) | |

## Stripping, splitting and laser

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Hakko FT-802 thermal stripper | ctx §2 | Hakko FT802-03 digital thermal wire stripper, tweezer handpiece, blades sold separately | https://www.amazon.com/dp/B07V4GNCGM | $516.14 | yes | overnight (Sep 29) | 5.0 stars, 3 ratings (thin) | Uses G4 blades (confirmed) | A G4 blade for about 22 AWG: no Prime listing found on 2026-09-28 (the G4-1603 blade seen is 26–38 AWG) |
| Weidmüller Stripax Plus 2.5 | ctx §3 | no Prime listing found on 2026-09-28 | | | | | | | |
| Flat ribbon cable splitter tool | ctx §1; RP (ref) | no Prime listing found on 2026-09-28 | | | | | | | |
| Benchtop automatic stripping machine, small gauge, sensor-triggered | ctx §2 | no Prime listing found on 2026-09-28 | | | | | | | |
| Automatic hand wire stripper, 10–24 AWG | procedure step 3 (strip), all explorers | KNIPEX automatic wire stripper, 10–24 AWG, 7.25 in | https://www.amazon.com/dp/B003B8WB5U | $47.99 | yes | Fri Oct 2 | 4.4 stars, 1,867 ratings; 600+ bought in past month; only 11 left | Reaches 24 AWG (confirmed) | Behaviour on soft silicone not stated |
| Flat cable stripper | ctx §1 | Automatic flat cable stripper, 0.75–2.5 mm² | https://www.amazon.com/dp/B085WV8F2J | $96.99 | yes | overnight (Sep 29) | 5.0 stars, 3 ratings (thin) | Flat-cable jacket stripping (confirmed) | 0.75–2.5 mm² range sits above 22 AWG (0.33 mm²) |
| K40-class CO₂ laser engraver | BM b4 | VEVOR 45 W CO₂ laser engraver, 12 × 8 in, rotary axis, air assist | https://www.amazon.com/dp/B0G5HG2NXD | $759.90 | yes | Sat Oct 3 | 3.6 stars, 4 ratings (thin) | CO₂ tube, 12 × 8 in bed, air assist (confirmed) | K40-class bed size; the price is above a basic K40 |
| Bambu laser module for the H2 series | BM b4 | no Prime listing found on 2026-09-28 | | | | | | | |
| Diode laser module, 5–10 W optical | RP a5 | LASER TREE 10 W optical laser module with FAC and air assist | https://www.amazon.com/dp/B0BJQ2224V | $137.17 | yes | Fri Oct 2 | 4.4 stars, 71 ratings; Amazon's Choice; only 20 left | 10,000 mW optical (confirmed). PWM input not stated in the bullets read | |
| Nylon brush wheel for a rotary tool | BM b4 | Merryland 72-pack nylon brushes (wheel, cup, end) for rotary tools | https://www.amazon.com/dp/B07QRG27Z7 | $15.90 | yes | next day (Sep 29) | 4.1 stars, 1,477 ratings; 100+ bought in past month | Nylon, not wire (confirmed) | |
| Single-edge razor blades, 0.009 in | PM p1, p1b, p3; RP a5 | AccuTec Pro APBL-7064 steel-back single-edge blades, 0.009 in, 100 pack | https://www.amazon.com/dp/B0BV46534X | $12.90 | yes | overnight (Sep 29) | 3.2 stars, 32 ratings (thin) | 0.009 in carbon steel, steel back (confirmed) | A higher-volume 100-pack, https://www.amazon.com/dp/B0C38XZZQ6, $6.29, 2.9K ratings, 4K+ bought in past month, does not state thickness (search result) |
| #11 scalpel blades | SL v6 | JMU 100-piece #11 scalpel blades, stainless | https://www.amazon.com/dp/B0C4TQR2M7 | $13.09 | yes | next day (Sep 29) | 4.5 stars, 534 ratings; 400+ bought in past month; Amazon's Choice | #11 (confirmed) | Handle not checked |
| 0.5 mm flux-core solder | CQ c3 | Weller WSW SCN M1 solder wire, 0.5 mm, 100 g | https://www.amazon.com/dp/B09LDHLM1F | $33.78 | yes | next day (Sep 29) | 4.8 stars, 116 ratings; Amazon's Choice | 0.5 mm; Sn99.3 Cu0.6 Ni0.05; 3.5 % flux (confirmed) | No-clean not stated on the page |
| Solder wire feeder | CQ c3 | YIHUA 929D-II motorized automatic-feed soldering gun kit | https://www.amazon.com/dp/B09CT296ZC | $49.99 | yes | overnight (Sep 29) | 4.0 stars, 186 ratings | Motor-driven solder feed, press-and-hold (confirmed) | Metering in 1 mm steps not stated |

## Robots and gantries

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| SO-101 follower arm, 12 V servos | ctx §7; BM b5; RP (ref); SL v2 (ref) | SO-101 follower arm electronics kit with 12 V Feetech STS3215 servos | https://www.amazon.com/dp/B0GH35175P | $184.99 | yes | Fri Oct 2 | 5.0 stars, 1 rating (thin); only 2 left | 6 × STS3215 12 V, 30 kg·cm; 12 V 5 A supply; Waveshare USB-C bus driver (confirmed) | No printed parts |
| SO-ARM101 Pro servo kit | ctx §7; BM b5 | LeRobot SO-ARM101 Pro servo kit, without printed parts | https://www.amazon.com/dp/B0FH8CPXP7 | $360.00 | yes | next day (Sep 29) | 3.9 stars, 9 ratings (thin); 50+ bought in past month | Leader and follower servos for LeRobot (confirmed) | |
| SO-ARM101, assembled with printed parts | ctx §7; BM b5 | Hiwonder SO-ARM101 kit, 12 bus servos, dual camera; Starter kit | https://www.amazon.com/dp/B0GT999ZFF | $389.99 (DIY $269.99, Standard $419.99, Advanced $459.99) | yes | Wed Sep 30 | no ratings (thin) | Printed parts included, assembled (confirmed) | |
| Ender 3 V3 SE (as a stage or gantry) | BM b3; HT a2; SL v1b | Creality Ender 3 V3 SE 3D printer | https://www.amazon.com/dp/B0F8J78BN1 | $219.00 | yes | Thu Oct 1 | 3.9 stars, 2,112 ratings; 500+ bought in past month | Working X/Y/Z with G-code over USB (the printer) | Another Prime listing of the same printer, https://www.amazon.com/dp/B0DD7F2BH9, $186.14, 791 ratings, 200+ bought in past month, Wed Sep 30 |
| 3018-class desktop CNC frame | FF f4; IH i4 | SainSmart Genmitsu 3018-PROVer V2 CNC router | https://www.amazon.com/dp/B07ZFD6SKP | $269.00 | yes | Fri Oct 2 | 4.2 stars, 1,286 ratings; only 9 left | 3-axis GRBL machine, pre-assembled gantry (confirmed) | Travel and screw type not read |
| Diode laser engraver as a belt gantry | HT a3 | LONGER Ray5 10 W laser engraver, 400 × 400 mm | https://www.amazon.com/dp/B0G13BBN9L | $268.99 | yes | next day (Sep 29) | 4.0 stars, 176 ratings; 50+ bought in past month | 400 × 400 mm X–Y over a fixed bed (confirmed) | Head payload not stated |
| Small vibratory bowl feeder | ctx §3; PM (ref); SL (ref); TS (ref) | INTBUYING 110 V disc vibrating feeder with linear feeder and controller | https://www.amazon.com/dp/B0FYMPJLLX | $419.00 | yes | Fri Oct 2 | 2.0 stars, 1 rating (thin); only 3 left | Stainless bowl, controller with voltage regulation and photo sensing (confirmed) | Bowl diameter not read |
| Automatic screw feeder, M1–M5 adjustable rail | TS a3, a3b | CGOLDENWALL automatic screw feeder, M1–M5 (<20 mm), count display | https://www.amazon.com/dp/B00JKDFYQ8 | $185.00 | yes | Fri Oct 2 | 4.0 stars, 6 ratings (thin); only 16 left | Adjustable track for M1–M5; presents one at a time (confirmed) | Rail slot width range not stated |

## Fixtures and small parts

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Feeler gauge set, 0.02–1.00 mm | BM b2; IH i1, i2, i5 | Hotop 17-blade metric feeler gauge, 0.02–1.00 mm | https://www.amazon.com/dp/B08GLN7K1R | $8.99 | yes | next day (Sep 29) | 4.5 stars, 361 ratings; 100+ bought in past month; Amazon's Choice | Removable leaves (confirmed) | Title says stainless; bullets say 65 manganese steel |
| Spring steel shim, 0.2–0.8 mm | HT a1 (all ideas) | Precision Brand 1095 blue-tempered shim assortment, 0.005–0.032 in, 6 × 12 in | https://www.amazon.com/dp/B00065V062 | $53.39 | yes | Thu Oct 1 | 4.5 stars, 48 ratings; Amazon's Choice; only 2 left | 1095 hardened and tempered; 0.005, 0.010, 0.015, 0.020, 0.025, 0.032 in (confirmed) | |
| Spring steel strip, 1.0 and 1.5 mm | SL v3 | no Prime listing found on 2026-09-28 | | | | | | | |
| HSS square blanks, 3 mm | CQ c1, c1b | 5-piece HSS square tool bits, 3 × 3 × 200 mm | https://www.amazon.com/dp/B08ZSMB557 | $9.99 | yes | next day (Sep 29) | 4.7 stars, 47 ratings; Amazon's Choice; only 14 left | 3 × 3 mm HSS (confirmed) | Grade (M2/M42) not stated |
| Dowel pins, 3–8 mm | FF f3, f4; PM p1, p1b, p5; RP a1b, a2 | 24-piece M6 × 40 mm stainless dowel pins, precision ground, chamfered | https://www.amazon.com/dp/B0GS1B62Y1 | $6.49 | yes | overnight (Sep 29) | 5.0 stars, 19 ratings (thin); Amazon's Choice | Precision ground (confirmed) | 304 stainless, not hardened; hardened h6/m6 alloy pins did not surface in the Prime search |
| Chrome steel balls, 6 mm | PM p1, p1b; RP a1b, a2 | BC Precision 6 mm chrome steel balls, G25, AISI 52100, 100 pack | https://www.amazon.com/dp/B07L8MLK2N | $6.65 | yes | next day (Sep 29) | 4.7 stars, 101 ratings | G25, 52100 (confirmed) | G10 25-piece https://www.amazon.com/dp/B081SQ1S3R, $5.69, 20 ratings (search result) |
| Neodymium disc magnets, 10 × 3 mm | PM p1, p1b; RP a1b, a2 | N52 D10 × 3 mm disc magnets, 60 pack | https://www.amazon.com/dp/B0GF7RLFXR | $23.99 | yes | overnight (Sep 29) | 4.8 stars, 24 ratings; 200+ bought in past month; Amazon's Choice | N52 grade stated (confirmed) | |
| Music wire, 0.025 in | PM p1 | K&S 5005 music wire, 0.025 in × 12 in, 4 wires | https://www.amazon.com/dp/B002WXNLI6 | $7.24 | yes | Fri Oct 2 | 4.7 stars, 750 ratings; only 11 left | 0.025 in straight lengths (confirmed) | |
| Small compression spring assortment | IH i3, i3b, i5 | Dianrui 300-piece compression spring kit, 23 sizes, 304 stainless | https://www.amazon.com/dp/B0BVTDP29W | $6.99 | yes | next day (Sep 29) | 4.6 stars, 1,030 ratings; 3K+ bought in past month; Amazon's Choice | Assortment (confirmed). Wire sizes not read | |
| Fine curved tweezers, ESD | TS a4, a5 | Best Tool ultra-fine curved-tip tweezers, non-magnetic, ESD safe | https://www.amazon.com/dp/B0BY7BDX41 | $12.76 | yes | Wed Sep 30 | 4.5 stars, 57 ratings; Amazon's Choice | Curved fine tip, ESD (confirmed) | |
| Smooth-jaw flat pliers | RP a5 | TEKTON PMN23001 mini flat nose pliers, smooth jaw | https://www.amazon.com/dp/B07CQ4M211 | $17.00 | yes | overnight (Sep 29) | 4.6 stars, 453 ratings; 100+ bought in past month; Amazon's Choice | Smooth jaw (confirmed) | Edge radius not stated |

## Items with no Prime listing found (2026-09-28)

- Terminal crimp press, 1.5–2 t, 110 V, for OTP applicators
- OTP side-feed applicator for XH chain contacts
- OTP XH crimper and anvil blade set
- JST WC-110
- SN-2549 replacement jaw set, sold alone
- Two-post guided die set
- XH contacts on carrier strip (reel)
- XH-mating IDC housing
- NEMA 17 worm-gear stepper
- Ground steel rod, 3 mm
- Crimp-height micrometer (point spindle with blade anvil)
- Drill blanks near 1.45 mm
- Vacuum pressure sensor module (XGZP6847 class)
- Weidmüller Stripax Plus 2.5
- Flat ribbon cable splitter tool
- Benchtop automatic stripping machine, small gauge, sensor-triggered
- Bambu laser module for the H2 series
- Spring steel strip, 1.0 and 1.5 mm

## Items skipped as generic

- LM8UU linear ball bearings (HT a4); the 8 mm rod and 10 mm bronze bushings above cover the guide
- GT2 open belt and flat rubber feed belts (HT a2; PM p1b, p3, p3b); pulleys above
- 608 bearings (PM p5)
- Bright 3 mm LEDs (TS a5)
- #3 scalpel handle (SL v6)
- 6 × 3 mm magnets (RP a1b, a2); the 10 × 3 mm N52 listing above shows the class

## Items requested later in the study

Observed **2026-09-28** in Derek's signed-in Chrome, with the conventions of the
tables above (Prime filter on every search, delivery for the account's default
address, "next day" = Tue Sep 29, **thin** = under about 50 ratings and no
bought-in-past-month line). These are the rows in each
`../explorers/*/sourcing-requests.md` that the tables above do not cover,
deduplicated across explorers. Every listing in a Listing and Link column was
opened. Where a page showed its Prime signal in some other way than a badge
beside the price of the variant named, the Caveat cell says how:
"FREE delivery … for Prime members" beside a delivery date on a page shipped by
Amazon, or the Prime logo on the variant's own row in the page's variant list.
"(search page)" marks a volume signal read from the Prime-filtered results
rather than the product page.

### Crimp, press and tooling

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Heavy disc springs, DIN 2093 series A, 35.5 × 18.3 × 2.0 mm | BM b1b, b1c; TS a1 and its K1 stop | Associated Spring Raymond metric chrome vanadium Belleville spring washers: 18.3 mm ID, 35.5 mm OD, 2.8 mm free height, 2.2 mm compressed height, 5,190 N max load, pack of 10 | https://www.amazon.com/dp/B005Y3A6FC | $5.37 ($0.54 each) | yes (see Caveat) | Sat Oct 3 | no ratings (thin); only 1 left | 5,190 N max load; chrome vanadium; page bullet "Physical Characteristics of Parts Comply with DIN 2093"; shipped and sold by Amazon.com (confirmed) | Prime signal is "FREE delivery … for Prime members" beside the date, with no badge beside the price; it appeared under the Prime filter |
| Heavy disc springs, spring steel, 20–31.5 mm OD | HT a4, a4b, a4c, a4d; SL station C; PM p5 and the b1b/p5 rod stack; FF f7; TS a2 | 20 pcs DIN2093 Belleville disc spring washers, 28 × 14.2 × 1.5 mm | https://www.amazon.com/dp/B0GL1C5H6Y | $11.99 | yes | next day (Sep 29) | 5.0 stars, 2 ratings (thin) | DIN 2093 in the title; material 60Si2MnA (confirmed). Load per disc not stated | The 25 × 12.2 × 1.5 mm size and other 20–25 mm OD heavy discs did not surface |
| NEMA 23 planetary gearbox, the 20:1 variant of the 10:1 row above | BM b1b | STEPPERONLINE planetary gearbox 20:1, backlash 20 arc-min, for 6.35 mm shaft NEMA 23 | https://www.amazon.com/dp/B0BPGNXJTJ | $79.00 | yes | next day (Sep 29) | 5 ratings (thin); only 7 left | Page table: max permissible torque 30 N·m, momentary 60 N·m; efficiency 94 %; 89.5 mm long (confirmed) | |
| Die springs, 16–20 mm OD, heavy load | PM p5b spring link, and the spring link between actuator and handle for BM b2 | Green heavy-load die spring, 20 mm OD × 10 mm ID × 25 mm | https://www.amazon.com/dp/B0FHGFR1S6 | $6.99 | yes | next day (Sep 29) | no ratings (thin) | Heavy load (green), 20 × 10 × 25 mm (confirmed). Rate and maximum deflection not stated | Title says 2 pieces, the package bullet says 5 |
| Small push-pull toggle clamp with a stated plunger stroke (GH-301 class) | SL v9b; FF f9, f9b | POWERTEC 301A push-pull toggle clamp, 100 lb holding, 2-pack | https://www.amazon.com/dp/B076H3WRLZ | $8.99 | yes | Wed Sep 30 | 4.4 stars, 656 ratings; 50+ bought in past month | 100 lb holding (confirmed) | Plunger stroke not found on the page |
| Mold ejector pins, 1.0–1.5 mm | FF f9b, f5b; RP K1, a10 | uxcell 10 pcs straight ejector pins, 1.5 mm × 150 mm, SKD61 | https://www.amazon.com/dp/B0CSDMLNVY | $9.09 | yes | Fri Oct 2 | 4.5 stars, 8 ratings (thin); only 3 left | SKD61, quenched and tempered, HRC 48–52; the page offers 24 diameters, 1 mm and 1.2 mm among them (confirmed) | uxcell 2 pcs 1.5 × 100 mm, https://www.amazon.com/dp/B0CSG187XQ, $7.59, 39 ratings (search result) |
| Precision ground tool-steel flat stock, O1 or A2 | FF f7, f5b, f10, FP1, FP2; CQ c6, c1c; HT a4b; SL v8, stations T and C; PM p1, p1d, p5, p5c, p7; RP K1, a2, a10 | O1 precision ground tool steel flat bar, 1/8 × 1-1/2 × 12 in, annealed | https://www.amazon.com/dp/B074PCLYLF | $27.95 | yes | Thu Oct 1 | 5.0 stars, 2 ratings (thin); only 16 left | O1, precision ground, annealed, oil hardening, 0.125 in thick (confirmed). Thickness tolerance not stated | 3/16 × 1-1/2 and 3/16 × 2 in O1 ground bars also appeared (search results). Thinner ground stock is in the no-Prime list below. PATIKIL 15N20 flat bar, 2 pcs, 1/16 × 1-1/2 × 12 in, 145 ratings, $9.79, is not ground (search result) |
| HSS parting blade, 1/16 in | FF f7; CQ c6 | HHIP 2000-6010 HSS parallel-type cut-off blade P1, 1/16 × 1/2 × 4-1/2 in | https://www.amazon.com/dp/B00N40478O | $15.99 | yes (see Caveat) | Mon Oct 5 | 4.4 stars, 196 ratings; Amazon's Choice | High-speed steel, parallel style P1, one beveled and one square end (confirmed) | Page bullet: a chip-breaker groove is ground along the blade's upper edge, so that edge is not flat. Prime signal is "FREE delivery … for Prime members", with the Prime logo on the size row. 3/32 in P2 blade, $10.19 (search result) |
| Plug pin gauges from 1.55 mm, and a 2.0 mm pin | CQ c6, c6b; HT a6b; IH k7; FF f6, f9b | HFS 190-piece minus pin gage set M1(−), 0.061–0.250 in | https://www.amazon.com/dp/B00UCQO4HM | $72.99 | yes | next day (Sep 29) | 423 ratings; 50+ bought in past month | 0.001 in steps from 0.061 in; 0.0002 in minus tolerance; HRC 60–62; 2 in long; sizes etched (confirmed) | Starts where the Accusize set above stops. 0.061 in = 1.549 mm, 0.063 in = 1.600 mm, 0.079 in = 2.007 mm [calc: inch to mm]; steps are 0.0254 mm, not 0.01 mm |
| Angle gauge block set | TS a5, a2d, a2 | Accusize 10-piece precision angle block set, 1–30°, EG02-0111 | https://www.amazon.com/dp/B00HZT7HNC | $42.00 | yes | Wed Sep 30 | 215 ratings; Amazon's Choice | 1° steps to 5°, 5° steps to 30°; ±30 arc-seconds; hardened and precision ground; 3 × 1/4 in blocks (confirmed) | |
| Cam follower, 16 mm, stud type (KR16 / CF6) | PM p5b, p5c | HARFINGTON 4 pcs CF6 (KR16) cam follower roller bearing, M6 × 1.0, 16 mm roller | https://www.amazon.com/dp/B0CJ4JD5H9 | $9.99 | yes | Thu Oct 1 | 4.4 stars, 33 ratings (thin); Amazon's Choice; only 3 left | 16 mm roller, 9 mm wide, 6 mm stud, M6 × 1.0 thread, bearing steel (confirmed). Dynamic load rating not stated | |
| Small constant-force springs, 5–20 N | IH i3b, i6 | SUS301 constant force spring, 2.62 lb load, 0.5 in wide, 0.0079 in thick, 24 in extended, pack of 5 | https://www.amazon.com/dp/B0DMM8YSMM | $35.99 | yes | Thu Oct 1 | 5.0 stars, 2 ratings (thin); only 9 left | 2.62 lb (≈11.7 N [calc]); ID 0.59 in, OD 0.82 in (confirmed) | Sibling listings ran 0.22–4.12 lb (≈1–18 N) at $29.99–42.50 (search results) |
| Compression springs with stated OD, wire and free length | IH i2d; HT a6b, a6c; CQ c1c | uxcell 5 pcs 304 stainless compression spring, 6 mm OD, 0.8 mm wire, 20 mm free length | https://www.amazon.com/dp/B0C33DD1WP | $6.49 | yes | Thu Oct 1 | 185 ratings; only 3 left | 6 mm OD, 0.8 mm wire, 20 mm free length (confirmed). Rate not stated | 6 × 0.8 mm springs in 10, 15, 25, 40 and 50 mm free lengths appeared in the same search. The 3–5 mm OD sizes for HT's 1–3 N seat were not opened |
| Module 0.5 gear rack and pinion | RP a8 | uxcell brass spur gear and gear rack 0.5 M, 18 T pinion, rack 10 × 5 × 300 mm, 4 mm bore | https://www.amazon.com/dp/B0GXJ9T8HT | $18.04 | yes | Thu Oct 1 | no ratings (thin); only 5 left | Module 0.5, brass (confirmed) | uxcell 0.5 module 45# carbon steel rack, 8 × 8 × 500 mm, $25.17, 8 ratings (search result) |
| Square steel pin or wire, 0.64 mm (0.025 in) | TS a6, x1, a4b, a4c, a5, x3; IH i6b, i2d″ (asked by IH and CQ) | 316 stainless square half-hard wire, 30 ft; 22 gauge variant, 0.64 × 0.64 mm | https://www.amazon.com/dp/B0G2LYBQTN | $9.99 | yes (see Caveat) | Fri Oct 2 (22 gauge) | 75 ratings (search page) | 0.64 × 0.64 mm square section in the variant list; 16 to 24 gauge offered (confirmed) | 316 stainless, half hard, not hardened steel, so tip wear over repeated spearing is open. The page opened on the 24 gauge variant; the 22 gauge row in its variant list carried the Prime logo |
| Stainless shim stock, 0.2–0.3 mm | PM valley tines (exchange on BM b1) | 30 pcs 304 stainless shim stock assortment, 1 × 6 in, 10 thicknesses 0.0007–0.010 in | https://www.amazon.com/dp/B0FP5CHK4N | $14.99 | yes | next day (Sep 29) | 4.6 stars, 42 ratings (thin); Amazon's Choice | 304 stainless, 10 thicknesses (confirmed) | Thickest leaf is 0.010 in (0.25 mm); the 1095 shim row above runs 0.005–0.032 in |
| Polyimide (Kapton) tape, 25–50 µm | HT a1, a6; PM, for the BM b2 blade electrode | APT 1 mil polyimide adhesive tape; variant shown 1 in × 36 yd | https://www.amazon.com/dp/B07HB81Q4L | $11.99 | yes | next day (Sep 29) | 4.7 stars, 1,141 ratings; 200+ bought in past month | 1 mil polyimide film (confirmed) | Total thickness with adhesive not stated; the 1/4 in width variant not read. A 4-pack of 1/8, 1/4, 1/2 and 1 in rolls, https://www.amazon.com/dp/B072Z92QZ2, $9.99, 2K+ bought in past month (search result) |
| Feeler gauge with long separate leaves | RP a7, a8 | Rannb metric feeler gauge, 12 in long, 17 blades, 0.02–1.00 mm | https://www.amazon.com/dp/B07DR83GX9 | $9.99 | yes | Wed Sep 30 | 4.4 stars, 573 ratings; Amazon's Choice | 12 in blades from 0.02 to 1.00 mm (confirmed) | Manganese steel with an oil coating, not stainless. "25 Blades Stainless Steel Long Feeler Gauge", https://www.amazon.com/dp/B0CG1LC57Y, $22.99, 100+ bought in past month (search result) |

### Contacts, housings and wire

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| 22 AWG silicone flat ribbon, 6 to 10 conductors | CQ c7 | BNTECHGO 22 AWG silicone ribbon cable 6P, black, 100 ft | https://www.amazon.com/dp/B09X47B2W6 | $62.98 | yes | Wed Sep 30 | 4.7 stars, 55 ratings; only 13 left | 22 AWG, 6 conductors, black; the same product family as the 3P, 4P and 5P on the bench (confirmed). Pitch and strand count not read | 6P 25 ft, $17.98, 102 ratings, next day (search result). 7, 9 and 10 conductors at 22 AWG are in the no-Prime list |
| JST XH straight through-hole header, 4 to 9 pin | PM p6, p4b, p1 (bench C) | Kidisoii XH 2.5 mm DIP header kit, 2–12 pin; "JST-2.5MM-XH-DIP-Vertical Header" variant | https://www.amazon.com/dp/B0CXMYPVNL | $10.69 | yes (see Caveat) | next day (Sep 29) | 4.8 stars, 8 ratings; 50+ bought in past month | Vertical XH DIP headers in 2 to 12 pin, 9 included (confirmed) | The page opened on the right-angle variant; the vertical variant's row carried the Prime logo at the same price. Genuine JST not claimed, and fit to the CQRobot housings is untested. Quantity per pin count not read |

### Motion and drive

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| 12 V self-locking worm gearmotor, 1.5–2 rpm, ≥7 N·m | BM b1c | BRINGSMART 12 V worm gear motor, self-locking; 12 V variants 5 to 470 rpm | https://www.amazon.com/dp/B07F8Y36PD | $28.97 (every variant) | yes (see Caveat) | next day (Sep 29) for 12 V 5 rpm | 4.2 stars, 140 ratings; 100+ bought in past month | Self-locking and reversible (title); "70kg.cm" appears on the page (confirmed) | Slowest variant is 5 rpm, and which speed the 70 kg·cm belongs to was not read; the 5 rpm row carried the Prime logo. MECCANIXITY 12 V 2 rpm reversible worm geared motor, 1:3000, 6 mm D shaft, https://www.amazon.com/dp/B0DP9WDRJ2, $21.89, Wed Sep 30, 1 rating, Prime, torque not stated |
| 12 V linear actuator, 500–750 N, faster than 10 mm/s | BM b2, b2b; PM, for BM b2 | Justech 750 N, 2 in / 50 mm, 12 V, with brackets | https://www.amazon.com/dp/B07M9Y2JHV | $30.99 | yes | next day (Sep 29) | 4.5 stars, 216 ratings; Amazon's Choice | Page table: 10 mm/s no load, 7 mm/s loaded; 0.8 A no load, 2.8 A max; limit switches; self-locking (confirmed) | No position feedback, and loaded speed equals the 1,500 N unit above. With feedback at this force and speed: no-Prime list |
| Pneumatic cylinder, 16 mm bore, 10–15 mm stroke | BM b1 (snatch route) | TAILONZ CDJ2B mini pneumatic cylinder, 16 mm bore × 10 mm stroke, with flange, Y connector and M5 fittings | https://www.amazon.com/dp/B0H416HRY2 | $14.99 | yes | Thu Oct 1 | 4.0 stars, 1 rating (thin); only 4 left | Double acting, single rod, M5 ports, 0.7 MPa max (confirmed) | A round pen cylinder, not a guided slide table |
| M8 inductive proximity switch | BM b1 (snatch route) | 5 pcs inductive proximity switch LJ8A3-2-Z/BX, NPN NO, M8, 3-wire | https://www.amazon.com/dp/B01LNOIAT4 | $21.99 | yes | next day (Sep 29) | 3.9 stars, 12 ratings (thin) | 2 mm ±10 % on iron; DC 6–36 V (confirmed) | |
| Air blow-off nozzle on a bendable stem | BM b1b, b1c; TS K2 | Baomain 1/4 in PT male Y-shape coolant hose, two 3 mm round nozzles, 11.8 in | https://www.amazon.com/dp/B01NBLE6HI | $6.99 | yes | Wed Sep 30 | 4.2 stars, 138 ratings; Amazon's Choice | Bendable segmented hose, 3 mm round nozzles, 1/4 in male thread (confirmed) | 3 mm bore, not the ~1 mm asked. A PT thread, so an adapter joins it to the 1/4 in push-to-connect line |
| Miniature linear stage, small stepper and lead screw, 10–50 mm | SL, for TS a2 + v1 (strip fence) and TS a5 (anvil Z) | Befenybay 50 mm mini linear rail guide, T6×1 lead screw, NEMA 11 motor | https://www.amazon.com/dp/B087NMCGPV | $54.80 | yes | Thu Oct 1 | 4.2 stars, 34 ratings (thin); Amazon's Choice | 50 mm travel; T6×1 (1 mm lead); 28 × 28 × 30 mm motor, 24 V, 0.5 A, 1.8°; 2.5 kg horizontal, 1 kg vertical (confirmed) | |
| NEMA 23 stepper with a DM542T driver, a second set | RP a1, a1c, a4 | STEPPERONLINE 1-axis kit: NEMA 23 2.4 N·m stepper and DM542T driver | https://www.amazon.com/dp/B0CS2TBLXP | $50.00 | yes | Wed Sep 30 | 5.0 stars, 2 ratings (thin) | Holding torque 2.4 N·m; driver 1.0–4.2 A, 20–50 VDC (confirmed) | 1.9 N·m kit with DM542T, https://www.amazon.com/dp/B0781GNX8W, $59.00, 16 ratings (search result) |
| DC motor H-bridge, BTS7960 class | PM, for BM b2 stall detection | HiLetgo BTS7960 43 A high-power motor driver module | https://www.amazon.com/dp/B00WSN98DC | $10.99 | yes | next day (Sep 29) | 4.1 stars, 280 ratings; 100+ bought in past month | BTS7960, 43 A (confirmed) | Current-sense outputs not stated in the bullets read |
| TMC2209 stepper driver modules | SL v7 (stack A) | BIGTREETECH TMC2209 V1.3, UART / step / dir, 5 pcs | https://www.amazon.com/dp/B07ZQ3C1XW | $26.99 | yes | next day (Sep 29) | 4.7 stars, 199 ratings; 100+ bought in past month; Amazon's Choice | TMC2209 with heatsinks, UART and step/dir (confirmed) | |
| ESP32 development boards | SL v7; PM p6, p4b, p5b, p5c | Hosyond ESP32-S3 N16R8 development board, 3-pack | https://www.amazon.com/dp/B0F5QCK6X5 | $18.99 | yes | Fri Oct 2 | 4.4 stars, 126 ratings; Amazon's Choice; 500+ bought in past month (search page) | ESP32-S3-WROOM-1, N16R8, USB-C (confirmed) | ESP32-S3 rather than the ESP32-WROOM DevKitC that PM names |
| Emergency-stop mushroom switch, NC | SL v7 | mxuteuk 22 mm red mushroom self-locking e-stop, 1 NC, HB2-BS542 | https://www.amazon.com/dp/B07R4J2Z54 | $8.99 | yes | next day (Sep 29) | 4.4 stars, 97 ratings; Amazon's Choice; 100+ bought in past month (search page) | 1 NC, self-locking, 22 mm (confirmed) | |
| PTFE tube, 1 mm ID × 2 mm OD | TS a4b | Quickun PTFE tubing, 1 mm ID × 2 mm OD, 10 ft | https://www.amazon.com/dp/B08Q83XNTT | $7.99 | yes | Wed Sep 30 | 4.6 stars, 130 ratings; Amazon's Choice | 1 × 2 mm (confirmed) | |

### Sensing and vision

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Load cell, 20 kg, with HX711 | HT a2d, a3, a4c, a6c; IH i3, i6, i6b, k8; SL station T (v8, v9); TS x2, x3, a4c | Geekstory 20 kg load cell with HX711 AD module | https://www.amazon.com/dp/B079FQNJJH | $8.98 | yes | Wed Sep 30 | 4.4 stars, 64 ratings; Amazon's Choice; only 11 left | 20 kg cell plus HX711 board (confirmed) | Bar form and mounting holes not stated in the bullets read |
| Load cell, 1 kg, with HX711 | TS a6 | ShangHJ 2 sets load cell with HX711; 1 kg variant | https://www.amazon.com/dp/B09K7G51KJ | $9.99 | yes | next day (Sep 29) | 4.0 stars, 15 ratings (thin) | 1 kg variant selected; HX711 included (confirmed) | The same page lists capacities up to 50 kg, the range HT a1 and a6 ask for; those variants' Prime status not checked |
| 24-bit ADC breakout, ADS1220 | BM b1, b1b, b1c; SL v7 (stack C), v8 | ADS1220 24-bit ADC converter module, SPI | https://www.amazon.com/dp/B0DPMKMGNN | $14.99 | yes | next day (Sep 29) | 4.5 stars, 6 ratings (thin) | ADS1220, up to 2,000 SPS (confirmed) | |
| 14-bit SPI magnetic angle encoder (AS5047P class) | BM crank-angle combinations; SL v3, v9, v7 (stack C) | AS5047P encoder module, 14-bit, SPI / ABZ / UVW / PWM | https://www.amazon.com/dp/B0H15G7NPX | $11.99 | yes | next day (Sep 29) | 5.0 stars, 5 ratings (thin) | AS5047P, 14-bit, SPI (confirmed) | Page: "diametrical magnet not included" |
| 0.001 mm indicator with a data route to a computer | FF f3, f6, f7, f9b, f10; HT a4, a4c; SL station C | AICEYI digital dial gauge ACE-Q25, 0–25.4 mm, 0.001 mm, with output interface | https://www.amazon.com/dp/B0CSCPMNDJ | $109.99 | yes | Thu Oct 1 | 4.3 stars, 6 ratings (thin) | 0.001 mm resolution; output-interface bullet (confirmed) | Its cable, AICEYI "Rs231 Data Cable for Digital Dial Indicators", https://www.amazon.com/dp/B0F3J171Y5, $39.99, Prime, Thu Oct 1, 2 ratings: mini USB, "for AICEYI digital displays", data into Excel without drivers. Whether it presents as a keyboard or a serial port is not stated |
| Digital hanging scale, 50 kg | HT a6; RP a2d, a10b, a9 | SKEAP 110 lb / 50 kg digital hanging scale | https://www.amazon.com/dp/B09PQB73JD | $9.98 | yes | next day (Sep 29) | 4.4 stars, 3,786 ratings; 4K+ bought in past month; Amazon's Choice | 5 g (0.01 lb) increment; data lock (confirmed) | Peak hold not stated; data lock holds a steady reading. "Bow Scale Equipped with Peak Holding Display, 110 lb / 50 kg", $69.99 (search result) |
| Small mirror for a 45° side view (precut first-surface mirror, 10–25 mm) | SL v9, v9b, v5 | 25 mm K9 glass right-angle prism, coated reflecting hypotenuse | https://www.amazon.com/dp/B08HR5P9V2 | $16.95 | yes | Thu Oct 1 | 4.8 stars, 21 ratings (thin) | 25 × 25 × 25 mm, K9, reflective coating on the long side (confirmed) | A prism mirror, not a first-surface mirror. 25 mm molybdenum CO₂-laser mirrors (bare metal faces), e.g. "Mo Mirror Dia 25 mm, Thk 3 mm", $30.59, 140 ratings, 50+ bought in past month (search result); visible reflectance not stated |
| White diffuser sheet, 1 mm | SL, for the TS–SL backlight vane | Qlvily LED light diffuser board, 11.8 × 7.8 × 0.04 in, 4-pack | https://www.amazon.com/dp/B0H69667R6 | $13.99 | yes | Fri Oct 2 | 4.8 stars, 6 ratings; 50+ bought in past month | 0.04 in (≈1.0 mm) diffuser board (confirmed); material given only as plastic | Evenness when lit from an edge not stated |
| Small LED backlight tile | TS a2d, x2, a6; PM p1c, p6, p7 | Adafruit 1626 LED backlight module, 12 × 40 mm, white, 2-pack | https://www.amazon.com/dp/B01N6XME2Q | $8.42 | yes | Wed Sep 30 | 4.2 stars, 30 ratings (thin) | 12 × 40 mm lit area; rigid (confirmed) | |
| Narrow-beam 3 mm white LEDs, 15–20° | SL v8, v9, v9b, v1 | CHANZON 100 pcs 3 mm white LED, clear round lens, 3 V 20 mA | https://www.amazon.com/dp/B01AUI4VR4 | $6.99 | yes | Fri Oct 2 | 4.6 stars, 908 ratings; Amazon's Choice | Clear lens, 6000–9000 K (confirmed) | Viewing angle not read |

### Stripping, splitting and laser

| Item | Serves | Listing | Link | Price | Prime | Delivery | Volume signals | Capability that mattered | Caveat |
|---|---|---|---|---|---|---|---|---|---|
| Precision die-hole stripper with a 20–22 AWG hole | BM b7, b2b | Ideal Stripmaster wire stripper, 30–20 AWG, 6-1/2 in, model 45-098 | https://www.amazon.com/dp/B000B5Y9YM | $55.68 | yes | Thu Oct 1 | 4.7 stars, 124 ratings; only 11 left | Wire gripper holds the wire centered in the hole; strips up to 7/8 in (22 mm) (confirmed) | Replacement blades for this model: no-Prime list |
| Precision hand stripper for fine gauges | BM b7, b2b | ENGINEER PA-14 precision wire stripper, made in Japan | https://www.amazon.com/dp/B001YHELPS | $28.30 | yes | next day (Sep 29) | 464 ratings; 200+ bought in past month | Stranded AWG 34–22, solid AWG 32–20; round finishing edge (confirmed) | Blades are part of the plier |
| Knife tip for the Hakko FX-888D (T18 series) | BM b7 | Hakko T18-K soldering tip, knife blade, 5.0 × 14 mm | https://www.amazon.com/dp/B004ORB8MY | $16.83 | yes | Wed Sep 30 | 146 ratings; only 1 left | Hakko store listing; model T18K (confirmed) | |
| Hobby ultrasonic cutter, ~40 kHz, replaceable blades | BM b7, b6 | HOZO NeoBlade wireless ultrasonic cutter, 40 kHz, 40 W | https://www.amazon.com/dp/B0FK9SB5KR | $149.99 | yes | next day (Sep 29) | 4.2 stars, 363 ratings; 700+ bought in past month | 40 kHz; six SK5 blades (standard, long, chisel, mini chisel, curved, double edge); replaceable battery (confirmed) | Cutting silicone rubber not stated |
| Laser safety glasses, OD 6+ at 445–455 nm | BM b4b, b4 | FreeMascot OD 6+ 190–490 nm laser safety glasses | https://www.amazon.com/dp/B07DCRR8NG | $26.99 | yes | next day (Sep 29) | 4.6 stars, 783 ratings | OD 6+ across 190–490 nm, listed for 445 and 450 nm (confirmed) | Certification not read |
| Laser safety panel for 445–455 nm | PM, for the enclosure of BM b4's station laser | YIBEICO OD7+ laser safety shield panel for diode engravers, 12 × 8 × 0.2 in | https://www.amazon.com/dp/B0FFGLMT4J | $49.98 | yes | next day (Sep 29) | 4.6 stars, 5 ratings (thin) | Blocks 200–540 nm, OD7+ (confirmed) | |
| Double-edge razor blades, 100 | RP a7, a7b, a8b | Astra Platinum double-edge safety razor blades, 100 (20 × 5) | https://www.amazon.com/dp/B001QY8QXM | $8.88 | yes | Wed Sep 30 | 4.6 stars, 55,603 ratings; 10K+ bought in past month; Amazon's Choice | 100 double-edge blades (confirmed) | Blade thickness not stated |
| Small wire straightener | RP a4, a9 | Y-II wire straightener, 5 bearings, flip-open body | https://www.amazon.com/dp/B0FMNN8CNH | $14.98 | yes | Fri Oct 2 | 3.8 stars, 40 ratings (thin) | 5 rotating metal bearings; 8 × 2.5 × 2 cm (confirmed) | Sold for round jewelry wire; whether it takes a 7–15 mm flat ribbon is not stated |
| Bench cut-to-length machine able to take flat cable | RP a4 (asked by BM) | Automatic wire stripper machine, computer wire peeling and cutting, 110 V, touchscreen, 0.5–30 mm stripping length | https://www.amazon.com/dp/B0FFMPK4K2 | $1,499.00 | yes | Fri Oct 2 (scheduled delivery) | rating count not shown (thin); only 2 left | Touchscreen length entry; built-in wire straightener (confirmed) | Flat-cable guide width, wire range and a cut-only mode not read |

### Also serves

New requests for items the earlier tables already cover:

- **SN-2549 replacement jaw set, sold alone** (no Prime): SL v8.
- **OTP XH crimper and anvil blade set** (no Prime): FF f3, f4, f6, f7; RP a2, a2d.
- **Two-post guided die set** (no Prime): FF f7, f5b.
- **Benchtop automatic stripping machine, sensor-triggered** (no Prime): BM b7.
- **NEMA 17 worm-gear stepper** (no Prime): PM p5b.
- **Clockwise DITR-0105 indicator** (DTCR-01 cable not on Prime; see the AICEYI row above): FF f3, f6, f7, f9b, f10; HT a4, a4c; SL station C.
- **PA-01-POT 750 N actuator with feedback**: BM b2, b2b; PM, for BM b2.
- **LASER TREE 10 W diode module**: BM b4b; PM, as a standalone module for BM b4.
- **Hotop feeler gauge set**: FF f1, f3, f6; HT a1, a6; IH i2d; PM p1c, p4b, p5b, p6; RP v3 × a2b stop-block shims; TS a6, a4b, a2b.
- **1095 blue-tempered shim assortment**: HT a1, a6; FF laminated fin.
- **XIAOSTAR A5 light pad**: FF f6; PM p1c, p6, p7; RP a7, a8; TS a6, a3.
- **Accusize pin gauge set (to 1.52 mm)**: RP a8, a8b.
- **Dianrui compression spring assortment**: CQ c1c; HT a6.
- **Miuzei MG90S and Deegoo MG996R servos**: PM p1c, p4b, p6; RP a1; TS a6, a2.
- **ZOSKAY DS3235 servo**: CQ c6; SL v8.
- **MGN12 rail**: TS a6. **Heschen HS-0530B solenoid**: CQ c1, c1c; TS a6.
- **TEMCo foot switch**: PM p6, p4b. **2.54 mm header strips**: PM p1c, p5b, p6.
- **MKS DLC32**: SL v7 (stack B). **BTT SKR Pico**: SL v7 (stack C).
- **AS5600 boards**: BM b1c. **500 kg button cell** and **10:1 NEMA 23 planetary**: SL station C.
- **HSS 3 mm square blanks**: SL v8. **Engineer PA-09**: CQ c6b.
- **Wago 221-415** and **6-circuit slip ring**: CQ c1c; the slip ring also RP a4.
- **#11 scalpel blades** and **K&S 0.025 in music wire**: BM b6.
- **GT2 pulleys** and **600 P/R encoder**: BM b8. **N20 encoder gearmotor**: RP a8b.
- **Beduan 12 V NC valve**: RP a8. **TAILONZ 5/2 valve**: TS K2.
- **POWERTEC 305CM toggle clamps**: FF f9, f9b; RP K1. **VEVOR AP-1 arbor press**, **6 mm chrome balls** and **N52 magnets**: RP K1, a9, a10.
- **HiLetgo roller microswitches**: SL v7 lid interlock.

### Items with no Prime listing found (2026-09-28), requested later

- 12 V linear actuator with position feedback, 500–750 N, ≥10 mm/s loaded
- 22 AWG silicone flat ribbon with 7, 9 or 10 conductors
- Precision ground O1 or A2 flat stock or gauge plate at 1/16 in (1.59 mm), 1.5 mm, 0.075 in and 3/32 in
- Hardened and ground alloy dowel pins, 3–6 mm, h6 or m6
- Replacement die blades for a 20–30 AWG die-hole stripper
- Wire stripping and twisting machine
- OTP side-feed applicator for 6.3 mm Faston female on reel
- HX717 load-cell amplifier module
- Soft bellows suction cup or bellows nozzle, 2–3 mm
- Phosphor bronze sheet, 0.1–0.2 mm
- Knurled or serrated steel strip, or small serrated gripper pads
- Steel round bar, 50–60 mm diameter, short length

### Items skipped as generic, requested later

- Sewing machine needles 80/12 and 90/14 and seam rippers (BM b6)
- Music wire 0.2–0.6 mm (BM b6 needles and harp); the K&S 0.025 in row above shows the family
- 2020 aluminium extrusion with T-nuts (PM p6, p3)
- 6700ZZ bearings, closed-loop GT2 belts and 3 mm-bore GT2 pulleys (RP a8b)
- Small 12/24 V solenoid air valve with 1/8 in ports (RP a8); the Beduan valve row above shows the class
- Powered USB 3 hub with per-port switches, 6 V 5–10 A servo supply, small UPS (SL v7)
- 1–3 mm frame-sync LEDs (SL v7); 5 mm LEDs and an active buzzer (HT a6)
- Non-insulated ring or fork terminals for 22 AWG (RP, v3 coupons)
