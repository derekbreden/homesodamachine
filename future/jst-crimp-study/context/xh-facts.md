# XH facts

The manufacturer-document facts every explorer designs against: the XH contact
and its strip, JST's tooling, the XHP housing, crimp force, inspection criteria,
what is in stock, and the wire. Labels: **[mfr]** manufacturer document,
**[source]** other published source, **[calc]** worked in [`calc/`](calc/),
**[estimate]**, **[assumption]**, **[repo]**. Links are at the foot of the file
(S1–S32, C1). Stock and prices were observed 2026-09-28.

**How this was gathered.** Documents were downloaded directly from JST,
J.S.T. UK, Digi-Key's media host, LCSC, Engineer Inc., BNTECHGO and archived
copies. JST's own part drawings (SXH-001T-P0.6.pdf, XHP-n.pdf) and the XH
handling manuals (CHM-1-151, CHM-1-2321, CHM-1-2342) sit behind a licence form
that asks for name, company, address and email and emails the files [mfr S16].
The form was not submitted, so JST's crimp height for SXH-001T-P0.6 and its
carrier-strip dimensions are **not** in this file. Clone makers' drawings of
the same contact fill part of the gap and are labelled as such. Web search
and page-fetch tools were blocked in this session and the browser was out of
bounds, so forum and teardown write-ups were not gathered.

## 1. The contact

### Naming (the shared context is right)

| Part | What it is | Wire | Insulation OD | Pack |
|---|---|---|---|---|
| **SXH-001T-P0.6** | Strip (chain) form, on carrier | AWG #28–#22 (0.08–0.33 mm²) | 0.9–1.9 mm | 8,000/reel |
| **BXH-001T-P0.6** | The same contact, loose piece | same | same | bag |
| SXH-001T-P0.6N | Low-insertion-force variant, "less resistant to the vibration" [mfr S1] | #26–#22 | 1.3–1.9 mm | 5,000/reel |
| SXH-002T-P0.6 | Thin-wire contact | #30–#26 | 0.9–1.3 mm | 8,000/reel |

- Model code: **S = strip form, B = loose piece**; XH series; 001 = #28–#22;
  T = tin-plated (reflow); P = phosphor bronze; 0.6 = post size [mfr S3 p.5].
  JST's tooling catalog lists BXH-001T-P0.6 as the "terminal in loose form" of
  SXH-001T-P0.6 [mfr S4 p.8].
- Material: phosphor bronze, tin-plated (reflow treatment) [mfr S1, S3].
- XH rating: 3 A at AWG #22, 250 V, −25 to +85 °C, 10 mΩ initial / 20 mΩ after
  environment tests; connector wire range AWG #30–#22, insulation OD
  0.9–1.9 mm [mfr S1].
- JST's wire rule: "tin-plated annealed copper stranded wire" is the applicable
  wire [mfr S5]. The BNTECHGO ribbon is tinned stranded copper (§7), so it is in
  class.
