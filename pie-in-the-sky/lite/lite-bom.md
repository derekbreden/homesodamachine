# Lite Edition — Bill of Materials

*Sourcing list for the Lite edition — Amazon (Prime) and Fresh Water Systems. Costs are resolved delivered single-unit (product + shipping + tax) where purchased, or catalog unit price pending an order. Order math lives in the shared ledger [../../hardware/purchases.md](../../hardware/purchases.md).*

| Subsystem | Item | Qty | Unit | Source | Notes |
|---|---|---:|---:|---|---|
| Flavor | Platypus Hoser 1 L hydration reservoir (Fast Flow Valve) | 2 | $25.62 | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | Flavor reservoir, one per pocket. Hangs spout-down from its built-in top loop; the threaded outlet takes Platypus drink tubes / closure caps and ships with the hose, so it carries the lid-to-hose adapter. 133 × 292 mm (5.25 × 11.5 in), per the listing. Purchased — order 112-4566389-9910625 (2026-05-30), 2 @ $23.89 = $47.78 + $3.46 tax = $51.24, $0 Prime shipping ($25.62/ea delivered). |
| Flavor | Beduan 12 V 1/4" solenoid valve (NC) | 12 | $9.64 | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | Manifold valves V-A … V-K-B per [fluid-topology-manifold.mmd](fluid-topology-manifold.mmd); same part as the Kitchen build ([../../hardware/bom.md](../../hardware/bom.md) §8). 1/4" push-connect ports. |
| Flavor | John Guest PP2308E two-way divider, 1/4" | 10 | $3.083 | [FWS](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | Manifold Y-junctions Y-A … Y-KB per the .mmd; same part as the Kitchen build (bom.md §8). Black PP, NSF 51+61, 1/4" push-connect. $3.083/ea from a bag of 10. |
| Flavor | neoFit stem-barb, 1/4" stem × 1/4" barb, black acetal (ATBC44-E) | 13 | $0.90 | [FWS ATBC44-E](https://www.freshwatersystems.com/products/neofit-acetal-black-stem-barb-connector-1-4-stem-x-1-4-barb) | One per clear-PVC landing on the PTC manifold — 6 valve ports (V-A, V-B, V-K-A, V-K-B, V-G, V-J) + 6 Y ports (Y-C, Y-D, Y-F, Y-G, Y-E, Y-H) + the inner port of the Lillium flow-control bulkhead (its push-connect inner face lands the clear run to V-A). The 1/4" stem pushes into the PTC port; the clear PVC slips over the 1/4" barb. Black acetal + Buna-N, FDA + NSF 51. $0.90/ea from a bag of 10 (13 → two bags). |
| Flavor | Clear flexible PVC, 1/4" ID × 3/8" OD, NSF-51 (FWS PVCA-0406) | ~13 ft | $0.14/ft | [FWS PVCA-0406](https://www.freshwatersystems.com/products/clear-flexible-pvc-tubing-1-4-id-x-3-8-od) | The 12 visible "green" runs in the .mmd (wall-port→valve, pump loops, bag runs, nozzle lines). 1/4" ID over the stem-barb's 1/4" barb. NSF-51 + FDA, 1/16" wall, 55 psi @ 68°F. $0.19/ft (10 ft) → $0.14/ft (100 ft roll). Length estimate below. |
| Flavor | Black 1/4" OD LLDPE tube, NSF-51 (neoFlo LLDPE4-BLACK) | ~7 ft | $0.12/ft | [FWS LLDPE4-BLACK](https://www.freshwatersystems.com/products/black-1-4-od-lldpe-polyethylene-tubing) | The grey manifold-internal runs in the [.mmd](fluid-topology-manifold.mmd) — every valve↔Y and Y↔Y push-connect hop. PTC fittings can't mate collet-to-collet, so each of the ~21 internal hops is a short rigid 1/4" OD jumper (~2 m/unit). Shares the Kitchen build's existing black-LLDPE roll ([../../hardware/purchases.md](../../hardware/purchases.md) order WEBFWS100673540, ACQUIRED — its 100 ft of 1/4" black LLDPE is "bulk stock for the flavor side / manifold runs"). neoFlo LLDPE, NSF 51 + FDA, push-connect. $0.12/ft (100 ft). |
| Flavor | neoFit flow-control bulkhead, 1/4" tube, black acetal (ABCVU44-E) | 1 | $4.39 | [FWS ABCVU44-E](https://www.freshwatersystems.com/products/neofit-acetal-black-flow-control-bulkhead-1-4-tube) | In the enclosure wall on the Lillium clean-water feed; an adjustable flow-control valve — the screw throttles the feed down so the manifold runs at its low (<10 PSI) working pressure. Push-connect 1/4", bulkhead-mount, acetal + food-grade EPDM, NSF 51/61, FDA, 150 psi @ 68°F, black. $4.39 single / $4.34 per 10. |
| Flavor | Supply Depot 3/8" red BiB connector | 2 | $10.00 | [B0DMFK9B6P](https://www.amazon.com/dp/B0DMFK9B6P) | Optional commercial-syrup input — one per channel (feeds V-K-A, V-K-B), so two distinct bag-in-box syrups. Same part as the Kitchen build ([../../hardware/bom.md](../../hardware/bom.md) §8). Snaps onto a commercial syrup bag's red fitment; output is a 3/8" **male** hose barb. Prime, $19.99/2-pack ($10.00/ea) — one 2-pack covers both channels. An "NSF" mark is molded on the collar but the listing states no cert — treat as unverified. |
| Flavor | Eldon James C6-4BN 3/8" × 1/4" nylon reducing coupler, black | 2 | $0.75 | [FWS C6-4BN](https://www.freshwatersystems.com/products/3-8-x-1-4-tube-id-nylon-reduction-coupler-black) | Steps each BiB leg from the connector's 3/8" barb down to the 1/4" clear PVC into V-K-A/V-K-B. Tube-ID barb both ends, 6/6 nylon, 150 psi @ 70°F. **Cert caveat:** the only food-defensible 3/8→1/4 barbed reducer found — Eldon James nylon (generally USP-VI / animal-free) — but no printed NSF/FDA on the listing; verify the cert sheet if a documented cert is required. Nylon is acid-sensitive (fine for diluted syrup). $0.75/ea (bag of 10 = $7.31). |
| Flavor | Food-grade 3/8" ID silicone tube stub + worm-gear clamps | ~6 in | — | [B089YGDB55](https://www.amazon.com/dp/B089YGDB55) | A short stub per channel bridges the connector's 3/8" male barb to the reducer's 3/8" male barb (two males can't mate directly), clamped. Draws from the Kitchen build's JoyTube 3/8" ID × 1/2" OD food-grade silicone (bom.md §5, ACQUIRED); ~3 in/channel + a worm-gear clamp on each push-on barb joint. |

## Clear-PVC length — ~13 ft/unit (estimate)

The enclosure is not designed yet (see [`README.md`](README.md) "Not designed"), so these are routing estimates from component sizes and a small under-sink envelope, not measured runs:

| Clear run group | Count | Est. each | Subtotal |
|---|---:|---:|---:|
| Wall-port → valve (Lillium, Hopper, BiB A, BiB B) | 4 | ~0.25 m | ~1.0 m |
| Pump loops (Y ↔ pump) | 4 | ~0.12 m | ~0.5 m |
| Bag runs (Y ↔ bag spout) | 2 | ~0.25 m | ~0.5 m |
| Nozzle / flavor lines (valve → through-counter faucet) | 2 | ~0.6 m | ~1.2 m |
| **Routed subtotal** | | | **~3.2 m** |
| Cut waste + service slack (~25%) | | | ~0.8 m |
| **Per unit** | | | **~4 m ≈ 13 ft** |

A 100 ft roll covers a 3–10 unit batch.

## Notes

- Costs are resolved delivered single-unit where purchased; FWS catalog unit prices get shipping + tax allocated at order time, per the Kitchen `bom.md` pattern.
- Dimensions are the manufacturer listing's; real measurements pending the physical units.
