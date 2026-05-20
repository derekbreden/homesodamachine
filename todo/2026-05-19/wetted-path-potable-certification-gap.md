# Wetted-path potable-water certification gap

**Date:** 2026-05-19
**Author:** hourly-todo-filler agent
**Status:** recommendation only — no code changes made
**Scope:** every component that contacts drinking water, carbonated water, or flavor concentrate, evaluated against the question *"can we point at a third-party certification that says this material is safe in a drinking-water appliance, and where does that document live?"*
**Distinct from sibling gaps:** [taste-acceptance-vs-can-reference-gap.md](taste-acceptance-vs-can-reference-gap.md) is about whether the dispensed soda tastes right; [reservoir-microbio-and-clean-policy-gap.md](reservoir-microbio-and-clean-policy-gap.md) is about whether the reservoir stays clean during use; [tap-water-quality-spec-gap.md](tap-water-quality-spec-gap.md) is about what tap water we accept on the inlet side. **This gap is about the wetted materials themselves and whether each one carries a paper trail back to NSF/ANSI 61 (drinking-water system components), NSF/ANSI 51 (food equipment materials), or FDA 21 CFR 177 (food-contact polymers).** Those three standards are the language a buyer, a state AG, or a product-liability insurer will use to ask the question. The repo today answers most of the question and is silent on the rest.

---

## 1. The gap in one sentence

There is no single source-of-truth document in the repo that maps every wetted part to its potable/food-contact certification status, and a wetted-materials census reveals that ~35 of ~70 wetted parts have only vendor-claimed food-grade status (no attached cert number), 2 wetted parts have no food-contact material specified at all (the hopper funnel and the reservoir caps), 1 critical user-facing fixture (the Westbrass faucet body) has its NSF status unconfirmed, and the 1 part that *does* have the right paper trail on its raw material (the flavor reservoir, SunTop FDA 21 CFR 177.1630 PETG) still has its final water + syrup dwell test pending — leaving the appliance technically defensible on commercial-standard grounds but with no consolidated answer to "is this NSF-listed for drinking water?" that the founder can hand to a buyer, a lawyer, or an insurer in under five minutes.

## 2. Why this matters at Founder Edition scale

Three forcing functions converge on this gap and none of them are visible in the current document tree.

**(a) The $7,500 buyer's question.** Per [marketing/target-market.md:264-270](../../marketing/target-market.md), the trust gap at Founder Edition pricing is enormous and the answer to "is this real?" is "Derek and his face." A buyer who has crossed that gap and is ~10 minutes from a credit-card decision will, at some point, ask one of: *"is the water it dispenses certified safe?"* / *"what about lead?"* / *"is the plastic food-safe?"* That is a 30-second question with a 30-second answer when the documentation exists, and a 30-minute scramble through `bom.md` and `purchases.md` when it does not. At 12 units/year the founder can scramble. The deeper problem is that the *scramble itself* is the trust failure — the buyer hears "let me check" and concludes the answer is "we hadn't really thought about it." That conclusion is wrong (the materials are commercial-equivalent) but it is the conclusion the buyer reaches.

**(b) The D2C-across-state-lines posture.** The appliance ships from a residential workshop in one state to homes in (potentially) 50 states. Several states have aggressive consumer-protection regimes around drinking-water appliances — California's AB 1953 (lead in drinking water plumbing, 0.25% weighted average lead content) and Proposition 65 (warning labels for lead, BPA, di(2-ethylhexyl) phthalate), Vermont and Maryland mirror laws, Massachusetts 248 CMR 10 (plumbing), Wisconsin SPS 384 (cross-connection control). California AB 1953 in particular is *enforced at the importer/seller level on every device that dispenses or treats water for human consumption.* The Multiplex 19-0897 is explicitly "lead-free brass body" per [hardware/future.md:23](../../hardware/future.md) which clears AB 1953 on that part. The Westbrass R2031-NL faucet model number contains "-NL" which the manufacturer uses for "no lead" but the repo does not confirm this. The brewhardware FFL38BARB38 swivel has a "chrome-plated brass swivel nut" — chrome-plated brass *typically* clears AB 1953 only if the underlying brass is lead-free, which is not asserted. None of this means the appliance is non-compliant. It means we don't know, and a state attorney general or a class-action plaintiff would not have to work hard to find the question.