- Digi-Key describes BXH-001T-P0.6 as "22-26AWG"; Newark and TME say 28–22 AWG
  and JST pairs it with SXH-001T-P0.6 (#28–#22) [source S26 vs mfr S4]. The
  documents disagree; for 22 AWG it does not matter.
- JST: "The wire crimp section is mechanically decoupled from the post
  insertion section", so crimping does not disturb the mating area [mfr S12].

### Dimensions

JST's public catalog gives only an outline. SXH-001T-P0.6 and SXH-002T-P0.6
are "Shape B"; P0.6N is "Shape A" [mfr S1, S2, S3].

| Feature | JST catalog, Shape B | Clone drawings (HDGC2501-T, DLL TJC3-T, CJT A2501-T, JXT B2542) |
|---|---|---|
| Overall length (front of box to rear of insulation barrel, tab excluded) | **6.1** [mfr S1, 2025 ed.] / **6.5** [mfr S2 2016, S3 2021] — editions disagree | 5.8 ±0.25 / 6.2 ±0.25 / 6.73 ±0.25 / 5.9 ±0.25 [source S19–S22] |
| Box (receptacle) length | 2 [mfr S1] | 2.0 [source S20, S22] |
| End-view envelope, W × H | 1.95 × 2.4 [mfr S1–S3] | box 1.85–1.90 × 2.2–2.35 [source S19–S22] |
| Post accepted | □0.64 mm header post [mfr S1] | box entry 0.60–0.70 [source S19, S21] |
| Stock thickness | not stated | **0.20 ±0.02 mm**, C5191 phosphor bronze [source S19–S21] |
| Conductor barrel, open W × H | not stated | 1.68–1.90 × 1.50–1.60 (±0.25) [source S19–S22] |
| Conductor barrel length | not stated | ~1.25–1.5 [estimate, reading clone drawings] |
| Insulation barrel, open W × H | not stated | 2.46–3.00 × 2.75–3.20 (±0.25) [source S19–S22] |
| Insulation barrel length | not stated | ~0.8–1.5 [estimate, reading clone drawings] |
| Retention lance | drawn on the contact, springing out of the floor side of the box toward the rear [mfr S1 drawing, as read] | stands 0.6–0.9 mm proud; tip ~2.4–2.6 mm behind the front [source S19–S22] |
| Mass | — | BXH-001T-P0.6 0.043 g per LCSC listing [source S27b] |

Shape A (P0.6N): 5.6 [mfr S1] or 6.5 [mfr S2, S3] long, box 1.6, end view
1.9 [S1] or 1.8 [S2, S3] × 2.35. Clone drawings put the insulation wings wider
and taller than JST's 1.95 × 2.4 end-view envelope suggests; whether JST's
wings are really that small is unresolved.

### The strip

- **Side feed.** The contacts hang perpendicular to the carrier, joined at the
  **rear (insulation-barrel end)** by a cut-off tab. JST's applicator for XH is
  the side-feed type (MKS-L), and the catalog illustration shows side-feed chain
  terminals with round holes and slots in the carrier [mfr S4 p.1, S2].
- **Pilot holes.** One round hole per contact on the contact's centreline, a
  rectangular slot between holes; Ø1.5 mm on the HDGC drawing [source S19; same
  pattern on S20–S22].
- **Tab.** ~0.7–1.15 mm between carrier edge and contact rear on clone drawings
  [estimate, reading S19, S21, S22]. After cut-off JST shows both "no cut-off
  length" and "too much cut-off length" as faults [mfr S5]; Molex's rule is 1.0–1.5× stock thickness, usually flush to
  one thickness [source S23].
- **Pitch between contacts: not dimensioned in any document read.** Scaling the
  clone drawings gives 7–9.5 mm, and those drawings are not to scale
  [estimate].
- **Reel:** 8,000 for SXH-001T-P0.6 [mfr S1]; clones 7,000 (DLL), 8,000 (CJT),
  9,000 (HDGC), 15,000 (CJT -A) [source S19, S20, S22]. The whole program
  (~3,200 crimps, per the shared context) is under half a reel.
- **Cut strip is sold.** Digi-Key sells SXH-001T-P0.6 in 100, 500 and 1,000
  piece lots besides the 8,000 reel; Heilind lists "cut strip" from 1,000 and
  "loose piece" from 1 [source S26] (Digi-Key's small lots are strip
  [assumption]).

### Strip length and crimp specification

| Contact | AWG | Strip (mm) | Conductor crimp H × W (mm) | Insulation crimp W (mm) | Pull-out min | Source |
|---|---|---|---|---|---|---|
| **SXH-001T-P0.6** | 22 | **2.4** | **not public** | not public | **39.2 N (4.0 kgf)** | [mfr S6] |
| | 24 | 2.4 | not public | | 29.4 N | [mfr S6] |
| | 26 | 2.4 | not public | | 19.6 N | [mfr S6] |
| | 28 | 2.4 | not public | | 9.8 N | [mfr S6] |
| SXH-002T-P0.6 | 26 / 28 / 30 | 2.3 | 0.62 / 0.60 / 0.57 × 1.30 | 1.80 | 19.6 / 9.8 / 7.8 N | [mfr S13] |
| SXA-01T-P0.6 (XA, similar size, analog) | 24 / 22 / 20 | 2.5 | 0.75 / **0.80** / 0.90 × 1.50 | 1.80 | 30 / 40 / 65 N | [mfr S14] |
| SPH-002T-P0.5L (PH, analog) | 28 / 26 / 24 | 2.5 | 0.50–0.55 / 0.52–0.57 / 0.57–0.62 × 1.40 | 1.40 | 14.7 / 19.6 / 29.4 N | [mfr S15] |
| **SXH-001T-P0.6 on BNTECHGO 22 AWG, estimated** | 22 | 2.4 | **~0.88 central, 0.69–1.12 bound; expect JST's number near 0.8–0.9** × ~1.5 | ~1.8–2.0 | — | [calc C1 §3] |

- The WC-110 numbers are for UL1007 wire; JST's calibration strips 2.4 mm for
  every gauge [mfr S6].
- J.S.T. UK tolerances: conductor height ±0.05, conductor width ±0.05,
  insulation width ±0.10; insulation crimp height "dependant on the
  specification of the wire used" [mfr S13, S14].
- JST's strip-length rule: L = E + A/2 + α, with α "depended on each terminal"
  [mfr S5]. Reading the figure, E is the conductor barrel and A the gap between
  barrels [assumption].
- JST measures crimp height with a crimp micrometer at the centre of each barrel,
  at the start, middle and end of a run [mfr S5].
- UL 486A pull-out for 22 AWG is 8 lbf (35.6 N). A 22 AWG conductor breaks at
  ~85–100 N depending on stranding [source S23]. So JST's 39.2 N is ~40–45 % of
  wire break.

## 2. JST's tooling for this contact

| Tool | What it is | Facts | Stock, price (2026-09-28) |
|---|---|---|---|
| **WC-110** (J.S.T. UK) | Ratchet hand tool, **loose piece** SXH-001T-P0.6 (and P0.6N except 28 AWG) | "Flap locator to ensure the correct positioning of the contact"; 3 cavities: 22, 24, 26/28 AWG; "the insulation barrel is set and cannot be adjusted"; replacement WC-110P flap locator [mfr S6, S7] | Digi-Key 147 at $536.51; Newark 49 at $668.99; TME 15 at $564.96; WC-110P locator Digi-Key 15 at $51.23 [source S26] |
| **YRS-110** | Parallel-action ratchet hand tool for the contact **in strip form** | One crimp section, removable dies [mfr S8, S4] | Digi-Key 9 at $1,565.93 [source S26] |
| YC-110R / YC-111R | Ratchet hand tools, loose piece; 24+26 AWG / 22+24 AWG | [mfr S9, S4] | Digi-Key 1 at $702.51 / 0 at $714.00 [source S26] |
| **XJ-06** | Extraction tool for SXH-001T-P0.6, -P0.6N, SXH-002T-P0.6 | [mfr S10, S4] | Digi-Key 20 at $63.69 [source S26] |
| **AP-K2N** | Semi-automatic press: crimps a wire to a chain terminal each footswitch press | **14.7 kN (1,500 kgf)**; 280 × 480 × 505 mm; ~90 kg; 100 VAC [mfr S4] | Digi-Key listed, 0 stock, no price [source S26] |
| **APLMK SXH001-06** | Applicator (MKS-L frame + MK/SXH-001-06 dies) for AP-K2N | [mfr S1–S3] | Digi-Key 0 stock, $3,439.52 [source S26] |
| APLSC SXH001-06 | MKS-SC applicator | "Strip-crimp applicator" [mfr S2]; that it strips and crimps in one stroke is read from the name [assumption] | — |
| **CDS SXH001-06/CMKS-L** | Industry-standard-press applicator for SXH-001T-P0.6 | 6 kg; shut height 135.78 mm; 40 mm stroke; dial crimp-height adjustment for conductor and insulation barrels; post-feed or pre-feed cams [mfr S11] | Digi-Key 0 stock, $4,599.36 [source S26] |

- **JST calls its hand tools prototype and repair tools**, with fixed dies:
  "the crimping height cannot be adjusted", so some catalog wires "may not be
  crimped properly"; check pull strength before use [mfr S4 p.3 notes].
- **Label disagreement.** The 2016 XH catalog marks only **MKS-SC** as the
  strip-crimp applicator and MKS-L as a plain crimp applicator [mfr S2]. The
  2022 tooling catalog captions **MKS-L** "strip-crimp applicator for side
  feeding terminals" [mfr S4 p.1].
- **What an applicator's feed and locator do.** A feed finger advances the strip
  one pitch per stroke, before or after the crimp (pre-feed or post-feed cam)
  [mfr S11]. The strip track and terminal stop place the contact under the
  punches. Track position sets bellmouth, cut-off tab length and insulation
  position together [source S23]. A cut-off punch shears the tab at the
  carrier, and a wire stop sets brush length [source S23]. Crimp height is set
  on dials [mfr S11]. Prior-art §3 describes the mechanism in more detail.
- **Third-party hand tools listed by their maker for XH.** Engineer Inc.'s
  compatibility table (2022-10-03) lists SXH-001T-P0.6 and BXH-001T-P0.6 for
  PAD-11, PAD-12, **PA-09, PA-20, PA-21** and PA-24; P0.6N only for PAD-11 and
  PA-09 [mfr S17].
  - PA-09 dies are 1.0 / 1.4 (1.7 mm thick) and 1.6 / 1.9 (1.8 mm thick). PA-20
    dies are 1.6 / 1.9 (2.0) and 2.0 / 2.3 (2.5). Engineer: die thickness =
    barrel length, die width = barrel width [mfr S18].
  - PA-09: 175 mm, 135 g, non-ratchet plier. It crimps the conductor barrel and
    the insulation barrel **in separate squeezes**, for "1.25–2.5 mm pitch"
    terminals; PA-20 covers 2.5–5.0 mm pitch [mfr S18].
  - For XH that likely means the 1.6 die for the conductor barrel and the 1.9
    die for the insulation barrel [estimate].
- **On the bench.** The iCrimp SN-2549 has an XH nest and no locator [repo].

## 3. XHP housing

| | XHP-4 | XHP-5 | XHP-6 | XHP-7 | XHP-9 |
|---|---|---|---|---|---|
| A, first to last cavity (mm) | 7.5 | 10.0 | 12.5 | 15.0 | 20.0 |
| B, body width | 10.7 | 13.2 | 15.7 | 18.2 | 23.2 |
| C, overall width | 12.3 | 14.8 | 17.3 | 19.8 | 24.8 |

- **Geometry.**
  - Pitch 2.50 mm, non-cumulative [mfr S1]. The kits' "2.54" is a common
    mislabel of 2.50 mm parts [source S32].
  - Width: A = (n−1) × 2.5, B = A + 3.2, C = A + 4.8 [mfr S2]. The 2025
    catalog's "B" is the 2016 catalog's "C" [mfr S1 vs S2].
  - Height along the mating axis 7.75 mm [mfr S2], drawn as 7.5 + 0.25 [mfr S1].
  - Depth 4.1 mm body, 5.7 mm including the lock ramp [mfr S2].
  - Assembled height on the header 9.8 mm; header posts □0.64 [mfr S1].
- **Material.** PA 6, natural white, UL94V-0 [mfr S1, S2]; clone housings are
  PA 66 [source S22, S20b].
- **Retention.** The lance is on the contact [mfr S1 drawing]. The housing's
  mating face shows a square post opening and, below it, a trapezoidal window at
  each cavity [mfr S1, S2]. Removal is with XJ-06 [mfr S10].
  - The window is the lance's catch and extraction access [assumption, from the
    drawing].
