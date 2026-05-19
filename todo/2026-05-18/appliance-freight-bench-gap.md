# Shipping the appliance: parcel vs. white-glove, the harvested-compressor liability trap, and the carton-class problem

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Distinct from siblings 2026-05-18:** the [CO2 sibling](co2-supply-ownership-gap.md) covers Class 2.2 cylinder hazmat for ongoing customer CO2 supply; the [install-consult sibling](install-consult-playbook-gap.md) covers the Zoom-call moment at the customer's kitchen; the [warranty sibling](warranty-and-rma-gap.md) covers post-delivery failure. **This doc is about the freight leg itself — the carrier handoff at step 9 of [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md), and Open Items 1, 3, and 6 of that procedure.**

---

## TL;DR

Three findings that, taken together, change the freight-bench decision:

1. **DOT hazmat is a non-issue.** 49 CFR 173.307(a)(4)(iii) exempts refrigerating machines containing **≤12 kg** of flammable non-toxic refrigerant from the entire Hazardous Materials Regulations subchapter. Our charge is 20–35 g — **two orders of magnitude under threshold**. The appliance ships as ordinary cargo. No UN 3358 marks, no Class 2.1 label, no shipping paper hazmat entry, no PHMSA registration, no Subpart H training, no Chemtrec. NewAir, Whynter, Magic Chef, and EdgeStar all ship hydrocarbon-charged refrigerators to consumers via UPS/FedEx Ground every day on the same statutory basis.

2. **The harvested compressor likely collapses the carrier's declared-value liability to roughly $3.50.** AAA Cooper Tariff Item 570 — representative of the industry — caps liability at **$0.10/lb, max $10,000/shipment** for any commodity that has been "rebuilt, reconditioned, remanufactured, or refurbished." At ~35 lb gross with a compressor harvested from a consumer ice maker, a claims adjuster can credibly classify the entire unit as "other than new." The Open Item 3 plan of "declare $7,500 with the carrier" almost certainly does not buy what it looks like it buys.

3. **At $7,500, UPS Ground doorstep delivery is a customer-experience mismatch.** Sub-Zero, Wolf, Miele, and Liebherr — the comparables at this price band — arrive via factory-certified white-glove install (two-person crew, room-of-choice, debris removal, walkthrough). UPS leaves a 35-lb carton on the porch with a photo POD. The price tag tells the customer to expect the former; the carrier tells them they got the latter.

This doc lays out the three decisions [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) Open Item 1 has to make, the regulatory/practical reality behind each one, and a recommended commit path for the Founder Edition run.

---

## What's actually unaddressed today

