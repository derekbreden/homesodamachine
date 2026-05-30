# Timeline — releasing the curator catalog over time

*Pie-in-the-sky, not roadmap. Captured 2026-05-14, expanded 2026-05-18.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A line of thinking about releasing the curator catalog ([`curator-brand.md`](curator-brand.md)) sequentially rather than launching everything at once — what ships first, what each release teaches, and how the brand grows past one appliance. The original framing in this doc was about the three appliance variants in this folder — Lite, Kitchen, Shop — as a numbered HSM 1/2/3 product line released sequentially rather than as alternative SKUs sold in parallel. The expanded framing keeps that numbering but adds the lower rungs of the catalog (free editorial, the CGA-320 kit, the CO2 services) as earlier releases that ship before any of the appliance variants.

## The framing

Going from earliest release to latest:

- **Free editorial** — a SodaStream-advice page, the local CO2 directory in [`local-co2.md`](local-co2.md). Ships first because the cost is minimal and the SEO surface seeds traffic for every later rung. ~$0 spend.
- **CGA-320 adapter kit** — [`cga320-kit.md`](cga320-kit.md). ~$110 BOM, ~$150 retail. Standard US 2 L soda-bottle thread + CGA-320 regulator + push-button head. First transactional rung.
- **CO2 delivery service** — [`co2-service.md`](co2-service.md) at $500 for new bottle, $250 for refill. Hazmat shipping through UPS or FedEx.
- **HSM 1** — the Lite Edition. ~$500 BOM, $1,500 retail. Flavor injection only, customer supplies the carbonator (Lillium-class) or pairs with one we resell.
- **HSM 2** — the Kitchen Edition without drain. ~$1,500 BOM, $3,500 retail. Integrated carbonator and refrigeration, faucet at the back of the sink, no plumbed drain.
- **HSM 3** — front dispense + drain. ~$2,000 BOM, $5,000 retail. Countertop-capable with proximity arm gesture and a plumbed drain for unattended clean cycles.
- **Flavor module** — slots in between HSM 2 and HSM 3, or after HSM 3, depending on what customer demand says by then.

## The numbering does real work, not cosmetic work

This isn't a relabeling of the three pie-in-the-sky docs. The numbers imply *continuity*. A customer who buys HSM 1 understands that HSM 2 is coming. That changes the buying mindset from "is this a real company?" to "this is the first one." The current Founder Edition / Standard Edition framing in `marketing/target-market.md` is fundamentally a scarcity-vs-availability story that depends on solo build capacity for its honesty. Numbered releases obviate the whole scarcity construct.

The unnumbered earlier rungs (editorial, kit, CO2 services) sit alongside the HSM series, not inside it. They are the catalog's wider base; the HSM series is the catalog's premium line. Both share the brand voice, and the customer can travel between them in any direction.

## Ring 1 becomes dramatically easier

`marketing/target-market.md` is unusually candid about the ring-1 problem: no one in the founder's current network would write a $7,500 check sight-unseen for a kitchen appliance from a stranger. HSM 1 at $1,500 is in a price band where people will casually buy from a one-person shop. The trust gap shrinks from "would I buy a Tesla from this guy" to "would I buy a fancy kitchen gadget from this guy." Completely different conversations.

The CGA-320 kit at $150 collapses the gap further — that's a price point where people will buy from a one-person shop on the strength of a thoughtful editorial page alone. Ring 1 expands from "ten friends willing to write a $2,000 check" to "a few hundred SodaStream-tired Googlers willing to try $150 of curated hardware."

## The marketing flywheel inverts

Today's marketing problem: how do we convince anyone that a $7,500 machine from an unknown brand is real? With HSM 1 the marketing problem becomes: how do we make a $1,500 entry product visible. With the editorial + kit + CO2 services rungs added below HSM 1, the problem shifts again: how do we own the search results for "CO2 refill near me" and "how do I make my SodaStream less bad." The 30-second pour video that the current plan needs anyway is the same content that sells HSM 1, HSM 2, and HSM 3 — the same Steve-Martin-moment hook works at every price tier. The earliest free rungs are the funnel door for the entire product line, permanently, not just at launch.

## Manufacturing economics swing the other way

HSM 1's BOM is mostly parts that ship in HSM 2 and HSM 3 as well — electronics shelf, peristaltic pumps, valve manifold, hopper, faucet, display, firmware. Volume on HSM 1 drops per-unit costs on every shared part. The "easy SKU subsidizes the harder SKUs through shared BOM" pattern is the historical norm for appliance brands at this scale. The current single-SKU plan does not have this lever.

The CGA-320 kit doesn't share BOM with the appliance line — it is a regulator + bottle + head, not electronics + pumps. So the kit doesn't pull appliance unit-cost down. What it drives down instead is *brand discovery cost*: shared traffic, shared SEO, shared trust capital. The economics of brand investment work the same way shared-BOM economics do — fixed cost amortized across more units.