- **Insertion and retention forces are not in any public JST document**; they
  are in the licence-gated product specification or handling manual
  [mfr S16].
- **Polarization and lock.**
  - The header's four-sided box shroud "prevents the receptacle from being
    misinserted or pried" [mfr S12].
  - The housing carries a Circuit No. 1 mark (a notch at one end) [mfr S2].
  - XH housings are listed "Non-Latching" (friction ramp, no positive latch)
    [source S28].
- **Which face goes up.** The contact goes in with its lance (floor side of the
  barrels) toward the face with the windows [assumption, common practice, not
  confirmed in a JST document]. One kit housing and contact settles it.
- **A correctly latched contact.** It stops at a consistent depth with a click,
  the lance sits behind its shoulder at the window, and a light tug does not
  withdraw it [assumption]. JST's manual criteria are licence-gated.

## 4. Crimp force

- **Published.** AP-K2N delivers 14.7 kN (1.5 t) [mfr S4]. No JST, Molex or TE
  document read here gives a crimp force for a 22–28 AWG open barrel.
  Applicator and press literature quotes press capacity, not the crimp's need.
  Prior-art covers the "2 t" presses.
- **Estimate** [calc C1 §4]:

| Part of the stroke | Force | When |
|---|---|---|
| Wing tips meet the punch and curl inward (conductor and insulation) | tens to a few hundred N | first ~70 % of the ~0.9 mm conductor-punch travel |
| Insulation wings close on silicone | ~30–130 N | same stroke, stepped punch |
| Carrier cut-off shear (only if cut in the same stroke) | ~50–160 N | set point in the stroke |
| **Conductor compaction and coining** | **peak 0.75–2.3 kN** | **last ~0.10–0.20 mm, peak at bottom dead centre** |
| Total peak | **~0.8–2.6 kN; design to 3 kN, 4–5 kN capacity** | |

