# Pump replacement

Both Kamoer KPHM600 pumps leave the appliance together in `enclosure-pump-cartridge`.
The customer replaces complete prepared pumps: each replacement has two smooth, machined natural PP-H Polystone P flanged stems
already fitted and secured in its pump tubing. The fixed TPU junctions, compound
returns, flat keepers, dry cradles and closing covers, and magnetic mounts remain installed
during pump changes.
No enclosure quadrant comes off for a pump change.

[4](JOINT_COUNT) flavor joints separate when the cartridge is pulled straight forward.
Each smooth Ø[6.35 mm](TUBE_OD) stem slides out of a stationary TPU socket. The four
printed junctions remain connected to their upper and lower valve paths behind the
receiver wall. Water, CO2 and carbonated-water
connections stay closed, so the carbonator remains connected and charged.

This is the service procedure for the built dock geometry. Pump-holder fit has its
[recorded physical acceptance](/hardware/reference/kamoer-kphm400/physical-fit.json).
The complete dock's sealing, insertion and withdrawal forces, retention under pressure,
cleanability and endurance remain to be established on the assembled hardware; those
properties do not follow from the CAD fit.

## What leaves the bay

| Rides out on `enclosure-pump-cartridge` | Stays in the appliance |
|---|---|
| [2](CART_PUMPS) complete pumps, their prepared flanged stems and the fitted top clamp | [4](RECEIVERS) permanent TPU junctions in the rigid wall and [4](KEEPERS) locked flat interior keepers |
| The contact pair's female half, its four motor leads and the two Faston pairs | The male contact half, fixed J13 ribbon and ridge-wall cable clip |
| The cartridge's positively retained SB443-IN magnets | Their positively retained mates in front-top |
| | [4](RETURNS) permanent compound TPU returns, their interlocking dry cradles and closing covers, and the [2](BOX_TEES) commercial source tees |
| | [8](TRAY_VALVES) valves on the two front-top trays and [3](CAP_VALVES) valves in the cold core's cap |
| | All stationary straight junction-to-valve and return links, other tubing, the funnel, display and cold core |

The wall locates each TPU receiver in X/Z. Its recessed collar bears in the wall;
one flat keeper per receiver slides down the interior face and captures its groove in Y.
Each keeper is locked in its wall guides at the factory by one M3×8 screw with a
Ø7 × 0.5 mm DIN 125A washer. The screw enters from the empty pump bay through
the recessed wall opening and threads into an RX-M3Sx4.0 insert in the keeper's
local 5 mm boss. These locks stay installed during a customer pump change.
The junction's rear keys prevent rotation. The return's broad flexible keys interlock
with its PET-GF cradle and closing cover. The straight junction-to-return link is captured
between supported socket stops and held against bowing by its dry guide. The keeper
has running clearance around the neck and does not position the junction across its
axis. These permanent parts stay seated during a pump change.

## The four separating joints

| Joint | Cartridge end | Staying end | Air-purge states |
|---|---|---|---|
| `fluid-11` | pump A suction stem | TPU junction Y-C inlet | 1 and 2 |
| `fluid-12` | pump A discharge stem | TPU junction Y-D inlet | 1 and 2 |
| `fluid-21` | pump B suction stem | TPU junction Y-F inlet | 3 and 4 |
| `fluid-22` | pump B discharge stem | TPU junction Y-G inlet | 3 and 4 |

The socket entrances are TPU funnels leading to tight straight sealing lands. Dedicated
outboard rigid stop lands on the receiver wall bear against the lower cradle to
establish its final position, while the broad aft faces retain [0.25 mm](DOCK_BODY_GAP) clearance. The prepared stem tips enter
the sockets together. The magnets hold that seated position; the TPU receiver is not
a cartridge stop. A straight pull parts the magnets, contact pair and four slip joints
without moving the permanent junctions, returns or their straight tube links.

## Dry mode

Run the four canonical air-purge states before opening the dock. Both pumps run forward
and each open valve carries flow from inlet to outlet.

| # | State | Open | Pump | Path |
|---|---|---|---|---|
| 1 | Air Purge In → Reservoir A | V-B, V-C, V-F | A | funnel → crossbar → V-C → `fluid-9` → Y-C → pump A → Y-D → V-F → reservoir A |
| 2 | Air Purge Through A | V-B, V-C, V-G | A | same inlet, then Y-D → `fluid-17` → V-G → faucet tip |
| 3 | Air Purge In → Reservoir B | V-B, V-D, V-I | B | mirror of 1 into reservoir B |
| 4 | Air Purge Through B | V-B, V-D, V-J | B | mirror of 2 to the faucet tip |

