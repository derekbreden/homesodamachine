# Where the parts come from

Every part the arrangements lean on, gathered by function, with where it was
seen, what it cost, how fast it comes, and what the page showed about volume.
Explorer codes and idea ids are those of the [ideas index](../ideas-index.md),
where every id links to its file.

**How the parts were checked**
- **Amazon.** Every Amazon row comes from
  [`sourcing/amazon-prime.md`](amazon-prime.md). Each listing was
  opened in Derek's signed-in Chrome on 2026-09-28 and had the Prime badge
  beside the price on its own product page.
  - Rows marked "Prime search" carried the badge in Prime-filtered results;
    their pages were not opened.
  - A few pages showed Prime another way: a "FREE delivery … for Prime
    members" line, or the Prime logo on the variant's own row. Those rows say
    so.
  - Delivery dates are what Amazon showed that day; "next day" is Tue Sep 29.
  - Only Prime listings count for this project.
- **Other vendors.** Distributor stock and prices (Digi-Key, Newark, TME,
  Heilind) come from the findchips aggregator, and LCSC's from its own pages,
  gathered by the facts pass ([`context/xh-facts.md`](../context/xh-facts.md)
  §6). Everything else is as each explorer labelled it:
  - **page:** the vendor's page was fetched;
  - **search:** only a search-result summary was read. eBay, Alibaba and
    AliExpress refused fetches, so every figure from them is a search
    summary;
  - **web:** the explorer recorded a web source without saying which.
- **Volume.** A listing's existence, or a familiar brand, is not evidence of
  volume.
  - On Amazon the volume column carries only what the page showed: ratings
    count, "N+ bought in past month" (written "N+/mo"), Amazon's Choice (AC)
    and "only N left".
  - **Thin** means fewer than about 50 ratings and no bought-in-past-month
    line.
  - For distributors, volume is units in stock.
- All observations are dated 2026-09-28. Nothing was ordered and no vendor
  was contacted.

**Explorer codes:** **HT** [hand-tool-as-press](../explorers/hand-tool-as-press/summary.md) ·
**TS** [terminal-supply](../explorers/terminal-supply/summary.md) ·
**FF** [force-and-form](../explorers/force-and-form/summary.md) ·
**RP** [ribbon-as-pallet](../explorers/ribbon-as-pallet/summary.md) ·
**IH** [into-the-housing](../explorers/into-the-housing/summary.md) ·
**BM** [borrowed-machines](../explorers/borrowed-machines/summary.md) ·
**PM** [procedure-is-the-machine](../explorers/procedure-is-the-machine/summary.md) ·
**SL** [machine-that-sees-and-learns](../explorers/machine-that-sees-and-learns/summary.md) ·
**CQ** [change-the-question](../explorers/change-the-question/summary.md) ·
**ctx** the prior-art pass ([`context/prior-art.md`](../context/prior-art.md), § section).

## What the parts landscape looks like

**Plentiful and immediate**
- **Genuine contacts and housings at distributors.**
  - SXH-001T-P0.6 (strip form):
    - Digi-Key: 1,329,000 on reels, and 100-piece strips at $4.71 with 3,100
      in stock.
    - Also Newark, TME, Heilind, and LCSC ($0.0127 at 100).
  - Clone reels at LCSC from $0.0073 a contact.
  - XHP-4 to XHP-7 sit in the tens to hundreds of thousands. XHP-9 is thinner
    (3,408 at Digi-Key, 260 at LCSC).
  - The whole program, about 3,200 crimps, is under half of one 8,000 reel.
- **Tools on Prime, delivered Sep 29 to Oct 3:**
  - the iCrimp SN-2549 (532 ratings, 100+/mo);
  - a genuine Engineer PA-09 (1,719 ratings, 200+/mo);
  - the CQRobot kit the bench uses;
  - VEVOR arbor presses: 1 t at 300+/mo; the 3 t models at 28–44 ratings.
- **Commodity parts on Prime, same delivery window:**
  - NEMA 17 lead-screw steppers and NEMA 23 gearboxes;
  - servos, and bar load cells with HX711;
  - MGN rails, pneumatic cylinders and valves;
  - cameras and light pads;
  - pin gauges, 1095 shim and a ground O1 bar at 1/8 in.