- **Reasoning.** Mean die pressure at bottom is 400–900 MPa [estimate]:
  work-hardened strands flow at 250–350 MPa, confined compaction needs 1.5–3×
  that, and 0.2 mm bronze wings coin at the same time. That pressure acts over crimp width ~1.5 mm × conductor barrel
  length ~1.3–1.6 mm.
- **Cross-check.** A 175 mm non-ratchet plier (PA-09) crimps XH by hand, one
  barrel per squeeze; 150–300 N of grip × 5–8 leverage = 0.75–2.4 kN
  [calc C1 §5, estimate of leverage].
- **Energy per crimp is ~0.3–0.4 J** [calc]. The precision that matters is the
  **bottom-dead-centre height, to ±0.02–0.05 mm**, since it sets crimp height;
  the rest of the stroke can be loose [estimate].
- A NEMA 23 at ~1.5 N·m reaches ~1.4 kN through a 2 mm trapezoidal lead screw,
  ~4 kN through a 2 mm ball screw, ~10 kN with 5:1 before a 4 mm ball screw
  [calc C1 §5]. The shop's 12-ton press is ~118 kN.

## 5. Inspection criteria

| Item | Criterion | Source |
|---|---|---|
| Crimp height | The key process variable; measure at barrel centres; J.S.T. UK tolerance ±0.05 mm on SXH-002 and SXA | [mfr S5, S13, S14]; TE examples ±0.03–0.05 [source S24] |
| Bellmouth | Must be present at the rear of the conductor barrel, not excessive; ~1–2× stock thickness (0.2–0.4 mm here) | [mfr S5]; [source S23, S24] |
| Conductor brush | Strands visible past the front of the conductor barrel, not reaching the contact (box) area | [mfr S5]; [source S23, S24] |
| Inspection window | Insulation enters the insulation barrel; conductor and insulation seen between the barrels "approximately 50/50"; insulation must not be under the conductor barrel | [mfr S5] |
| Cut-off tab | Present and short; ~1.0–1.5× thickness, usually flush to one thickness | [mfr S5]; [source S23] |
| Insulation crimp | Holds the insulation without cutting through to strands; survives 60–90° bends several times | [mfr S5]; [source S23] |
| Shape | No bend-up/down, twist or roll of the contact at the barrel; no strands outside the barrel; lance and box undeformed | [mfr S5]; [source S24] |
| Pull-out | ≥39.2 N at 22 AWG (JST); ≥35.6 N (UL 486A) | [mfr S6]; [source S23] |
| Strands | No cut or nicked strands from stripping; strands not spread apart or over-twisted | [mfr S5] |