**(c) The product-liability insurance underwriting question.** Cross-referenced from [todo/2026-05-19/workshop-as-factory-gap.md](workshop-as-factory-gap.md) — the workshop liability exposure is real. The companion exposure is *product* liability: when fielded unit #007 dispenses a glass that a customer's child drinks, and three months later the child's blood-lead screening comes back elevated, the insurer's first question is "what's the wetted-materials certification posture?" not "what was the BOM cost?" An underwriter who reads a one-page certifications matrix can write a policy. An underwriter who has to read 19 commits across `bom.md` + `purchases.md` + `future.md` + `assembly/*.md` to assemble the same picture will either decline the risk or load the premium aggressively. The gap is operational, not just documentary: the insurance application is a forcing function for the document.

The combination — buyer asks, state regulator asks, insurer asks — means the document needs to exist regardless of whether the *underlying compliance posture* changes. Today the posture is largely defensible. The document is missing.

## 3. What the repo actually has today

Reading the BOM, purchases.md, future.md, the assembly procedure docs, and the printed-parts docs end-to-end, here is what is documented per wetted part. (Full part-by-part table is in §4; this section is the patterns.)

**What is well-documented and defensible:**

- **John Guest push-to-connect fittings (PP010822E, PP0308E, PP1208E, PP2308E).** Approximately 20 fittings across the appliance carry **NSF 51 + NSF 61 listing** explicitly noted in [hardware/purchases.md](../../hardware/purchases.md) from the Fresh Water Systems orders WEBFWS100673541 (May 9) and WEBFWS100675224 (May 15). The cert is in the order-line description verbatim: *"black polypropylene 1/4", NSF 51 + NSF 61 listed, FDA-approved materials, 150 psi @ 70°F."* This is the gold-standard documentation pattern for the rest of the BOM to imitate.
- **Multiplex 19-0897 backflow preventer.** ASSE 1022-certified (carbonated-beverage-specific) explicitly noted in [hardware/future.md:23, 35](../../hardware/future.md). Lead-free brass body. This part's documentation is correct and complete.
- **316L SS pressure-vessel body and end plates.** Material choice is explicitly justified (molybdenum addition for chloride + carbonic-acid pitting resistance) and citric-acid passivation is documented [hardware/future.md:11, 29](../../hardware/future.md). 316L SS is the commercial standard for brewery bright tanks and carbonators; the equivalence argument is made in the doc. The vessel is *not* NSF-stamped because the appliance is not pursuing UL/ETL listing (cited in [business/regulatory.md] per future.md). That is an acceptable posture for D2C but should be stated affirmatively in the certifications document rather than left to inference.
- **PTFE-soft-seat check valves (GASHER).** PTFE-on-metal explicitly documented as the food-process / brewery industry standard [hardware/assembly/cold-core.md], chosen over elastomer for creep resistance under CO2 back-pressure. Defensible.
- **Sparge stone (FERRODAY 0.5 µm sintered 316 SS).** Inert stainless filter, in contact only with CO2 gas before bubble formation, not stored carbonated water. Standard commercial-beverage component.

**What is vendor-claimed without an attached cert:**

- **Silicone tubing in three sizes** — JoyTube 3/8" ID food-grade (B089YGDB55, suction-side hose), Metaland 1/4" ID food-grade (sparge-stone internal tube, B08L1ST6ST area), Kamoer pump-head 1/8" ID × 1/4" OD food-grade (B0BM4KQ6RT area). All three carry "food-grade silicone" in the listing. None has FDA 21 CFR 177.2600 cert numbers, USP Class VI documentation, or NSF 51 listing attached to the BOM line.
- **SEAFLO 22-Series diaphragm pump.** Marketed as RV/marine potable-water pump. No NSF 61, NSF 372 (lead-free), or specific food-contact certification noted in the BOM.
- **Kamoer KPHM400-SW3B25 peristaltic pump.** Marketed with food-grade silicone tube internals. No third-party cert claimed.
- **LLDPE 1/4" OD tubing from Fresh Water Systems (neoFlo brand).** Purchases.md May 9 entry distinguishes this as "vendor-rated LLDPE (the proper LLDPE callout) vs Amazon's generic 'PE'" — FWS makes the NSF 51 + FDA claim verbally but no cert number is attached.
- **MAACFLOW SS 3/8" barb × 1/4" NPT adapter, LTWFITTING SS 1/4" barb × 1/4" MNPT adapter, TAISHER 316L SS NPT elbows.** All 316/316L SS, standard for potable service, no specific food cert claimed.
- **Westbrass R2031-NL-62 Touch-Flo faucet body (B07KH285GJ).** Marketed as "cold water dispenser faucet." Model suffix "-NL" implies no-lead brass under Westbrass's nomenclature, but this is not confirmed in the repo against AB 1953 / NSF 372 lead-free standards. Listed in [hardware/bom.md] §9 with no cert annotation.
- **Beduan 12 V 1/4" solenoid valves (NC).** Industrial solenoid; no food-contact certification claimed. *Maybe acceptable* depending on whether they are in direct flavor-concentrate contact or only gate flow upstream/downstream of NSF-listed fittings — but the BOM does not adjudicate this.

