# CO2 Delivery Service — hooking into mature consumer hazmat shipping

*Pie-in-the-sky, not roadmap. Captured 2026-05-18.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A consumer service that delivers filled 5 lb CGA-320 cylinders to residential addresses through UPS Ground or FedEx Ground hazmat parcel, with empties shipping back as plain non-hazmat parcel under [49 CFR 173.29](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29). One rung on the curator-brand menu in [`curator-brand.md`](curator-brand.md), available to any household with a CGA-320 cylinder — paintball, kegerator, homebrew, aquarium, MIG-welder, and home-soda customers.

## The infrastructure already exists

To be unambiguous: **the carrier infrastructure for residential hazmat delivery already exists, is mature, and is used at consumer scale every day.** SodaStream and Drinkmate ship millions of consumer-direct CO2 cylinders to residential addresses across the lower 48 — almost all via USPS (under [DOT-SP 20796](https://www.phmsa.dot.gov/hazmat/documents/offer/SP20796.pdf/offerserver/SP20796) and similar permits) and UPS Ground (for orders of 3+); [SodaStream's empty-return support page](https://support-us.sodastream.com/hc/en-us/articles/14243394657179-How-do-I-return-my-empty-cylinders) and [Drinkmate's exchange shipping instructions](https://idrinkproducts.com/pages/co2-exchange-shipping-instructions) are direct evidence of how this works at scale. Specialty-gas suppliers ship hazmat to grad students at home routinely. We do not need to build a delivery network. We hook into one.

- **UPS Ground** accepts Class 2.2 compressed gases in the lower 48. UN1013 (carbon dioxide) is on the [accepted-via-Ground list](https://www.ups.com/assets/resources/media/UPS_TDG_Ground_Accepted_Table.pdf), and the [UPS Hazardous Materials Service Definition](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide/hazardous-material-service-definition) confirms residential-destination delivery is allowed.
- **FedEx Ground** is the same — Class 2.1 and 2.2 accepted, lower 48 only — per the [FedEx Ground Hazardous Materials Shipping Guide](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf).
- All carrier "restrictions" are shipper-side, not destination-side. Once shipper-side compliance is in place — accept the contract, train one person, label the box correctly — the carrier picks up at the fulfillment address and drops on any lower-48 residential doorstep.

The market gap that makes this an opportunity is structural rather than infrastructural: 60 L SodaStream / Drinkmate cylinders ship to homes under existing DOT-SPs; 5 lb-and-up cylinders ship by fleet truck to commercial accounts; the 5 lb consumer cylinder is in the gap. No DOT-SP holder bothered with the 5 lb form factor because their existing business didn't require it. Concrete proof the gap is real: a direct probe of American Brewmaster's online "2.5# CO2 Tank Full" listing — which reads like exactly what we'd be offering — turned out to be in-store-fill only ("YES - WE FILL CO2 TANKS! BRING IT IN, AND WE'LL FILL IT UP!"). The "online order, ships to home, filled cylinder" pattern does not exist at the 5 lb form factor today. We don't need a DOT-SP either — we use the per-shipment hazmat surcharge route through UPS / FedEx Ground.

## The 49 CFR 173.29 return-leg trick

Per [49 CFR 173.29 "empty packagings"](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29), an empty Division 2.2 non-flammable gas cylinder at <29 psig ships as standard parcel — no hazmat handling, no surcharge, no shipping paper. Open the valve, equalize to atmospheric, return as plain UPS / FedEx Ground or USPS. Industry shorthand: "valve open = empty."

The round trip is asymmetric. Outbound = regulated hazmat parcel with a ~$45 carrier surcharge. Return = plain parcel. Per-swap cost is dominated by the outbound leg. The customer verifies "valve open" trivially — turn until it stops, listen for absence of hiss — and the empty box becomes the return container for the next full cylinder.

## Pricing

| Tier | Customer pays | What they get |
|---|---:|---|
| Refill | $250 | Send back an empty, get a full |
| New bottle | $500 | First-time customer; cylinder included; no return required |

Refill is the steady-state subscription. New bottle is the customer-acquisition product — anyone whose first interaction is "I want CO2 at home and I don't have a tank yet" gets an immediate full cylinder and sits on the refill tier going forward.

A 3-can/day household pays roughly $1,000–1,800 per year for the service — comparable to a streaming-and-services bundle, framed against the recovered weekend mornings.

## Rough unit economics

Per-swap direct cost at the refill tier, no overhead allocation:

| Line | Approx |
|---|---:|
| Cylinder fill, amortized | ~$20 |
| UPS / FedEx Ground hazmat surcharge | ~$45 |
| Freight | ~$18 |
| Return label (173.29 plain parcel) | ~$15 |
| Box + foam insert, amortized | ~$3 |
| Payment processing | ~$8 |
| **Direct cost per refill** | **~$109** |

Gross margin at $250 refill: **~$141**. New bottle ($500 minus ~$95 cylinder COGS at quantity, minus the same ~$109 logistics) sits around ~$296 gross.

Excluded from the table: hazmat shipper apparatus amortization, customer-service labor, cylinder-fleet financing (~$95 of working capital per cylinder in rotation), hydro-test cadence (every 5 years on 3AL aluminum). And — load-bearing for the section below — insurance.

## The shipper apparatus

The five-step UPS / FedEx onboarding to ship hazmat parcel:

- Open a hazmat shipper account (no fee; addendum to an existing parcel account)
- [49 CFR 172.704](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-172/subpart-H/section-172.704) training for one person (~$49 online, valid 3 years)
- Chemtrec subscription (~$1,000/yr) for 24-hour emergency contact
- UN 4G / 4GV overpack inventory (~$100 for an initial 10)
- [PHMSA Hazmat Registration](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2025-04/Hazmat-Registration-Brochure-2025-2026.pdf) (~$275/yr small business)

Plus a starter cylinder fleet (~$300 for 5 recertified 5 lb aluminums) and initial fills (~$125). Reference startup is **~$600 one-time** + **~$1,300/yr recurring** + **~$109/shipment variable**. No DOT Special Permit. The math on a permit is $40–145k all-in and 12–24 months; amortizes only above ~1,000 shipments/year sustained over years — out of reach for this brand's scale.

The apparatus itself is small and well-defined. Standing it up isn't the gating question. The gating question is the next section.

## The real decision: insurance, or the uninsured risk

Neither UPS nor FedEx requires hazmat shippers to carry insurance. Federal law (PHMSA, 49 CFR) does not require it either. The evidence: the [UPS Dangerous Goods Agreement (Form 2008)](https://www.ups.com/assets/resources/media/hazmat_contract.pdf) — the full 2-page shipper contract — was retrieved and reviewed in entirety; it contains zero mentions of insurance, indemnification, certificate of insurance, additional-insured status, or minimum financial responsibility. The [FedEx Ground Hazardous Materials Shipping Guide](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf) (99 pages) was downloaded and grepped for "insur", "indemn", "liabil" — zero hits in any shipper-requirements context. Two unverified caveats remain: the OP-910 form that FedEx distributes through account executives isn't publicly posted (might impose terms not in the public guide), and the UPS Tariff that Form 2008 references is a larger document whose hazmat sections might add insurance language not in Form 2008 itself. The "you need hazmat insurance" claim that pervades search results traces consistently to 3PL fulfillment providers (requiring it of their customers as a contract term, not law), hazmat-trucking insurance brokers (selling commercial-vehicle policies to fleet operators — wrong product for a parcel shipper), and compliance-vendor marketing (bundling insurance into "complete hazmat compliance solutions") — none of which are the carrier or the regulator.

So the decision is binary, and it is the real decision this service has to make:

- **Ship uninsured.** ~$600 one-time apparatus + ~$1,300/yr recurring + ~$109/shipment variable. Real catastrophic-tail risk: cylinder valve failure in a UPS facility or in a customer's hallway, customer drops a 12 lb cylinder on their foot and sues, customer asphyxiates in a small room with the valve open. Industry-wide, each of these happens occasionally across consumer CO2 shipping. If our cylinder is the one, defense costs alone reach $30–100k before any settlement; settlements at six or seven figures are not unusual. Bankrupts a small operation.
- **Pay for insurance.** The actual product needed is a standalone specialty (E&S) product-liability policy covering Class 2.2 hazmat parcel exposure for a one-person, no-track-record shipper. The "Class 2.2 endorsement on an existing product-liability policy" framing applies to an established business with a policy already in force; that does not describe this operation, which is pre-revenue and uninsured today. Standard-market GL carriers (Hiscox, Next, Hartford) mostly decline hazmat exposure outright — it is outside their underwriting box. Specialty-market minimum-premium floors are real and binding: $5,000–10,000/yr is a common floor regardless of theoretical risk-adjusted price, and a no-name shipper without operating history prices toward the upper end. A $1M/$2M policy realistically lands **$8,000–15,000/yr**, with $10k as a fair working midpoint. Some carriers simply decline. At $10,000/yr insurance + $1,300/yr apparatus = **~$11,300/yr fixed**, break-even sits at **80 refills/year sustained** — a swap every 4–5 days, every week, for a brand with no traffic. At any plausible launch volume the fixed cost exceeds gross margin on every cylinder shipped. "Volume catches up" is not a credible path at the scale this brand operates. This is a guaranteed multi-year loss, possibly forever.

Both options are seriously on the table, but the honest framing of the binary is: ship uninsured and bet that no cylinder valve fails in the wrong place for as long as the service operates, or pay $8,000–15,000/yr for a specialty policy that turns the service into a guaranteed multi-year loss. The apparatus question — whether to stand up a hazmat shipper account at all — is downstream of this decision, not parallel to it.

## Who the customer is, beyond home soda

The 5 lb CGA-320 cylinder is the standard form factor across:

- Homebrew kegerators (millions of cylinders in service in the US)
- Paintball / airsoft 5–20 lb cylinders
- Planted-aquarium CO2 injection
- Home draft beer culture
- MIG welders (with adapter — CO2 or Ar / CO2 mix)
- Mushroom cultivation, calibration-gas users, craft-soda hobbyists
- Small B2B: brewery taprooms, restaurants under the NuCO2 commercial threshold, coffee shops with nitro cold brew

Each segment has the same problem — welding suppliers feel commercial, run business hours, sit in industrial parks, require a counter interaction. The convenience tax is paid by anyone with an opinion about their time.

## How this strengthens the curator brand

The service is not a moat for the appliance. It is one of the rungs on the curator menu, and most of the rungs lean on it:

- The CGA-320 adapter kit customer ([`cga320-kit.md`](cga320-kit.md)) has a 5 lb tank to refill — they are the highest-volume CO2 customer in the catalog by user count.
- The Kitchen / Shop Edition customer has a 5 lb tank to refill. Bundling N free refills into Founder Edition pricing is the natural appliance-side integration.
- The SodaStream owner who took our editorial advice and bought a 5 lb tank with an adapter is a perfect cross-sell.
- A customer who never buys our appliance is still a happy CO2-service customer. That alone makes this a real business rather than an attached feature.

## What's worth doing next on this

1. **Resolve the insurance binary.** The decision in the section above is the gating question. Either commit to the uninsured risk profile, or get a broker quote from a specialty E&S carrier for a standalone product-liability policy covering Class 2.2 hazmat parcel exposure. Many carriers will decline. The realistic landing zone for a brand-new shipper is $8,000–15,000/yr. Until this is decided, nothing else here matters.
2. **Stand up the apparatus.** Once the insurance decision is made, the five-step onboarding is mechanical. ~$600 one-time and some paperwork.
3. **Branding.** A standalone service needs a name. Not necessarily a homesodamachine sub-brand — could stand alone, with curator-brand integration as the route into it.