IPC/WHMA-A-620 has sections for each of these: inspection window 5.1.1.1,
bellmouth 5.1.4, conductor brush 5.1.5, carrier cut-off tab 5.1.6, and Table
3-1 "Allowable Strand Damage" [source S25, table of contents only]. Its numeric
limits were not read; the standard is sold by IPC.

## 6. Availability, observed 2026-09-28

Digi-Key, Newark, TME and Heilind figures come from the findchips aggregator
[source S26]. LCSC figures come from LCSC product pages or JLCPCB's parts
library, which mirrors LCSC [source S27, S28]. Mouser was not observed:
blocked, and absent from the aggregator.

| Part | Distributor, form | Stock | Price |
|---|---|---:|---|
| **SXH-001T-P0.6** | Digi-Key reel (455-1135TR-ND) | 1,329,000 | $0.0235 @ 8k |
| | Digi-Key 100 / 500 / 1,000 lots (455-1135-100/-500/-1000-ND) | 3,100 / 2,500 / 5,000 | $0.0471 / $0.0421 / $0.0401 |
| | Newark 51AC2234 (cut) / 49Y1258 (reel) | 236,854 / 1,624,000 | $0.0556 @1, $0.039 @201 / $0.019 @8k |
| | TME | 137,204 | from $0.0215 @200 |
| | Heilind reel / cut strip / loose piece | 732,000 / 39,000 / 10,695 | $0.0227 @8k / $0.0305 @1k / $0.0301 @1 |
| | LCSC C140573 | 406,500 | $0.0127 @100 (min 100), $0.0100 @1k |
| **BXH-001T-P0.6** | Digi-Key BXH-001T-P0.6-ND | 137,303 | $0.0444 @50, $0.0423 @100 |
| | Newark 73M9274 | 300,647 | $0.0455 @1 |
| | TME | 48,717 | $0.0420 @5 |
| | LCSC C594456 | 400 | $0.0705 @10 |
| SXH-001T-P0.6N | Digi-Key reel / 100 lot | 140,000 / 3,900 | $0.0299 @5k / $0.0579 |
| **XHP-4** | Digi-Key 455-2267-ND / Newark / LCSC (black XHP-4-BK C493084) | 126,939 / 893,374 / 3,637 | $0.0584 @50 / $0.0501 @1 / $0.0488 |
| **XHP-5** | Digi-Key 455-2268-ND / Newark / LCSC C144404 | 19,566 / 363,896 / 7,786 | $0.0646 @50 / $0.0552 / $0.0246 |
| **XHP-6** | Digi-Key 455-2218-ND / Newark / LCSC C144405 | 106,462 / 292,105 / 22,915 | $0.0748 @50 / $0.0663 / $0.0278 |
| **XHP-7** | Digi-Key 455-2269-ND / Newark / LCSC C144406 | 70,162 / 40,447 / 8,450 | $0.0826 @50 / $0.0678 / $0.0325 |
| **XHP-9** | Digi-Key 455-2217-ND / Newark / LCSC C157883 | 3,408 / 7,725 / 260 | $0.1226 @50 / $0.1120 / $0.0346 |

### Genuine JST vs clones

- **Clone contacts are catalogued, on reels, at LCSC.**
  - CJT A2501-TP, C339286: 665,523 at $0.0079 [source S28].
  - DLL TJC3-T, C22374382: ~8,800 at $0.010 [source S28].
  - HDGC2501-T, C5292543: 6,338 at $0.0073 [source S28].
- **Clone drawings agree with each other and with JST's outline:** 0.20 mm
  C5191 phosphor bronze, tin-plated (over nickel on HDGC and CJT); ~5.8–6.7 mm long; box ~1.85–1.9 wide;
  #28–#22 [source S19–S22].
- **Differences visible on paper** [source S1 vs S19–S22]:
  - Insulation barrels drawn wider and taller (2.5–3.0 × 2.75–3.2 open) than
    JST's 1.95 × 2.4 end-view envelope.
  - Insulation OD minimum 1.2 mm (DLL) or "1.9 max" (CJT), against JST's
    0.9–1.9.
  - Reel counts differ.
