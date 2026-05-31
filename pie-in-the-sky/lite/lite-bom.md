# Lite Edition — Bill of Materials

*Sourcing list for the Lite edition — Amazon Prime ASINs and resolved delivered single-unit costs (product + shipping + tax). Order math lives in the shared ledger [../../hardware/purchases.md](../../hardware/purchases.md).*

| Subsystem | Item | Qty | Unit | Source | Notes |
|---|---|---:|---:|---|---|
| Flavor | Platypus Hoser 1 L hydration reservoir (Fast Flow Valve) | 2 | $25.62 | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | Flavor reservoir, one per pocket. Hangs spout-down from its built-in top loop; the threaded outlet takes Platypus drink tubes / closure caps and ships with the hose, so it carries the lid-to-hose adapter. 133 × 292 mm (5.25 × 11.5 in), per the listing. Purchased — order 112-4566389-9910625 (2026-05-30), 2 @ $23.89 = $47.78 + $3.46 tax = $51.24, $0 Prime shipping ($25.62/ea delivered). |
| Flavor | Beduan 12 V 1/4" solenoid valve (NC) | 12 | $9.64 | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | Manifold valves V-A … V-K-B per [fluid-topology-manifold.mmd](fluid-topology-manifold.mmd); same 12-valve set and part as the Kitchen build ([../../hardware/bom.md](../../hardware/bom.md) §8). 1/4" push-connect ports — the clear-PVC runs land here via a tube insert. |
| Flavor | John Guest PP2308E two-way divider, 1/4" | 10 | $3.083 | [FWS](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | Manifold Y-junctions Y-A … Y-KB per the .mmd; same 10-divider set and part as the Kitchen build (bom.md §8). Black PP, NSF 51+61, 1/4" push-connect. FWS-sourced, not Amazon — $3.083/ea from a bag of 10. |
| Flavor | 1/4" OD tube insert (clear-PVC stiffener) | 12 | ~$0.09 | [B0FM77LLM1](https://www.amazon.com/dp/B0FM77LLM1) (confirm ID) | One per manifold takeoff (6 valve ports + 6 Y ports) — stiffens the soft PVC so it push-connects into each 1/4" PTC port, replacing a stem-barb bridge. The repo's Siptenk 1/4" stiffener (bom.md §8) is sized for LLDPE's ~0.17" ID; the thicker-wall 1/8"-ID PVC wants an ID-matched insert. 100-pk, so per-unit cost is negligible; buy spares. |
| Flavor | Clear food-grade PVC, 1/8" ID × 1/4" OD (PVCA-0204 class) | ~13 ft | ~$0.50/ft | ASIN to confirm; Sealproof family ([B07D9DK94V](https://www.amazon.com/dp/B07D9DK94V) is the repo's 1/4"ID×3/8"OD variant) or FWS PVCA-0204 | The 12 visible "green" runs in the .mmd (wall-port→valve, pump loops, bag runs, nozzle lines). 1/4" OD for PTC fit. Length is a routing estimate — breakdown below. |

## Valve manifold — fittings + clear-PVC length

The manifold is the same valve/Y set as the Kitchen build — 12 Beduan 1/4" PTC solenoids and 10 JG PP2308E two-way dividers — per [`fluid-topology-manifold.mmd`](fluid-topology-manifold.mmd). The hidden routing between them is 1/4" OD LLDPE on push-connect (grey in the diagram); the runs the user reads through the transparent enclosure are clear PVC (green).

**Clear-PVC-to-manifold joint.** Each clear run lands directly in a valve or Y 1/4" PTC port — the soft PVC is stiffened with a tube insert and pushed in, rather than bridged through a stem-barb adapter. One insert per takeoff: 6 at valve ports (V-A, V-B, V-K-A, V-K-B, V-G, V-J) and 6 at Y ports (Y-C, Y-D, Y-F, Y-G, Y-E, Y-H) = 12. The far end of each run (pump, nozzle, bag spout, or wall-port barb) is not a push-fit and needs no insert. Standardizing on 1/4" OD PVC keeps every manifold joint a 1/4" PTC push-fit at one insert size.

**Clear-PVC length — ~13 ft/unit (estimate).** The enclosure is not designed yet (see [`README.md`](README.md) "Not designed"), so these are routing estimates from component sizes and a small under-sink envelope, not measured runs:

| Clear run group | Count | Est. each | Subtotal |
|---|---:|---:|---:|
| Wall-port → valve (Lillium, Hopper, BiB A, BiB B) | 4 | ~0.25 m | ~1.0 m |
| Pump loops (Y ↔ pump) | 4 | ~0.12 m | ~0.5 m |
| Bag runs (Y ↔ bag spout) | 2 | ~0.25 m | ~0.5 m |
| Nozzle / flavor lines (valve → through-counter faucet) | 2 | ~0.6 m | ~1.2 m |
| **Routed subtotal** | | | **~3.2 m** |
| Cut waste + service slack (~25%) | | | ~0.8 m |
| **Per unit** | | | **~4 m ≈ 13 ft** |

The nozzle lines dominate and carry the most uncertainty: if the hidden riser up to the faucet is run in LLDPE rather than clear PVC, drop ~1 m (→ ~10 ft). A 100 ft roll covers a 3–10 unit batch.

## Notes

- Unit is the resolved delivered cost (product + shipping + tax); full order math is in the shared ledger [../../hardware/purchases.md](../../hardware/purchases.md).
- Dimensions are the manufacturer listing's; real measurements pending the physical units.