**What is silent on material specification entirely:**

- **Hopper funnel.** [hardware/bom.md] §7 lists "Flavor hopper funnel (top-front, SodaStream-pour sized) 0.4 kg PETG @ $12.99/kg = $5.20." No filament ASIN is specified, no food-contact-PETG callout is made. The hopper is the **single point in the appliance where the user pours raw concentrate** that they then drink — the most direct food-contact surface in the wetted path on the user-facing side. If this is printed on standard Bambu PETG, it is not food-contact-certified.
- **Reservoir caps.** Cold-core.md describes the reservoir cap (threaded onto the printed reservoir body, sealed with a TPU 90A gasket) but does not specify whether the cap is printed on the same SunTop food-contact PETG as the reservoir body itself, or on standard PETG. The cap interior surface contacts headspace gas above stored concentrate. If concentrate splashes during dispense pulses, it contacts the cap.

**What has the right paper trail but pending final qualification:**

- **Flavor reservoirs (printed, SunTop B0FP34MJ94).** [hardware/assembly/cold-core.md] notes the SunTop filament *raw material* complies with **FDA 21 CFR 177.1630** (PETG resin food-contact). This is correct material-level certification. The open item flagged in cold-core.md is "Reservoir final-qualification status... still pending water + syrup-dwell pass." That is the right next step — material cert is necessary but not sufficient; the *printed part* must be validated for layer-line porosity, biofilm harborage, and concentrate-stability over dwell time. The test exists as a plan but no pass/fail result is recorded.

## 4. Wetted-parts census, organized by fluid path

The full census (~70 wetted parts across 6 fluid path segments) is summarized below. The cert column uses three codes: **CERT** = certification number / standard documented in repo with traceable order-line or datasheet; **CLAIM** = vendor or marketing claim, no cert number attached; **SILENT** = no material or cert documented.

### 4.1 Tap → diaphragm pump inlet (suction side)

| Part | Material | Cert status |
|------|----------|-------------|
| Multiplex 19-0897 backflow preventer | Lead-free brass + SS internals | **CERT** — ASSE 1022 |
| brewhardware FFL38BARB38 swivel × barb | 304 SS barb + chrome-plated brass swivel | **CLAIM** — 304 SS standard; AB 1953 brass status unconfirmed |
| JoyTube 3/8" ID silicone hose (B089YGDB55) | Food-grade silicone | **CLAIM** — no FDA/NSF cert in repo |
| SEAFLO 22-Series diaphragm pump (B0166UBJX4) | Mixed elastomer/SS internals | **CLAIM** — vendor potable-rated, no third-party cert |

### 4.2 Pump outlet → vessel water inlet (top plate, Port 2)

| Part | Material | Cert status |
|------|----------|-------------|
| MAACFLOW 3/8" barb × 1/4" NPT SS adapter | 316 SS | **CLAIM** — material standard, no cert |
| GASHER 1/4" NPT SS check valve (PTFE soft seat) | 316L SS + PTFE | **CLAIM** — material rationale documented, no cert number |
| JG PP010822E warm-side NPT↔PTC adapter | PP + EPDM O-ring | **CERT** — NSF 51 + 61 (FWS order) |
| 1/4" OD LLDPE through foam shell (neoFlo) | LLDPE | **CLAIM** — FWS vendor NSF 51 + FDA claim, no cert # |
| JG PP010822E cold-side NPT↔PTC adapter | PP + EPDM O-ring | **CERT** — NSF 51 + 61 |
| TAISHER 316L SS 90° NPT M×F street elbow | 316L SS | **CLAIM** — material standard |
| Vessel top plate, 1/4" NPT tapped | 316L SS (passivated) | **CLAIM** — equivalent to commercial carbonator, no NSF vessel stamp |