Place a container under the faucet for expelled air and residual concentrate. With
the pumps rotating and moving fluid, these states sweep all four separating joints;
a film or a remaining drop still needs wiping when the cartridge is out. An elapsed
cycle does not verify pump rotation, dry lines or depressurization of both pump ports.
The states are specified in
[`fluid-topology.md`](/hardware/topology/fluid-topology.md#operations--valve-states).

## Procedure

The release steps below apply to a qualified, depressurized flavor dock. Release
with a stalled or faulted pump remains unqualified pending the isolated per-port
vent test in the [pressure and retention review](/hardware/printed-parts/enclosure/pump-dock/pressure-retention-review.json).
The test must establish the actual valve behavior and residual pressure for the
service state; the topology and Dry timer do not establish them.

1. **Establish the qualified depressurized service state, then disconnect power.**
   Use Dry mode for fluid clearing under the pump and valve conditions covered by
   the completed port-vent qualification. Leave the collection container under the
   faucet. Proceed only with the flavor dock depressurized under those qualified
   conditions; elapsed time alone does not establish that condition. Then unplug
   the appliance and confirm that its display is dark and both pumps have stopped.

2. **Withdraw the depressurized cartridge.** With the release condition above
   satisfied, brace the appliance and pull evenly using the cradle's
   hand pockets. Keep the cradle on its bay floor and draw it straight forward until
   all four tube ends and the electrical contacts have separated. If resistance becomes
   uneven or a tube remains caught, stop and return the cartridge to its seat; do not
   twist it or use a pump as a lever.

3. **Inspect the open dock.** Wipe any residual syrup from the four socket entrances
   and tube ends with a clean damp cloth. The TPU funnels must remain seated, clear of
   debris and free of cuts, folds or displaced lips.
   Wipe the electrical contact faces and magnet faces dry. A displaced receiver, damaged
   socket or loose magnetic mount requires appliance service; it is not a customer
   replacement item.

4. **Replace the complete pumps.** Pull each Faston receptacle by its insulated body,
   then remove the [2](CAP_SCREWS) M3×[60](CAP_SCREW_LEN) clamp screws. Lift the clamp with
   its contact half and leads together, then lift out the pumps. Lower the prepared
   replacements onto the cradle's skirt lands, with all four straight stems facing
   aft and each integral flange seated in its cradle capture. Lower the clamp over both bosses and tighten the screws evenly until the clamp
   seats. If it will not sit flat, lift and reseat the pumps. Do not use screw force to
   correct alignment. The clamp closes the stem flanges' upward escape; the cradle
   captures their axial load. Confirm firm pump retention and seated flanges.

5. **Reconnect and seat.** Reconnect the Faston pairs to the marked motor tabs: the
   +X crown-groove pair serves pump A and the −X pair serves pump B. Return the leads to
   their grooves below the clamp crown. With power still disconnected, set the cartridge
   on its bay floor and present all four stem tips to the TPU funnels. Push squarely and
   evenly until the rigid stop lands seat and the front face finishes flush. Do not
   count a magnetic snap as full seating: check the complete perimeter, receiver lips
   and electrical contact engagement. The stems must remain straight and the receivers
   must remain seated when the cartridge is gently pulled against its retention.

6. **Re-prime and observe.** Restore power and prime each channel through the funnel-fill
   path, then dispense from each until flow is clean. Inspect the four dock joints and
   the pump-end tubing for seepage. Stop and disconnect power if a joint leaks, a pump
   shifts, or the cartridge moves off its seats.

## Factory preparation of replacement pumps

Prepare each pump with the specified BPT tube around the rotor and two smooth,
machined natural PP-H Polystone P tube stems fitted into its ends. Each stem has a 6.35 mm OD,
4.3 mm bore and integral retention flange. The smooth wet portion enters the TPU;
the flange seats in the cradle outside that sealing region. Verify each bare stem's
flange-to-tip datum in its [setting fixture](/hardware/printed-parts/enclosure/pump-dock/machined-stem.md#factory-fixture-and-review),
then remove it and fit its tail into the BPT. Use calipers to set the BPT end
0.15 mm fore of the flange's fore face, and the
existing 2.54 mm nylon tie center 1.75 mm fore of that same face, toward the pump.
The tie center is 1.60 mm fore of the BPT cut end. These are enclosure Y76.10 mm
and Y74.50 mm respectively; the tie occupies
Y73.23–75.77 mm. Keep its head toward +Z in the open channel. The stem flange has
Ø16 mm outside diameter and a 2.5 mm section, with fore/aft faces at Y76.25/78.75 mm.
Verify that the cradle, with its cap seated, captures the flange axially and closes
its upward escape. The flange bearing supplies the cartridge-withdrawal load path.

Use the printed setting jig against the cartridge's flat rear seating face to verify
all four free tips at [7.75 mm](TIP_FROM_CARTRIDGE) aft of that face. This is enclosure
Y[90.015 mm](TIP_Y) when seated; the modeled flexible-tube start-to-tip projection is
[12.851 mm](TUBE_PROJECTION). Check the flange seats, smooth wet surfaces, clean bores,
pump-end sealing and all four tip positions before supplying the replacement set.
The customer receives the complete prepared pumps and does not machine, cut, trim
or transfer the stems.

## Output condition

- Both complete pumps sit firmly on their cradle lands under the seated clamp.
- Both Faston pairs are connected and all four leads remain below the crown.
- All four straight stems enter seated TPU receivers together; the cartridge is
  flush against its rigid seats and the contact pair is engaged.
- Junction funnels, all four locked keepers, compound returns, dry cradles and covers,
  and magnetic mounts remain fixed in the appliance.
- Both channels prime and dispense with no observed dock or pump-end seepage.
- The water, CO2 and carbonated-water connections remain closed.

Dry-run wear of the BPT tubing and a customer return/drain procedure remain separate
service questions. This pump procedure does not depressurize the carbonator for shipping.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