[`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) flags Open Items 1 (carrier selection), 3 (damage-claim workflow), 5 (international), 6 (carton + foam + transit caps), and 7 (precise shipping weight). The doc reads as if these are loose ends to be closed off later. The research underneath them says they are the **central freight-bench decisions** with non-obvious answers:

- **Open Item 1 — carrier selection.** Working default is "UPS Ground or FedEx Ground." But "ground" subdivides into parcel-ground (UPS/FedEx, doorstep) vs. LTL freight (XPO, Estes, AAA Cooper, palletized) vs. specialty final-mile (XPO Last Mile, RXO, AGS, J.B. Hunt Final Mile, threshold-to-white-glove tiers). The cost, the customer experience, and the damage exposure are all materially different across those three.
- **Open Item 3 — damage-claim workflow.** Hinges on the harvested-compressor liability cap, which is not currently named anywhere in the repo.
- **Open Item 6 — carton + foam.** The carton's *density* drives NMFC class on the LTL path. A loose, over-packaged 5.3 ft³ carton for a 35-lb appliance lands at ~6.6 lb/ft³, which under modern NMFC density-only rules pushes the unit from Class 92.5 (refrigerator) into Class 125+. Rate goes up materially.

The [marketing target-market doc](../../marketing/target-market.md) "no plumber, no special tools, plug and play" framing also makes an implicit promise the freight bench has to deliver into. None of "no plumber, no special tools, plug and play" survives a porch-drop scenario where the customer has to maneuver a 35-lb $7,500 appliance through their kitchen alone.

---

## Decision 1: Parcel-ground vs. final-mile vs. LTL

### Parcel-ground (UPS Ground / FedEx Ground / FedEx Home Delivery)

**Statutory posture:** Ordinary parcel. UN 3358 is on UPS's Ground-Accepted DG table when shipped *as hazmat*; under §173.307(a)(4)(iii) we ship not-as-hazmat and it's just a 35-lb carton.

**Dimensional envelope:** UPS Ground / FedEx Ground residential max is **150 lb, 108" longest side, 165" length + girth (2W+2H+L)**. Our working envelope at 60×50×50 cm ≈ 24×20×20 in gives L+G ≈ 104 in — comfortably under the 130 in Large Package surcharge threshold, comfortably under the 165 in Over-Maximum threshold.

**Cost:** ~$50–120 lower-48 residential ground at our weight + dim envelope.

**Customer experience:** Doorstep / first-dry-area drop. Photo POD. Customer is on their own from there. No signature is mandatory at residential ground unless explicitly requested.

**Damage exposure:** UPS/FedEx liability up to $100 included; declared value to $50,000 with surcharge. **But:** "other than new" / refurbished-component exclusion (see Decision 2) likely caps actual recovery at the $0.10/lb floor regardless of what you declared.

**Industry precedent:** This is what NewAir, Whynter, EdgeStar, Magic Chef, and Avanti use for hydrocarbon-charged residential refrigeration appliances. The lane is mature.

### Specialty final-mile (XPO Last Mile / RXO / AGS / J.B. Hunt Final Mile)

**Statutory posture:** Same ordinary-cargo posture under §173.307. These carriers' DG paperwork is needed only when the article is actually hazmat-regulated.

**Service tiers (XPO Last Mile published ladder):** Porch → Threshold → Room-of-Choice → Standard Install → White-Glove with takeaway.

**Cost (market norms, lower-48 single-unit residential drop):**
| Tier | Typical lane cost |
|---|---|
| Threshold | $120–180 |
| Room-of-choice | $180–300 |
| Standard install | $250–400 |
| White-glove with takeaway | $300–600 |

**Customer experience:** Two-person crew, scheduled delivery window, the carton (or unpacked appliance) goes where the customer wants it. White-glove tier matches Sub-Zero / Wolf / Miele norms.

**Damage exposure:** Carrier-specific tariffs. Same "other than new" exclusion language is common. Independent cargo insurance is the cleaner answer (see Decision 2).

**Pickup origin:** Founder's garage works — appointment scheduling, the carrier sends a truck. No loading dock needed at our weight.

### LTL freight (palletized, XPO LTL / Estes / AAA Cooper / R&L)

**Statutory posture:** Same ordinary-cargo posture.

**NMFC class trap:** Household refrigerators historically classified at NMFC item 60500, **Class 92.5** (density band 10.5–12 lb/ft³). At ~35 lb in 5.3 ft³ our carton density is ~6.6 lb/ft³, **falling below the 92.5 band into Class 125 or higher** under NMFTA's density-only restructure. Effect: per-pound rate roughly 1.5–2× the rate a full-size Whirlpool gets, despite shipping the same NMFC item number.

**Cost:** $150–300 lower-48 lane, but the residential-pickup surcharge ($75–150), residential-delivery surcharge ($75–150), and liftgate surcharges ($75–150 on each end) stack quickly. Net usually $300–500 for a single unit. Worse than specialty final-mile at the same price point.

**Customer experience:** Pallet on the curb. Customer cuts the shrink wrap, lifts the appliance off the pallet, gets it inside, disposes of the pallet. **At $7,500 this is the worst outcome of the three.**

**LTL only makes sense if:** (a) palletizing protects the unit substantially better than a carton-and-foam-cap pack-out, AND (b) we're committed to a freight-class commodity declaration that survives the density-only rule.

### Recommendation: pick parcel-ground for ring 1, specialty final-mile (room-of-choice tier) for ring 2+

**Ring 1 (the first 10, friends-and-family per [target-market.md](../../marketing/target-market.md) "rings of trust"):** Parcel-ground via UPS Ground or FedEx Ground. The buyers in this ring are absorbing risk — they know the founder, they know what they're getting, they don't need white-glove framing. Cost is ~$80 vs. ~$300+; the delta funds the unit's actual margin in a ring where unit price is intentionally far below $7,500. **The founder may also choose to hand-deliver locally for ring-1 buyers in driving distance** — the install consult Zoom call ([sibling todo](install-consult-playbook-gap.md)) becomes a face-to-face install for free.

**Ring 2+ (extending past the founder's network):** Specialty final-mile at **room-of-choice tier**. The threshold tier is too thin for the price band; full white-glove is more than the package actually needs (the install is plug-and-play once the appliance is in the kitchen). Room-of-choice — carton delivered into the kitchen, customer unboxes during the install consult Zoom call — is the right fit. Vendors to quote: XPO Last Mile / RXO, AGS, J.B. Hunt Final Mile, Metropolitan Warehouse.

**The Founder Edition cold buyer (the cohort the $7,500 anchor was written for) gets the room-of-choice tier from day one.** The "first 50 hand-built" framing collapses if the unit arrives on the porch in the rain.

---

## Decision 2: Insurance — accept the $0.10/lb cap, or buy independent cargo coverage

The "other than new" exclusion in AAA Cooper Tariff Item 570 is representative of the LTL industry's standard released-rates language. Similar language appears in UPS Released Value tariffs and FedEx Money-Back Guarantee terms, sometimes named "used," "refurbished," "remanufactured," or "secondhand." A claims adjuster reading our published material — which openly describes the compressor as harvested from a consumer ice maker (see [`hardware/harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md)) — has every basis to apply the cap.