### 4.3 Inside the vessel (carbonated water at 2 °C, pH ~3.5–4, 90 PSI)

| Part | Material | Cert status |
|------|----------|-------------|
| 316L SS body (commodity 5" OD × 0.065" wall welded tube) | 316L SS, citric-acid passivated | **CLAIM** — material rationale + passivation procedure documented; not NSF-stamped (D2C posture) |
| 316L SS end plates (laser-welded, citric-acid passivated) | 316L SS | **CLAIM** — same posture |
| 1/8" 316L SS float-guide rod (Tandefio B0CY4DWJFQ) | 316L SS | **CLAIM** — material standard |
| Magnetic donut float (harvested from DEVMO B07T18PGJ4) | Ferrite magnet inside plastic donut | **CLAIM** — *plastic donor is unspecified*; potentially in long-term contact with carbonated water for the appliance's full service life |
| Sparge stone internal silicone tube (~3" of 1/4" ID, Metaland B08L1ST6ST area) | Food-grade silicone | **CLAIM** — no cert |
| LTWFITTING 1/4" hose-barb × 1/4" MNPT SS adapter (Port 1 inside face) | 316 SS barb + brass MNPT | **CLAIM** — brass thread is **not lead-free-asserted** in the BOM; this thread is dry on the brass side but wet on the SS-barb side |
| FERRODAY 0.5 µm sintered 316 SS sparge stone (B091C5Y6L9) | 316 SS sintered | **CLAIM** — material standard, marketed for beverage |

The **magnetic donut float** is the most overlooked part in the census. It is harvested from a donor liquid-level switch and the plastic shell that contacts the water column is undocumented as to material. If it is polypropylene or HDPE, fine; if it is unspecified, it is in direct continuous contact with carbonated water at low pH for years.

The **brass MNPT thread on the LTWFITTING** is dry (sealed with PTFE tape on the threads, sparge-side barb is SS) but the AB 1953 question is *was the brass cast as lead-free.* If it was, no exposure even if a thread leaks. If it wasn't, a small thread leak could path carbonic acid past brass and leach lead. This is not asserted either way.

### 4.4 CO2 path (regulator → vessel Port 1)

| Part | Material | Cert status |
|------|----------|-------------|
| Interstate Pneumatics WR1110 secondary regulator (B07J2L8LF3) | Aluminum body, brass internals, PTFE seals | **CLAIM** — pneumatic industrial, no food cert (CO2 is non-consumable gas before dissolution) |
| DERPIPE 5/16" tube × 1/4" NPT PTC | (unspecified, likely brass + PP) | **SILENT** — not characterized as wetted-path in BOM |
| GASHER 1/4" NPT SS check valve (dry-side CO2) | 316L SS + PTFE | **CLAIM** |
| JG PP010822E adapter (×2 on CO2 path) | PP + EPDM | **CERT** — NSF 51 + 61 |
| 1/4" OD LLDPE through foam shell (CO2-side, neoFlo) | LLDPE | **CLAIM** |
| JG PP0308E in-cavity 90° elbow | PP + EPDM | **CERT** — NSF 51 + 61 |
| TAISHER 316L SS 90° NPT elbow at Port 1 | 316L SS | **CLAIM** |

The CO2 path is materially low-risk (gas only, dissolves at the sparge interface, no stored CO2 reservoir downstream of the regulator) but should still be in the matrix because the dissolved-CO2 carbonic acid back-loads onto any backflow into the CO2 line — the GASHER check is what prevents this.

### 4.5 Flavor concentrate path (hopper → solenoid → pump → reservoir → manifold → nozzle)

