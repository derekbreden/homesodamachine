# Local CO2 Pickup Guide — the free curated directory

*Pie-in-the-sky, not roadmap. Captured 2026-05-18.*

A free, public, curated directory of food-grade-CO2 fill points in the US, organized by zip code. The lowest rung on the curator catalog (see [`curator-brand.md`](curator-brand.md)) and the editorial counterpart to the paid [`co2-service.md`](co2-service.md). Not a product per se — the deliverable is *knowledge and curation*, not hardware. Pitched as the first interaction many visitors will have with the brand, and the trust-building surface that the rest of the menu rides on.

## What it is

A web tool: `homesodamachine.com/refill?zip=NNNNN` returns the customer's three closest food-grade-CGA-320 fill points, with hours, current pricing if known, parking notes, and what to ask for at the counter. Plus a per-location confidence flag — Airgas branches are reliable across the country; a local paintball shop may or may not fill food-grade, and we say so.

Underneath the tool: a markdown directory in the repo, one file per metro (or one per state, as it scales), maintained by us via agent-assisted research and verification at metro-level cadence. Each entry carries the same fields:

- Business name, address, phone
- Hours
- Food-grade vs. industrial-grade availability (often both, sometimes only one)
- Refill price range and whether the price includes hazmat fees
- Cylinder-swap policy (do they swap empties for full, or refill yours while you wait)
- "What to ask for" copy — counter-staff vocabulary varies and the customer needs words that work
- Last-verified date

## Why this exists

Three friction points in the current CO2 ownership story (per [`../marketing/target-market.md`](../marketing/target-market.md) 272–274 and [`../todo/2026-05-18/co2-supply-ownership-gap.md`](../todo/2026-05-18/co2-supply-ownership-gap.md) Part 1):

- **"CO2 refill near me" returns garbage.** Welding suppliers, paintball stores, and homebrew shops in random order, with no info on which fills food-grade. The customer Googles, picks the closest, drives over, and finds out they only carry industrial.
- **Food-grade vs. industrial-grade vocabulary is opaque.** Many welding suppliers carry both. Counter staff sometimes don't know which the customer wants. We can hand the customer the right phrasing.
- **Hours and parking are not on welding-supplier websites.** A trip to Airgas that fails because the loading-dock entrance is on a different street is the exact kind of small humiliation the curator brand exists to prevent.

## Who it's for

- The CGA-320 adapter kit customer ([`cga320-kit.md`](cga320-kit.md)) who refills their own tank and would rather not pay for delivery.
- The Kitchen / Shop Edition customer's first cylinder refill (after the included one runs out — see [`../todo/2026-05-18/co2-supply-ownership-gap.md`](../todo/2026-05-18/co2-supply-ownership-gap.md) C2 for the included-cylinder decision).
- Anyone with a CGA-320 cylinder who Googles "CO2 refill near me" and lands on us — paintball, kegerator, homebrew, aquarium. Most will never buy anything from us. Some will eventually buy the appliance.
- People who haven't bought anything from anyone yet and are doing research. The guide is plausibly their first impression of the brand.

## Why it's free

Three reasons it earns its keep at zero direct revenue:

- **SEO surface.** "CO2 refill near me" is a high-volume search with no good answer today. Owning that result for free is worth more than monetizing it.
- **Trust seed.** The customer who reads honest advice that didn't sell them anything is the customer most receptive to the rest of the catalog later. Same logic as the SodaStream-advice editorial page — the curator brand earns the right to recommend its own products by recommending other things first.
- **Upgrade path to [`co2-service.md`](co2-service.md).** The guide ends with: "or, if `drive somewhere during business hours` is the part you hate, we deliver for $250 per swap. Click here." A free tool that funnels into a paid service is a real conversion mechanism.

## How it relates to [`co2-service.md`](co2-service.md)

The two are siblings on the menu — the lowest-budget option and the convenience option for the same underlying problem.

| Dimension | Local pickup guide | CO2 delivery service |
|---|---|---|
| Customer cost | $0 for the guide; ~$25–50 per fill at the supplier | $250 per exchange swap |
| Customer effort | Drive there, lift cylinder, counter interaction, business hours | None — UPS arrives |
| Brand revenue | $0 (drives traffic) | ~$141 gross margin per swap |
| Friction owned by | The customer | Us |

A real curator-brand customer journey is "started with the free guide, got tired of the drive after the third refill, upgraded to the service."

## Editorial scope at launch

A full national directory is a multi-year project. The minimum viable launch is much smaller:

1. **One metro to start.** Lincoln NE — Derek's home market — plus Omaha as the obvious nearby second. Three to five fill points per metro. Verified in person by Derek. ~4 hours of work each.
2. **The food-grade vs industrial-grade explainer page.** One page. Covers the actual chemical difference (purity ppm, residue limits, regulatory grade per CGA G-6.2 and FDA 21 CFR 184.1240) and why we recommend food-grade for soda use even though the difference is small. Plus the counter vocabulary the customer can use.
3. **The hydro-test schedule explainer.** One page. DOT 3AL aluminum cylinders are re-tested every 5 years; the date stamp on the cylinder collar tells the customer when. Welding suppliers will refuse to fill a cylinder past its re-test date.
4. **The web tool.** A small page that accepts a zip and returns the metro's directory if we have it, or "we don't cover your area yet — here's the national-chain list" if we don't. The fallback list is Airgas / AirWeld / Praxair-Linde / NuCO2-commercial / homebrew-chain finders, sorted by likely food-grade availability. This is the unscalable-but-honest version that earns trust while we expand.

## "BOM" — labor and editorial, not hardware

| Item | Approx |
|---|---:|
| Initial Lincoln + Omaha directory (research + visits + writeup) | ~4 hours |
| Food-grade vs industrial-grade explainer | ~2 hours |
| Hydro-test schedule explainer | ~1 hour |
| Web tool (zip lookup, fallback list, branded page) | ~4 hours |
| **One-time launch effort** | **~11 hours** |

Recurring cost is per-metro: roughly a half-day to add a new metro at launch, then per-metro upkeep on the order of an hour per year (price drift, hours changes, businesses closing). National coverage is plausibly 50 metros, which is ~25 days of editorial at launch and a couple of weeks per year on upkeep. All deferrable past the first appliance ship.

## What's worth doing next on this

1. **Write the Lincoln + Omaha directory entries today.** This is the smallest version of the product and it costs nothing to ship. ~4 hours.
2. **Stand up the URL.** Even a static `homesodamachine.com/refill` page that lists the two metros and falls back to national chains is enough to start. The zip-lookup tool can come later.
3. **Plan the agent-assisted expansion path.** Agent resources make metro-level research and verification cheap enough to do at a fine pass — Airgas branches, paintball stores, homebrew shops, food-grade availability, hours, prices. The per-metro template: pick the next metro, run a thorough research pass, then a verification pass (phone calls where needed), then publish. Out of scope before the first metro is live.
