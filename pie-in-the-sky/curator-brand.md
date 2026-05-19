# Curator Brand — homesodamachine.com as a guide, not a SKU

*Pie-in-the-sky, not roadmap. Captured 2026-05-18.*

*BOM figures referenced in this doc are first-pass estimates intended to size the idea, not specifications.*

A frame for what homesodamachine.com becomes once it grows past being a landing page for one appliance. The site greets a visitor with a curated map of home soda experiences — from "advice for the SodaStream you already own" up through the integrated under-counter appliance — and recommends honestly across the whole map based on the visitor's pain tolerance, budget, and where they are in life. We sell most of the rungs ourselves; for the ones we don't, we still recommend the right product. The brand promise is curation and honesty, not a single SKU.

## The thesis

Everyone who hates the cans (per [`../marketing/target-market.md`](../marketing/target-market.md)) wants out of them, but their budgets and tolerances vary enormously. Today's plan answers one slice — the homeowner at $200K+ who can spend $7,500 on a hand-built appliance — and treats every other slice as someone else's problem. The curator framing rejects that: the SodaStream owner who could be happier with a 5 lb tank, the renter who can't drill a faucet, the homebrewer who needs CO2 delivered, the bar/garage owner who wants the appliance on a countertop — these are all the same customer at different points in their life. We are the brand that walks the whole map with them.

## What makes this brand distinctive

There is no other store on the internet that organizes the home soda problem this way. The existing landscape:

- SodaStream sells SodaStream. They are not going to tell you that a 5 lb CGA-320 tank and a generic 2 L bottle would serve you better.
- Welding-supply distributors sell CO2 to bars and restaurants. They are not going to explain food-grade vs industrial-grade, or that you can get one cylinder filled near you for $25.
- Lillium and Brio sell their own integrated carbonators. They do not sell a kit, and they do not deliver CO2.
- Wirecutter and other reviewers cover one SKU at a time, not the whole map.

The gap is not a product; it is a curator. The curator is the brand.

## The voice

We are people who hated the cans, tried every option, and have honest opinions about each one. We will recommend a competitor's product if it is right for the customer in front of us. We will tell a SodaStream owner the air-removal trick even though they didn't buy from us. We will tell a Lillium owner the Lillium is a fine carbonator, and pair it with our flavor injector rather than make them throw it out. We do this because the only way to be a credible guide is to be genuinely indifferent to the SKU the customer ends up with — at this customer, at this moment, with this budget.

The Steve-Martin "He hates these cans" moment from [`../marketing/target-market.md`](../marketing/target-market.md) is the hook for the whole brand, not just the appliance. Recognition is the entry point at every price tier.

## The map of offerings

Going from lowest pain tolerance and lowest budget upward. Each is a real shelf on the homepage of homesodamachine.com.

| Shelf | Cost to customer | Sold by us? | Doc |
|---|---:|---|---|
| Advice for your existing SodaStream | Free | Editorial | (none yet — would live on the site) |
| Local CO2 pickup guide | Free (customer pays ~$25–50 per fill at the supplier) | Editorial | [`local-co2.md`](local-co2.md) |
| CGA-320 adapter kit (regulator + 2 L bottle + push-button) | ~$150 | Yes | [`cga320-kit.md`](cga320-kit.md) |
| CO2 delivery service | $250 / $500 per swap | Yes | [`co2-service.md`](co2-service.md) |
| Lillium + Lite Edition bundle | ~$2,500 | Yes (Lite) + resale (Lillium) | [`lite.md`](lite.md) |
| Kitchen Edition appliance | $5,500 / $7,500 | Yes | [`../hardware/future.md`](../hardware/future.md) |
| Shop Edition appliance | $5,500 / $7,500 | Yes | [`shop-edition.md`](shop-edition.md) |
| Flavor Module add-on | $1,800 / $2,500 | Yes | [`flavor-module.md`](flavor-module.md) |

Two of these run *across* the map rather than at one rung — the local pickup guide and the delivery service serve the kit customer and the appliance customer equally. The Lillium row is the one rung where we resell rather than build, and we do not pretend otherwise.

## Why the bottom of the ladder matters

A single-SKU brand has no answer for the customer who isn't ready to spend $5,500. A curator brand has three answers — advice, the kit, and the CO2 services — before the customer ever sees an appliance price. Three benefits compound:

- **Trust seeded early.** A SodaStream owner who landed on the site for "how do I make my SodaStream less bad" reads an honest answer. They didn't pay anything. When their kitchen renovation moves the conversation toward an integrated appliance, they remember which site treated them as a person rather than a lead.
- **Discovery surface for the rest of the menu.** The free SodaStream advice and the free local-CO2 pickup guide are SEO-friendly, shareable content about real problems. Most of the people who search "CO2 refill near me" are not buying a $7,500 appliance today. Many of them will. We are not going to be the answer if we don't show up here.
- **A first transaction at $150.** The CGA-320 adapter kit lowers the first-purchase price by 50× from the appliance. Some buyers will only ever buy the kit. Some will upgrade. Both outcomes are good. Single-SKU plans give us neither.

## Why the top of the ladder matters

The appliance does not stop being the halo product under this framing. It is the proof that the curator knows what they are talking about. A customer who reads the SodaStream advice and notices that the same people built a $7,500 hand-built integrated machine takes the advice more seriously, not less. The curator framing extends the appliance's reach; it does not dilute it.

## How this relates to the existing docs

- [`../marketing/target-market.md`](../marketing/target-market.md) describes the appliance buyer specifically. Under this framing it is the target-market doc for the upper end of the ladder, not the whole brand. A companion doc for the lower-end buyer profiles is implied by this reframe and out of scope here.
- [`../hardware/future.md`](../hardware/future.md) is the engineering spec for the Kitchen Edition rung.
- [`lite.md`](lite.md), [`shop-edition.md`](shop-edition.md), [`flavor-module.md`](flavor-module.md) are engineering sketches for three of the rungs.
- [`co2-service.md`](co2-service.md), [`cga320-kit.md`](cga320-kit.md), [`local-co2.md`](local-co2.md) are sketches for three more rungs (the lower end and the services).
- [`hsm-1-2-3.md`](hsm-1-2-3.md) is the older, smaller framing — three sequential SKUs of one product line. The curator framing supersedes it. Once this doc is in shape and the existing rung docs have caught up, `hsm-1-2-3.md` can be retired.

## What's worth doing first

Nothing on the catalog side commits real money. The Kitchen Edition ships first regardless, because it is the credibility anchor and because the engineering is already deep. In parallel, very cheaply:

1. The local-CO2 pickup guide. A markdown doc for Lincoln NE that lists the three closest food-grade fill points and what to ask for. The smallest possible version of the editorial product. Posted under a URL that is shareable.
2. A SodaStream-advice editorial page. Air-removal trick, chill-the-water-first, the 5-lb-tank-and-adapter upgrade. Maybe a video. Same cost-to-build as the local CO2 guide.
3. A landing-page sketch — even a hand-drawn one — of the homepage with all the rungs on it. The point is to see whether the curator framing reads cleanly to a visitor, before any of the lower-rung products are built.

The CGA-320 kit and the CO2 service each have separate validation paths in their own docs. The Flavor Module and the Shop Edition are downstream of the Kitchen Edition shipping. Nothing in this doc changes those orderings; this doc reframes how the existing shelf is shown to a visitor and how more shelves get added later.