| Part | Material | Cert status |
|------|----------|-------------|
| **Hopper funnel (printed)** | "0.4 kg PETG" (no filament ASIN specified) | **SILENT** — *critical gap, direct user-pour food contact* |
| Removable silicone hopper cover | TPU or silicone | **CLAIM** — dishwasher-safe marketing, no cert |
| Solenoid-selected route valves (Beduan, B07NWCQJK9 area) | Plastic body, SS internals | **SILENT** — no food cert; in direct concentrate contact |
| Kamoer KPHM400-SW3B25 peristaltic pump (B09MS6C91D) | Pump body + food-grade silicone tube internal | **CLAIM** — vendor food-grade tube, no cert # |
| Silicone tube 1/8" ID × 1/4" OD pump-head (B0BM4KQ6RT) | Food-grade silicone | **CLAIM** — vendor food-grade, no cert # |
| 1/4" OD LLDPE flavor manifold runs | LLDPE | **CLAIM** — FWS vendor NSF 51 + FDA, no cert # |
| JG PP2308E two-way Y-divider (×~5 per unit, 10 total per appliance) | PP + EPDM | **CERT** — NSF 51 + 61 |
| JG PP1208E 1/4" PTC bulkhead at reservoir cap (×2) | PP + EPDM | **CERT** — NSF 51 + 61 |
| **Flavor reservoir (printed)** | SunTop food-contact PETG (B0FP34MJ94) | **CERT-PENDING** — FDA 21 CFR 177.1630 raw material claim; reservoir final qualification (water + syrup dwell test) **not yet completed per cold-core.md open items** |
| **Reservoir cap (printed)** | (unspecified — std PETG or food-contact PETG?) | **SILENT** — direct concentrate-headspace contact |
| TPU 90A reservoir cap gasket | TPU 90A | **CLAIM** — TPU is food-contact material class but no specific cert |
| PTFE vent membrane (LVDALAB B0D41KT345, 13 mm × 0.45 µm) | PTFE | **CLAIM** — PTFE is inert |
| 1/8" 316L SS reservoir-internal float rod | 316L SS | **CLAIM** |
| Reservoir-internal magnetic float (harvested) | (unspecified plastic donut) | **SILENT** — same issue as carbonator float |

### 4.6 Vessel outlet → faucet → user's glass

