# ASSE 1022 faucet drain

Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible.

The Multiplex 19-0897 vent discharges through a separate white
[4](DRAIN_OD) mm OD / [2.5](DRAIN_ID) mm ID LLDPE tube. Its square-cut end is
inside the faucet tip's unsealed pocket. A round Ø4 mm underside opening
provides a visible major-fault drip over the sink bowl. Plain printed guide
walls carry the continuous beverage tubes and insulated conductors; no
additional drain gasket or bung is fitted. Incidental escape into the faucet
housing is accepted during that fault.

## Parts

| Part | Specification and source | Quantity |
| --- | --- | --- |
| OVER bulkhead | Black neoFit ABU44M-E, [4](DRAIN_OD) mm tube, M[15](DRAIN_THREAD_D) × [1.5](DRAIN_THREAD_PITCH) panel barrel, [FWS](https://www.freshwatersystems.com/products/neofit-acetal-black-bulkhead-connector-4mm-5-32-tube) | 1 |
| Direct vent sleeve | [Printed TPU 85A adapter](/hardware/printed-parts/asse-drain-adapter/README.md), 6.10 mm barb socket / 3.80 mm tube socket, 14 mm tube insertion; unprinted fit candidate | 1 |
| Sleeve ties | Existing 4-inch nylon ties, 2.54 mm wide; one on each inserted part in its own recessed land | 2 |
| Drain tube | White neoFlo LLDPE4M-WHITE, [FWS](https://www.freshwatersystems.com/products/white-4mm-od-lldpe-polyethylene-tubing). The [neoFlo manufacturer sheet](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf) specifies [4](DRAIN_OD) mm OD, [2.5](DRAIN_ID) mm ID, [0.75](DRAIN_WALL) mm wall and R[25](DRAIN_BEND_R) minimum bend radius; W denotes white. | Appliance return and one continuous umbilical/faucet run |
| Identification | White rectangular OVER ring with black lettering; white OVER collar bored 4.28 mm | 1 each |

The black bulkhead matches the existing rear fittings. Its 4 mm socket distinguishes the white drain from the white 1/4-inch TAP supply by size. The faucet tube remains one continuous piece inside the sleeve and shell.

## Assembly

1. Work on the open back-top. The ASSE, its vent sleeve and the OVER bulkhead all belong to back-top, and the connected vent rides with it as the box closes. Make up the OVER bulkhead through its white rectangular chip at the middle-left rear station ([enclosure mechanical §2](/hardware/assembly/enclosure-mechanical.md#2-populate-the-rear-connection-face)). The 6 mm panel stack fits its [8.1](DRAIN_PANEL_BARREL) mm bare barrel. Tighten only enough to hold the chip and fitting without distorting the printed wall; maximum nut torque from the neoFit sheet is 1.1 ft lb.
2. Seat the ASSE's two hexes in back-top's integral upper seat, with its vent pointing down. Snap the lower cap into the seat, keeping the vent in its bottom slot. Fit the [TPU vent elbow](/hardware/printed-parts/asse-drain-adapter/README.md) over the barb below the hex, with its small socket pointing aft. Close its two recessed tie lands around the barb and the marked 14 mm tube insertion.
3. Connect the short white tube directly to OVER. The elbow and rear fitting remain together on back-top. Keep the atmospheric passage open and leave both tie heads accessible.
4. Feed the white 4 mm tube between the two flavors through the counter stack and shell base. Its R25-or-larger bends gather against the cold-line foam under the common sleeve. Put the 4.28 mm bore OVER collar on the bare tail.
5. With the tip separate, feed the continuous S/F1/F2 tubes and four
   continuously insulated display conductors through its printed guides.
   Advance D through the upstream guide so its square-cut end projects into
   the open pocket, clear of the wall and other tubes. The downstream guide
   has no D passage. Close the curved shell joint while feeding tube slack.
   Trim only the three beverage outlets flush at their symmetric face.
6. Leave all four appliance-end tails free. Connect white 4 mm OVER to OVER
   and the larger white supply to TAP. Aim the fixed faucet into the bowl and
   confirm the complete Ø4 mm underside hole is over the bowl, exposed and
   unobstructed.



## Evidence scope

The [current geometry reading](/hardware/printed-parts/faucet/vent-qualification/simple-drip-check.json)
checks an open pocket-to-hole connection, nominal tube clearance and the
retained joint/dispense face. The Ø4 mm hole has 2.56 times the nominal area
of the Ø2.5 mm tube bore. That is a geometric comparison, not a flow rating.
The direct sleeve is an unprinted fit candidate; socket seating, zip-tie
retention and water tightness have no acceptance record. Physical drip behavior
and the complete rising vent route's capacity are unmeasured. The separate beverage flow remains inside the tubes and donor.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_asse_drain_sync.py`
