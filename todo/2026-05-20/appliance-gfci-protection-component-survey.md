# Appliance GFCI / shock-protection path — component survey, verified options, and revised recommendation that supersedes Part 3 of yesterday's electrical-safety-acceptance gap doc

**Author:** hourly agent, 2026-05-20
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents
**Supersedes:** Part 3 (lines 137–170) and item 3 of "What I'd want to read" (lines 226–228) in [`../2026-05-19/electrical-safety-acceptance-gap.md`](../2026-05-19/electrical-safety-acceptance-gap.md). Parts 1, 2, 4, 5 of that doc are unaffected by this work and stand as written.

---

## Why this doc exists

The 2026-05-19 electrical-safety-acceptance-gap.md was written in a single pass and committed two specific factual claims that I could not verify in follow-up research, and that on re-examination are wrong:

1. **"Leviton GFCI 5-15 plug-in adapter"** (line 154 of the parent doc) was named as the recommended in-box portable GFCI for customers whose under-sink receptacle is not GFCI-protected. Leviton does **not** sell a plug-in GFCI adapter on Amazon Prime in any wall-pack form factor — the search returns wall-mount receptacles, industrial connectors, and breakers, none of which is the bricklet form factor described. The specific model "Leviton 15300-DS" mentioned in chat by an earlier turn also does not exist as a Prime listing today (2026-05-20).
2. **"NEMA 5-15P → C13 LCDI cord"** (line 163 of the parent doc, and the "what I'd want to read" follow-up at line 227) was named as the long-term hardware fix — a self-protecting line cord that would make the appliance safe on any wall outlet. After a supplier-by-supplier check (13 catalogs), **this product configuration does not exist** at any major line-cord OEM. The LCDI segment is built around NEMA 5-15P / 6-15P / 6-20P terminations with bare-wire pigtail or hardwired ends for room ACs, dehumidifiers, and pool pumps; the C13/C14 ecosystem is the IT/AV world where LCDI was never required, and the two product trees never meet on a shelf. UL 943C in the parent doc was also miscited (it's the special-purpose-GFCI standard for 480/600 V industrial, not the LCDI standard — LCDI is governed by UL 1699 and pulled in via UL 484 for room ACs).

Both of those wrongs together degrade the parent doc's Part 3 from "actionable plan" to "needs research before any action is taken." This doc closes that gap with verified components.

---

## TL;DR — what changes

| | Parent doc Part 3 said | Verified-as-of-2026-05-20 reality |
|---|---|---|
| Customer-side in-box adapter | "Leviton GFCI 5-15 plug-in adapter, $20–40" | No name-brand (Leviton/Hubbell/Pass&Seymour) wall-pack manual-reset GFCI adapter exists on Amazon Prime today. Available options are all Chinese-OEM (ELEGRP, EP, AIDA, GREATIDE) at $16–20 retail, with `UL Listed` per listing copy but no easily-verifiable UL file number. Tower Manufacturing 30439005 ($19.68) is name-brand but **auto-reset**, which is a different safety profile from what most use cases want. |
| Long-term hardware fix | "Move the cord to an LCDI variant (NEMA 5-15P → C13 LCDI), self-protecting on any wall" | No 5-15P/LCDI/C13 cord exists at Tripp Lite, Volex, Quail, Interpower, Tower, Sungold, Aerospec, L-com, StarTech, Monoprice, Amazon Prime, Digi-Key, Mouser. **BUT** — the closely-related **5-15P/GFCI/C13 cord** does exist as a stocked, UL-listed, Leviton-built unit at Americord at $65.60 ([direct link](https://www.americord.com/products/10ft-leviton-gfci-5-15p-to-iec-320-c-13ra-computer-power-cord-14-3-sjtw-na), 10 ft, 14/3 SJTW, UL/CSA approved, in stock). That cord is what the parent doc thought the LCDI cord would be, with a different listing class (UL 943 Class A GFCI, 6 mA trip, residential personnel protection) that is actually the **correct** listing for this use case anyway — LCDI's job is cord-arc-fire protection on room ACs, not shock protection at the load. |
| Internal GFCI on the appliance | Not discussed in parent doc | Code-legal (NEC 422.5(B)(5) explicitly permits "factory installed within the appliance") and standards-recognized (UL 943 scope permits Class A GFCIs to be integrated into other devices). Buildable from a $0.30 onsemi RV4145A sense IC (PDIP-8 or SOIC-8), plus a sense CT, latching relay, SCR, and ~15 passives — ~$8–13 BOM at qty-50. **But** the UL 943 listing of the integrated subassembly is the dominant cost driver at low volume, not the BOM. Defer to Standard Edition (qty ≥ 1000). |

The net recommendation revision: **switch the included line cord from a generic 5-15P → C13 to the Americord/Leviton GFCI 5-15P → C13 unit**. That is the practical, off-the-shelf, UL-listed, supply-chain-stable answer for Founder Edition. The internal-GFCI module is the Standard Edition path once a custom AC PCB exists. The Chinese-OEM in-box adapter is no longer needed.

---

## Part A — Internal GFCI: is it actually a thing?

Short answer: **code-legal and standards-recognized, but not a common consumer-appliance industry pattern**. The dominant industry pattern is in-cord LCDI/ALCI for room ACs and dehumidifiers, and upstream-receptacle GFCI for hot tubs, pool pumps, electric water heaters, and commercial under-counter dishwashers. I could not, in a structured search across six product categories, locate a single specific consumer/commercial appliance with a documented factory-installed internal GFCI board.

### What the code says

**NEC 422.5(B)** lists five permissible GFCI placements for appliances. The fifth is verbatim: ["Factory installed within the appliance"](https://www.ecmweb.com/national-electrical-code/qa/article/21213038/stumped-by-the-code-nec-requirements-for-gfci-protection-of-appliances) (cross-confirmed at [captaincode2020.leviton.com/node/261](https://captaincode2020.leviton.com/node/261)).

### What the standard says

**UL 943** scope language: "These Class A GFCIs are permitted to be integrated into other devices, in which case, besides complying with this Standard, these devices are to comply with the corresponding applicable Standard for the device in question." ([UL standards catalog, UL 943 product page](https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=31122).)

### What the products say

Hot tubs (Balboa, Gecko spa controllers): GFCI is in the **service panel or line-of-sight sub-panel**, NOT inside the spa pack. 120 V plug-and-play hot tubs ship with a **15 ft in-cord GFCI cord set** ([reference: Balboa BP7 install manual](https://spacare.com/assets/images/G5361%20BP7%20Installation%20Manual.pdf); [hot tub installation post](https://www.hottuboutpost.com/hot-tub-electrical-installation-hookup-gfci/)).

Pool pumps (Pentair, Hayward): GFCI is an **external breaker** ([Pentair PA220GF page](https://www.pentair.com/en-us/products/residential/pool-spa-equipment/pool-automation/gfci_circuit_breakers.html)).

Dehumidifiers (Haier and similar): in-cord LCDI/GFI plug, not internal ([Haier support 35264](https://www.haierappliances.com/support/support-content/35264)).

Window/portable air conditioners: in-cord LCDI per UL 484 + NEC 440.65 ([Tower Manufacturing LCDI page](https://www.towermfg.com/lcdi/), [IAEI Magazine on AC LCDI](https://iaeimagazine.org/2017/julyaugust-2017/air-conditioning-equipment-installations/)).

Electric water heaters: typically hardwired; no internal GFCI; protection (if any) is in the branch circuit when triggered by location ([KB Electric 2020 NEC summary](https://kbelectricpa.com/nec-2020-code-changes-for-gfci-protection-what-you-should-know/)).

Commercial under-counter dishwashers: GFCI is upstream (breaker or receptacle); [forum discussion at mikeholt.com](https://forums.mikeholt.com/threads/commercial-kitchen-dishwasher-gfi-requirement.2561962/) confirms NEC's "factory installed within the appliance" option is recognized but no specific product was named.

Countertop ice makers: no mention of internal GFCI in any manual surfaced ([Frigidaire EFIC117 manual at manuals.plus](https://manuals.plus/frigidaire/efic117-26-lbs-ice-maker-manual)).

### What this means for our appliance

Internal GFCI is a **legitimate engineering path**, not a regulatory novelty. It is also **not a common industry choice for this product category**. If we go with it, we are establishing precedent (similar to how the project is establishing precedent on R-600a refrigerant in a non-listed unit) rather than following one. The two pieces of precedent compound: a non-listed plumbed appliance with hydrocarbon refrigerant and an integrated GFCI is a more novel design than the parent doc reckoned, and the case for following the off-the-shelf cord path strengthens.

---

## Part B — The four paths to the customer's safety, ranked

### Path 1 — Americord/Leviton GFCI line cord (RECOMMENDED for Founder Edition)

[Americord product page](https://www.americord.com/products/10ft-leviton-gfci-5-15p-to-iec-320-c-13ra-computer-power-cord-14-3-sjtw-na) — *verified 2026-05-20, in stock, $65.60.*

The included line cord is replaced with a UL/CSA-listed 14/3 SJTW assembly with an integrated **Leviton GFCI plug head** at the wall end and a C13 right-angle connector at the appliance end. The Leviton head is **UL 943 Class A, 6 mA trip, 15 A / 125 V** — the textbook listing for residential personnel protection. The Leviton portable GFCI heads are documented at [store.leviton.com](https://store.leviton.com/products/portable-automatic-reset-gfci-cord-set-15a-125v-25-ft-cord-gfa15-25c) for the GFA15-series cord assemblies (auto-reset variants); the manual-reset family is similar. **The Americord listing does not specify manual vs. auto reset** — that is a clarification to obtain from Americord or Leviton before ordering quantity (see Open Items §1 below).

**Why this is right:**
- Off-the-shelf, no custom build, no UL listing exercise, no MOQ gate.
- C14 panel-mount inlet stays exactly as-is — no enclosure or AC-side changes.
- Customer's receptacle does not need to be GFCI. The cord is self-protecting at the wall plug.
- Documented UL listing path (Leviton is the listed manufacturer; Americord is the assembler with downstream UL/CSA approval on the assembly).
- Trust story scales with the Founder Edition narrative: "this is a real UL-listed safety device wired into a real appliance." No hand-waving.

**Cost reality:**
- $65.60 single-quantity from Americord.
- $5 was the assumed cost of a generic 5-15P → C13 cord previously. Net delta is **~$60/unit**.
- At $7,500 Founder Edition pricing, $60 = 0.8 % of revenue. At $5,500 Standard Edition pricing, $60 = 1.1 % of revenue. Within reasonable headroom for both tiers if the listing-and-recognition trade-off is judged worth it.
- Bulk pricing at 50-unit quantity needs an Americord or Leviton quote. Comparable Leviton in-cord GFCI assemblies (the [GFA15-25C 25 ft auto-reset cord set](https://store.leviton.com/products/portable-automatic-reset-gfci-cord-set-15a-125v-25-ft-cord-gfa15-25c)) list at $80–110 retail, suggesting $40–55 at OEM bulk is realistic. Confirm before committing.

**Open risks / gotchas:**
- The cord is detachable. A customer can swap it for a generic C13 cord and defeat the protection. The Americord cord head is large enough that visual recognition is likely (the GFCI brick is unmistakable). The user manual should explicitly state "do not replace the supplied line cord."
- "Right-angle C13" (C-13RA) is the connector geometry — verify it physically clears the rear-panel C14 inlet's recess shroud (per `printed-parts/enclosure/back-panel/README.md` the inlet is recessed 3–5 mm; the C13RA's housing geometry needs to nest into that).
- 10 ft cord is what's stocked. A 6 ft variant may not be standard and would require a custom run. 10 ft is the safer choice for the use case anyway (under-sink to under-sink receptacle is short, but the customer's outlet might be on the opposite wall).
- Manual vs. auto reset: a kitchen plumbed appliance is closer to a hot-tub / dishwasher use case where manual reset is preferable (a tripped device should require human acknowledgment, not silent re-energization). Leviton manufactures both; the Americord page does not specify which is shipped — clarify before order.

### Path 2 — In-box plug-in GFCI wall-pack adapter (NOT recommended — supply chain fragility)

A separate brick goes in the carton. Customer plugs the brick into the wall, then the generic C13 cord into the brick.

**What's available on Amazon Prime (verified 2026-05-20):**

| Brand / Model | ASIN | Price | Reset | Form Factor | Notes |
|---|---|---|---|---|---|
| ELEGRP Manual Reset Single Outlet GFCI Adapter (yellow) | [B096WVP698](https://www.amazon.com/dp/B096WVP698) | $17.99 | Manual | Wall-pack, 5-15P → 5-15R, 15 A | UL Listed per listing copy; self-test every 5 sec; LED |
| EP GFCI Adapter (yellow) | [B0CCHMMYFZ](https://www.amazon.com/dp/B0CCHMMYFZ) | $16.99 | Manual | Wall-pack, 5-15P → 5-15R, 15 A | Identical spec/wording — appears to be same OEM as ELEGRP under different brand |
| AIDA GFCI Adapter (white) | [B0D49B3CMT](https://www.amazon.com/dp/B0D49B3CMT) | $19.99 | Manual | Wall-pack, 5-15P → 5-15R, 15 A | Same OEM, **white color** — best aesthetic for under-sink |
| GREATIDE GFCI Adapter (yellow) | [B0DPKGMF1H](https://www.amazon.com/dp/B0DPKGMF1H) | $16.89 | Manual | Wall-pack, 5-15P → 5-15R, 15 A | Same OEM, cheapest of the four |
| Tower Manufacturing 30439005 (yellow) | [B00UOU6OVU](https://www.amazon.com/dp/B00UOU6OVU) | $19.68 | **Auto** (disqualifying for this use case) | Wall-pack, 5-15P → 5-15R, 15 A | Name brand (Tower is the OEM-only LCDI specialist); auto-reset is wrong for a kitchen plumbed appliance |

**Why this path is worse than Path 1:**
- The four manual-reset Amazon Prime options (ELEGRP / EP / AIDA / GREATIDE) all appear to be the same Chinese-OEM product rebranded. Stock continuity is at the mercy of one factory's relationship with whichever brand is in stock that month. For a product the founder intends to bundle in every shipping carton over a 4-year Founder Edition run, this is a real supply-chain risk.
- Name-brand Leviton / Hubbell / Pass & Seymour portable wall-pack GFCIs are absent from Amazon Prime. Direct-from-distributor (Grainger, McMaster) would cost more and ship later.
- The customer has to plug two things in series (brick + cord), which is one more physical surface to fail and one more visual element under the sink.
- The brick is a separate object the customer can lose, misplace, or replace.

**Cost:** ~$17 retail per brick; OEM bulk likely $5–10 at quantity-50 (Tower Manufacturing or similar would be the contact, OEM-only) — but the supply chain reliability argument trumps the cost saving over Path 1.

### Path 3 — Internal GFCI module on the appliance AC board (RECOMMENDED long-term for Standard Edition)

A small PCB on the electronics shelf, between the C14 inlet and the AC distribution block, that does ground-fault detection and opens a relay if leakage exceeds the trip threshold.

**Verified IC options:**

| Part | Manufacturer | Self-test (UL 943 post-2015) | Status | Qty-1 | Qty-1000 | Package | Notes |
|---|---|---|---|---|---|---|---|
| [RV4145A](https://www.onsemi.com/products/power-management/gfci-controllers/rv4145a) | onsemi (formerly Fairchild) | **No** | Active (datasheet Rev. 3 June 2024) | $0.30 (Rochester) | $0.41 (Rochester); $0.17 (LCSC) | SOIC-8 / PDIP-8 | Cheapest. Legacy non-self-test part. Acceptable for a non-listed integrated module; would fail listed-standalone UL 943 test. |
| [NCS37010](https://www.onsemi.com/products/power-management/gfci-controllers/ncs37010) | onsemi | **Yes** | Active, in stock | $1.87 (DigiKey / Mouser, 2,640 units) | $0.95–$1.01 | QFN-16 / TSSOP-16 | **Recommended IC** if pursuing the integrated path with possible future UL listing. Self-tests at power-up and every ~17 min, locks out on test failure. |
| [NCS37014](https://www.onsemi.com/products/power-management/gfci-controllers/ncs37014) | onsemi | Yes | Active | (similar to 37010) | (similar) | — | Self-test variant; alternative to NCS37010. |
| [NCS37021](https://www.onsemi.com/products/power-management/gfci-controllers/ncs37021) | onsemi | Yes | Active (datasheet (c) 2024) | (TBD) | (TBD) | — | Newest in the NCS370xx family. |
| [FAN4149](https://www.onsemi.com/products/power-management/gfci-controllers/fan4149) + [FAN41501](https://www.onsemi.com/products/power-management/gfci-controllers/fan41501) | onsemi | Yes (pair-based) | Active | (TBD) | (TBD) | — | Findchips shows ~150 units total stock — sourcing risk vs. NCS370xx. |
| NCS37000 | onsemi | Yes | Active but broker-only stock | (broker) | (broker) | — | **Skip — superseded** by 37010/37014/37021. |
| LM1851 | TI / National | — | **Obsolete** | broker only | broker only | — | Skip. |

Cross-check at [findchips.com/search/RV4145A](https://www.findchips.com/search/RV4145A) and [findchips.com/search/NCS37010](https://www.findchips.com/search/NCS37010) — RV4145A verified active with Rochester 11,869 units, NCS37010 verified active with DigiKey 2,640 units.

**Reference design (verified):** Arrow Electronics hosts a typical-app reference for the RV4145A at ["Typical GFI Application Circuit for RV4145A"](https://www.arrow.com/en/reference-designs/typical-gfi-application-circuit-for-rv4145a-3-wire-low-power-ground-fault-interrupter/fbae4b6a8e6d502b627382f01431edce004b97686b). The onsemi datasheet ([Mouser hosted PDF](https://www.mouser.com/datasheet/2/149/RV4145A-116878.pdf)) carries the typical-application schematic on page 5–6 (two sense CTs, bridge rectifier, SCR, mechanical relay, ~15 passives).

**BOM estimate (synthesized from datasheet typical app):**

| Item | Cost @ qty-50 |
|---|---|
| RV4145A SOIC-8 | $0.40 |
| Differential zero-sequence CT (~1000:1, Coilcraft / Triad / Würth) | $2.00–$4.00 |
| Grounded-neutral CT (~1000:1) | $1.00–$2.00 |
| SCR (MCR100-class, 0.8 A) | $0.20 |
| Latching relay 15 A AC (Panasonic ADW1212HLW or Omron G2RL) | $2.50–$4.00 |
| Bridge rectifier (DB107) | $0.10 |
| Test push-button, reset mechanism | $0.50–$1.50 |
| ~15 passives | $0.50 |
| 2-layer PCB (~25 × 40 mm or ~40 × 60 mm with CTs) | $0.30 |
| **Subtotal** | **~$8–13** |

At qty-1000, expect ~$4–7 BOM. Under the $15 target at both tiers.

**The catch — UL listing of the subassembly:**

A custom integrated GFCI subassembly that is sold inside a consumer appliance generally needs to be **UL 943 listed** (or the integrated assembly listed under both UL 943 and the appliance's own standard, per UL 943's scope language). Listing fees for a configuration change are typically $15K–40K one-time, plus engineering and sample build costs.

At qty-50 (Founder Edition), the listing amortization is $300–800/unit, which crushes the BOM-cost advantage and makes Path 1 dramatically cheaper. At qty-1000 (Standard Edition), amortization is $15–40/unit, which makes Path 3 the clear winner: $20–48/unit all-in vs. $40–55/unit for the Americord cord at bulk pricing.

**The harder-to-quantify side benefit:** Path 3 cannot be defeated by the customer swapping the cord. The integrated GFCI is downstream of the C14 inlet on the appliance side; whatever cord they plug in, the GFCI fires. Path 1 is defeatable by cord swap. This matters more than it might seem because the Founder Edition trust narrative ([target-market.md](../../marketing/target-market.md) "rings of trust") is built on the appliance being demonstrably safe regardless of the customer's home wiring or their care in following the manual.

### Path 4 — Customer's wall (do nothing on our side)

The appliance is sold with a generic 5-15P → C13 cord. The install consult requires the customer to have GFCI protection on the branch circuit before energization. If they don't, they get an electrician.

**Why this is the worst path:**
- The customer is buying a $7,500 plumbed appliance from a one-person shop and being told to call an electrician before they can plug it in. This is the opposite of the "buying from a person you trust" Founder Edition narrative.
- The install-consult gating turns a smooth Phase A install into a "your house isn't ready" deferral, which costs both calendar time and trust.
- The cost saving vs. Path 1 ($60 per unit) does not justify the customer-experience tax.

This was the parent doc's third customer-facing option ("the kitchen-counter receptacle pass-through"); it remains valid as a customer choice, but it should not be the default position.

---

## Part C — Why the parent doc reached for LCDI specifically

Worth understanding before judging the previous agent harshly. LCDI is mandatory by [NEC 440.65](https://www.electricallicenserenewal.com/Electrical-Continuing-Education-Courses/NEC-Content.php?sectionID=333.1) for single-phase cord-and-plug room air conditioners, and the dominant supplier (Tower Manufacturing) makes a public spectacle of being the LCDI specialist for that market. LCDI sounds like the right thing to copy if you're looking for "the cord-end safety device that ships pre-installed on real appliances."

But LCDI and GFCI are protecting against **different failure modes**:
- **GFCI (UL 943 Class A, 6 mA)** detects current leaking from H/N to ground. Personnel protection against shock. The use case is "appliance has a fault to chassis and you touch the chassis."
- **LCDI (UL 1699)** detects current leaking from H/N to a **shield in the cord**. Cord-arc-fire protection against a damaged cord. The use case is "the cord is pinched or crushed, the insulation cracks, and arcing starts in the cord jacket itself" — a failure mode specific to high-current cord-and-plug equipment that sits in window frames and gets pinched by sliding glass.

A plumbed kitchen appliance with a C14 inlet sitting safely behind a cabinet has effectively zero risk of the LCDI's specific failure mode (no pinch hazards on a captive C13 cord run six feet to a wall). It has substantial risk of the GFCI's failure mode (every chassis bond can corrode, every Y-cap can drift). **The correct standard for our use case is UL 943 Class A, not UL 1699**, and the Americord/Leviton cord is exactly that.

So the previous agent reached for the wrong analogy. The corrected analogy is: "we want what hot tubs do, except as a cord-end device instead of a sub-panel device, and that is the Americord/Leviton GFCI cord."

---

## Part D — Specific edits to recommend for the parent doc

If the parent doc is to be updated (not in this session — this doc is recommendation only), the surgical changes:

### Edit 1 — Parent doc line 154

> **Before:**
> > 2. **Add a portable GFCI between the wall outlet and our cord** ($20–40, Leviton GFCI 5-15 plug-in adapter). Works immediately; survives the install consult.
>
> **After:**
> > 2. **Add a portable GFCI between the wall outlet and our cord** ($17–20, manual-reset wall-pack — see verified component table below; note Leviton/Hubbell name brands are not available on Amazon Prime in this form factor, so the in-box choice is a Chinese-OEM product with thinner provenance). Works immediately; survives the install consult.

### Edit 2 — Parent doc line 161

> **Before:**
> > … ship the Founder Edition with the portable GFCI adapter (Option 2 above) in the box, at ~$25 BOM-add per unit …
>
> **After:**
> > … ship the Founder Edition with **a Leviton 6 mA GFCI line cord (Americord 10 ft 14/3 SJTW UL/CSA, $65.60 retail, expected $40–55 at OEM bulk) replacing the generic 5-15P → C13 line cord** — ~$60 BOM-add per unit. This converts a customer-side risk into a ship-side risk we control without depending on the customer's branch-circuit upgrade or on a separate in-box brick that can be lost.

### Edit 3 — Parent doc lines 163–170 (entire "hardware alternative" section)

> **Before:** the section starting "Air conditioners and pool pumps ship with LCDI…" and ending at "Both paths converge on the same Customer Promise…"
>
> **After:**
> ### The hardware path forward — UL 943 GFCI line cord, not LCDI
>
> The 2026-05-20 component survey ([`../2026-05-20/appliance-gfci-protection-component-survey.md`](../2026-05-20/appliance-gfci-protection-component-survey.md)) verified that the **NEMA 5-15P → C13 LCDI cord** assumed in earlier drafts of this doc does not exist as a stock item. The right product is the **NEMA 5-15P → C13 UL 943 Class A GFCI cord**, stocked at Americord with a Leviton GFCI plug head — UL/CSA approved, 6 mA trip, 15 A / 125 V, 10 ft 14/3 SJTW, $65.60 retail. This is the correct listing class for our use case anyway (personnel protection against shock at the load — what the appliance needs); LCDI is a cord-arc-fire device for room-AC pinch hazards that don't apply to a plumbed kitchen appliance.
>
> Recommended Founder Edition action: replace the generic 5-15P → C13 cord on the BOM with the Americord/Leviton GFCI cord. The C14 inlet stays. The customer plugs the appliance into any wall outlet and is protected. The install consult's GFCI question becomes informational (still useful to know about) rather than gating.
>
> Longer-term Standard Edition path: migrate to an **internal GFCI module** on the AC PCB (onsemi NCS37010 self-test sense IC, ~$8 BOM at qty-1000, plus UL 943 listing of the integrated subassembly amortized over Standard Edition volume). The integrated path cannot be defeated by cord swap, and at Standard Edition volume is cheaper than the Americord cord. Defer until the AC PCB exists for other reasons (relay control, current sensing, etc.) — the GFCI module rides on that PCB.

### Edit 4 — Parent doc lines 226–228 (the "what I'd want to read" LCDI question)

> **Before:**
> > 3. Whether the **LCDI cord** is available off-the-shelf as a NEMA 5-15P → C13 (rather than the more common 5-15P → bare-wire pigtail used in air conditioners). Quick supplier check — Tripp Lite, Quail Electronics, Volex. If the C13 variant is not stocked, the in-box portable GFCI (Part 3 Option 2) is the immediate path.
>
> **After:**
> > 3. **Resolved 2026-05-20 ([`../2026-05-20/appliance-gfci-protection-component-survey.md`](../2026-05-20/appliance-gfci-protection-component-survey.md)):** the LCDI variant does not exist in 5-15P/C13 at any major OEM. The correct substitute is the UL 943 GFCI variant (Americord 10 ft Leviton, $65.60, stocked) which is the correct listing class for this use case. The in-box portable GFCI option is no longer needed.

---

## Part E — Verified components and links (one-shot reference)

Everything in this section was loaded and read on 2026-05-20. If anything has changed by the time someone reads this later, refresh each link before ordering.

### Line cord with integrated UL 943 Class A GFCI

- **Americord, "10FT Leviton GFCI 5-15P to IEC 320 C-13RA Computer Power Cord 14/3 SJTW NA"** — [americord.com product page](https://www.americord.com/products/10ft-leviton-gfci-5-15p-to-iec-320-c-13ra-computer-power-cord-14-3-sjtw-na) — $65.60, in stock, UL/CSA approved, 15 A / 125 V, SKU 2723.120.003496. Manual vs. auto reset not stated on the page; clarify with Americord before ordering.
- Leviton portable cord-set family (for reference) — [store.leviton.com](https://store.leviton.com/products/portable-automatic-reset-gfci-cord-set-15a-125v-25-ft-cord-gfa15-25c) lists the GFA15-25C 25 ft auto-reset variant; the manual-reset family is similar.

### Amazon Prime in-box adapters (fallback path, not recommended)

- **ELEGRP Manual Reset Single Outlet GFCI Adapter**, yellow — [Amazon B096WVP698](https://www.amazon.com/dp/B096WVP698) — $17.99 Prime.
- **EP GFCI Adapter**, yellow — [Amazon B0CCHMMYFZ](https://www.amazon.com/dp/B0CCHMMYFZ) — $16.99 Prime.
- **AIDA GFCI Adapter**, white (best under-sink aesthetic) — [Amazon B0D49B3CMT](https://www.amazon.com/dp/B0D49B3CMT) — $19.99 Prime.
- **GREATIDE GFCI Adapter**, yellow (cheapest) — [Amazon B0DPKGMF1H](https://www.amazon.com/dp/B0DPKGMF1H) — $16.89 Prime.
- **Tower Manufacturing 30439005**, yellow, auto-reset (disqualifying — name-brand but wrong reset profile) — [Amazon B00UOU6OVU](https://www.amazon.com/dp/B00UOU6OVU) — $19.68 Prime.

All five appear to be the same OEM product rebranded for the first four; supply chain caveat applies as discussed in Part B.

### Internal-GFCI sense ICs (long-term Standard Edition path)

- **onsemi RV4145A** product page — [onsemi.com/products/power-management/gfci-controllers/rv4145a](https://www.onsemi.com/products/power-management/gfci-controllers/rv4145a). Datasheet at [Mouser-hosted PDF](https://www.mouser.com/datasheet/2/149/RV4145A-116878.pdf). Status: active. Distributors at [findchips.com/search/RV4145A](https://www.findchips.com/search/RV4145A).
- **onsemi NCS37010** product page — [onsemi.com/products/power-management/gfci-controllers/ncs37010](https://www.onsemi.com/products/power-management/gfci-controllers/ncs37010). UL 943 self-test compliant. Distributors at [findchips.com/search/NCS37010](https://www.findchips.com/search/NCS37010).
- **onsemi NCS37014** — [onsemi.com/products/power-management/gfci-controllers/ncs37014](https://www.onsemi.com/products/power-management/gfci-controllers/ncs37014).
- **onsemi NCS37021** — [onsemi.com/products/power-management/gfci-controllers/ncs37021](https://www.onsemi.com/products/power-management/gfci-controllers/ncs37021).
- **onsemi FAN4149** + **FAN41501** pair — [FAN4149 page](https://www.onsemi.com/products/power-management/gfci-controllers/fan4149) and [FAN41501 page](https://www.onsemi.com/products/power-management/gfci-controllers/fan41501).
- Arrow reference design — [arrow.com/en/reference-designs/typical-gfi-application-circuit-for-rv4145a](https://www.arrow.com/en/reference-designs/typical-gfi-application-circuit-for-rv4145a-3-wire-low-power-ground-fault-interrupter/fbae4b6a8e6d502b627382f01431edce004b97686b).

### Standards (regulatory references)

- **UL 943** product page — [shopulstandards.com](https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=31122). The Class A standard, 6 mA trip, residential personnel protection. The right standard for our use case.
- **UL 943C** product page — [shopulstandards.com](https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=25152). Class C/D/E for 480/600 V industrial. The parent doc's "UL 943C" citation was incorrect — that standard does not apply.
- **UL 1699** product page — [shopulstandards.com](https://www.shopulstandards.com/ProductDetail.aspx?UniqueKey=27236). The LCDI/AFCI standard. Does not apply to a plumbed kitchen appliance.
- **NEC 422.5(B) summary** — [ECM Magazine Q&A](https://www.ecmweb.com/national-electrical-code/qa/article/21213038/stumped-by-the-code-nec-requirements-for-gfci-protection-of-appliances). Names the five GFCI placement options including factory-installed-in-appliance.
- **UL 943 vs UL 943C comparison** — [Consulting-Specifying Engineer Magazine](https://www.csemag.com/uls-new-gfci-classes/).

### Tower Manufacturing (for OEM in-cord LCDI/GFCI quotes if ever needed)

- LCDI product family — [towermfg.com/lcdi](https://www.towermfg.com/lcdi/) — OEM-only, sold to customer spec.
- GFCI product family — [towermfg.com/gfci](https://www.towermfg.com/gfci/) — OEM-only.
- Phone for RFQ: 401-467-7550 (per the Tower LCDI page).

### Volex (for custom UL-listed cord assembly if ever needed)

- Product family — [volex.com/our-products](https://www.volex.com/our-products/power-cords-plugs-connectors-receptacles/wires-and-cables/). Custom-cord quick-turn service offered; specific MOQ and pricing not published.

---

## Part F — Open items

1. **Manual vs. auto reset on the Americord/Leviton cord.** The Americord listing does not specify which Leviton GFCI head is in the cord. A kitchen plumbed appliance benefits from **manual reset** (tripped → human acknowledges → resets), not auto. Contact Americord (or Leviton via the GFA15 product family) to confirm before ordering. If only auto-reset is available at this configuration, weigh it against the value of the C13 termination — it may still be acceptable, but the trade-off should be conscious.
2. **Right-angle C13 housing fit against the recessed C14 inlet.** The rear panel's C14 inlet is recessed 3–5 mm into a printed shroud ([`hardware/printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md)). The C-13RA (right-angle) connector housing on the Americord cord needs to nest into that without forcing the cable into a kink. Order one sample, dry-fit on the rear panel print, before committing the BOM change.
3. **Bulk pricing from Americord and direct from Leviton.** Single-quantity at $65.60 is a placeholder. The realistic OEM/quantity-50 quote needs an actual conversation with Americord (or with Leviton through their distributor network — Anixter, Graybar, RexelUSA all stock the Leviton GFCI head family). The case for or against Path 1 vs. Path 2 depends materially on what the bulk price comes out at.
4. **UL 943 listing scope question for an integrated subassembly.** If the project ever pursues an internal GFCI module (Path 3), the UL listing scope question — does the integrated module need its own UL 943 listing, or does it inherit from the appliance's overall listing path — needs a real conversation with a UL-recognized test lab (Intertek, TUV, CSA Group). The 2015 self-test mandate likely means the IC choice is NCS37010 (or 37014/37021), not RV4145A, if pursuing listing.
5. **In-life monitoring of the four chassis bonds.** The parent doc Part 5 deferred this. The integrated-GFCI path (Path 3) addresses it indirectly: if any of the four chassis bonds degrades, fault current routes through the customer's wet hand or through the cord's earth conductor; the integrated GFCI catches both. So Path 3, at Standard Edition volume, also closes the in-life-monitoring open item from the parent doc.

---

## Bottom line

The previous agent's instinct was right — the appliance needs GFCI protection that doesn't depend on the customer's house wiring. The execution was wrong on two specific part-level claims. The corrected execution is:

- **Founder Edition (now → unit ~50):** Switch the line cord from a generic 5-15P → C13 to the **Americord/Leviton GFCI 5-15P → C13** ([americord.com link](https://www.americord.com/products/10ft-leviton-gfci-5-15p-to-iec-320-c-13ra-computer-power-cord-14-3-sjtw-na)). Net BOM increase: ~$60/unit. Settles every concern in Parent Doc Part 3 without any enclosure, AC-board, or UL-listing work. Confirm manual-reset variant before ordering.
- **Standard Edition (unit ~51+):** Migrate the GFCI inside the appliance using an **onsemi NCS37010 self-test sense IC** + sense CT + 15 A latching relay on a small PCB on the electronics shelf. ~$8 BOM at qty-1000. Defeat-proof against cord swap. Defer until the AC PCB exists for other reasons.
- **Don't:** ship a Chinese-OEM in-box brick (Path 2 — supply chain risk for 4-year run), or rely on the customer's wall (Path 4 — wrong trust posture for Founder Edition).

The cost of being wrong here is a customer feeling a shock through a wet hand at the kitchen faucet. The fix is a $60 cord upgrade. Same magnitude of decision as the ASSE 1022 backflow preventer or the SF76E thermal fuse — small line item, load-bearing safety claim.