- **Quick-turn services:**
  - [JLCPCB](https://jlcpcb.com/pcb-stencil) 304 stainless stencils from $3,
    shipped in about a day;
  - [SendCutSend](https://sendcutsend.com/materials/mild-steel/) laser-cut
    steel in 2–4 days;
  - JLCPCB boards for post beds and header nests.
- **Already on the bench** [repo: `hardware/ledger/tools.md`], so nothing is
  bought:
  - the SN-2549 and the idle VEVOR 12-ton press;
  - a NEMA 23 with DM542T and the ELP 16 MP camera;
  - the two H2C printers, the caliper and the 0.1 g scale.

**Reachable only with shipping time or quotes**
- **XH steel for a press.**
  - The OTP side-feed "XH2.54" mini-applicator:
    - eBay: $150–167 plus $80–91 shipping;
    - Alibaba: $200–250;
    - Sanao: $125–150.
  - Its knife set: listing titles only, price not read.
  - Both come from China, in days to weeks. Neither has a Prime listing, so
    every arrangement tagged "bought mini-applicator or knife set" in the
    index waits on this route.
- **Presses made for applicators.**
  - Sanao's 1.5–2 t mute press: $310, freight "contact supplier".
  - eBay: $968. Zonesun: $950–2,079. ETCO Mighty-T: $2,950.
  - JST AP-K2N: $12,500, with a 116-day lead.
- **Made dies.** Wire EDM at JLCCNC (±0.05 mm stated) or Xometry ("in days").
  No price observed: ~$50–200 a part and 1–3 weeks [estimate,
  [FF f7](../explorers/force-and-form/ideas/f7-where-the-steel-comes-from.md)].
- **JST's own tools.**
  - WC-110: in stock at Digi-Key ($536.51, 147 units).
  - YRS-110: $1,565.93.
  - JST applicators: 0 in stock ($3,439.52 and $4,599.36).
- **Other items off Amazon:**
  - Bambu's H2C laser kit ($698 or $1,348), in stock at 3D Universe;
  - a Dobot MG400 ($2,890–3,495, backorders allowed);
  - StepperOnline's NEMA 23 with 30:1 worm (C$76.69, ships in 24 h);
  - a wiper gearmotor with a two-week lead;
  - Mitutoyo SPC indicators ($451–668);
  - Misumi guide-post sets (not priced).

**Not found anywhere.** None of these had a Prime listing, and no explorer
recorded another source.
- **Parts:**
  - an IDC housing that mates the XH wafer (JST's KR is PH's IDC twin; nothing
    for XH);
  - a point-and-blade crimp-height micrometer (Prime has a point micrometer and
    a blade micrometer, each alone);
  - a flat-ribbon splitter hand tool near 1.7 mm pitch;
  - 22 AWG silicone ribbon in 7, 9 or 10 conductors;
  - a hardened 0.64 mm square steel pin (Prime has only half-hard 316
    stainless);
  - a 12 V actuator with position feedback at 500–750 N and ≥10 mm/s loaded.
- **Stock:**
  - ground O1 or A2 at 1/16 in, 1.5 mm, 0.075 in or 3/32 in;
  - hardened h6 dowels at 3–6 mm;
  - 1.0 and 1.5 mm spring-steel strip;
  - a 50–60 mm round bar;
  - 0.1–0.2 mm phosphor bronze;
  - knurled strip.

  A McMaster-class supplier is assumed for these and none was priced
  [assumption, [FF f3](../explorers/force-and-form/ideas/f3-knee-micropress.md)].
- **Small items:**
  - an XGZP6847 vacuum sensor, an HX717 board and a 2–3 mm bellows cup;
  - the DTCR-01 cable for the Clockwise indicator;
  - a Hakko G4 blade for 22 AWG;
  - die blades for a 20–30 AWG die-hole stripper;
  - a DIN 2093 25 × 12.2 × 1.5 mm disc.
- **Numbers that are not public.** These are the numbers behind the parts:
  - JST's crimp height for SXH-001T-P0.6;
  - the SXH carrier pitch;
  - XHP insertion and retention forces.

  They sit behind JST's licence form [mfr, xh-facts §1–3]. The Würth analog
  drawing (7.10 mm pitch) stands in for the pitch until one $4.71 strip is
  under a caliper.

## Contacts and housings

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| SXH-001T-P0.6, genuine, cut strip in 100 / 500 / 1,000 lots | Digi-Key 455-1135-100/-500/-1000-ND | $4.71 a strip of 100 ($0.0471); $0.0421; $0.0401 | 3,100 / 2,500 / 5,000 | 09-28, aggregator | Genuine JST. One 100-strip ≈ 1.9 units; it is also the measuring strip for pitch, pilot hole, tab and wing width | every **S** and **L/S** arrangement in the index; the measuring strip in TS a7, BM b1b, HT a2, RP a2, a10b, SL v3 | [Digi-Key](https://www.digikey.com/en/products/detail/jst-sales-america-inc/SXH-001T-P0-6/527371) · [findchips](https://www.findchips.com/search/SXH-001T-P0.6) |
| SXH-001T-P0.6, reel of 8,000 | Digi-Key 455-1135TR-ND | $0.0235 each (~$188 a reel) | 1,329,000 | 09-28, aggregator | ~150 units a reel | TS a1, a2d; BM b1, b8b; RP a1, a2; SL v9 | [findchips](https://www.findchips.com/search/SXH-001T-P0.6) |
| SXH-001T-P0.6 at other distributors | Newark (cut / reel); TME; Heilind; LCSC C140573 | Newark $0.0556 at 1, $0.039 at 201, $0.019 at 8k; TME from $0.0215 at 200; Heilind $0.0305 cut, $0.0227 reel; LCSC $0.0127 at 100, $0.0100 at 1k | Newark 236,854 cut, 1,624,000 reel; TME 137,204; Heilind 732,000 reel, 39,000 cut, 10,695 loose; LCSC 406,500 | 09-28, aggregator; LCSC page | The same JST part at five distributors | as above | [LCSC](https://www.lcsc.com/product-detail/C140573.html) |
| Clone contacts on reel: CJT A2501-TP, DLL TJC3-T, HDGC2501-T | LCSC | $0.0079; $0.010; $0.0073 | 665,523; ~8,800; 6,338 | 09-28, LCSC page | Drawings agree with JST's outline (0.20 mm C5191, 5.8–6.7 mm long). Insulation wings drawn 2.46–3.0 mm open, wider than JST's 1.95 mm envelope. Reels hold 7,000–15,000; pitch and lance vary by maker | FF f2; TS a1, a2, a2d, a7; BM b1, b2b, b8b; CQ c4 | [CJT](https://www.lcsc.com/product-detail/housing-contact_cjt-changjiang-connectors-a2501-tp_C339286.html) · [DLL](https://www.lcsc.com/product-detail/housing-contact_dll-tjc3-t_C22374382.html) · [HDGC](https://www.lcsc.com/product-detail/housing-contact_hdgc-hdgc2501-t_C5292543.html) |
| BXH-001T-P0.6, genuine loose piece | Digi-Key; Newark 73M9274; TME; LCSC C594456 | $0.0444 at 50, $0.0423 at 100; $0.0455; $0.0420; $0.0705 | 137,303; 300,647; 48,717; 400 | 09-28, aggregator; LCSC page | Loose form of SXH. Digi-Key's description says 22–26 AWG; Newark, TME and JST say 28–22 | HT a2b; BM b2b; RP a2c; FF f1b; CQ c4; TS a7 | [findchips](https://www.findchips.com/search/BXH-001T-P0.6) · [LCSC](https://www.lcsc.com/product-detail/C594456.html) |
| SXH-001T-P0.6N, low insertion force | Digi-Key | $0.0299 on a 5k reel; $0.0579 in the 100 lot | 140,000; 3,900 | 09-28, aggregator | JST: "less resistant to the vibration" [mfr] | CQ c4 (as an option) | — |
| CQRobot "JST XH 2.54 mm" kit, housings plus loose contacts | Amazon (Prime) | $10.99 for the 2P/3P/4P set (30 each of header and housing, 280 contacts); single sizes $7.99–8.99 | next day | 09-28, Prime page | 4.6★, 167 ratings, AC. JST genuineness not claimed on the page | every explorer (the contacts on hand); IH i2d (an XHP-2 stub) | [amazon](https://www.amazon.com/dp/B0731NHS9R) |
| XHP-4 / 5 / 6 / 7 / 9 housings, genuine | Digi-Key 455-2267/2268/2218/2269/2217-ND; Newark; LCSC | Digi-Key $0.0584 / 0.0646 / 0.0748 / 0.0826 / 0.1226 at 50; LCSC $0.0246–0.0488 | Digi-Key 126,939 / 19,566 / 106,462 / 70,162 / 3,408; Newark 893,374 / 363,896 / 292,105 / 40,447 / 7,725; LCSC 3,637 / 7,786 / 22,915 / 8,450 / 260 | 09-28, aggregator; LCSC page | PA 6. Clone housings (CJT A2501H) match body width and depth, and are PA 66 | every arrangement that inserts; CQ c5 | [XHP-4](https://www.findchips.com/search/XHP-4) · [XHP-9](https://www.findchips.com/search/XHP-9) (findchips) |
| XH headers B4B-XH-A, B9B-XH-A, as test wafer and nest | Newark; TME; Digi-Key | B4B $0.0722–0.2770; B9B $0.1747–0.3400 | B4B: Newark 171,802, TME 22,053. B9B: Digi-Key 44,226, Newark 54,182 | 09-28, aggregator | JST says to check continuity only against the applicable header [mfr] | IH i5; HT a2d, a6; PM p1, p4b, p6, p6b; CQ c1; BM b2b; RP a9 | — |
| Kidisoii XH 2.5 mm vertical DIP header kit, 2–12 pin | Amazon (Prime, logo on the variant row) | $10.69 | next day | 09-28, Prime page | 4.8★, 8 ratings, 50+/mo. Genuine JST not claimed; fit to the kit housings untested | PM p1, p4b, p6 | [amazon](https://www.amazon.com/dp/B0CXMYPVNL) |
| JST ASXHSXH22K305, 22 AWG socket-to-socket lead, 12 in | Digi-Key | $0.90; $0.765 at 10; $0.65 at 100 | 26,279 | 09-28, page | A genuine factory crimp to measure. Black discrete wire; insulation type not given | CQ c2; the reference crimp in IH i2, i5, k7, FF f1b, f2, HT a1b, PM p6, TS a7 | [Digi-Key](https://www.digikey.com/en/products/detail/jst-sales-america-inc/ASXHSXH22K305/6684932) |
| JST-XH balance leads, 22 AWG silicone: XH-5 200 mm (5 pcs); XH-9 30 cm (10 pcs) | Amazon (Prime) | $8.99; $13.99 | overnight | 09-28, Prime page | 376 ratings, 50+/mo, AC; 32 ratings, AC. Wires are separate, not bonded flat. 500–600 mm at 22 AWG not found | CQ c2 | [XH-5](https://www.amazon.com/dp/B07Q29TG24) · [XH-9](https://www.amazon.com/dp/B08L36NDVX) |
| Pre-crimped single XH wires, 22 AWG silicone, 6 colours × 15 | Amazon (Prime) | $16.99 | overnight | 09-28, Prime page | 95 ratings, 100+/mo, AC. Length not stated; not black-only | CQ c2 | [amazon](https://www.amazon.com/dp/B0CM315RFP) |
| BNTECHGO 22 AWG silicone ribbon, 6P, 100 ft | Amazon (Prime) | $62.98 | Sep 30; only 13 left | 09-28, Prime page | 55 ratings. Same family as the 3P/4P/5P on the bench; pitch and strands not read. 25 ft at $17.98, 102 ratings (Prime search) | CQ c7 | [amazon](https://www.amazon.com/dp/B09X47B2W6) |
| JST XJ-06 extraction tool | Digi-Key | $63.69 | 20 | 09-28, aggregator | Genuine; fits SXH-001T-P0.6 and P0.6N | CQ c2 (J2's cavity 3) | [findchips](https://www.findchips.com/search/XJ-06) |
| JRready pin removal kit with XH2.54 tip | Amazon (Prime) | $34.00 | next day; only 18 left | 09-28, Prime page | 1 rating (thin) | CQ c2 | [amazon](https://www.amazon.com/dp/B0H25W39YS) |

- **No Prime listing:** XH contacts on strip or reel; an XH-mating IDC housing
  ([CQ c4](../explorers/change-the-question/ideas/c4-parts-that-mate-the-wafer.md));
  22 AWG silicone ribbon in 7, 9 or 10 conductors
  ([CQ c7](../explorers/change-the-question/ideas/c7-straight-across.md)).
- **Carrier-strip analog.** Würth's WR-WTB 2.50 mm contact drawing gives pitch
  7.10 mm, carrier 3.00 mm and Ø1.50 pilots, with 10,000 to a reel
  ([drawing](https://www.we-online.com/components/products/datasheet/64600113722.pdf)).
  It is not an XH part: its box is 1.45 × 2.00 mm.
- **Open here.**
  - Whether the CQRobot contacts are JST or clone is unknown. Their open
    wing width decides which arrangements they suit
    ([CQ c4](../explorers/change-the-question/ideas/c4-parts-that-mate-the-wafer.md),
    [TS a7](../explorers/terminal-supply/ideas/a7-if-the-contacts-switch-to-strip.md)).
  - Strip-fed arrangements (tagged **S** in the index) get their contacts only
    from distributors: no Prime listing sells XH strip or reels.

## Crimp tooling and dies

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| iCrimp SN-2549 ratcheting crimper, XH nest, AWG 28–18 | Amazon (Prime) | $22.29 | overnight | 09-28, Prime page | 4.5★, 532 ratings, 100+/mo, AC. A second iCrimp listing: 194 ratings, 50+/mo (Prime search) | BM b2; FF f1, f4; HT a1, a2, a3; RP a2, a2b, a2d; PM p6; every "SN-2549 or similar hand-tool dies" arrangement in the index | [amazon](https://www.amazon.com/dp/B01N4L8QMW) · [second](https://www.amazon.com/dp/B01N1RFZZ4) |
| iCrimp SN-2549, direct | icrimptools.com; TH3D | $20.99; $17.99 | — | 09-28, web | Jaws are wire-EDM cut and held by two screws (2.5 mm hex) | FF f1; HT a1 | — |
| SN-series jaw set alone, 2549 profile | icrimptools.com | $4.99–9.99 a set | days (FF f7) | 09-28, web | No Prime listing sells the jaws alone. The SN chassis is shared across the SN tools | FF f3 (route a), f7; HT a4, a4b, a4c, a6c; SL v8 | — |
| iCrimp IWS-0723K 7-piece set with a 2549 die | Amazon (Prime) | $46.59 | Sep 30 | 09-28, Prime page | 9 ratings (thin). Five interchangeable dies. The only Prime route to a loose 2549 die, and it comes in a frame | BM b2; FF f3; HT a4 | [amazon](https://www.amazon.com/dp/B09CP8RV94) |
| Engineer PA-09 micro connector plier, no ratchet | Amazon (Prime) | $38.99 | next day; only 18 left | 09-28, Prime page | 4.5★, 1,719 ratings, 200+/mo, AC. Genuine, made in Japan. Dies 1.0 / 1.4 / 1.6 / 1.9 mm. Engineer lists it for SXH- and BXH-001T-P0.6 [mfr] | HT a5; IH i1; CQ c6b; SL v3 | [amazon](https://www.amazon.com/dp/B002AVVO7K) |
| JST WC-110 with flap locator; WC-110P spare locator | Digi-Key; Newark; TME | $536.51; $668.99; $564.96. WC-110P $51.23 | 147; 49; 15. WC-110P 15 | 09-28, aggregator | Genuine. No Prime listing | FF f1b; HT a1 (drops into its cradle); BM b2 | [Digi-Key](https://www.digikey.com/en/products/detail/jst-sales-america-inc/WC-110/527372) |
| JST YRS-110 (strip form); YC-110R / YC-111R | Digi-Key | $1,565.93; $702.51 / $714.00 | 9; 1 / 0 | 09-28, aggregator | JST calls its hand tools prototype and repair tools, with fixed dies [mfr] | RP a2 (reference) | [findchips](https://www.findchips.com/search/YRS-110) |
| OTP side-feed mini-applicator, "XH2.54" | eBay; Alibaba; Sanao (Made-in-China) | eBay $150–167 plus $80–91 shipping; Alibaba $250 for 1–4, $200 for 5+; Sanao $125–150 | from China, days to weeks; no Prime listing | 09-28, search (eBay, Alibaba); page (Sanao) | OTP-standard mount. Which XH contact its tooling is cut for is unknown, probably a clone [assumption]. Post-feed and pre-feed cam positions are unconfirmed on OTP units | TS a1; FF f2, f2b, f2c; BM b1, b1b, b1c, b8, b8b; RP a1, a1c, a2e, a4, a9; PM p6b; SL v9, v9b | [eBay](https://www.ebay.de/itm/405412063260) · [Sanao](https://sanaoelectronic.en.made-in-china.com/product/LtTrEpiOqDkW/China-1-5t-2t-Mute-Terminal-Crimping-Machine-Wire-Terminal-Crimp-Cable-Crimper-Equipment-for-Jst-Terminal-Crimping.html) |
| OTP "XH2.54" knife set: conductor and insulation crimpers, anvils, no applicator | eBay item 376757376428; AliExpress item 3256803331644772 | not read; ~$30–100 [estimate] | 1–3 weeks from China [estimate]; no Prime listing | 09-28, search (titles only) | An OTP tooling pack is 19 mm wide, with CH/IH wedges, in one maker's applicator | TS a2, a2b, a2d, a3b, a4, a4b, a5, x2; FF f3 (route d), f4, f6, f7, f9b, f10; RP a2, a2d; BM b3 | — |
| OTP applicator spec, KS-EM40R, as a reference for the class | crimpapplicator.com | — | — | 09-28, page | 135.78 mm shut height, 40 mm stroke, 4 kg, CH/IH wedge in 0.02 mm steps over 2 mm | FF f2, f6, f7; PM p5 | [page](https://www.crimpapplicator.com/product/140.html) |
| JST applicators and press: APLMK SXH001-06; CDS SXH001-06/CMKS-L; AP-K2N | Digi-Key; TLC Electronics | $3,439.52; $4,599.36; AP-K2N $12,500 at TLC | Digi-Key 0 stock for all three; AP-K2N 116-day manufacturer lead | 09-28, aggregator; TLC page (ctx §4) | Genuine JST; the MKS-L manual supplies the feed and stop facts other arrangements use | reference for FF f2, BM b1, TS a1 | [TLC](https://tlcelectronics.com/tlc-4910.html) |
| Wire-EDM dies cut to a drawing | JLCCNC; Xometry | not observed; ~$50–200 a part [estimate] | Xometry "in days"; 1–3 weeks [estimate] | 09-28, web | JLCCNC states ±0.05 mm. SKD11 hardens to 58–62 HRC | the index's "made dies" arrangements: FF f5, f5b, f8; IH i1b, i2, i2b, k7; TS a4c, x3; PM p1d, p5c; RP a10; CQ c1b, c6; also FF f3 (route b), f7, f10 | — |
| O1 precision ground flat bar, 1/8 × 1-1/2 × 12 in, annealed | Amazon (Prime) | $27.95 | Oct 1; only 16 left | 09-28, Prime page | 2 ratings (thin). Thickness tolerance not stated. 3/16 in bars also appeared (Prime search) | FF f7, f5b, f10; CQ c6, c1c; HT a4b; SL v8; PM p1, p1d, p5, p5c, p7; RP a2, a10 | [amazon](https://www.amazon.com/dp/B074PCLYLF) |
| HSS parting blade, 1/16 × 1/2 × 4-1/2 in (HHIP) | Amazon (Prime, delivery line and size-row logo) | $15.99 | Mon Oct 5 | 09-28, Prime page | 196 ratings, AC. A chip-breaker groove runs along the upper edge, so that edge is not flat | FF f7; CQ c6 | [amazon](https://www.amazon.com/dp/B00N40478O) |
| HSS square blanks, 3 × 3 × 200 mm, 5 | Amazon (Prime) | $9.99 | next day; only 14 left | 09-28, Prime page | 47 ratings, AC. Grade not stated | CQ c1, c1b; SL v8 | [amazon](https://www.amazon.com/dp/B08ZSMB557) |
| SKD61 ejector pins, 1.5 × 150 mm, 10 (24 diameters offered) | Amazon (Prime) | $9.09 | Oct 2; only 3 left | 09-28, Prime page | 8 ratings (thin). HRC 48–52 | FF f9b, f5b; RP a10 | [amazon](https://www.amazon.com/dp/B0CSDMLNVY) |
| 1095 blue-tempered shim assortment, 0.005–0.032 in | Amazon (Prime) | $53.39 | Oct 1; only 2 left | 09-28, Prime page | 48 ratings, AC | HT a1, a6; FF f7, f10 (laminated fin); TS x2 | [amazon](https://www.amazon.com/dp/B00065V062) |

- **No Prime listing:** OTP applicator; OTP knife set; JST WC-110; the SN jaw
  set alone; a two-post die set; ground O1 or A2 thinner than 1/8 in; an OTP
  side-feed applicator for 6.3 mm Faston females, for the far end on the same
  press as [BM b1](../explorers/borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md)
  (no other source recorded).
- **Open here.**
  - Whether the SN-2549's jaws bottom face to face decides whether they set
    crimp height. Holding the closed tool to a light settles it
    ([FF f3](../explorers/force-and-form/ideas/f3-knee-micropress.md),
    [HT a4](../explorers/hand-tool-as-press/ideas/a4-dies-in-a-die-set.md)).
  - Which contact an OTP applicator or knife set is cut for is unknown until
    one arrives. [BM b1b](../explorers/borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)'s
    jack test runs the vendor's reel, then a $4.71 genuine strip, through the
    same die.
  - On Prime, hardened XH crimp steel exists only in the hand tools and the
    IWS-0723K's 2549 die. Applicators and knife sets come from eBay or
    Made-in-China ([BM summary](../explorers/borrowed-machines/summary.md)).

## Presses and drives

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| VEVOR AP-1 1 t arbor press: 150 mm maximum opening, 81 mm throat, 10 mm ram bore | Amazon (Prime) | $61.90 | Oct 2 | 09-28, Prime page | 4.3★, 281 ratings, 300+/mo, AC. Handwheel version $76.90, 126 ratings, 100+/mo (Prime search) | FF f2b; TS a1, a2, a4, a5; RP a9, a10 | [amazon](https://www.amazon.com/dp/B0CGJ4QT17) · [handwheel](https://www.amazon.com/dp/B0CGJ33KWN) |
| VEVOR AP-3 3 t (310 mm opening, 130 mm throat); VEVOR PR-3 3 t ratchet | Amazon (Prime) | $255.90; $262.14 | Oct 2 | 09-28, Prime page | 28 ratings (thin); 44 ratings, 50+/mo. The AP-3's opening takes a mini-applicator | FF f2b, f5 | [AP-3](https://www.amazon.com/dp/B0CGJ4PRMQ) · [PR-3](https://www.amazon.com/dp/B0CGHXCQ1P) |
| Central Machinery 1 t arbor press #59766 | Harbor Freight | $79.99 (member $54.99) | — | 09-28, page | 20:1, 2,000 lb. Opens 139.7 mm, too short for a mini-applicator (166–176 mm needed); takes a knife-set block | TS a2, a2d (knife-set block); FF f2b, f5 (ruled out for an applicator) | — |
| 1.5–2 t "mute" terminal press for OTP applicators, foot switch, 30 mm stroke | Sanao (Made-in-China) | US$310 at MOQ 1, $300 at 10+; applicator extra | freight "contact supplier"; 50 kg crate; no Prime listing | 09-28, page | Cycles once per pedal closure, ~0.5 s, speed adjustable [Sanao] | BM b1; ctx §4 | [Made-in-China](https://sanaoelectronic.en.made-in-china.com/product/LtTrEpiOqDkW/China-1-5t-2t-Mute-Terminal-Crimping-Machine-Wire-Terminal-Crimp-Cable-Crimper-Equipment-for-Jst-Terminal-Crimping.html) · [specs](https://www.sanaoequipment.com/1-5t-2t-mute-terminal-crimping-machine-product/) |
| The same press class elsewhere | eBay; Zonesun; WIREPRO TU-N02 | eBay 1.5 t $968.30; Zonesun $950 and $2,079; WIREPRO page shows "$201", read as a placeholder [assumption] | — | 09-28, search (eBay); page | — | BM b1 | [Zonesun](https://www.zonesun.com/collections/terminal-crimping-machines) · [WIREPRO](https://www.wireproauto.com/product/tu-n02-1-5t-2t-3t-semi-automatic-terminal-crimping-machine/) |
| ETCO Mighty-T bench press with mini-applicators | ETCO | $2,950; Mighty-Mini applicator from $1,850 plus tooling | — | 09-28, page (ctx §4) | Cast iron, 40 mm stroke, 4,450 lbf | ctx §4 | [ETCO](https://www.etco.com/wire-crimping-press-complete-with-terminal-applicator/) |
| Pneumatic bench crimper AM-10 with 14 die sets, pedal | Amazon (Prime); also vevor.com | $159.00; vevor.com $209.90 | Oct 2; only 7 left | 09-28, Prime page; page | 14 ratings (thin). Dies for lugs and insulated terminals; no open-barrel XH die | ctx §4 | [amazon](https://www.amazon.com/dp/B0B8T9X2DK) |
| Electric bench crimper, 7 die sets, pedal, counter | Amazon (Prime) | $899.00 | Sep 30; only 3 left | 09-28, Prime page | 1 rating (thin). No XH die listed; OTP fit not stated | ctx §4 | [amazon](https://www.amazon.com/dp/B0FHDRR22T) |
| BIG RED TA91206 12 t air-over-hydraulic bottle jack | Amazon (Prime) | $136.04 | Sep 30; only 9 left | 09-28, Prime page | 290 ratings, AC. A lifting jack; fit in the VEVOR 12 t frame not stated | RP a2b | [amazon](https://www.amazon.com/dp/B00026Z3HM) |
| 12 V linear actuators: Progressive Automations PA-01-POT 750 N with pot feedback; Justech 1,500 N; Justech 750 N | Amazon (Prime) | $155.39; $29.99; $30.99 | Oct 2 (8 left); Oct 1 (10 left); next day | 09-28, Prime page | no ratings (thin); 230 ratings, AC; 216 ratings, AC. Both Justech run 7 mm/s loaded, with limit switches and no feedback | BM b2, b2b; FF f1, f2b; RP a2 | [PA-01-POT](https://www.amazon.com/dp/B0G7DD9QWQ) · [1,500 N](https://www.amazon.com/dp/B0F5Q1HXSX) · [750 N](https://www.amazon.com/dp/B07M9Y2JHV) |
| Progressive Automations PA-14 / PA-14P, pot feedback | Progressive Automations | not observed | "ships within 24 hours" | 09-28, web | — | FF f1, f2b; HT (noted) | — |
| Gearboxes for a crank: StepperOnline NEMA 23 planetary 10:1 and 20:1; Heechoo NEMA 23 with 30:1 worm; NMRV030 40:1; StepperOnline NEMA 17 with 26.85:1 planetary | Amazon (Prime) | $48; $79; $120; $38.99; $41.91 | Sep 29 to Oct 1; 1 to 12 left | 09-28, Prime page | All thin (4–36 ratings). Permissible torque: 10 N·m (10:1), 30 N·m (20:1), 3 N·m (NEMA 17). The worm's output torque is not stated. The NMRV030's 11 mm bore needs a sleeve | BM b1b, b3; FF f2; SL v8 | [10:1](https://www.amazon.com/dp/B0BPGMZ5LM) · [20:1](https://www.amazon.com/dp/B0BPGNXJTJ) · [30:1 worm](https://www.amazon.com/dp/B07XFRL9GP) · [NMRV030](https://www.amazon.com/dp/B09HGS2SSG) · [NEMA 17 PG27](https://www.amazon.com/dp/B00QEUZ9EM) |
| StepperOnline 23HS30-2804S-RVS30-G30: NEMA 23 with NMRV030 30:1 | StepperOnline | C$76.69 | 200 in stock; ships in 24 h | 09-28, web | 20 N·m permissible, 65 % efficiency | FF f2; BM b1b, b1c | — |
| 12 V gearmotors: Greartisan 10 rpm self-locking worm, 40 kg·cm; BRINGSMART self-locking worm, 5 rpm; MECCANIXITY 2 rpm worm; BEMONOC 50 rpm right-angle, 6 N·m | Amazon (Prime; BRINGSMART by variant-row logo) | $26.99; $28.97; $21.89; $46.88 | next day; next day; Sep 30; Oct 2 | 09-28, Prime page | 40 ratings; 140 ratings, 100+/mo; 1 rating; 117 ratings, AC | HT a1, a4; FF f10; BM b1b, b1c | [Greartisan](https://www.amazon.com/dp/B07YBXB4N7) · [BRINGSMART](https://www.amazon.com/dp/B07F8Y36PD) · [2 rpm](https://www.amazon.com/dp/B0DP9WDRJ2) · [BEMONOC](https://www.amazon.com/dp/B01GJ4VPH2) |
| 5840-31ZY 12 V worm gearmotor | nfpshop.com | $18.50 | — | 09-28, web | Self-locking worm; ~2.3 N·m working | HT a1, a4 | — |
| 240 Series wiper DC gear motor, 40 N·m, 65:1 planetary | AmEquipment | $172.65 | two-week lead | 09-28, page | Not self-locking as stated | PM p5; BM b1b | [page](https://www.amequipment.com/shop/240-series-dc-gear-motor/) |
| Pneumatics: SC63×50 and SC32×25 cylinders; CDJ2B 16×10 mini cylinder; 24 V 5/2 valve; flow controls; bendable blow-off nozzle | Amazon (Prime) | $33.49; $20.99; $14.99; $16.99; $14.99 (5); $6.99 | Sep 29 to Oct 2 | 09-28, Prime page | Ratings: 13; 272 (AC); 1; 188 (50+/mo, AC); 415 (50+/mo, AC); 138 (AC). The nozzle bore is 3 mm, not the ~1 mm asked | BM b1, b1b, b1c; FF f3; TS a1 | [SC63](https://www.amazon.com/dp/B0788NFXFV) · [SC32](https://www.amazon.com/dp/B092HJ3341) · [CDJ2B](https://www.amazon.com/dp/B0H416HRY2) · [valve](https://www.amazon.com/dp/B07SGDDKL1) · [flow](https://www.amazon.com/dp/B085NRHHSJ) · [nozzle](https://www.amazon.com/dp/B01NBLE6HI) |
| Push-pull toggle clamps: POWERTEC 305CM 500 lb, 2-pack; POWERTEC 301A 100 lb, 2-pack | Amazon (Prime) | $18.25; $8.99 | overnight; Sep 30 | 09-28, Prime page | 605 ratings, 50+/mo, AC; 656 ratings, 50+/mo. Plunger stroke not stated on either | BM b1b, b2; CQ c1b; FF f9, f9b; SL v9b | [305CM](https://www.amazon.com/dp/B0D227VW2B) · [301A](https://www.amazon.com/dp/B076H3WRLZ) |
| Springs for stops and preload stacks: DIN 2093 A35.5 × 18.3 × 2.0 discs (5,190 N max), 10; DIN 2093 28 × 14.2 × 1.5 discs, 20; light stainless Belleville assortment; 8 mm light die springs; 20 × 10 × 25 mm heavy die spring | Amazon (Prime; the A35.5 discs by delivery line) | $5.37; $11.99; $14.99; $16.95; $6.99 | Oct 3 (only 1 left); next day; next day; Sep 30; next day | 09-28, Prime page | no ratings (thin); 2 ratings; 68 ratings, 50+/mo, AC; 70 ratings, AC; no ratings. The A35.5 is chrome vanadium to DIN 2093, sold by Amazon.com. The 28 mm disc's load is not stated | BM b1b, b1c, b2; TS a1, a2; HT a4, a4b, a4c, a4d; FF f5, f7; PM p5, p5b; SL v8 | [A35.5](https://www.amazon.com/dp/B005Y3A6FC) · [28 mm](https://www.amazon.com/dp/B0GL1C5H6Y) · [assortment](https://www.amazon.com/dp/B07CSQDS7F) · [8 mm](https://www.amazon.com/dp/B081DSZTV6) · [heavy](https://www.amazon.com/dp/B0FHGFR1S6) |

- **No Prime listing:** a 1.5–2 t press for OTP applicators; a NEMA 17
  worm-gear stepper; a 12 V actuator with feedback at 500–750 N and ≥10 mm/s;
  a 25 × 12.2 × 1.5 mm heavy disc.
- **Open here.**
  - The A35.5 discs showed "only 1 left".
  - The NEMA 23 30:1 worm on Prime states no output torque or self-locking.
  - The 20:1 planetary's 30 N·m permissible, against the ≥20 N·m
    [BM b1b](../explorers/borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
    asks, comes from one page table.

## Stripping, splitting and laser

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| KNIPEX automatic stripper, 10–24 AWG | Amazon (Prime) | $47.99 | Oct 2; only 11 left | 09-28, Prime page | 1,867 ratings, 600+/mo. Behaviour on soft silicone not stated | procedure step 3, every explorer | [amazon](https://www.amazon.com/dp/B003B8WB5U) |
| Ideal Stripmaster 45-098, 30–20 AWG die-hole stripper | Amazon (Prime) | $55.68 | Oct 1; only 11 left | 09-28, Prime page | 124 ratings. The gripper holds the wire centred in the hole. Replacement blades: no Prime listing | BM b7, b2b | [amazon](https://www.amazon.com/dp/B000B5Y9YM) |
| ENGINEER PA-14 precision stripper, stranded AWG 34–22 | Amazon (Prime) | $28.30 | next day | 09-28, Prime page | 464 ratings, 200+/mo. Blades are part of the plier | BM b7, b2b | [amazon](https://www.amazon.com/dp/B001YHELPS) |
| Hakko FT-802 thermal stripper, blades separate | Amazon (Prime) | $516.14 | overnight | 09-28, Prime page | 3 ratings (thin). A G4 blade for about 22 AWG: no Prime listing. Silicone does not melt; hot-blade behaviour on it is unverified | ctx §2 | [amazon](https://www.amazon.com/dp/B07V4GNCGM) |
| Hakko T18-K knife tip for the FX-888D on the bench | Amazon (Prime) | $16.83 | Sep 30; only 1 left | 09-28, Prime page | 146 ratings. Hakko store listing | BM b7 | [amazon](https://www.amazon.com/dp/B004ORB8MY) |
| HOZO NeoBlade ultrasonic cutter, 40 kHz, six SK5 blades | Amazon (Prime) | $149.99 | next day | 09-28, Prime page | 363 ratings, 700+/mo. Cutting silicone rubber not stated | BM b7, b6 | [amazon](https://www.amazon.com/dp/B0FK9SB5KR) |
| Hakko CHP-170 micro soft flush cutter, 2 pairs, to close by a servo as the carrier-tab cutter | Amazon (Prime) | $22.91 | overnight | 09-28, Prime page | 24,508 ratings, 500+/mo. Genuine Hakko | TS a2, a2c | [amazon](https://www.amazon.com/dp/B0765LT5JG) |
| Automatic flat-cable stripper, 0.75–2.5 mm² | Amazon (Prime) | $96.99 | overnight | 09-28, Prime page | 3 ratings (thin). Range sits above 22 AWG (0.33 mm²) | ctx §1 | [amazon](https://www.amazon.com/dp/B085WV8F2J) |
| Blades: AccuTec 0.009 in single-edge, 100; Astra double-edge, 100; #11 scalpel blades, 100 | Amazon (Prime) | $12.90; $8.88; $13.09 | overnight; Sep 30; next day | 09-28, Prime page | 32 ratings (thin); 55,603 ratings, 10K+/mo, AC; 534 ratings, 400+/mo, AC. A 100-pack of single-edge blades at $6.29 with 2.9K ratings and 4K+/mo does not state thickness (Prime search) | PM p1, p1b, p3; RP a1, a5, a7, a7b, a8, a8b; SL v6; BM b6 | [AccuTec](https://www.amazon.com/dp/B0BV46534X) · [Astra](https://www.amazon.com/dp/B001QY8QXM) · [#11](https://www.amazon.com/dp/B0C4TQR2M7) |
| Single-edge razor blades, 100 | American Cutting Edge | $10 per 100 | — | 09-28, page | — | RP a1, a8 | [page](https://americancuttingedge.com/converting/single-edge-razor-blades) |
| Bambu Lab laser upgrade kit for H2D/H2C, 455 nm, 10 W or 40 W | 3D Universe | $698; $1,348 | "In-Stock Now"; no Prime listing | 09-28, page | "H2D/H2C supports both 10W and 40W laser" [same page]. At 455 nm copper absorbs ~65 %, so the laser scores and never strips through | BM b4, b4b | [3D Universe](https://shop3duniverse.com/products/bambu-lab-laser-upgrade-kit-laser-module-included) |
| VEVOR 45 W CO₂ engraver, 12 × 8 in, air assist | Amazon (Prime) | $759.90 | Sat Oct 3 | 09-28, Prime page | 4 ratings (thin). An OMTech K40+ at CA$999.99 on OMTech Canada (search). CO₂ self-limits at copper | BM b4 | [amazon](https://www.amazon.com/dp/B0G5HG2NXD) |
| LASER TREE 10 W optical diode module, air assist | Amazon (Prime) | $137.17 | Oct 2; only 20 left | 09-28, Prime page | 71 ratings, AC. PWM input not stated | RP a5; BM b4, b4b | [amazon](https://www.amazon.com/dp/B0BJQ2224V) |
| Laser safety: OD 6+ glasses, 190–490 nm; OD7+ shield panel, 200–540 nm | Amazon (Prime) | $26.99; $49.98 | next day | 09-28, Prime page | 783 ratings; 5 ratings (thin). Certification not read | BM b4, b4b | [glasses](https://www.amazon.com/dp/B07DCRR8NG) · [panel](https://www.amazon.com/dp/B0FFGLMT4J) |
| Nylon brush wheels for a rotary tool, 72 | Amazon (Prime) | $15.90 | next day | 09-28, Prime page | 1,477 ratings, 100+/mo | BM b4 | [amazon](https://www.amazon.com/dp/B07QRG27Z7) |
| Sensor-triggered bench strippers: used Schleuniger RotaryStrip 2400; WIREPRO SP-2015E; VEVOR electric and "computer" strippers | eBay and CAE (used); WIREPRO; vevor.com | Schleuniger: not observed; WIREPRO: quote only; VEVOR from $128.99 and $1,099 | no Prime listing for the small-gauge, sensor-triggered class | 09-28, search (eBay); page (WIREPRO); search page (VEVOR) | RotaryStrip: incision in 0.01 mm steps, controlled twist; silicone is not in its rated list. Most VEVOR machines target larger cable | BM b7; RP a8, a8b | [CAE](https://caeonline.com/buy/machine-tools/schleuniger) · [WIREPRO](https://www.wireproauto.com/product/high-accuracy-electrical-wire-stripper-machine/) · [VEVOR](https://www.vevor.com/s/benchtop-automatic-wire-stripping-machine) |
| Solder: Weller 0.5 mm Sn99.3Cu0.6Ni, 100 g; YIHUA 929D-II auto-feed gun | Amazon (Prime) | $33.78; $49.99 | next day; overnight | 09-28, Prime page | 116 ratings, AC; 186 ratings. No-clean not stated; feed metering in 1 mm steps not stated | CQ c3 | [solder](https://www.amazon.com/dp/B09LDHLM1F) · [feeder](https://www.amazon.com/dp/B09CT296ZC) |
| Wire straightener, 5 bearings | Amazon (Prime) | $14.98 | Oct 2 | 09-28, Prime page | 40 ratings (thin). Sold for round wire; fit on a 7–15 mm flat ribbon not stated | RP a4, a9 | [amazon](https://www.amazon.com/dp/B0FMNN8CNH) |
| Bench cut-and-strip machine, touchscreen, 0.5–30 mm strip | Amazon (Prime) | $1,499.00 | Oct 2 (scheduled); only 2 left | 09-28, Prime page | ratings not shown (thin). Flat-cable guide width and a cut-only mode not read | RP a4 | [amazon](https://www.amazon.com/dp/B0FFMPK4K2) |

- **No Prime listing:** Weidmüller Stripax Plus 2.5; a flat-ribbon splitter
  tool; the Bambu laser module; a strip-and-twist machine; replacement die
  blades for a 20–30 AWG die-hole stripper.
- **Open here.**
  - How any of these blades, heads or lasers behave on 22 AWG silicone at a
    0.49 mm wall is untested, and so is whether the web peels cleanly (repo
    Open item 5).
  - The Knipex, the Stripmaster and the PA-14 are hand tools.
    [BM b7](../explorers/borrowed-machines/ideas/b7-borrowed-strip-head-one-conductor.md)
    sets out the blade geometry a stripper needs when it is fed one
    conductor at a time.

## Motion and control

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| NEMA 17 with integrated 240 mm Tr8×2 screw and anti-backlash nut (Iverntech) | Amazon (Prime) | $27.99 | Oct 1 | 09-28, Prime page | 21 ratings (thin). 2 mm lead, 500 mN·m | BM b1; CQ c1b; FF f3, f4; IH i1, i2, i3; PM p1, p2, p3; RP a1, a4, a6; TS a2, a2c, a4 | [amazon](https://www.amazon.com/dp/B094CRRSRQ) |
| NEMA 17 external linear stepper, 310 mm Tr8×2, brass nut (MybotOnline) | Amazon (Prime) | $27.78 | Oct 2; only 9 left | 09-28, Prime page | 5 ratings (thin). The nut is not anti-backlash | HT a1, a3, a5; RP a1, a4, a6 | [amazon](https://www.amazon.com/dp/B07TB7FPPP) |
| NEMA 17 with 38 cm Tr8×8 screw | Pololu 2690 | $158.78 | "active and preferred", backorders allowed | 09-28, page | Shows the class | PM (slides) | [Pololu](https://www.pololu.com/product/2690) |
| NEMA 17 stepper, 200 steps, 20 N·cm | Adafruit 324 | $14.00 | — | 09-28, page | — | IH | — |
| NEMA 23 2.4 N·m with DM542T driver, a second set | Amazon (Prime) | $50.00 | Sep 30 | 09-28, Prime page | 2 ratings (thin). The bench has one set already [repo] | RP a1, a1c, a4 | [amazon](https://www.amazon.com/dp/B0CS2TBLXP) |
| Mini linear stage, 50 mm, T6×1 screw, NEMA 11 | Amazon (Prime) | $54.80 | Oct 1 | 09-28, Prime page | 34 ratings, AC (thin) | SL (for TS a2's strip fence with v1, and TS a5's anvil Z) | [amazon](https://www.amazon.com/dp/B087NMCGPV) |
| Rails: MGN12 300 mm with MGN12H; MGN9 200 mm with MGN9H; HGR15 400 mm pair with 4 × HGH15CA | Amazon (Prime) | $20.49; $16.12; $48.99 | Oct 1 (9 left); Sep 30; Sep 30 | 09-28, Prime page | 615 ratings, AC; 34 ratings, AC; 40 ratings. HGR15 preload class not stated | BM b1; CQ c1; HT a2; IH i1, i2, i3, i5; PM p1, p2, p3; RP a1; TS a6; FF f2 | [MGN12](https://www.amazon.com/dp/B07ZVFFXQZ) · [MGN9](https://www.amazon.com/dp/B0DY4LGPS5) · [HGR15](https://www.amazon.com/dp/B0C4DG3HLR) |
| Ball screws: SFU1204 200 mm; SFU1605 450 mm kit with BK12/BF12 | Amazon (Prime) | $35.99; $41.59 | Oct 1 (4 left); Sep 30 (9 left) | 09-28, Prime page | 24 ratings, AC; 63 ratings, AC. The SFU1204 has no end supports; accuracy class not stated | CQ c1; TS a1 | [SFU1204](https://www.amazon.com/dp/B07XXSL3CC) · [SFU1605](https://www.amazon.com/dp/B089DGRFY9) |
| Guides: 8 × 100 mm case-hardened rods (h8), 2; 10 × 300 mm case-hardened rods, 4; 10 mm sintered-bronze flange bushings, 10 | Amazon (Prime) | $6.99; $17.99; $11.99 | next day; next day; Sep 30 | 09-28, Prime page | 567 ratings, AC; 279 ratings; 29 ratings (thin). h6 not found; running clearance not stated | HT a4; FF f3, f4, f5, f5b | [8 mm](https://www.amazon.com/dp/B09RVS4PXZ) · [10 mm](https://www.amazon.com/dp/B0D2312R72) · [bushings](https://www.amazon.com/dp/B0GCH3THWM) |
| Bearings: UCP204 pillow blocks, 2; HK1010 needle, 5; CF6 (KR16) cam followers, 4; 12 in lazy-susan ring | Amazon (Prime) | $26.99; $7.79; $9.99; $22.99 | Sep 30; Oct 1; Oct 1 (3 left); overnight | 09-28, Prime page | 234 ratings; 162 ratings; 33 ratings, AC; 2,611 ratings, 200+/mo. Load ratings not stated | BM b1b; FF f2; PM p5, p5b, p5c, p1b | [UCP204](https://www.amazon.com/dp/B09T5NFMGZ) · [HK1010](https://www.amazon.com/dp/B07GCBXRQN) · [CF6](https://www.amazon.com/dp/B0CJ4JD5H9) · [lazy susan](https://www.amazon.com/dp/B01L8EHD6K) |
| Transmission: GT2 20T pulleys, 5; module 0.5 brass rack and pinion; UHMWPE (Dyneema) cord | Amazon (Prime) | $5.99; $18.04; $17.95 | overnight; Oct 1; Sep 30 | 09-28, Prime page | 980 ratings, 50+/mo, AC; no ratings; 608 ratings, 50+/mo, AC | HT a1, a2; PM p1b, p3, p3b; BM b8; RP a8 | [GT2](https://www.amazon.com/dp/B07CXR7SFL) · [rack](https://www.amazon.com/dp/B0GXJ9T8HT) · [cord](https://www.amazon.com/dp/B07BKQLFRB) |
| Servos: MG90S 4-pack; MG996R 4-pack; DS3218MG 20 kg; DS3235 35 kg | Amazon (Prime) | $13.88; $18.99; $14.99; $27.99 | Sep 29–30 | 09-28, Prime page | Ratings: 794 (900+/mo); 1,346 (300+/mo); 5,306 (100+/mo); 1,755 (100+/mo); all AC. A 60 kg class did not surface | BM b1, b2; IH i1, i2, i4; SL v1, v3, v6, v8; PM p1c, p4b, p6; RP a1; TS a2, a2b, a3, a6; HT a2, a3; FF f3, f4; CQ c6 | [MG90S](https://www.amazon.com/dp/B0CP98TZJ2) · [MG996R](https://www.amazon.com/dp/B07MFK266B) · [DS3218](https://www.amazon.com/dp/B076CNKQX4) · [DS3235](https://www.amazon.com/dp/B07S9XZYN2) |
| Small drives: 28BYJ-48 with ULN2003, 5 sets; N20 12 V worm motor with encoder, 2; Heschen 12 V push-pull solenoid, 10 mm | Amazon (Prime) | $14.99; $27.99; $7.99 | overnight; overnight; next day | 09-28, Prime page | 831 ratings, 400+/mo, AC; unrated; 383 ratings, 50+/mo, AC. Solenoid: 5 N maximum | TS a2, a4, a4b, a5, a6; BM b2, b3; RP a8b; SL v4; PM p2, p5; CQ c1, c1c | [28BYJ](https://www.amazon.com/dp/B01CP18J4A) · [N20](https://www.amazon.com/dp/B0D9V62J3W) · [solenoid](https://www.amazon.com/dp/B07MJJB12M) |
| Controllers: BTT SKR Pico (4 × TMC2209); MKS DLC32 (ESP32, GRBL); TMC2209 modules, 5; ESP32-S3 boards, 3; BTS7960 H-bridge | Amazon (Prime) | $35.99; $38.50; $26.99; $18.99; $10.99 | Sep 29 to Oct 2 | 09-28, Prime page | 74 ratings, AC; 6 ratings, 50+/mo; 199 ratings, 100+/mo, AC; 126 ratings, AC, 500+/mo (Prime search page); 280 ratings, 100+/mo | BM b1, b3; PM (every arrangement's motion), p4b, p5b, p5c, p6; SL v7; IH i6 | [SKR Pico](https://www.amazon.com/dp/B09MYKL9MP) · [DLC32](https://www.amazon.com/dp/B0GY43P1CL) · [TMC2209](https://www.amazon.com/dp/B07ZQ3C1XW) · [ESP32-S3](https://www.amazon.com/dp/B0F5QCK6X5) · [BTS7960](https://www.amazon.com/dp/B00WSN98DC) |
| BTT SKR Pico V1.0, direct | BIQU | $39.85 (sale from $55.68) | in stock | 09-28, page | Runs Klipper | PM; SL v7 | [BIQU](https://biqu.equipment/products/btt-skr-pico-v1-0) |
| Operator inputs: TEMCo aluminium foot switch, SPDT; 22 mm mushroom e-stop, 1 NC | Amazon (Prime) | $13.76; $8.99 | Sep 30; next day | 09-28, Prime page | 24 ratings, AC; 97 ratings, AC, 100+/mo (Prime search page) | BM b2; PM p4b, p6; SL v7 | [foot switch](https://www.amazon.com/dp/B00EF98MRU) · [e-stop](https://www.amazon.com/dp/B07R4J2Z54) |
| Software: Klipper (load cells: HX711 at 80 SPS, HX717 at 320 SPS), FluidNC, LeRobot, OpenPnP, OpenCV, ntfy, TouchDRO | free | $0 | — | 09-28, page | Klipper reads load cells and angle sensors; FluidNC is ESP32 CNC firmware; TouchDRO reads Mitutoyo SPC on an ESP32 | SL v1b, v2, v3, v4, v7; BM b3, b5; IH i6; HT a2; FF f3 | [Klipper](https://www.klipper3d.org/Load_Cell.html) · [FluidNC](https://github.com/bdring/FluidNC) · [ntfy](https://docs.ntfy.sh/publish/) |

- **Open here.**
  - StepperOnline's pages refused fetches for two explorers. The C$76.69 worm
    gearmotor figure is force-and-form's web record
    ([FF sourcing](../explorers/force-and-form/sourcing-requests.md)).
  - Which control stack suits Derek is his question
    ([SL v7](../explorers/machine-that-sees-and-learns/ideas/v7-the-run.md)):
    his own PlatformIO firmware, FluidNC or Klipper.

## Sensing and vision

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| Bar load cells with HX711: ShangHJ 5 kg, 2 sets; same page, 1 kg variant; Geekstory 20 kg | Amazon (Prime) | $9.99; $9.99; $8.98 | overnight; next day; Sep 30 (11 left) | 09-28, Prime page | 24 ratings, 100+/mo, AC; 15 ratings (thin); 64 ratings, AC. A 10 kg 4-set at $15.99 (Prime search) | ctx §6; BM b1; HT a2, a2d, a3, a4c, a6c; IH i1, i2, i3, i5, i6, i6b, k8; PM p1; SL v8, v9; TS a6, x2, x3, a4c | [5 kg](https://www.amazon.com/dp/B09K7G3477) · [1 kg](https://www.amazon.com/dp/B09K7G51KJ) · [20 kg](https://www.amazon.com/dp/B079FQNJJH) |
| Bar load cell 5 kg (1/10/20 kg variants listed); HX711 breakout; 14 mm piezo | Adafruit 4541; 5974; 1740 | $3.95; $9.95; $0.95 | HX711 in stock | 09-28, page | HX711 at 10 or 80 SPS | IH i1, i2, i5, i6 | [4541](https://www.adafruit.com/product/4541) · [5974](https://www.adafruit.com/product/5974) · [1740](https://www.adafruit.com/product/1740) |
| TAL220 10 kg bar load cell | SparkFun | $12.95 | in stock | 09-28, web | — | HT a2; SL v8 | — |
| Heavier cells: S-type 100 kg; 500 kg compression button; Φ20 × 12 mm button, 200 kg; 5 t bellows cell with indicator and peak hold | Amazon (Prime) | $37.71; $74.99; $49.99; $129.00 | Sep 30 (20 left); Oct 1 (6 left); Sep 30 (12 left); Oct 1 (2 left) | 09-28, Prime page | all thin (0–16 ratings). No amplifier with the S-type; the 5 t cell's raw mV/V access not stated; no 1 t button surfaced | FF f1, f2, f3, f4, f5; HT a1, a4; SL v8 | [S-type](https://www.amazon.com/dp/B077YHNNCP) · [500 kg](https://www.amazon.com/dp/B0GZZRQC6Y) · [Φ20](https://www.amazon.com/dp/B0DGFS22T3) · [5 t](https://www.amazon.com/dp/B0DY7JJ7ZV) |
| Miniature tension/compression cells to 500 kg | ATO | $172.49 | — | 09-28, web | A threaded form, not a button | FF f2, f3, f4 | — |
| Strain and ADC: BF350 foil gauges, 4; SparkFun HX711; ADS1220 24-bit ADC | Amazon (Prime) | $6.99; $11.50; $14.99 | next day | 09-28, Prime page | 4 ratings; 75 ratings, 100+/mo, AC; 6 ratings. ADS1220 to 2,000 SPS | BM b1, b1b, b1c, b3; FF f1, f3, f4; RP a1; PM p1; SL v7, v8 | [BF350](https://www.amazon.com/dp/B0CNJTY2F3) · [HX711](https://www.amazon.com/dp/B079LVMC6X) · [ADS1220](https://www.amazon.com/dp/B0DPMKMGNN) |
| Angle: AS5600 12-bit boards, 3; AS5047P 14-bit SPI board | Amazon (Prime) | $7.99; $11.99 | next day | 09-28, Prime page | 70 ratings, 100+/mo; 5 ratings. The AS5047P page says the diametric magnet is not included | FF f2; HT a1, a4; IH i5; BM b1c; SL v3, v7, v9 | [AS5600](https://www.amazon.com/dp/B094F8H591) · [AS5047P](https://www.amazon.com/dp/B0H15G7NPX) |
| 0.001 mm indicators: Clockwise DITR-0105 (RS232 port); AICEYI ACE-Q25 with its USB data cable | Amazon (Prime) | $52.99; $109.99 plus $39.99 cable | next day; Oct 1 | 09-28, Prime page | 67 ratings, AC; 6 and 2 ratings (thin). The DITR-0105's DTCR-01 cable: no Prime listing. Whether the AICEYI cable presents as keyboard or serial is not stated | FF f3, f4, f6, f7, f9b, f10; HT a4, a4c; SL v3, v8; IH i2 | [DITR-0105](https://www.amazon.com/dp/B07888LX1R) · [ACE-Q25](https://www.amazon.com/dp/B0CSCPMNDJ) · [cable](https://www.amazon.com/dp/B0F3J171Y5) |
| Mitutoyo ID-C indicator with SPC output | gauge dealers (judgetool.com, aftfasteners.com) | $451–668 | — | 09-28, web | TouchDRO reads its SPC protocol on an ESP32 | FF f3; IH i2 | — |
| Micrometers: Shars 303-2307 point, 0.0001 in; Shars 303-2202 blade | Amazon (Prime) | $61.95; $98.75 | Oct 1 (9 left); Sep 30 (7 left) | 09-28, Prime page | 13 and 14 ratings (thin). Neither is a point-and-blade crimp micrometer | ctx §6; PM; SL v3, v5 | [point](https://www.amazon.com/dp/B082QWT3ST) · [blade](https://www.amazon.com/dp/B082T4MWRM) |
| SKEAP 50 kg digital hanging scale, for pull tests | Amazon (Prime) | $9.98 | next day | 09-28, Prime page | 3,786 ratings, 4K+/mo, AC. Peak hold not stated | HT a6; RP a2d, a9, a10b | [amazon](https://www.amazon.com/dp/B09PQB73JD) |
| Cameras: MMlove 16 MP IMX298 on an M12 mount; ELP 16 MP 118° board; 12 mm M12 lens; NEEWER 15× clip-on macro; Plugable 250× USB microscope | Amazon (Prime) | $69.99; $74.99; $9.99; $24.99; $59.95 | Sep 29–30 | 09-28, Prime page | 16 ratings; 39 ratings, AC; 12 ratings; 87 ratings, 100+/mo, AC; 6,580 ratings, 200+/mo. The IMX298 module does 4656 × 3496 MJPEG at 10 fps | SL v1, v5; FF f4; IH i3, i4 | [IMX298 M12](https://www.amazon.com/dp/B0C54VCKZV) · [ELP](https://www.amazon.com/dp/B0C289GYVZ) · [12 mm](https://www.amazon.com/dp/B07CZ49BMK) · [macro](https://www.amazon.com/dp/B0FKSKTLQX) · [microscope](https://www.amazon.com/dp/B00XNYXQHE) |
| Raspberry Pi HQ camera (IMX477, C/CS); 16 mm and 6 mm lenses | Adafruit 4561 | $55; $77.50; $49.30 | 1 in stock, limit 10 per customer | 09-28, page | Needs a Pi to host it | SL v1 | [Adafruit](https://www.adafruit.com/product/4561) |
| Mirrors: first-surface 100 × 100 × 3 mm; 25 mm K9 right-angle prism | Amazon (Prime) | $20.90; $16.95 | Sep 30; Oct 1 | 09-28, Prime page | no ratings; 21 ratings (thin). The plate needs cutting to 10–50 mm | SL v1, v5, v9, v9b | [mirror](https://www.amazon.com/dp/B0GW4WT69F) · [prism](https://www.amazon.com/dp/B08HR5P9V2) |
| Light: XIAOSTAR A5 pad; opal acrylic, 3 mm; 1 mm diffuser board; Adafruit 1626 12 × 40 mm backlight (on Amazon); WS2812B 16-LED rings; AmScope 144-LED ring; 3 mm white LEDs, 100; 650 nm line laser; 1 mm PMMA fibre | Amazon (Prime) | $16.99; $11.98; $13.99; $8.42; $18.99; $35.99; $6.99; $42.00; $10.89 | Sep 29 to Oct 2 | 09-28, Prime page | Ratings: 4,700 (50+/mo, AC); 341 (100+/mo); 6 (50+/mo); 30; 40 (50+/mo, AC); 664 (100+/mo, AC); 908 (AC); 73; 477 (50+/mo) | SL v1, v4, v4b, v5, v6, v8, v9, v9b; FF f6; PM p1, p1b, p1c, p4, p6, p7; RP a7, a8; TS a2d, a3, a5, a6, x2 | [A5](https://www.amazon.com/dp/B08QJ2JMHZ) · [opal](https://www.amazon.com/dp/B0G4JJSFCS) · [diffuser](https://www.amazon.com/dp/B0H69667R6) · [1626](https://www.amazon.com/dp/B01N6XME2Q) · [WS2812B](https://www.amazon.com/dp/B0B2D5QXG5) · [ring](https://www.amazon.com/dp/B00JZJO7YC) · [LEDs](https://www.amazon.com/dp/B01AUI4VR4) · [line laser](https://www.amazon.com/dp/B01KNQ5RBC) · [fibre](https://www.amazon.com/dp/B07W979RH3) |
| Switches and beams: roller micro limit switches, 10; 3 mm IR break-beam pair; slotted optocouplers, 10; SS49E linear Hall, 20; M8 inductive proximity, 5 | Amazon (Prime) | $5.99; $9.99; $9.99; $7.99; $21.99 | Sep 29 to Oct 1 | 09-28, Prime page | Ratings: 724 (1K+/mo, AC); none; 29 (50+/mo, AC); 86 (100+/mo, AC); 12 | IH i3b, i4, i5; PM p1, p3, p4, p5; SL v7; BM b1 | [microswitch](https://www.amazon.com/dp/B07X142VGC) · [break-beam](https://www.amazon.com/dp/B0DXT9H7VR) · [slotted](https://www.amazon.com/dp/B0CHDRF497) · [Hall](https://www.amazon.com/dp/B0CZ6RL4B2) · [inductive](https://www.amazon.com/dp/B01LNOIAT4) |
| Length encoders: 600 PPR with 300 mm wheel and bracket; bare 600 P/R encoder | Amazon (Prime) | $81.00; $18.99 | Sep 30 | 09-28, Prime page | 5 ratings (thin); 77 ratings, 50+/mo, AC. The wheel gives 20 counts per 10 mm, short of the 100 wanted | PM p3; BM b8 | [wheel](https://www.amazon.com/dp/B07H29BBLK) · [bare](https://www.amazon.com/dp/B07MX1SYXB) |
| Far-end test electrodes: Wago 221-415, 25; P75-E2 pogo pins, 100; 6-circuit capsule slip ring; 12-circuit slip ring | Amazon (Prime) | $28.00; $6.49; $9.99; $19.99 | Sep 30 (6 left); Sep 30; overnight; overnight (5 left) | 09-28, Prime page | 6,963 ratings, 50+/mo; 21, 50+/mo, AC; 136, 50+/mo, AC; 6 ratings. The pogo pins have conical heads; crown-head P75 and receptacles: no Prime listing | HT (far-end block in every idea); CQ c1c; PM p3, p3b; RP a4, a6; BM b8 | [Wago](https://www.amazon.com/dp/B0107SYYGU) · [pogo](https://www.amazon.com/dp/B099F1DRYJ) · [6 ckt](https://www.amazon.com/dp/B07H2SRMXP) · [12 ckt](https://www.amazon.com/dp/B07Y9P8N3Y) |
| Slip ring with flange, 6 circuits; P75-H2 crown-head pogo pins, 10 | Adafruit 736; 2429 | $14.95 ($13.46 at 10+); $4.95 | in stock | 09-28, page | The crown heads suit the 1.7 mm pitch face | PM p3, p3b; RP a4, a6; BM b8; CQ c5 | [736](https://www.adafruit.com/product/736) · [2429](https://www.adafruit.com/product/2429) |

- **No Prime listing, and no other source recorded:** a point-and-blade
  crimp-height micrometer; the DTCR-01 cable; an XGZP6847 vacuum sensor; an
  HX717 board.
- **Open here.**
  - Force monitoring sees gross faults only. One strand of 60 is about 1.7 %
    of force, inside a monitor's ±4 % band. The backlit picture of the
    stripped tip is the strand guard
    ([SL v3](../explorers/machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md),
    [FF f1](../explorers/force-and-form/ideas/f1-motorised-ratchet-crimper.md)).
  - Which camera and lens reach the barrel's detail at the working distance is
    worked in [SL v1](../explorers/machine-that-sees-and-learns/ideas/v1-watched-nest.md).

## Robots and gantries

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| SO-101 follower electronics kit, 6 × STS3215 12 V, bus driver, no printed parts | Amazon (Prime) | $184.99 | Oct 2; only 2 left | 09-28, Prime page | 1 rating (thin) | BM b5; SL v2 | [amazon](https://www.amazon.com/dp/B0GH35175P) |
| LeRobot SO-ARM101 Pro servo kit (leader and follower), no printed parts | Amazon (Prime) | $360.00 | next day | 09-28, Prime page | 9 ratings, 50+/mo | BM b5; SL v2 | [amazon](https://www.amazon.com/dp/B0FH8CPXP7) |
| Hiwonder SO-ARM101, assembled with printed parts and two cameras | Amazon (Prime) | $389.99 (DIY $269.99; Standard $419.99; Advanced $459.99) | Sep 30 | 09-28, Prime page | no ratings (thin) | BM b5; SL v2 | [amazon](https://www.amazon.com/dp/B0GT999ZFF) |
| SO-101 bill of materials; kits from PartaBot, Seeed Studio, WowRobo | GitHub (SO-ARM100 README) | $229.88 leader and follower; $121.94 follower alone | — | 09-28, page | Open design; prior art puts servo kits at $220–240 and printed parts at ~$35 or self-printed | SL v2; BM b5 | [README](https://github.com/TheRobotStudio/SO-ARM100) |
| Dobot MG400 4-axis desktop arm, ±0.05 mm, 440 mm reach | RobotSourced; Pololu 5400 | $2,890; $3,495 | Pololu: in stock, backorders allowed; no Amazon route checked | 09-28, page | 500–750 g payload, 16 digital I/O, air port | BM b5; SL v2; PM p1 (alternative carrier) | [RobotSourced](https://robotsourced.com/robots/educational/dobot-mg400/) · [Pololu](https://www.pololu.com/product/5400) |
| Creality Ender 3 V3 SE, as a stage or gantry | Amazon (Prime) | $219.00; a second Prime listing at $186.14 | Oct 1; Sep 30 | 09-28, Prime page | 2,112 ratings, 500+/mo; 791 ratings, 200+/mo. Working X/Y/Z with G-code over USB | BM b3; HT a2; SL v1b | [amazon](https://www.amazon.com/dp/B0F8J78BN1) · [second](https://www.amazon.com/dp/B0DD7F2BH9) |
| Creality Ender-3 V3 SE, direct | Creality store | $199 | ships Sep 28–30 (estimate on the page) | 09-28, page | — | HT a2; SL v1b | [Creality](https://store.creality.com/products/ender-3-v3-se-3d-printer) |
| SainSmart Genmitsu 3018-PROVer V2 CNC | Amazon (Prime) | $269.00 | Oct 2; only 9 left | 09-28, Prime page | 1,286 ratings. GRBL, pre-assembled gantry; travel and screw type not read | FF f4; IH i4 | [amazon](https://www.amazon.com/dp/B07ZFD6SKP) |
| LONGER Ray5 10 W laser engraver, 400 × 400 mm, as a belt gantry | Amazon (Prime) | $268.99 | next day | 09-28, Prime page | 176 ratings, 50+/mo. Head payload not stated | HT a3 | [amazon](https://www.amazon.com/dp/B0G13BBN9L) |
| Opulo LumenPnP open-source pick-and-place | Opulo | $1,995 | — | 09-28, page (ctx §3) | Its per-nozzle vacuum check and feeders are borrowed as mechanisms; the machine itself is not used | reference for IH i4, SL v4 | [Opulo](https://www.opulo.io/products/lumenpnp) |
| INTBUYING 110 V disc vibratory feeder with linear track and controller | Amazon (Prime) | $419.00 | Oct 2; only 3 left | 09-28, Prime page | 1 rating (thin). Bowl diameter not read | ctx §3 (TS, SL, PM refer to it) | [amazon](https://www.amazon.com/dp/B0FYMPJLLX) |
| CGOLDENWALL automatic screw feeder, M1–M5 rail | Amazon (Prime) | $185.00 | Oct 2; only 16 left | 09-28, Prime page | 6 ratings (thin). Rail slot range not stated | TS a3, a3b | [amazon](https://www.amazon.com/dp/B00JKDFYQ8) |
| Screw presenters: eBay units; ATO; Hakko AT-1050 | eBay; ATO; Hakko | ~$123–189; $369.38; $630.17 | — | 09-28, web | ATO's rail rule: "bite-wing ~0.5 mm larger than thread"; 200–220 cc hopper | TS a3 | — |
| Vacuum pick: 12 V diaphragm pump, −75 kPa; Beduan 12 V NC valve; Juki 503 tungsten nozzle | Amazon (Prime) | $26.99; $9.99; $14.99 | next day; overnight; Oct 1 (6 left) | 09-28, Prime page | 74 ratings, AC; 432 ratings, 200+/mo; no ratings. The valve's 1/4 NPT body is large for a pick-up line | SL v4, v4b; RP a8 | [pump](https://www.amazon.com/dp/B08RCRJH9M) · [valve](https://www.amazon.com/dp/B07N2LGFYS) · [nozzle](https://www.amazon.com/dp/B07DWYRM2F) |
| Coin vibration motors, 10 × 3 mm, 20 | Amazon (Prime) | $12.99 | next day | 09-28, Prime page | 307 ratings, 200+/mo, AC | RP a2c; TS a3 | [amazon](https://www.amazon.com/dp/B07Q1ZV4MJ) |

- **No Prime listing:** a soft 2–3 mm bellows suction cup.
- **Open here.**
  - An SO-101's tip wanders about ±2–6 mm, so in
    [BM b5](../explorers/borrowed-machines/ideas/b5-desktop-arm-as-operator.md)
    and [SL v2](../explorers/machine-that-sees-and-learns/ideas/v2-arm-taught-by-hand.md)
    it carries work between docks, and the docks do the precision.
  - The ±0.05 mm tier, the MG400, costs $2,890–3,495 and no Amazon route was
    checked.
  - Every feeder listing here is thin, and none states a slot or bowl size
    that fits an XH contact.

## Fixtures and small parts

| Part | Vendor | Price | Stock / lead | Seen | Volume or interchangeability | Used by | Link |
|---|---|---|---|---|---|---|---|
| Laser-cut 304 stainless stencil sheet (blades, combs, tines, nests, laminated carriers) | JLCPCB | from $3 (100 × 100 mm) | "most stencil orders are shipped within 24 hours" | 09-28, page | Thickness options not listed; 0.10–0.20 mm assumed [assumption] | BM b6, b8; CQ c1, c6; FF f7; HT a2c, a2d, a6; IH i1, i2, i2b, i2d, i3, i4, i5, i6, k7; RP a7; TS a4c, x2 | [JLCPCB](https://jlcpcb.com/pcb-stencil) |
| PCBs as post beds and header nests | JLCPCB | not priced here | — | 09-28, page | Hole position ±0.075 mm; through-hole size +0.13/−0.08 mm; press-fit holes ±0.05 mm | IH i6b, i5 | [capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) |
| Laser-cut steel plate: A36 mild steel to 12.7 mm, 4130, AR500, 1095 (3.18 and 4.75 mm, hardens to Rc 65), CPM MagnaCut (3.94 mm) | SendCutSend | instant online quote; not priced here | 2–4 days | 09-28, page | ±0.005 in (0.127 mm); no heat-treat service listed | BM b1b, b3; FF f2, f3, f5, f5b, f6, f7, f9b; IH i2; RP a2, a10 | [SendCutSend](https://sendcutsend.com/materials/mild-steel/) |
| Ball guide-post sets; two-post die sets | Misumi | not observed | — | 09-28, page | No two-post die set on Prime | FF f3, f5, f5b, f7 | — |
| Ground flat stock and drill rod beyond the Prime sizes | McMaster-class supplier | not priced | — | — | [assumption] | FF f3 (route c) | — |
| Pin gauges: Accusize 0.011–0.060 in (0.28–1.52 mm), 50; HFS 0.061–0.250 in, 190 | Amazon (Prime) | $45.58; $72.99 | next day | 09-28, Prime page | 167 ratings, AC; 423 ratings, 50+/mo. 60–62 HRC. Both sets step 0.001 in (0.0254 mm), not 0.01 mm | SL v1, v5; TS a2, a2b, a2c; RP a8, a8b; CQ c6, c6b; HT a6b; IH k7; FF f6, f9b | [Accusize](https://www.amazon.com/dp/B00JOLCSF6) · [HFS](https://www.amazon.com/dp/B00UCQO4HM) |
| Accusize angle blocks, 1–30°, 10 | Amazon (Prime) | $42.00 | Sep 30 | 09-28, Prime page | 215 ratings, AC. ±30 arc-seconds | TS a2, a2d, a5 | [amazon](https://www.amazon.com/dp/B00HZT7HNC) |
| Feeler gauges: Hotop 17-blade 0.02–1.00 mm; Rannb 12 in long blades | Amazon (Prime) | $8.99; $9.99 | next day; Sep 30 | 09-28, Prime page | 361 ratings, 100+/mo, AC; 573 ratings, AC. Hotop's title says stainless and its bullets say 65 manganese steel; the Rannb is manganese steel | BM b2; FF f1, f3, f6; HT a1, a6; IH i1, i2, i2d, i5; PM p1c, p4b, p5b, p6; RP a2b, a7, a8; TS a2b, a4b, a6 | [Hotop](https://www.amazon.com/dp/B08GLN7K1R) · [Rannb](https://www.amazon.com/dp/B07DR83GX9) |
| 304 stainless shim assortment, 0.0007–0.010 in | Amazon (Prime) | $14.99 | next day | 09-28, Prime page | 42 ratings, AC (thin). Thickest leaf 0.25 mm | PM (valley tines for BM b1) | [amazon](https://www.amazon.com/dp/B0FP5CHK4N) |
| Locating hardware: M6 × 40 ground stainless dowels, 24; 6 mm G25 chrome balls, 100; N52 10 × 3 mm magnets, 60; M8 spring ball plungers, 8 | Amazon (Prime) | $6.49; $6.65; $23.99; $7.79 | overnight; next day; overnight; overnight (3 left) | 09-28, Prime page | 19 ratings, AC; 101 ratings; 24 ratings, 200+/mo, AC; 25 ratings. The dowels are 304, not hardened; hardened h6/m6 did not surface | FF f3, f4; PM p1, p1b, p5; RP a1b, a2, a9, a10 | [dowels](https://www.amazon.com/dp/B0GS1B62Y1) · [balls](https://www.amazon.com/dp/B07L8MLK2N) · [magnets](https://www.amazon.com/dp/B0GF7RLFXR) · [plungers](https://www.amazon.com/dp/B099JXP155) |
| Posts: 2.54 mm header strips, 20; 25 mm long-pin headers, 30; 316 stainless 0.64 mm square wire (22 gauge variant), 30 ft | Amazon (Prime; square wire by variant-row logo) | $7.99; $15.49; $9.99 | overnight; Oct 2 (8 left); Oct 2 | 09-28, Prime page | 441 ratings, 500+/mo, AC; 76 ratings; 75 ratings (Prime search page). Header pin section not stated. The square wire is half-hard stainless, so tip wear over ~3,500 spearings is open | HT a1, a3; TS a4, a4b, a4c, a5, a6, x1, x3; PM p1c, p5b, p6; IH i2d, i6b | [headers](https://www.amazon.com/dp/B01MQ48T2V) · [long pins](https://www.amazon.com/dp/B07DK4BDHK) · [square wire](https://www.amazon.com/dp/B0G2LYBQTN) |
| K&S 5005 music wire, 0.025 in × 12 in, 4 | Amazon (Prime) | $7.24 | Oct 2; only 11 left | 09-28, Prime page | 750 ratings. Round, not square | PM p1, p1d; BM b6; FF f10 (tip comb) | [amazon](https://www.amazon.com/dp/B002WXNLI6) |
| Springs: Dianrui 300-piece compression assortment; uxcell 6 mm OD × 0.8 mm × 20 mm, 5; SUS301 constant-force springs, 2.62 lb (≈11.7 N), 5 | Amazon (Prime) | $6.99; $6.49; $35.99 | next day; Oct 1 (3 left); Oct 1 (9 left) | 09-28, Prime page | 1,030 ratings, 3K+/mo, AC; 185 ratings; 2 ratings (thin). Rates not stated | IH i2d, i3, i3b, i5, i6; CQ c1c; HT a6, a6b, a6c | [assortment](https://www.amazon.com/dp/B0BVTDP29W) · [6 mm](https://www.amazon.com/dp/B0C33DD1WP) · [constant force](https://www.amazon.com/dp/B0DMM8YSMM) |
| Hand items: ESD curved fine tweezers; TEKTON smooth-jaw mini flat pliers | Amazon (Prime) | $12.76; $17.00 | Sep 30; overnight | 09-28, Prime page | 57 ratings, AC; 453 ratings, 100+/mo, AC | TS a4, a5; RP a5 | [tweezers](https://www.amazon.com/dp/B0BY7BDX41) · [pliers](https://www.amazon.com/dp/B07CQ4M211) |
| Tape and tube: 1 mil polyimide tape; PTFE tube 1 mm ID × 2 mm OD, 10 ft | Amazon (Prime) | $11.99; $7.99 | next day; Sep 30 | 09-28, Prime page | 1,141 ratings, 200+/mo; 130 ratings, AC | HT a1, a6; PM (BM b2 blade electrode); TS a4b | [Kapton](https://www.amazon.com/dp/B07HB81Q4L) · [PTFE](https://www.amazon.com/dp/B08Q83XNTT) |

- **No Prime listing, and no other source recorded:**
  - hardened, ground alloy dowels, 3–6 mm, h6 or m6;
  - ground O1 or A2 at 1/16 in, 1.5 mm, 0.075 in and 3/32 in;
  - a ~1.45 mm drill blank (the Accusize pin set covers 1.448 mm);
  - a 3 mm ground rod;
  - 1.0 and 1.5 mm spring-steel strip;
  - 0.1–0.2 mm phosphor bronze;
  - knurled or serrated strip;
  - a 50–60 mm steel round bar.
- **Open here.**
  - JLCPCB's stencil thickness options were not on its page.
  - Several die and fin arrangements want ground stock near 1.5–1.9 mm,
    which exists on Prime only as 1095 shim stacked to size
    ([FF f7](../explorers/force-and-form/ideas/f7-where-the-steel-comes-from.md):
    0.032 + 0.025 in = 1.448 mm; 0.032 + 0.032 + 0.010 in = 1.88 mm).