## Risk profile inverts

Current plan: spend the project budget betting that the hard engineering (custom 316L vessel, refrigerant teardown and recharge, hydrocarbon safety architecture) lands at the right time, then validate go-to-market against the finished machine.

HSM-1-first plan: ship something, validate everything that isn't engineering — does the video convert, does the install story work, does the syrup supply chain hold up, does the iOS app feel right, do real kitchens cooperate with the install pattern, does the brand mean anything yet, what's the real failure rate of a peristaltic pump in a customer's home. Then invest the HSM 2 carbonator and refrigeration R&D against a validated market.

The CGA-320 kit pulls validation earlier still — it ships at a $150 transaction, which is enough to test the brand voice, the editorial funnel, and the customer-support workflow without any of the syrup or install variables. The CO2 service has its own gating decision before launch (laid out in [`co2-service.md`](co2-service.md)) but ships before HSM 1 in any timeline where the answer is yes. By the time HSM 1 ships, the brand has already learned which of the curator voice cues resonate and which fall flat.

The carbonator engineering doesn't get cancelled in this framing. It gets *funded* by HSM 1 revenue and *aimed* by HSM 1 learnings — with the lower rungs funding and aiming HSM 1 in the same way.

## The founder's learning curve changes shape

Today the founder is learning pressure-vessel fabrication and refrigerant brazing — skills about making the thing. With HSM 1 shipping first the founder also learns: customer support, returns processing, install troubleshooting, real-world six-month reliability data, support-ticket volume, syrup-supply hiccups, kitchen-install edge cases. Those are skills HSM 2 depends on and currently has no data behind. By HSM 2 ship date the founder is genuinely a product company rather than a person who has built one prototype.

With the CGA-320 kit and CO2 services as earlier releases, the customer-support and order-fulfillment skills land even earlier — at $150 transactions long before any $1,500 ones. Returns processing, a working customer-email workflow, a Stripe-and-fulfillment habit, a "how do I respond to a confused customer" voice — all in place before HSM 1 is ready to take a deposit.

## A retention and upgrade path materializes

HSM 1 customer pours soda happily for a year and builds the household habit around it. HSM 2 announcement: everything you love, colder, fizzier, no Lillium on the counter. They already trust the brand. They have already written a check. They have already converted their household. They are the warmest possible HSM 2 lead in the world. The current single-SKU plan has no equivalent installed base when it tries to sell its second product.

The path now extends downward too. CGA-320 kit customer pours soda happily for six months, gets tired of carbonating one bottle at a time, upgrades to Lite. Lite customer pours soda happily for a year, gets tired of pre-chilling water, upgrades to HSM 2. The catalog gives the customer a stepping stone at every level of frustration with their current setup. Same brand, same trust, same UI grammar — different machinery.

## The flavor module decision becomes data-driven

By HSM 2 release there is an installed base of HSM 1 customers. The founder knows which two flavors they actually use, whether they have asked for four, whether a second faucet in the kitchen is a thing real customers want or just an idea. The flavor module gets built when (and if) that data says build it. It also launches into a customer base that already wants it.

## HSM 3 stops carrying weight that isn't HSM 3's to carry

Front dispense + drain + proximity + arm switch is the *halo* version — visually striking, made-for-short-form-video, conversation-starting. Inside a single-SKU plan that variant competes with the Kitchen Edition for "which is the wow product." Under sequential numbering HSM 3 does not have to be the price floor or the brand introduction — the kit, the CO2 services, and HSM 1 carry those. HSM 3 gets to be unapologetically premium and demonstration-friendly, launching into a customer base that already knows the brand.

## How this sits next to the other docs

- [`curator-brand.md`](curator-brand.md) is the catalog index that this timeline sequences. The catalog says "here's the full menu we offer"; the timeline says "and here's when each item shows up on it."
- `marketing/target-market.md`'s "rings of trust" model and "the founder's face is the product at Founder Edition scale" arguments compose naturally with HSM 1. Ring 1 is exactly the customer base that an HSM 1 launch reaches first. The earlier rungs (editorial, kit, CO2 services) reach a wider audience than Ring 1 by design.
- `hardware/future.md` describes the integrated under-counter machine in present tense as "the appliance." Under this framing that document is the engineering spec for HSM 2 specifically.
- `pie-in-the-sky/shop-edition.md` is the engineering sketch for HSM 3.
- `pie-in-the-sky/lite/` is the engineering sketch for HSM 1.
- `pie-in-the-sky/flavor-module.md` is the engineering sketch for an add-on that slots into the numbered release schedule at whatever point customer demand justifies.
- `pie-in-the-sky/cga320-kit.md` is the engineering sketch for the entry kit.
- `pie-in-the-sky/co2-service.md` is the business sketch for the paid CO2 delivery tier.
- `pie-in-the-sky/local-co2.md` is the editorial sketch for the free CO2 pickup guide.