- **Clone housings** (CJT A2501H) match XHP's body width (A + 3.2) and depth
  4.1 mm, are drawn 8.0 mm tall, and are PA 66 [source S22].
- **CQRobot kit parts.** Their origin is unknown [repo], and no maker page
  documents them. Forum or teardown write-ups on genuine-versus-clone behaviour
  were **not gathered**: web search was unavailable to this pass (Unresolved).

## 7. The wire: BNTECHGO 22 AWG silicone flat ribbon

| Property | Value | Label |
|---|---|---|
| Conductor | **60 × 0.08 mm tinned copper** per conductor ("60*4 strands" for 4P) | [source S29] |
| Copper area | 0.302 mm² (22 AWG nominal 0.324) | [calc C1 §1] |
| Conductor OD, and ribbon pitch | **1.7 mm ±0.1 per conductor**; ribbon "1.7*N mm" (4P 1.7 × 6.8, 5P 1.7 × 8.5) | [source S29, S29b, S29c] |
| Strand bundle diameter | ~0.69–0.74 mm | [calc C1 §1] |
| Insulation wall | ~0.43–0.55 mm, nominal ~0.49 | [calc C1 §1] |
| Ratings | 200 °C, −60 °C, 600 V | [source S29] |
| Web between conductors (thickness, notch depth), tear strength | **not stated by BNTECHGO** | — |
| Fit to XH | 1.7 mm OD is inside XH's 0.9–1.9 range, near the top; inside P0.6N's 1.3–1.9 too | [mfr S1] |
| Splay | 1.7 → 2.5 mm pitch: a 5P's outer conductors move ±1.6 mm; in J1 (5P + 4P into XHP-9) the outermost moves ~3.2 mm | [calc C1 §2] |

The repo's bom lines "1.7 × 3 mm section" (3P) and "1.7 × 5 mm section" (5P)
restate BNTECHGO's "1.7*N" notation. The sections are 1.7 × 5.1 and
1.7 × 8.5 mm [source S29, S29b, S29c].

### Silicone insulation and stripping

- **Material** [source S31]:
  - Silicone rubber has "low tensile strength and poor wear-and-tear
    properties".
  - It is a cured elastomer that does not melt. Its decomposition products
    containing silicon "are less volatile" than those of carbon polymers.
  - Silicone cables serve from about −90 to 200 °C.
- **Blade stripping.** The insulation is soft and compressible. It is expected
  to stretch and tear rather than part on a shallow score, leaving a ragged
  end. A blade set deep enough to part it reaches the 0.08 mm strands
  [assumption; repo notes the tear behaviour]. A 60-strand conductor has many
  outer strands to nick. JST wants no nicked strands [mfr S5].
- **Thermal (hot-blade) stripping.** Silicone does not melt, so a hot blade
  decomposes it slowly rather than cutting it [assumption, from S31]. Prior-art
  lists a trial.
- **Lasers.**
  - **CO₂** (10.6 µm) is the usual choice for polymer insulation [source S30].
    Copper reflects almost all of 10.6 µm, so the conductor is largely safe
    [assumption, general optics]. Silicone ablates to a white silica ash that
    must be brushed or wiped off before crimping [assumption, consistent with
    S31].
  - **Fiber** (1.06 µm): black insulation absorbs through its pigment. Copper
    absorbs more than at 10.6 µm, and the tin plating melts at 232 °C. The
    risk to strands is higher than with CO₂ [assumption]. Derek's XLaserlab X1
    Pro is a kW-class welder/cleaner and would need heavy attenuation or pulse
    control for 0.5 mm insulation [estimate].
  - **Diode** (~445–455 nm): black silicone absorbs well, and copper absorbs far
    more in blue than in IR. Strand damage is the main risk at low power
    [assumption].
  - No document read gives silicone-specific laser stripping parameters.

## Unresolved

Each item gives what the documents could not settle and the single observation
that would settle it.

1. **SXH-001T-P0.6 crimp height and width for 22 AWG** are licence-gated
   (JST drawing, handling manual CHM-1-151). Derek can request the XH manual
   through JST's form, which emails it. Or: crimp five contacts on the ribbon,
   measure crimp height at the barrel centre with a point micrometer (a crimp
   micrometer measures better than a caliper [source S23]), and pull-test
   against 39.2 N.
2. **Carrier pitch, pilot-hole size and position, tab length and barrel
   lengths.** One 100-piece Digi-Key strip (455-1135-100-ND, $4.71) under a
   caliper or the Revopoint scanner settles all of them.
3. **Whether the CQRobot contacts match JST.** Caliper one kit contact against
   §1: length, box 1.85 or 1.95 wide, stock 0.20 mm, barrel open widths. Check
   whether the lance catches in a genuine XHP housing.
