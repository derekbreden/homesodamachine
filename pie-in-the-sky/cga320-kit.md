# CGA-320 Adapter Kit — the budget entry

*Pie-in-the-sky, not roadmap. Captured 2026-05-18.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A kit that pairs a 5 lb CGA-320 CO2 cylinder (customer-supplied or service-supplied) with a 2 L PET pressure-rated bottle and a push-button carbonation head. The bottom rung of the curator catalog (see [`curator-brand.md`](curator-brand.md)) at roughly $150 retail. The customer chills their own water, carbonates a bottle at a time, refrigerates the bottle, pours from it. Same daily mechanic as a SodaStream, but running on a 5 lb tank instead of a 60 L SodaStream cartridge — 17× the CO2 per cylinder swap, at one-tenth the per-liter cost.

## What's in the kit

- **CGA-320 single-stage regulator.** Output adjustable in the 30–60 PSI range; gauge for tank pressure. Same connector standard the customer's 5 lb tank uses. This is the largest single line item in the kit and the reason the kit price moved from "$50 BOM-only" thinking to a realistic $150 retail.
- **2 L PET pressure-rated bottle.** Carbonation-rated, refillable, dishwasher-safe lower body. **Standard US 2 L soda-bottle neck thread** — the same finish as a Coca-Cola, Pepsi, or generic store-brand 2 L bottle from any grocery store. The customer gets a nice branded bottle in the kit, but the head fits just about any 2 L bottle they have at home or buy at the store. This is intentional: drop the proprietary lock-in, embrace the commodity. Other CGA-320 carbonation kits on the market already do this; we are following an established norm, not introducing a new one.
- **Push-button carbonation head.** Threads onto the bottle, hose-connects to the regulator output, presses to inject CO2 into the bottle. Vent button (or built-in cracking valve) for releasing headspace before unthreading.
- **Hose.** ~4 ft of food-grade tubing between regulator output and head.
- **Instruction card.** Chill the water before carbonating. Two-second bursts work better than one long burst — sparging is more efficient at higher headspace pressure that bleeds down between presses. After carbonation, vent the headspace before unthreading the head. To keep a refrigerated bottle from going flat overnight, squeeze the bottle to expel air before re-capping (the air-removal trick).

## What the kit does not include

- **No 5 lb CO2 cylinder.** Customer brings their own, or buys one via the curator brand's other rungs — pick one up locally per [`local-co2.md`](local-co2.md), or have one delivered per [`co2-service.md`](co2-service.md)'s non-exchange tier.
- **No flavor injection.** The kit makes plain carbonated water. Customers who want flavor can buy SodaStream concentrate bottles separately (the same concentrates that ship with the appliance) and add to the glass after pouring. Same workflow as the SodaStream bottle-and-pour level.
- **No refrigeration.** Customer uses their existing refrigerator.
- **No installation.** Sits on the counter. Cylinder lives wherever the customer puts it — under the counter, in a corner, in the basement, on a shelf.

## BOM sketch

| Item | Approx |
|---|---:|
| CGA-320 single-stage regulator (commodity homebrew-class) | ~$60 |
| 2 L PET pressure-rated bottle | ~$12 |
| Push-button carbonation head + cracking valve | ~$25 |
| Hose + fittings | ~$5 |
| Instruction card + box + branding | ~$8 |
| **BOM total** | **~$110** |

At $150 retail, margin per kit is ~$40 — thin in isolation, but the kit is not the margin engine; it is the entry rung. Two real outcomes from a kit sale:

- A customer who is happy with the kit forever, refilling their tank via [`local-co2.md`](local-co2.md) or [`co2-service.md`](co2-service.md). The kit is the entire product for them; we own their CO2 supply for life.
- A customer who likes the kit and upgrades to the appliance line. The Lillium + Lite bundle ([`lite/`](lite/README.md)) is the natural next step; the Kitchen Edition is the long-term destination.

Both outcomes are good. The kit is honest about what it is — a budget answer with real tradeoffs — and the customer keeps using the brand for CO2 either way.

## What the customer experience is, honestly

The kit is closer to a SodaStream than to the appliance, and the marketing copy says so. What the customer gives up vs the appliance:

- **One bottle at a time.** No always-cold on-demand pour. Carbonate, refrigerate, pour. The kitchen workflow is "make a bottle, leave it in the fridge, refill in 1–2 days."
- **Pre-chilled water required.** Cold water holds carbonation; warm water doesn't. Customers who skip this step taste the result and stop using the kit.
- **Flavor mixed in the glass.** No dedicated faucet, no peristaltic pump, no automatic injection. Pour the carbonated water, then add concentrate from a SodaStream bottle in the same glass. Some customers will love the control. Some will find it tedious.
- **Headspace flat-out.** Even with the air-removal trick, a refrigerated bottle gets flatter over 24–48 hours. Customers who pour from a 2-day-old bottle taste the difference.

What the customer gets vs a SodaStream:

- **17× the CO2 per cylinder swap.** A 5 lb tank lasts months. A SodaStream 60 L cartridge lasts weeks.
- **Lower per-liter cost.** ~$25 fill on a 5 lb tank works out to a few cents per liter of carbonated water. SodaStream's per-liter economics are ~10× worse.
- **No proprietary lock-in, anywhere in the kit.** CGA-320 is the industry-standard cylinder fitting — any welding supplier fills it. The bottle thread is the industry-standard US 2 L soda-bottle thread — any 2 L bottle from a grocery store fits the head. Drop the kit, keep the tank and head, hook either up to anything else later — kegerator, planted aquarium, the next 2 L bottle from recycling, the appliance.

Net: the kit is a meaningfully better deal than a SodaStream for someone with high consumption, and a worse deal for someone with very low consumption. The marketing copy says exactly that.

## What's worth doing next on this

1. **Source the regulator.** A reliable $60 CGA-320 single-stage regulator from a homebrew supplier is the load-bearing part of the kit.
2. **Confirm the standard 2 L bottle thread spec.** The US grocery-store thread used on Coca-Cola, Pepsi, and store-brand 2 L PET bottles — believed to be PCO 1810 (older 28 mm carbonated-soft-drink finish), worth confirming against current production. The head is designed to that spec specifically so the customer can use bottles they already have. Worth checking that competitor CGA-320 carbonation kits also target this same spec (they appear to), to confirm consistency in the commodity.
3. **Prototype the head.** A push-button head with built-in cracking valve is well-established hardware in the homebrew world (Carbonator Cap and similar). The kit version may just be a re-labelled commodity head with our hose attached and our instruction card in the box.
4. **Write the editorial page** for "how to make a SodaStream less bad," which is the natural traffic source for the kit. The page recommends the kit at the bottom and links to the appliance rungs for the upgrade path.

The hard work is editorial and sourcing, not engineering.
