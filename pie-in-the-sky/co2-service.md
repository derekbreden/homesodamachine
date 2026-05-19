# CO2 Delivery Service — consumer CO2 exchange, built on 49 CFR 173.29

*Pie-in-the-sky, not roadmap. Captured 2026-05-18.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A standalone service that delivers filled 5 lb CGA-320 cylinders to residential addresses and ships the empties back as standard non-hazmat parcel. Pitched not as an appliance accessory but as one rung on the curator-brand menu in [`curator-brand.md`](curator-brand.md) — available to any household with a CGA-320 cylinder, including paintball, kegerator, homebrew, aquarium, MIG-welder, and home-soda customers. The operational and regulatory backbone — carriers, contracts, federal rules, cost breakdowns — is captured in detail in [`../todo/2026-05-18/co2-supply-ownership-gap.md`](../todo/2026-05-18/co2-supply-ownership-gap.md) Parts 2 and 3; this doc is the product-and-business sketch that lives in the catalog.

## What the service is

A consumer subscription (or per-swap) offering: the customer's cylinder gets low, an app or web prompt says "ready for a swap," a fresh full cylinder arrives by UPS Ground or FedEx Ground, the customer attaches a return label to the same box with the empty inside, drops it back at any retail UPS/FedEx counter. No drive to a welding-supply branch. No business hours. No counter interaction.

The legal mechanism that makes the return leg cheap is [49 CFR 173.29 "valve open = empty"](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29) — an empty Division 2.2 cylinder at <29 psig ships as plain parcel, no hazmat handling. The outbound leg is regulated hazmat parcel; the return is not. Whole story in the gap todo's Part 2.

## Pricing tiers

| Tier | Customer pays | Customer has |
|---|---:|---|
| Self-serve baseline (we don't sell this, but it's what we compete with) | ~$50 per refill | Their own cylinder, willingness to drive |
| Exchange | $250 per swap | An empty to send back |
| Non-exchange | $500 | Nothing — first-time customer; they keep the cylinder |

The $200 markup over self-serve buys "never drive to a welding supplier again." A 3-can/day household burns through a 5 lb cylinder in roughly 50–100 days (per the consumption math in [`../todo/2026-05-18/co2-supply-ownership-gap.md`](../todo/2026-05-18/co2-supply-ownership-gap.md) C5), which prices the service at ~$1,000–1,800 per year — comparable to a streaming-and-services bundle, framed against the recovered weekend mornings.

The non-exchange $500 tier is the customer-acquisition product: anyone whose first interaction is "I want CO2 at home and I don't have a tank yet" gets an immediate full cylinder. After the first cylinder is empty, they are on the $250 exchange tier forever.

## Rough unit economics

Per-swap direct cost at the exchange tier, no overhead allocation:

| Line | Approx |
|---|---:|
| Cylinder fill, amortized | ~$20 |
| UPS / FedEx Ground hazmat surcharge | ~$45 |
| Freight | ~$18 |
| Return label (173.29 plain parcel) | ~$15 |
| Box + foam insert, amortized | ~$3 |
| Payment processing | ~$8 |
| **Direct cost per exchange** | **~$109** |

Gross margin at $250 retail: ~$141/swap. The non-exchange tier ($500 minus ~$95 cylinder COGS at quantity, minus the same ~$109 logistics) sits around $296 gross.

Excluded from the table: hazmat shipper apparatus amortization, customer-service labor, cylinder-fleet financing (each cylinder in rotation is ~$95 of working capital), hydro-test cadence (every 5 years on 3AL aluminum). All real, all manageable at the scale the curator brand operates at.

## Who the customer is, beyond home soda

The 5 lb CGA-320 cylinder is the standard form factor across:

- Homebrew kegerators (millions of cylinders in service in the US)
- Paintball / airsoft 5–20 lb cylinders
- Planted-aquarium CO2 injection
- Home draft beer culture
- MIG welders (with adapter — CO2 or Ar/CO2 mix)
- Mushroom cultivation, calibration-gas users, craft-soda hobbyists
- Small B2B: brewery taprooms, restaurants under the NuCO2 commercial threshold, coffee shops with nitro cold brew

Each segment has the same problem — welding suppliers feel commercial, run business hours, sit in industrial parks, require a counter interaction. The convenience tax is paid by anyone with an opinion about their time.

## What it would take to ship

The five-step shipper apparatus is documented in detail in the gap todo. In short:

- Open a UPS or FedEx hazmat shipper account (no fee; addendum to an existing parcel account)
- 49 CFR 172.704 training for one person (~$49, valid 3 years)
- Chemtrec subscription (~$1,000/yr) for 24-hour emergency contact
- UN 4G/4GV overpack inventory (~$1,000 for an initial 100)
- PHMSA Hazmat Registration (~$275/yr small business)

Plus the cylinder fleet (~$3,000 for 50 recertified 5 lb aluminums) and initial fills (~$1,250). Reference startup cost is ~$5,300 one-time + ~$1,300/yr recurring + ~$109/shipment variable. No insurance is legally required and neither carrier mandates it; the broker conversation worth having later is "Class 2.2 endorsement on the appliance product-liability policy," not "hazmat shipper insurance."

We explicitly do not pursue a DOT Special Permit. The math is in the gap todo: $40–145k all-in, 12–24 months calendar, amortizes only above ~1,000 shipments/year sustained over years. Out of reach for this brand's scale.

## How this strengthens the curator brand

The service is not a moat for the appliance. It is one of the rungs on the curator menu, and most of the rungs benefit from it:

- The CGA-320 adapter kit customer ([`cga320-kit.md`](cga320-kit.md)) has a 5 lb tank to refill. They are the highest-volume CO2 customer in the catalog by user count.
- The Kitchen / Shop Edition customer has a 5 lb tank to refill. Bundling N free swaps into Founder Edition pricing (per [`../todo/2026-05-18/co2-supply-ownership-gap.md`](../todo/2026-05-18/co2-supply-ownership-gap.md) C2 and C6) is the natural appliance-side integration.
- The SodaStream owner who took our editorial advice and bought a 5 lb tank with an adapter is a perfect cross-sell.
- A customer who never buys our appliance is still a happy CO2-service customer. That alone makes this a real business rather than an attached feature.

The free [`local-co2.md`](local-co2.md) directory is the sibling rung — the lower-budget, higher-friction answer to the same underlying problem. The pickup guide drives traffic; the delivery service converts that traffic into revenue when the customer decides driving to the supplier is no longer worth the time.

## What's worth doing next on this

The pre-revenue stance from the gap todo applies here unchanged: nothing in this doc commits money before there is a paying customer.

1. **Local hand-delivery validation.** Five to ten local customers, $250 in cash via a Stripe Payment Link, Derek drives the cylinder. No PHMSA Registration, no Chemtrec, no UN overpacks, no shipper account — none of it is needed for local hand-delivery. ~$1–2k experiment that runs alongside the appliance work, tests willingness-to-pay without testing the shipping product.
2. **Decision point.** If demand validates locally, decide whether to stand up the Option B shipper apparatus. The ~$5,300 one-time cost is the bar. The real question: does Derek want to be a hazmat shipper of record, and is the demand signal strong enough to justify the spend.
3. **Branding.** A standalone service needs a name that works for a paintball owner, a kegerator owner, and a homesodamachine customer. Not necessarily a homesodamachine sub-brand — could stand alone, with curator-brand integration as the route into it. Worth a separate thinking exercise.

Anything past step 2 — fill stations, regional hubs, full subscription product, appliance bundling — is downstream of validation and out of scope for this doc.