4. **Contact insertion force and retention in XHP** are not public. Push a
   crimped contact home with the 0.1 g scale under the housing; pull a latched
   one with a hook and luggage scale.
5. **Lance-to-window orientation and what "latched" looks like** are not in a
   public JST document. Look at one kit housing with a contact in it under the
   ELP camera.
6. **Ribbon web geometry and peel behaviour** (web thickness, notch depth,
   whether it zips without nicking) are unstated by BNTECHGO and remain repo
   Open item 5. Section one ribbon with a blade and measure; peel a metre.
7. **Actual strand bundle and wall** (the calc says ~0.72 mm and ~0.49 mm).
   Measure one stripped conductor with the caliper.
8. **Crimp force** is estimated only (0.8–2.6 kN). Squeeze the SN-2549 through
   an XH crimp against a bathroom scale and multiply by the tool's measured
   handle-to-die ratio; or crimp once on a load cell.
9. **Silicone laser behaviour by wavelength** is unsourced. One test strip at
   low power with the fiber laser, if Derek chooses, shows ash, charring and
   strand damage.
10. **IPC/WHMA-A-620 numbers** (bellmouth, brush, tab, Table 3-1 strand damage)
    were not read; the standard is paid.
11. **Mouser stock** was not observed.
12. **Genuine-versus-clone field reports** (forums, teardowns) were not
    gathered; web search was blocked in this pass.
13. **MKS-L versus MKS-SC as the "strip-crimp" applicator**: JST's 2016 XH
    catalog and its 2022 tooling catalog disagree.
14. **JST contact length, 6.1 or 6.5 mm (Shape B):** the 2025 and 2016/2021
    catalogs disagree. Item 2's strip measurement settles it.

## Sources

- **C1** [`calc/xh_crimp_estimates.py`](calc/xh_crimp_estimates.py), output [`calc/xh_crimp_estimates.out.txt`](calc/xh_crimp_estimates.out.txt)
- **S1** [JST XH catalog, 2025 edition (eXH.pdf)][S1]
- **S2** [JST XH catalog, 2016 edition (LCSC-hosted copy)][S2]
- **S3** [JST XH catalog, 2021 edition (J.S.T. UK copy)][S3]
- **S4** [JST Application Tooling catalog, 2022 (LCSC-hosted copy)][S4]
- **S5** [JST Handling Precautions for Terminals and Connectors, incl. Precautions for Crimping Process][S5]
- **S6** [JST WC-110 Tool Specification and Calibration (Digi-Key host)][S6]
- **S7** [J.S.T. UK WC-110][S7]
- **S8** [J.S.T. UK YRS-110][S8]
- **S9** [J.S.T. UK YC-110R][S9] · [YC-111R][S9b]
- **S10** [J.S.T. UK XJ-06][S10]
- **S11** [J.S.T. UK CDS SXH001-06/CMKS-L applicator][S11]
- **S12** [J.S.T. UK XH connector series page][S12]
- **S13** [J.S.T. UK crimp specification SXH-002-P0.6][S13]
- **S14** [J.S.T. UK crimp specification SXA-01T-P0.6][S14]
- **S15** [J.S.T. UK crimp specification SPH-002T-P0.5L][S15]
- **S16** [JST XH product page (licence-gated drawings and manuals)][S16]
- **S17** [Engineer Inc. JST compatibility table, 2022-10-03][S17]
- **S18** [Engineer Inc. die matrix][S18] · [Engineer tool selection page][S18b]
- **S19** [HDGC2501-T (XH2.5-T) drawing, LCSC][S19]
- **S20** [DLL/ZJLQ TJC3 XH2.54-T drawing][S20] · [DLL TJC3 catalog][S20b]
- **S21** [JXTCONN B2542-2DP1 XH2.5 terminal drawing][S21]
- **S22** [CJT A2501 series catalog][S22]
- **S23** [Molex Quality Crimping Handbook (2001, archived copy)][S23]
- **S24** [TE Crimp Quality Guidelines poster (archived)][S24]
- **S25** [IPC/WHMA-A-620B table of contents (archived)][S25]
- **S26** findchips aggregator: [SXH-001T-P0.6][S26], and the same URL pattern for BXH-001T-P0.6, XHP-n, WC-110, YRS-110, YC-110R, XJ-06, APLMK SXH001-06, CDS SXH001-06
- **S27** [LCSC C140573 SXH-001T-P0.6][S27] · [LCSC C594456 BXH-001T-P0.6][S27b]
- **S28** [JLCPCB parts library (LCSC stock)][S28]; clone pages: [C339286][S28a] · [C22374382][S28b] · [C5292543][S28c]
- **S29** [BNTECHGO 22 AWG 4P ribbon][S29] · [3P][S29b] · [5P][S29c] · [22 AWG single wire][S29d]
- **S30** [Laser Wire Solutions FAQ][S30]
- **S31** [Wikipedia: Silicone rubber][S31]
- **S32** [Wikipedia: JST connector][S32]

