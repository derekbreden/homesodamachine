# Timeline — releasing the curator catalog over time

*Pie-in-the-sky, not roadmap. Captured 2026-05-14, expanded 2026-05-18.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A line of thinking about releasing the curator catalog ([`curator-brand.md`](/future/pie-in-the-sky/curator-brand.md)) sequentially rather than launching everything at once — what ships first, what each release teaches, and how the brand grows past one appliance. The plan the tree actually holds is [`/future/README.md`](/future/README.md): one appliance in Derek's kitchen, then ten in ten kitchens, then the Founder Edition run. This doc wants a different order — the cheap rungs first, the appliance funded and aimed by what they earn. Only the appliance exists. Every other rung named below is a want with no plan behind it, which is what this folder is for.

## The framing

Going from earliest release to latest:

- **Free editorial** — a SodaStream-advice page, the local CO2 directory in [`local-co2.md`](/future/pie-in-the-sky/local-co2.md). Ships first because the cost is minimal and the SEO surface seeds traffic for every later rung. ~$0 spend.
- **CGA-320 adapter kit** — [`cga320-kit.md`](/future/pie-in-the-sky/cga320-kit.md). ~$110 BOM, ~$150 retail. Standard US 2 L soda-bottle thread + CGA-320 regulator + push-button head. First transactional rung.
- **CO2 delivery service** — [`co2-service.md`](/future/pie-in-the-sky/co2-service.md) at $500 for new bottle, $250 for refill. Hazmat shipping through UPS or FedEx.
- **The flavor injector** — ~$500 BOM, $1,500 retail. Flavor injection only, customer supplies the carbonator (Lillium-class) or pairs with one we resell. No sketch in the tree; its geometry stands at `lite-edition-final:pie-in-the-sky/lite/`.
- **The appliance** — $5,500 / $7,500 retail per [`/marketing/target-market.md`](/marketing/target-market.md), against the per-unit BOM in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md). Integrated carbonator and refrigeration, faucet at the back of the sink, no plumbed drain. The one rung the tree builds: [`/hardware/README.md`](/hardware/README.md).
- **The countertop unit** — front dispense + drain, same two prices. Countertop-capable with proximity arm gesture and a plumbed drain for unattended clean cycles. [`shop-edition.md`](/future/pie-in-the-sky/shop-edition.md).
- **The flavor module** — slots in between the appliance and the countertop unit, or after it, depending on what customer demand says by then. [`flavor-module.md`](/future/pie-in-the-sky/flavor-module.md).

## Numbering the appliance rungs would do real work, not cosmetic work

Nothing here is numbered, and part of the want is that the three appliance rungs become a first, a second and a third rather than alternative SKUs sold in parallel. Numbers imply *continuity*. A customer who buys the first understands that the second is coming. That changes the buying mindset from "is this a real company?" to "this is the first one." The Founder Edition / Standard Edition framing in `marketing/target-market.md` is fundamentally a scarcity-vs-availability story that depends on solo build capacity for its honesty. Numbered releases would obviate the whole scarcity construct.

The lower rungs (editorial, kit, CO2 services) would sit alongside a numbered series, not inside it. They are the catalog's wider base; the appliance rungs are its premium line. Both share the brand voice, and the customer can travel between them in any direction.

## Ring 1 becomes dramatically easier

`marketing/target-market.md` is unusually candid about the ring-1 problem: no one in the founder's current network would write a $7,500 check sight-unseen for a kitchen appliance from a stranger. An injector at $1,500 is in a price band where people will casually buy from a one-person shop. The trust gap shrinks from "would I buy a Tesla from this guy" to "would I buy a fancy kitchen gadget from this guy." Completely different conversations.

The CGA-320 kit at $150 collapses the gap further — that's a price point where people will buy from a one-person shop on the strength of a thoughtful editorial page alone. Ring 1 expands from "ten friends willing to write a $2,000 check" to "a few hundred SodaStream-tired Googlers willing to try $150 of curated hardware."

## The marketing flywheel inverts

Today's marketing problem: how do we convince anyone that a $7,500 machine from an unknown brand is real? With an injector first the marketing problem becomes: how do we make a $1,500 entry product visible. With the editorial + kit + CO2 services rungs added below it, the problem shifts again: how do we own the search results for "CO2 refill near me" and "how do I make my SodaStream less bad." The 30-second pour video that the plan needs anyway is the same content that sells every appliance rung — the same Steve-Martin-moment hook works at every price tier. The lowest free rungs are the funnel door for the whole ladder, permanently, not just at launch.

## Manufacturing economics swing the other way

The injector's BOM is mostly parts that ship in the appliance and the countertop unit as well — main board, peristaltic pumps, valve manifold, funnel, faucet, display, firmware. Volume on the injector drops per-unit costs on every shared part. The "easy SKU subsidizes the harder SKUs through shared BOM" pattern is the historical norm for appliance brands at this scale. A single-rung plan does not have this lever.

The CGA-320 kit doesn't share BOM with the appliance rungs — it is a regulator + bottle + head, not electronics + pumps. So the kit doesn't pull appliance unit-cost down. What it drives down instead is *brand discovery cost*: shared traffic, shared SEO, shared trust capital. The economics of brand investment work the same way shared-BOM economics do — fixed cost amortized across more units.

