# Lite Edition — Bill of Materials

*Sourcing list for the Lite edition — Amazon Prime ASINs and resolved delivered single-unit costs (product + shipping + tax). Order math lives in the shared ledger [../../hardware/purchases.md](../../hardware/purchases.md).*

| Subsystem | Item | Qty | Unit | Source | Notes |
|---|---|---:|---:|---|---|
| Flavor | Platypus Hoser 1 L hydration reservoir (Fast Flow Valve) | 2 | $25.62 | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | Flavor reservoir, one per pocket. Hangs spout-down from its built-in top loop; the threaded outlet takes Platypus drink tubes / closure caps and ships with the hose, so it carries the lid-to-hose adapter. 133 × 292 mm (5.25 × 11.5 in), per the listing. Purchased — order 112-4566389-9910625 (2026-05-30), 2 @ $23.89 = $47.78 + $3.46 tax = $51.24, $0 Prime shipping ($25.62/ea delivered). |
| Flavor | Beduan 12 V 1/4" solenoid valve (NC) | 12 | $9.64 | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | Manifold valves V-A … V-K-B per [fluid-topology-manifold.mmd](fluid-topology-manifold.mmd); same 12-valve set and part as the Kitchen build ([../../hardware/bom.md](../../hardware/bom.md) §8). 1/4" push-connect ports — the clear-PVC runs land here via a tube insert. |
| Flavor | John Guest PP2308E two-way divider, 1/4" | 10 | $3.083 | [FWS](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | Manifold Y-junctions Y-A … Y-KB per the .mmd; same 10-divider set and part as the Kitchen build (bom.md §8). Black PP, NSF 51+61, 1/4" push-connect. FWS-sourced, not Amazon — $3.083/ea from a bag of 10. |
| Flavor | Tube insert, 1/4" OD × 1/8" ID, 316 SS (McMaster 5182K326) | 12 | $5.06 | [5182K326](https://www.mcmaster.com/5182K326/) | One per manifold takeoff (6 valve + 6 Y ports) — stiffens the soft PVC into each 1/4" PTC port. **FWS does not stock a 1/8"-ID insert** (its John Guest TSI inserts are 1/4"-ID-and-up — too fat for the bore), so this is McMaster-sourced. 316 SS for the food/syrup path; leaded-brass [50915K243](https://www.mcmaster.com/50915K243/) ($1.02 ea) is the same geometry but not food-rated. See sourcing notes below. |
| Flavor | Clear flexible PVC, 1/8" ID × 1/4" OD, NSF-51 (FWS PVCA-0204) | ~13 ft | $0.11/ft | [FWS PVCA-0204](https://www.freshwatersystems.com/products/clear-flexible-pvc-tubing-1-8-id-x-1-4-od) | The 12 visible "green" runs in the .mmd (wall-port→valve, pump loops, bag runs, nozzle lines). Confirmed 1/8" ID × 1/4" OD, 1/16" wall, NSF-51 + FDA; $11.54/100 ft. Rated **68 psi @ 68°F** — see the Lillium-feed margin note below. Length is a routing estimate — breakdown below. |

## Valve manifold — fittings + clear-PVC length

The manifold is the same valve/Y set as the Kitchen build — 12 Beduan 1/4" PTC solenoids and 10 JG PP2308E two-way dividers — per [`fluid-topology-manifold.mmd`](fluid-topology-manifold.mmd). The hidden routing between them is 1/4" OD LLDPE on push-connect (grey in the diagram); the runs the user reads through the transparent enclosure are clear PVC (green).

**Clear-PVC-to-manifold joint.** Each clear run lands directly in a valve or Y 1/4" PTC port — the soft PVC is stiffened with a tube insert and pushed in, rather than bridged through a stem-barb adapter. One insert per takeoff: 6 at valve ports (V-A, V-B, V-K-A, V-K-B, V-G, V-J) and 6 at Y ports (Y-C, Y-D, Y-F, Y-G, Y-E, Y-H) = 12. The far end of each run (pump, nozzle, bag spout, or wall-port barb) is not a push-fit and needs no insert. Standardizing on 1/4" OD PVC keeps every manifold joint a 1/4" PTC push-fit at one insert size.

**Sourcing notes (web research, 2026-05-30).**

- **The insert is McMaster, not FWS.** FWS's John Guest tube inserts (TSI family) are all sized for 1/4" tube *ID* and up — body ~2× too fat for the 1/8" bore. The correct 1/4" OD × 1/8" ID geometry is McMaster: **316 SS [5182K326](https://www.mcmaster.com/5182K326/), $5.06 ea** (food-safe — the syrup path) or leaded brass [50915K243](https://www.mcmaster.com/50915K243/), $1.02 ea (same geometry, not food-rated). At 12/unit the food-safe insert is **~$61/unit** — the largest single manifold-fitting line, so worth weighing against the alternative below.
- **PVC pressure margin.** PVCA-0204 is rated 68 psi @ 68°F. The flavor runs are low-pressure and fine; the run that matters is the Lillium clean-water feed (→ V-A) at ~70 PSI, at/over the rating. Either confirm the Lillium output stays under 68 PSI, or run that one line in a thicker-wall clear PVC or in LLDPE.
- **PVC is off-label for John Guest push-fits.** JG approves PE, nylon, and PU tube and endorses inserts for soft/thin-wall tube, but does not list PVC. The insert only keeps the OD round under the collet (JG seals on the OD), so this is low-risk at this duty — but dry-fit a 10-pack and pressure-hold before committing the build.
- **Cleaner alternative if testing disappoints:** JG's native 1/4" OD LLDPE push-fits with no insert ([FWS, ~$0.85/ft](https://www.freshwatersystems.com/products/john-guest-black-1-4-od-lldpe-polyethylene-tubing), NSF-51) — the zero-risk connection, at the cost of the clear-tube look on those runs.

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