[S1]: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf
[S2]: https://datasheet.lcsc.com/datasheet/pdf/51bbcb0476af7caf7f697437212da775.pdf
[S3]: <https://www.jst.co.uk/downloads/series/eXH_(21-04-07).pdf>
[S4]: https://datasheet.lcsc.com/datasheet/pdf/c2c6da2f6fcb6815701d2cc397c6283c.pdf
[S5]: https://www.jst-mfg.com/product/pdf/eng/handling_e.pdf
[S6]: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8948/WC-110%20SPEC%20&%20CAL.pdf
[S7]: https://www.jst.co.uk/productSeries.php?pid=10793
[S8]: https://www.jst.co.uk/productSeries.php?pid=10792
[S9]: https://www.jst.co.uk/productSeries.php?pid=10794
[S9b]: https://www.jst.co.uk/productSeries.php?pid=10795
[S10]: https://www.jst.co.uk/productSeries.php?pid=10597
[S11]: https://www.jst.co.uk/productSeries.php?pid=11276
[S12]: https://www.jst.co.uk/productSeries.php?pid=11809
[S13]: https://www.jst.co.uk/downloads/series/SXH-002-P0.6.pdf
[S14]: https://www.jst.co.uk/downloads/series/SXA-01T-P0.6.pdf
[S15]: https://www.jst.co.uk/downloads/series/SPH-002T-P0.5L.pdf
[S16]: https://www.jst-mfg.com/product/detail_e.php?series=277
[S17]: https://www.nejisaurus.engineer.jp/_files/ugd/104650_594335d26d724883affcaa8929df7c19.pdf
[S18]: https://www.nejisaurus.engineer.jp/_files/ugd/104650_b9d3bc13ee574fb3a87bbe3b5562e9fc.pdf
[S18b]: https://www.nejisaurus.engineer.jp/crimping-tool-selection-method
[S19]: https://datasheet.lcsc.com/datasheet/pdf/85b41e09dabe29edfe9d0c560ebdecf1.pdf
[S20]: https://datasheet.lcsc.com/datasheet/pdf/4530046e74edb8f06c46e12373985b12.pdf
[S20b]: https://datasheet.lcsc.com/datasheet/pdf/31bf21d92bce9b5aa1a911e28f332df8.pdf
[S21]: https://datasheet.lcsc.com/datasheet/pdf/4792d01d3badb0b74be887c5ac38e1da.pdf
[S22]: https://datasheet.lcsc.com/datasheet/pdf/85df6f829f18440db2c480a1e8b8ad36.pdf
[S23]: https://web.archive.org/web/20210818182409/https://www.shearwater.com/wp-content/uploads/2012/08/qual_crimp.pdf
[S24]: https://web.archive.org/web/20130702004747/http://tooling.te.com/pdf/US_crimpposter.pdf
[S25]: https://web.archive.org/web/2016/http://www.ipc.org/TOC/IPC-WHMA-A-620B.pdf
[S26]: https://www.findchips.com/search/SXH-001T-P0.6
[S27]: https://www.lcsc.com/product-detail/C140573.html
[S27b]: https://www.lcsc.com/product-detail/C594456.html
[S28]: https://jlcpcb.com/parts
[S28a]: https://www.lcsc.com/product-detail/housing-contact_cjt-changjiang-connectors-a2501-tp_C339286.html
[S28b]: https://www.lcsc.com/product-detail/housing-contact_dll-tjc3-t_C22374382.html
[S28c]: https://www.lcsc.com/product-detail/housing-contact_hdgc-hdgc2501-t_C5292543.html
[S29]: https://bntechgo.com/bntechgo-22-gauge-silicone-ribbon-cable-copper-wire-4p-flat-cable-22-awg-flexible-soft-silicone-rubber-parallel-wire-stranded-tinned-copper-wire-4-pin-black-250-ft/
[S29b]: https://bntechgo.com/bntechgo-22-gauge-silicone-ribbon-cable-copper-wire-3p-flat-cable-22-awg-flexible-soft-silicone-rubber-parallel-wire-stranded-tinned-copper-wire-3-pin-black-250-ft/
[S29c]: https://bntechgo.com/bntechgo-22-gauge-silicone-ribbon-cable-copper-wire-5p-flat-cable-22-awg-flexible-soft-silicone-rubber-parallel-wire-stranded-tinned-copper-wire-5-pin-black-250-ft/
[S29d]: https://bntechgo.com/22-awg-silicone-wire-stranded-tinned-copper-wire-1-feet-11-colors-optional/
[S30]: https://www.laserwiresolutions.com/faqs/
[S31]: https://en.wikipedia.org/wiki/Silicone_rubber
[S32]: https://en.wikipedia.org/wiki/JST_connector