## Risk profile inverts

The plan: spend the project budget betting that the hard engineering (custom 316L carbonator, refrigerant teardown and recharge, hydrocarbon safety architecture) lands at the right time, then validate go-to-market against the finished machine.

Injector-first: ship something, validate everything that isn't engineering — does the video convert, does the install story work, does the syrup supply chain hold up, does the iOS app feel right, do real kitchens cooperate with the install pattern, does the brand mean anything yet, what's the real failure rate of a peristaltic pump in a customer's home. Then invest the appliance's carbonator and refrigeration R&D against a validated market.

The CGA-320 kit pulls validation earlier still — it ships at a $150 transaction, which is enough to test the brand voice, the editorial funnel, and the customer-support workflow without any of the syrup or install variables. The CO2 service has its own gating decision before launch (laid out in [`co2-service.md`](/future/pie-in-the-sky/co2-service.md)) but ships before the injector in any order where the answer is yes. By the time the injector ships, the brand has already learned which of the curator voice cues resonate and which fall flat.

The carbonator engineering doesn't get cancelled in this framing. It gets *funded* by injector revenue and *aimed* by injector learnings — with the lower rungs funding and aiming the injector in the same way.

## The founder's learning curve changes shape

Today the founder is learning pressure-vessel fabrication and refrigerant brazing — skills about making the thing. With an injector shipping first the founder also learns: customer support, returns processing, install troubleshooting, real-world six-month reliability data, support-ticket volume, syrup-supply hiccups, kitchen-install edge cases. Those are skills the appliance depends on and currently has no data behind. By the appliance's ship date the founder is genuinely a product company rather than a person who has built one prototype.

With the CGA-320 kit and CO2 services as earlier releases, the customer-support and order-fulfillment skills land even earlier — at $150 transactions long before any $1,500 ones. Returns processing, a working customer-email workflow, a Stripe-and-fulfillment habit, a "how do I respond to a confused customer" voice — all in place before the injector is ready to take a deposit.

## A retention and upgrade path materializes

Injector customer pours soda happily for a year and builds the household habit around it. Then the appliance: everything you love, colder, fizzier, no Lillium on the counter. They already trust the brand. They have already written a check. They have already converted their household. They are the warmest possible lead in the world for it. A single-rung plan has no equivalent installed base when it tries to sell its second product.

The path extends downward too. CGA-320 kit customer pours soda happily for six months, gets tired of carbonating one bottle at a time, moves up to the injector. Injector customer pours soda happily for a year, gets tired of pre-chilling water, moves up to the appliance. The catalog gives the customer a stepping stone at every level of frustration with their current setup. Same brand, same trust, same UI grammar — different machinery.

## The flavor module decision becomes data-driven

By the appliance's release there is an installed base of injector customers. The founder knows which two flavors they actually use, whether they have asked for four, whether a second faucet in the kitchen is a thing real customers want or just an idea. The flavor module gets built when (and if) that data says build it. It also launches into a customer base that already wants it.

## The countertop unit stops carrying weight that isn't its to carry

Front dispense + drain + proximity + arm switch is the *halo* version — visually striking, made-for-short-form-video, conversation-starting. Inside a single-rung plan that variant competes with the appliance for "which is the wow product." Sequenced last it does not have to be the price floor or the brand introduction — the kit, the CO2 services, and the injector carry those. It gets to be unapologetically premium and demonstration-friendly, launching into a customer base that already knows the brand.

## How this sits next to the other docs

- [`curator-brand.md`](/future/pie-in-the-sky/curator-brand.md) is the catalog index that this timeline sequences. The catalog says "here's the full menu we offer"; the timeline says "and here's when each item shows up on it."
- [`/future/README.md`](/future/README.md) is the plan the tree holds, and it sequences the appliance rung alone — one machine, then ten, then the Founder Edition run. What is written here is a want laid beside that plan, not a revision of it.
- `marketing/target-market.md`'s "rings of trust" model and "the founder's face is the product at Founder Edition scale" arguments compose naturally with an injector-first order. Ring 1 is exactly the customer base an injector launch reaches first. The lower rungs (editorial, kit, CO2 services) reach a wider audience than Ring 1 by design.
- [`/hardware/README.md`](/hardware/README.md) describes the integrated under-counter machine in present tense as "the appliance," because it is the one rung the tree builds.
- [`shop-edition.md`](/future/pie-in-the-sky/shop-edition.md) is the engineering sketch for the countertop unit.
- The flavor injector has no engineering sketch in the tree; its geometry stands at `lite-edition-final:pie-in-the-sky/lite/`.
- [`flavor-module.md`](/future/pie-in-the-sky/flavor-module.md) is the engineering sketch for an add-on that slots into the order at whatever point customer demand justifies.
- [`cga320-kit.md`](/future/pie-in-the-sky/cga320-kit.md) is the engineering sketch for the entry kit.
- [`co2-service.md`](/future/pie-in-the-sky/co2-service.md) is the business sketch for the paid CO2 delivery tier.
- [`local-co2.md`](/future/pie-in-the-sky/local-co2.md) is the editorial sketch for the free CO2 pickup guide.