The math:
- Declared value $7,500, carrier insurance premium paid.
- Damage in transit. Vessel cracked, faucet snapped, compressor displaced.
- Carrier invokes "other than new" cap. Liability collapses to $0.10/lb × 35 lb = **$3.50**.
- Customer (or founder) eats $7,500.

This is not a theoretical risk. Per Flock Freight's 2022 market study, **86% of LTL shippers experienced at least one damage claim that year**. Per-unit damage rates on residential-tier final-mile lanes commonly run 5–10%. At 50 units over four years of Founder Edition, that's 2–5 damage events expected. The carrier-insurance-only path means each event is paid out-of-pocket against the founder's solo margin.

### Three honest paths

**A. Self-insure, eat the damage events.** Build a damage-loss reserve into the unit price. At 5% incidence × $5,000 average loss (replacement at landed cost, not retail) = $250/unit reserve. Acceptable inside the Founder Edition price, brutal at the eventual Standard Edition $5,500.

**B. Independent cargo insurance via Roanoke, Falvey, Shipsurance.** Annual all-risk policies in the $1,000–3,000/year range cover up to a declared value per shipment with broader terms than carrier-released-rates language. Watch for "inherent vice" / "pre-existing defect" exclusions — a policy that excludes failure of refurbished components is no better than the carrier exclusion. Negotiate the exclusion language *before* the first claim, not after. **Likely the right answer once we get to ring 3.**

**C. Reframe the harvested compressor.** The repo currently describes the compressor as "harvested from a donor ice maker" — accurate, defensible, also a hand-grenade in any insurance conversation. The compressor itself is mechanically the most reliable component in the appliance once installed (it's been bench-burned-in during the donor's manufacturing test cycle, then vented + recharged + burned-in again on our refrigerant loop bench per [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md)). Whether the insurance-side framing should describe it as "incorporated component" or "remanufactured unit" or some other accurate-but-less-trigger-loaded phrase is a real question with real dollars at the end of it. **Not a recommendation to be dishonest — a recommendation to think about how the freight underwriter reads our build documentation.**

### Recommendation: B for rings 2+ — get a Roanoke / Falvey quote during ring-1 build

Get the independent-cargo quote now (against the published build doc as-is — they will ask), so the policy is in place before the first cold-buyer Founder Edition unit ships in ring 2+. Read the "inherent vice" exclusion carefully and negotiate it if it would exclude compressor-related failures. The premium budget is ~$30–60/unit at our volume; a single avoided claim pays for years.

Ring 1 self-insures by virtue of the relationship — friends-and-family buyers who paid $2,000–3,000 will not lawyer up over a damaged unit; the founder makes them whole directly.

---

## Decision 3: Carton density — design for NMFC 60500 / Class 92.5 if LTL ever happens

If the working envelope holds at 60×50×50 cm / ~35 lb gross, our carton density is ~6.6 lb/ft³. That's a Class 125+ density-only rate on LTL, ~1.5–2× the per-pound cost of Class 92.5.

