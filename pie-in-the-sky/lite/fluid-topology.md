# Lite Edition — Flavor Manifold Topology

*Pie-in-the-sky, not roadmap.*

The Lite reuses the integrated flavor manifold defined in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) (valve set, Y-junctions, numbered tube segments, operations) and its diagram [`/hardware/topology/fluid-topology-manifold.mmd`](/hardware/topology/fluid-topology-manifold.mmd). This doc records only where the Lite diverges, and which tube segments run clear vs stay push-to-connect.

## Divergences from the integrated manifold

**No chill — the bag is a room-temperature reservoir, not a chilled buffer.** Every divergence below follows from this.

**BiB dispenses direct, with no bag pre-load.** In the integrated build, BiB feeds the bag (`BiB → pump → bag`) so the syrup chills before dispense. With no chill there is no reason to decant BiB into the internal bag — a room-temperature BiB and a room-temperature bag deliver identical syrup. So BiB dispenses straight through: `BiB → V-K → pump → V-G/V-J → nozzle`. The segment map already wires this path; it is an operations change, not a re-plumb — open the nozzle gate (`V-G`/`V-J`) where the integrated table opens the bag-fill gate (`V-F`/`V-I`). Drop "Fill from BiB → Bag" from the op table; add "Dispense from BiB." The internal bag becomes the hopper reservoir only; a BiB customer bypasses it. BiB and the hopper-filled bag are alternative sources into pump→nozzle, not a single load-the-bag path.

**Clean water comes from the Lillium.** `V-A`'s upstream is the customer's Lillium water outlet entering a rear-panel push-connect port, not internal house tap water. The integrated build's flow regulator (segments 1–2, sized for house-line pressure) is not carried over.

**No carbonator path through this manifold.** As in the integrated build, carbonated water reaches the faucet from the customer's Lillium and never passes through the flavor manifold; the flavor lines meet it only at the nozzle.

## Tube material per segment

The enclosure is transparent and the customer runs prime, refill, and clean by eye, so the segments the user reads run in **clear NSF-51 PVC**; the hidden manifold routing stays **JG push-to-connect on LLDPE**. Segment numbers reference the base topology.

**Clear (visible)** — clear PVC, joined to the PTC manifold with a JG stem-barb bridge at each takeoff:

| Segments | Run | Why the user reads it |
|---|---|---|
| 21, 34 | `V-G → Nozzle A`, `V-J → Nozzle B` | "Hold PRIME until flavoring reaches the faucet" and "until no air pulses" — watch the color climb and the bubbles clear. |
| 17, 18, 19 / 30, 31, 32 | Bag A / Bag B legs | Fill and draw flow, alongside the bag-collapse gauge. |
| 14, 15 / 27, 28 | Pump A / Pump B loops | *Optional* — only if the pump sits where the flavor pulse is visible. |

**PTC / LLDPE (hidden manifold routing — unchanged from the integrated build):**

- Source selection + channel select: 3–8.
- Internal valve↔Y links: 13, 16, 20, 26, 29, 33.
- BiB internal routing: 10, 11, 12 / 23, 24, 25.

**External, customer-facing (stay push-connect):**

- Clean-water inlet at `V-A`: rear-panel JG 1/4" push-connect, Lillium line in, bridged to the internal run with a JG stem-barb.
- BiB inlets (segments 9, 22), if BiB is kept: the customer's BiB barb line.

## Bore per line

- **Flavor lines (visible, tiny dose):** 1/8" ID clear PVC — minimize dead volume and prime time.
- **Clean-cycle / bag-fill water:** 1/4" ID — flush flow, dead volume not a concern.

## Candidate parts

- Clear flavor tube: neoPure Clear PVC 1/8" ID × 1/4" OD (`PVCA-0204`), NSF 51, 68 psi.
- Clear clean-cycle tube: neoPure Clear PVC 1/4" ID × 3/8" OD (`PVCA-0406`), NSF 51, 55 psi.
- PTC↔barb bridge: JG Stem Barb Connector 1/4" stem × 1/4" barb (`PI250808S`), or NSF-51 neoFit `ATBC44`.
- Valves stay PTC (the integrated Beduan solenoids), so the only barbs are the stem-barb bridges at the visible takeoffs.

## Open

- Keep BiB on the Lite as a direct source, or drop `V-K-A`/`V-K-B` entirely?
- Pump placement — visible (pump loops go clear) or hidden (stay PTC)?
- Does dropping the flow regulator hold, or does the Lillium outlet need its own gate at `V-A`?
