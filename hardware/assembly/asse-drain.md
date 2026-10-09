# ASSE 1022 faucet drain

Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible.

The Multiplex 19-0897 vent discharges through a separate white [4](DRAIN_OD) mm OD LLDPE tube. Its square-cut end is inside the gooseneck's round chamber. A separate bottom-center opening discharges over the sink bowl; two retained 85A bungs contain the chamber. The beverage face retains two symmetric flavor outlets above its soda outlet.

## Parts

| Part | Specification and source | Quantity |
| --- | --- | --- |
| DRAIN bulkhead | Black neoFit ABU44M-E, [4](DRAIN_OD) mm tube, M[15](DRAIN_THREAD_D) × [1.5](DRAIN_THREAD_PITCH) panel barrel, [FWS](https://www.freshwatersystems.com/products/neofit-acetal-black-bulkhead-connector-4mm-5-32-tube) | 1 |
| Vent hose adapter | Black neoFit ATBC44-E, 1/4-inch hose barb × 1/4-inch stem, [FWS](https://www.freshwatersystems.com/products/neofit-acetal-black-stem-barb-connector-1-4-stem-x-1-4-barb) | 1 |
| Elbow | Black neoFit AEU44-E, 1/4-inch tube × 1/4-inch tube, [FWS](https://www.freshwatersystems.com/products/neofit-acetal-black-union-elbow-1-4-tube-x-1-4-tube) | 1 |
| Metric reducer | Black neoFit ARD4M4-E, 4 mm tube × 1/4-inch stem, [FWS](https://www.freshwatersystems.com/products/neofit-acetal-black-stem-reducer-4mm-5-32-tube-x-1-4-stem) | 1 |
| Drain tube | White neoFlo LLDPE4M-WHITE, [FWS](https://www.freshwatersystems.com/products/white-4mm-od-lldpe-polyethylene-tubing). The [neoFlo manufacturer sheet](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf) specifies [4](DRAIN_OD) mm OD, [2.5](DRAIN_ID) mm ID, [0.75](DRAIN_WALL) mm wall and R[25](DRAIN_BEND_R) minimum bend radius; W denotes white. | Appliance return and one continuous umbilical/faucet run |
| Vent hose | Clear neoPure PVCA-0406-FT-C, 1/4-inch ID × 3/8-inch OD PVC, [FWS](https://www.freshwatersystems.com/products/clear-flexible-pvc-tubing-1-4-id-x-3-8-od), fully covering each barb on the straight downward vent connection | 1 cut-to-fit hose |
| Hose clamps | Basics WC-316SS-04, SAE #4, 316 stainless, 1/4–5/8-inch range, [FWS](https://www.freshwatersystems.com/products/stainless-steel-hose-clamp-316-sae-4-1-4-5-8); one over each hose barb | 2 |
| Identification | White rectangular DRAIN ring with black lettering; white DRAIN collar bored 4.25 mm | 1 each |

The black bulkhead matches the existing rear fittings. Its 4 mm socket distinguishes the white drain from the white 1/4-inch TAP supply by size. The faucet tube remains one continuous piece inside the sleeve and shell.

## Assembly

1. Seat the ASSE chain in its keyed cradle with the vent facing down. Fit the straight clear hose downward onto the upward-facing ATBC44-E barb. Fully cover both barbs and clamp each end. Confirm an open, unkinked bore and retain access to release both connections.
2. Insert the ATBC44-E stem into the elbow to its marked full insertion depth. Point its free socket aft and insert the ARD4M4-E stem. Mark and fully insert the internal [4](DRAIN_OD) mm return into the reducer and bulkhead. Form two tangent R[25](DRAIN_BEND_R) half-turns in the rear space: the first turns aft to fore while rising east, and the second turns fore to aft while rising west. Finish with the two R[25](DRAIN_BEND_R) arcs of the S bend into the middle rear row. Keep the white tube clear of the foam cap, pump, DATA jack and flavor returns. The flavor-B return rises [7.5](FLAVOR_B_RETURN_RISE) mm and passes 13 mm west of its rear-union column around the black adapters; its front support and both rear collets retain their positions. Its rear return bends hold R25.4. No fitting can pull the hose tight or collapse its bore.
3. Make up the DRAIN bulkhead through its white rectangular chip. The 6 mm panel stack fits its [8.1](DRAIN_PANEL_BARREL) mm bare barrel. Tighten only enough to hold the chip and fitting without distorting the printed wall; maximum nut torque from the neoFit sheet is 1.1 ft lb.
4. Feed the white 4 mm tube between the two flavors through the counter stack and shell base. Its R25-or-larger bends pass forward of the two flavor unions and gather against the cold-line foam under the common sleeve. Put the 4.25 mm bore DRAIN collar on the bare tail.
5. With the tip separate, follow [vent seal assembly](/hardware/printed-parts/faucet/asse-vent-seals/README.md). Pre-thread the upstream bung, then the distal bung, onto the three beverage tubes and four peeled, continuously insulated conductors. Keep D out of the tip while seating the distal bung. Feed D through the preloaded upstream bung and set its square cut a nominal 8.0 ± 0.2 mm beyond that bung's flange front. Advance the precut D tube and upstream bung together at that mark, seating the bung with the curved perimeter pusher. Rotate the tip socket over the base plug while feeding tube slack. Trim only the three beverage outlets flush at their symmetric face.
6. Leave all four appliance-end tails free. Connect white 4 mm DRAIN to DRAIN and the larger white supply to TAP. Place the nominal 1-3/8-inch mounting-hole center no more than 50.8 mm behind the bowl edge and aim the fixed faucet within 10° of straight into the bowl. Confirm the complete separate bottom opening is over the bowl, exposed and unobstructed. [Native vent evidence](/hardware/printed-parts/faucet/vent-qualification/README.md) records the installation envelope.


## Engineering qualification

The CAD establishes routing, bend radii, separate outlets and mounting clearance. It does not establish vent capacity. The smaller bore and rise can add backpressure; a wet line can also retain a water column. Release requires manufacturer confirmation or a fixture-based fault-discharge qualification of the complete installed route. Measure upstream pressure, vent flow and vent backpressure through dry, water-filled and partially obstructed runs at the specified supply limits, then show that the device's required backflow protection and discharge are preserved. Applicable approval and installation limits must supply the acceptance values before this test is treated as qualification.

Printed fit, support removal, tube feeding and repeatable assembly remain physical checks on the next print. Existing mechanical acceptance records retain their original scope in [mechanical qualification](/hardware/mechanical-qualification/README.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_asse_drain_sync.py`