This is **moot for parcel-ground or specialty final-mile** (their rates are not NMFC-class-driven). It bites only if we end up on traditional LTL — most likely if we ever co-ship a CO2 cylinder + appliance on the same pallet per the [CO2 sibling's Section 6 "Practical implementation"](co2-supply-ownership-gap.md). That sibling assumes "the Founder Edition unit ships LTL anyway (heavy appliance)" — which contradicts the parcel-ground recommendation in this doc.

**The two docs need to agree.** Either:
- Appliance ships parcel-ground or specialty final-mile (this doc) and the CO2 cylinder ships separately on its own LTL lane from the welding-gas distributor, OR
- Appliance ships LTL and the CO2 sibling's co-pallet plan is the actual lane.

Recommended: **resolve at the next Derek sync. The CO2 sibling's assumption is older than this doc's research; this doc's parcel-ground recommendation is the newer call.**

If the parcel-ground path holds, Open Item 6 (carton design) can optimize for **drop survival**, not freight class — molded foam end-caps tuned for the ~30" / 5-corner FedEx Ground drop test, not for palletization. That's a meaningfully different carton design.

If LTL becomes the path, the carton has to be designed for **density**: ship the appliance + faucet bag + install kit in the **smallest** possible carton that still cradles the unit, and palletize tightly. Density-only NMFC rules reward compact packing directly.

---

## Decision 4: California Prop 65 carton marking

OEHHA's "Household Appliances" fact sheet requires Prop 65 warning before consumer exposure for refrigerating appliances that contain listed chemicals (common in compressor lubricants, plasticizers, lead in solder). The warning must reach the consumer *before* exposure — most appliance OEMs (U-Line, Sub-Zero, GE) place it on the **outer carton** and in the manual.

Online sales into California also trigger the §25602(b)(1) website warning at the point-of-sale page.

**This is a 1-day task:**
- Add the Prop 65 warning to the outer carton artwork (alongside the W021 flame symbol that's already required under SNAP / UL 60335-2-89).
- Add the §25602(b)(1) website warning to the homesodamachine.com purchase page.

Both are recommendation-tier; the math says any unit shipped to a CA address without this marking is a tort-of-record waiting to happen. The marking itself is free; the lawsuit is not.

Other state wrinkles: **WA, MA, NY** have appliance energy-efficiency reporting requirements at the manufacturer level (CEC/DOE-aligned). At 12 units/year the registration thresholds are unlikely to apply. Reading the actual exemption language is a separate research task.

---

## What this means for the repo, concretely

If the recommendations here hold, the following changes land:

### [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) — close Open Items 1, 3, 6

- **Open Item 1 (carrier selection):** commit to "UPS Ground / FedEx Ground for ring 1; specialty final-mile room-of-choice tier (XPO Last Mile / RXO / AGS quoted) for ring 2+." Note the boundary in the doc.
- **Open Item 3 (damage-claim workflow):** name the "other than new" exclusion explicitly; commit to independent cargo insurance via Roanoke or Falvey for ring 2+; document the self-insure-via-relationship posture for ring 1.
- **Open Item 6 (carton + foam source):** commit to a parcel-ground-optimized carton design (foam end-caps tuned for drop survival, not for palletization). Source: local custom-cut packaging house, working assumption stays in place.

### Step 9 (carrier handoff) — rewrite the declared-value paragraph

Current text: *"Declared value at the carrier's insurance level is TBD pending the damage-claim decision (Open item 3); working assumption is full declared value of $7,500."*

New text should: (a) name the $0.10/lb / "other than new" cap, (b) commit to the independent-cargo policy as the actual coverage mechanism for ring 2+, (c) keep the carrier declared-value at $7,500 anyway as a paper trail for the policy's underwriter — but understand it does not buy what it looks like.

### New: outer carton artwork file

`hardware/printed-parts/shipping/carton-artwork.md` or similar — captures:
- ISO 7010 W021 flame symbol (also on the appliance per UL 60335-2-89; carton marking is a courtesy to the carrier, not a regulatory requirement under §173.307)
- Refrigerant charge note: "Contains R-600a, XX g" — same format NewAir / Whynter use
- Orientation arrows ("THIS SIDE UP") and "FRAGILE" pictograms
- **Prop 65 warning** for CA-destination compliance
- Founder Edition unit serial sticker — discreet, on the long face

### Cross-reference fix with the CO2 sibling

[`co2-supply-ownership-gap.md`](co2-supply-ownership-gap.md) section "Practical implementation" assumes appliance ships LTL and CO2 cylinder co-pallets. If the parcel-ground recommendation here holds, that assumption breaks. Resolve by either:
- Editing the CO2 sibling to drop the co-pallet plan and instead source CO2 cylinder delivery from the local welding-gas distributor on a separate LTL lane to the customer, **OR**
- Edit this doc's Decision 1 to accept LTL for the appliance specifically to enable the co-pallet plan — and accept the NMFC density penalty in exchange for the customer's CO2-day-one experience.

The first option is cleaner; the second option preserves the [marketing target-market.md](../../marketing/target-market.md) "first pour happens the day the appliance arrives" promise more directly. **A decision worth making with Derek before either doc edits the other.**

---

## What I did not investigate (followups for later agents)

- **International shipping** (finish-pack-ship.md Open Item 5). The §173.307 exception is U.S.-domestic. International shipping invokes IATA DGR (air, almost certainly off the table for a refrigeration appliance) or IMDG (sea, possible but requires UN 3358 declaration). Out of scope for the lower-48 Founder Edition run, real work needed before international demand can be answered.
- **The specific carton/foam SKU.** A quote from one or two local packaging houses (Atlas Box & Crating, ULINE, McMaster custom-foam) is the next concrete step; out of scope for a recommendation doc.
- **Carrier-specific account setup.** UPS Ground vs. FedEx Ground vs. specialty final-mile each require account setup, residential-pickup arrangement, and a label-generation API integration. The fulfillment-ops mechanics live downstream of the strategic carrier choice here.
- **Returns / RMA freight.** The [warranty sibling](warranty-and-rma-gap.md) covers the warranty terms; the return-leg freight logistics for a damaged or warranty-claimed unit need their own pass. Outbound: $80 parcel or $300 white-glove. Inbound from a customer's kitchen: a noticeably harder question, especially for a unit that may have been water-filled and is therefore no longer dry-ship-compliant.
- **Whether the founder elects to hand-deliver ring 1 locally.** A pure-recommendation question; flagged here as the obvious cost-saver and customer-experience-win in the ring where it's most defensible.

---

## Primary sources

The detailed regulatory and carrier-policy citations live in the research notes that informed this doc:

- **49 CFR 173.307(a)(4)(iii)** — refrigerating-machine exception, 12 kg flammable-non-toxic threshold ([eCFR](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-G/section-173.307))
- **49 CFR 172.301** — non-bulk marking (relevant only for non-excepted shipments) ([eCFR](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-172/subpart-D/section-172.301))
- **49 CFR 172.704** — hazmat employee training (not applicable when shipping under 173.307) ([eCFR](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-172/subpart-H/section-172.704))
- **PHMSA Hazmat Registration brochure** — registration not required when shipping only under exception ([PHMSA](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2024-04/Registration-Process-Brochure-2024-2025-Web-04-17-2024.pdf))
- **UPS Ground-Accepted DG Table** ([UPS](https://www.ups.com/assets/resources/media/UPS_TDG_Ground_Accepted_Table.pdf))
- **UPS shipping dimensions & weight ceilings** ([UPS](https://www.ups.com/us/en/support/shipping-support/shipping-dimensions-weight))
- **FedEx Ground Hazmat Shipping Guide** ([FedEx](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf))
- **AAA Cooper Tariff Item 570** — "other than new" $0.10/lb / $10,000 cap ([AAA Cooper](https://www.aaacooper.com/docs/default-source/default-document-library/tariff/item-570.pdf?sfvrsn=ce7cfd51_4))
- **XPO Last Mile service tiers** ([XPO](https://last-mile.xpo.com/last-mile-network/))
- **OEHHA Prop 65 Household Appliances fact sheet** ([OEHHA](https://www.p65warnings.ca.gov/sites/default/files/downloads/factsheets/household_appliances_fact_sheet.pdf))
- **Sub-Zero/Wolf Factory Certified Installation** — the residential-appliance customer-experience comparable at $7,500+ ([Sub-Zero](https://www.subzero-wolf.com/assistance/answers/multi-brand/sub-zero-and-wolf-product-delivery))
- **NewAir, Whynter** — industry precedent for R-600a-charged residential refrigeration via UPS/FedEx Ground ([NewAir](https://www.newair.com/products/newair-126-can-freestanding-stainless-steel-beverage-fridge), [Whynter](https://www.whynter.com/product/68-can-freestanding-beverage-frige-cooler-in-stainless-steel-lock-br-062ws/))

---

## The single most important thing in this doc

The repo has internalized "the appliance ships dry" and "we'll figure out carrier at step 9." Both are true and both are answerable. What the repo has *not* internalized is that **the published "compressor harvested from a donor ice maker" language is a $7,500-per-unit liability exposure** under the standard carrier "other than new" exclusion. The fix is not technical — it is some combination of (a) independent cargo insurance with negotiated exclusion language, (b) the room-of-choice carrier tier that reduces damage incidence at the front door, and (c) a build-doc audit pass on how the compressor is described in customer-facing and underwriter-facing materials. None of that is hard. None of it is in the repo today. At ring 2 it starts to matter for real.