| Part | Material | Cert status |
|------|----------|-------------|
| Vessel bottom plate Port 3 (1/4" NPT) | 316L SS, passivated | **CLAIM** |
| TAISHER 316L SS 90° elbow at Port 3 (if used) | 316L SS | **CLAIM** |
| 1/4" OD LLDPE chilled dispense run (FWS, blue-coded for ID) | LLDPE | **CLAIM** — FWS NSF 51 + FDA claim |
| Insulation foam over LLDPE (CARGEN nitrile, 1/4" ID × 3/8" wall) | Closed-cell nitrile | n/a — external insulation, not wetted |
| Touch-flo-shell printed gooseneck (PET-CF) | PET-CF (Bambu) | n/a — explicitly *not* food-contact per touch-flo-shell/MATERIAL.md; the wetted path stays inside the LLDPE tubes inside the spout |
| 3× LLDPE dispense tubes inside the spout | LLDPE | **CLAIM** |
| **Westbrass R2031-NL-62 faucet body (B07KH285GJ)** | Brass body, nickel-plated | **CLAIM** — model suffix "-NL" implies no-lead in Westbrass nomenclature but **NSF 61 / NSF 372 / AB 1953 status is not confirmed in repo** |
| Siptenk 1/4" OD brass tube stiffener (B0FM77LLM1) | Brass | **CLAIM** — *not lead-free-asserted*; inside LLDPE, low exposure path |

The faucet body is the highest-visibility wetted part. The user's hand touches it every dispense; the visible spout is the appliance's signature surface. The "-NL" suffix is almost certainly correct (Westbrass uses NL for their no-lead line and an "-NL-62" SKU is consistent with their AB 1953-compliant matte-black product family). But "almost certainly correct based on reading the SKU" is not a citation.

## 5. Recommendations

These are ordered by ratio of *gap-closure leverage* to *founder time*. The first four are inexpensive and high-leverage; the rest are graduated according to appetite.

### 5.1 Create a single source-of-truth document: `hardware/wetted-materials-certifications.md`

One file, structured as the table in §4 of this gap report, maintained alongside the BOM. Columns: part, material, fluid-path position, cert status (CERT / CLAIM / SILENT), cert document (URL or attached PDF), source (purchases.md line item or external cert lookup), date last verified.

The document does three things at once: (a) it is the answer to the buyer's "is this NSF-listed?" question, (b) it is the artifact the insurance underwriter reads, (c) it is the worklist for closing the remaining gaps.

**Founder time:** 2–3 hours to populate first version from this report + the BOM. Updates are 30 sec per BOM change.

**Companion change:** add a one-line cert-status column to [hardware/bom.md] for every wetted-path row (`NSF 61` / `NSF 51 / FDA 177.1630` / `claim` / `—`). Cross-references back to wetted-materials-certifications.md for the document. This survives BOM revisions without re-stating cert details.

### 5.2 Specify the hopper-funnel filament as a food-contact PETG

The hopper funnel is the direct user-pour surface. It must be printed on food-contact-certified filament. The SunTop B0FP34MJ94 already specified for the flavor reservoirs (FDA 21 CFR 177.1630) is the natural choice — same filament, same supplier, no incremental qualification work. Change [hardware/bom.md] §7:

- From: *"Flavor hopper funnel ... 0.4 kg PETG"*
- To: *"Flavor hopper funnel ... 0.4 kg SunTop food-contact PETG (FDA 21 CFR 177.1630, B0FP34MJ94)"*

Same change for reservoir caps and any other printed part that contacts concentrate, carbonated water, or the user's pour stream. Confirm by re-reading every print-spec file under [hardware/printed-parts/] for the wetted-side parts (cold-core/reservoir/, anything that lives above the hopper).

**Founder time:** 30 minutes to find every affected BOM line. Marginal filament cost is small (PETG is ~$13/kg either way; food-contact PETG runs ~$25–35/kg; per-unit delta on a ~1 kg total food-contact print mass is ~$20).

### 5.3 Confirm the Westbrass R2031-NL-62 NSF 61 / NSF 372 / AB 1953 status

This is a 30-minute phone call or email to Westbrass technical support, asking specifically: *"Is the R2031-NL-62 faucet body NSF 61 listed and NSF 372 (lead-free) compliant? Can you send me the cert document?"* Westbrass is a mid-sized US faucet manufacturer; they will have the answer and the PDF. File the PDF in `hardware/certifications/` (new folder) and reference it from the wetted-materials-certifications.md row.

If the answer is *no* — i.e., the R2031-NL is marketed as a non-potable dispenser-only fitting — replace with an NSF 61-listed alternative. Moen, Delta, and Kraus all make NSF 61-listed cold-water dispenser faucets in matte black at similar price points.

**Founder time:** 30 minutes. **Cost if replacement needed:** likely $30–80 swap, no BOM-architecture change.

### 5.4 Collect vendor cert PDFs for the high-volume CLAIM parts

For each of: JoyTube silicone hose, Metaland silicone tube, Kamoer pump-head silicone, SEAFLO diaphragm pump, Kamoer peristaltic pump, neoFlo LLDPE (Fresh Water Systems). Email the seller, ask for the FDA 21 CFR 177 cert / NSF datasheet / USP Class VI documentation. Most beverage-industry suppliers will provide this on request; some Amazon resellers will not, in which case substitute with a vendor that will (USP-Class-VI silicone tube from McMaster-Carr is a one-line substitution for the Metaland stock).

Save PDFs in `hardware/certifications/<part-name>.pdf`. Reference from the matrix.

**Founder time:** 2–3 hours total spread across six vendor emails. Two-week turnaround for responses.

**What to do with vendors who decline:** the silicone-tube market and the diaphragm-pump market both have an NSF-cert tier above the food-grade-claim tier. The cost delta is small (~$5–15 per unit total). Substituting to a cert-paper-trail vendor is preferable to litigating with a non-responsive Amazon seller.

### 5.5 Address the harvested-component certification voids

Two harvested-component plastics are in long-term wetted contact and unspecified:

1. **Magnetic donut floats** (DEVMO MINI float switch B07T18PGJ4) — one in the carbonator, one in each flavor reservoir. The float's outer plastic shell sits in carbonated water (pH 3.5–4) or in flavor concentrate for the appliance's full life.

2. **Donor ice-maker condenser fan + cold-side plumbing**, to the extent that any donor-ice-maker plumbing remains in the water path. Per [hardware/future.md:49-58](../../hardware/future.md) the factory finger-plate evaporator is discarded and only the refrigerant-side components (compressor, condenser, capillary, drier) are kept — these are isolated from the drinking-water path by the new copper evaporator coil and the 316L vessel wall. So the harvested-plumbing risk on the drinking-water side is in fact zero. The float donor remains the live exposure.

**Recommendation for the float:** procure a single-source food-grade level-sensing magnetic float assembly (Gems Sensors LS-3 series or equivalent) rather than harvest from a generic float switch. The cost is $10–30 per float; the certification trail comes with the part. Alternatively, contact DEVMO and ask for the donor part's plastic-shell material certification — if it is polypropylene with food-contact claim, accept the harvest with a documented cert. If it is unspecified, replace.

**Founder time:** 30 minutes to source. Marginal cost: ~$25 per appliance.

### 5.6 Document the no-listing posture affirmatively

The repo's position — D2C only, no UL/ETL/NSF appliance listing pursued, vessel not NSF-stamped — is *defensible* (it is what SodaStream and many small carbonator builders do). But the defense is currently inferred from [business/regulatory.md] (referenced by future.md:27) rather than stated in the certifications document. The certifications document should have a one-paragraph "Listing posture" section that says explicitly:

> *"This appliance is sold direct-to-consumer at hand-built scale. It is not pursuing UL 60335, ETL listing, NSF/ANSI 18 appliance certification, or NSF 61 system certification because none of these are required for D2C sales in any U.S. state. Each individual wetted material is selected to meet or exceed the certification it would carry as a component in a UL-listed appliance: NSF 51/61 for fittings, ASSE 1022 for backflow prevention, FDA 21 CFR 177.1630 for food-contact polymers, AB 1953 for lead-free brass. Where component-level certification is documented, the cert is filed under hardware/certifications/. Where only vendor claim is available, the cert posture is noted as 'vendor claim, no third-party document.' The 'aggregate of certified components' approach is the same posture taken by SodaStream commercial and Lillium for their D2C units."*

This is the paragraph the underwriter wants to see and the buyer would understand. It is also the paragraph that prevents the founder from being asked the same question twelve times.

**Founder time:** 30 minutes to write, then it is durable.

### 5.7 Add the certifications matrix to the customer-facing materials

At Founder Edition pricing, the certifications-matrix one-pager is something the buyer asks for *after* they're convinced. It is reassurance, not pitch. But it should exist in PDF form so the founder can attach it to a Zoom-call follow-up email without composing it from scratch each time.

The matrix lives in two forms:

- **Long form** (the source-of-truth markdown in the repo): all 70 parts, every cert document, every CLAIM disclosure, every SILENT acknowledgment.
- **Short form** (a one-page PDF for buyer-facing use): the seven or eight cert numbers that matter to a layperson — ASSE 1022, NSF 51, NSF 61, FDA 21 CFR 177.1630, 316L SS passivation per commercial carbonator standard, lead-free brass per AB 1953. Plus the affirmative statement of the D2C / no-listing posture.

**Founder time:** 1 hour to draft the short form once the long form exists.

### 5.8 Bind cert verification to the per-unit build procedure

In the assembly procedure docs ([hardware/assembly/]), the existing build-step language is *"install JG PP010822E adapter at vessel inlet."* The certs-aware version is *"install JG PP010822E adapter (NSF 51 + 61, cert in hardware/certifications/john-guest-pp010822e.pdf) at vessel inlet."* The cert reference is the live link the assembler sees while building, and it surfaces any cert-document-missing condition at build time rather than at customer-call time.

**Founder time:** 1 hour to update all wetted-path build steps after the certifications folder exists.

### 5.9 Run the pending SunTop reservoir water + syrup dwell test

Per [hardware/assembly/cold-core.md] open items, this test is planned but not completed. The cert paper trail on the SunTop filament covers the raw material. The dwell test covers what 200 µm layer lines do to that raw material over weeks of contact with high-sugar-substitute concentrate at 8–15 °C. Without this test, the reservoir is the strongest *paper* cert in the appliance and the weakest *functional* validation.

**Recommended test outline:**
- Print one reservoir on the SunTop B0FP34MJ94, target-production layer settings.
- Fill 1/3 with distilled water + 1/3 with Pepsi-made SodaStream concentrate, leave 1/3 headspace.
- Hold at refrigerator temperature (4 °C) for 30 days.
- After dwell: sensory check (off-flavor, off-color, off-smell), visual check of the wetted surface for layer-line erosion or concentrate intrusion, weight check (loss > 0.1% suggests dissolution or permeation).
- Repeat with reservoir held at room temperature (20 °C) for 30 days as accelerated worst case.

Pass/fail recorded in cold-core.md and in wetted-materials-certifications.md. This converts the SunTop entry from CERT-PENDING to CERT.

**Founder time:** 1 hour to set up, 30 days dwell, 1 hour to evaluate. **Material cost:** one extra reservoir print (~$5 in filament).

### 5.10 (Optional, larger scope) Take a position on California Prop 65

Prop 65 requires warning labels on consumer products sold in California that expose users to listed chemicals (lead, BPA, DEHP, etc.) above safe-harbor thresholds. Small businesses with <10 employees are statutorily exempt. The founder is a sole proprietor — exemption applies. But two issues:

1. The exemption is from the warning-label requirement, not from underlying safety obligations.
2. The exemption goes away if the founder hires.

This is one paragraph in the certifications document acknowledging the exemption and committing to revisit on first hire. It is not a structural change.

**Founder time:** 30 minutes.

## 6. What this report deliberately does not address

- **NSF/ANSI 18 (food equipment and beverage dispensers as system-level certification).** This is the certification a UL-listed retail product would carry. The repo's stated D2C posture explicitly opts out of this; that is correct for Founder Edition and Standard Edition. Recommend revisiting before any retail-channel pivot (Costco, big-box, Amazon "Climate Pledge Friendly" tier all want NSF 18). Out of scope here.
- **The CO2 gas itself.** Beverage-grade CO2 (ISBT specification, ~99.9% purity) is the customer's responsibility (they refill at a welding-gas supplier or via the proposed CO2 service per [pie-in-the-sky/co2-service.md]). Whether the customer is sourcing beverage-grade vs industrial-grade CO2 is a separate gap — see [todo/2026-05-18/co2-supply-ownership-gap.md] (yesterday).
- **The tap water on the inlet side.** Covered separately in [tap-water-quality-spec-gap.md](tap-water-quality-spec-gap.md).
- **Microbial control in the reservoir during use.** Covered in [reservoir-microbio-and-clean-policy-gap.md](reservoir-microbio-and-clean-policy-gap.md). The materials question (this report) and the in-service biofilm question (that report) are complementary.
- **The faucet penetration in the customer's countertop.** Covered in [countertop-faucet-penetration-gap.md](countertop-faucet-penetration-gap.md).
- **Refrigerant-side certifications (R-600a, the compressor electrical class).** Not a drinking-water gap; R-600a is on the cold side of the vessel wall and the EPA Section 608 venting carve-out is documented.

## 7. Cross-references

- This gap interacts with [todo/2026-05-19/workshop-as-factory-gap.md](workshop-as-factory-gap.md) (the *workshop* liability — building 50 units in a residence) and with [todo/2026-05-18/warranty-and-rma-gap.md](../2026-05-18/warranty-and-rma-gap.md) (the *product* liability — what happens when a fielded unit fails). Together they form the three legs of the liability-insurance underwriting case: workshop, product, materials. All three need their own one-pager.
- The certifications document recommended in §5.1 should be referenced from the future "regulatory" section in [business/regulatory.md] (referenced by future.md:27 but not read for this report — confirm it exists; if not, that itself is a sub-gap).
- The hopper-funnel filament fix (§5.2) is a small change to [hardware/bom.md] §7 and any print-spec docs for the funnel — one print-spec doc per related part, easy to scope.
- The SunTop dwell test (§5.9) closes the open item already flagged in [hardware/assembly/cold-core.md].

## 8. The smallest version of this recommendation

If the founder reads this report and has 90 minutes to spend on it before moving on:

1. **(60 minutes)** Create `hardware/wetted-materials-certifications.md` using the table in §4 as the seed. Fill in CERT / CLAIM / SILENT for every row. This document alone is the gap closure.
2. **(15 minutes)** Update [hardware/bom.md] §7 to specify SunTop food-contact PETG (B0FP34MJ94) for the hopper funnel and reservoir caps. This closes the two SILENT entries on the printed side.
3. **(15 minutes)** Email Westbrass for the R2031-NL-62 NSF 61 / NSF 372 cert. File in `hardware/certifications/` when it arrives.

Everything else is incremental from there. The wetted-materials-certifications.md document is the single deliverable that converts the current state ("defensible if you know where to look") into the desired state ("one paragraph and a one-page PDF answers every question"). It is also the artifact that makes the rest of the recommendations land cleanly — each subsequent fix is an edit to one row in one document, rather than three edits across three docs that have to be kept in sync.

---

*End of report. No repo changes made. Commit and push of this report only.*
