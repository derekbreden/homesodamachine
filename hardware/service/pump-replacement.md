# Pump replacement

Both Kamoer KPHM600 pumps leave the appliance together in `enclosure-pump-cartridge`.
The customer replaces complete prepared pumps: each replacement has two straight 1/4" LLDPE tubes
already fitted in its pump tubing and clamped there by the pump head's own housing. The four
pump tees, front-top's collet plate, the valves, the tubing and front-top's
magnets remain installed during pump changes.
No enclosure quadrant comes off for a pump change.

[4](JOINT_COUNT) flavor joints separate when the cartridge is pulled straight forward.
Each smooth Ø[6.35 mm](TUBE_OD) pump tube passes front-top's collet plate and stands bottomed
in the branch collet of a John Guest PP0208E pump tee. Pulling the cartridge drags each tube
and its tee forward the collet's [1.5 mm](TEE_STROKE) stroke while the plate holds the collet
in; at the end of the stroke the collet is pressed home and the tube draws out. The
tees stay connected to their upper tubes and hairpins. Water, CO2 and carbonated-water
connections stay closed, so the carbonator remains connected and charged.

This is the service procedure for the built dock geometry. Pump-holder fit has its
[recorded physical acceptance](/hardware/reference/kamoer-kphm400/physical-fit.json).
The complete dock's release and insertion forces, sealing, retention under pressure,
cleanability and endurance remain to be established on the assembled hardware; those
properties do not follow from the CAD fit.

## What leaves the bay

| Rides out on `enclosure-pump-cartridge` | Stays in the appliance |
|---|---|
| [2](CART_PUMPS) complete pumps, their four clamped LLDPE tubes and the fitted top clamp | [4](PUMP_TEES) PP0208E pump tees, each in its bore through front-top's tee wall behind the collet plate |
| The contact pair's female half, its four motor leads and the two Faston pairs | The male contact half and fixed J13 ribbon behind the bulkhead |
| The cartridge's [4](CART_MAGNETS) printed-in SB443-IN magnets | Their [4](CART_MAGNETS) printed-in mates in front-top |
| | The pump tees' upper tubes and hairpins, and the source tees Y-A and Y-B: [6](BOX_TEES) PP0208E tees in all |
| | [8](TRAY_VALVES) valves on the two front-top trays and [3](CAP_VALVES) valves in the cold core's cap |
| | All other tubing, the funnel, display and cold core |

Each pump tee's branch stands in a bore through front-top's tee wall behind the collet plate.
The bore holds the tee in X and Z and lets it slide along Y: the plate stops it at the fore end
of its collet stroke, and the seated cartridge's bottomed pump tube holds it at connected. The
tee's upper collet takes a short tube to its fore valve and its lower collet one LLDPE hairpin to its rear valve; both
tubes flex with the tee's travel. These parts stay assembled during a customer pump change.

## The four separating joints

| Joint | Cartridge end | Staying end | Air-purge states |
|---|---|---|---|
| `fluid-11` | pump A suction tube | pump tee Y-C branch collet | 1 and 2 |
| `fluid-12` | pump A discharge tube | pump tee Y-D branch collet | 1 and 2 |
| `fluid-21` | pump B suction tube | pump tee Y-F branch collet | 3 and 4 |
| `fluid-22` | pump B discharge tube | pump tee Y-G branch collet | 3 and 4 |

In service each tee stands at **connected**: its branch collet extended with its nose on the
collet plate's release face and the pump tube bottomed at the tee's own stop. The collet grips
the tube and holds it against pressure. Pushing the cartridge in passes the four tube tips
through the plate's holes into the collets; the tips bottom in the tees and push each tee back
to connected. The two magnet columns then draw the cartridge home, and their meeting poles set
its final position with [0.25 mm](DOCK_BODY_GAP) of air between the broad faces; the magnets
seat the cartridge and do not hold the tubes. A straight pull parts the magnets, the contact pair and the four collet joints while the tees
and the tubing stay in the machine.

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
with a stalled or faulted pump remains unqualified: it requires a demonstrated
depressurization route that establishes the actual valve behavior and residual
pressure at both ports of the failed pump
([pump dock evidence](/hardware/printed-parts/enclosure/pump-dock/README.md#engineering-evidence)).
A timed command, an accepted PWM, the topology and the Dry timer do not establish
rotation, flow or venting.

1. **Establish the qualified depressurized service state, then disconnect power.**
   Use Dry mode for fluid clearing under the pump and valve conditions covered by
   the depressurization qualification. Leave the collection container under the
   faucet. Proceed only with the flavor dock depressurized under those qualified
   conditions; elapsed time alone does not establish that condition. Then unplug
   the appliance and confirm that its display is dark and both pumps have stopped.

2. **Withdraw the depressurized cartridge.** With the release condition above
   satisfied, brace the appliance and pull evenly using the cradle's
   hand pockets. Keep the cradle on its bay floor and draw it straight forward. Each
   tee slides its [1.5 mm](TEE_STROKE) stroke until the collet plate holds its collet
   in, and the four tubes draw out together as the electrical contacts separate. If
   resistance becomes uneven or a tube remains caught, stop and return the cartridge
   to its seat; do not twist it or use a pump as a lever.

3. **Inspect the open dock.** Wipe any residual syrup from the four plate holes and
   tube ends with a clean damp cloth. Through each hole the collet face must be clean,
   free of debris and undamaged. Wipe the electrical contact faces and magnet faces
   dry. A damaged collet or a chipped magnet requires appliance service; it is not a
   customer replacement item.

4. **Replace the complete pumps.** Pull each Faston receptacle by its insulated body,
   then remove the [2](CAP_SCREWS) M3×[60](CAP_SCREW_LEN) clamp screws. Lift the clamp with
   its contact half and leads together, then lift out the pumps. Lower the prepared
   replacements onto the cradle's skirt lands, with all four straight tubes facing
   aft through the cradle's open tube passages. Lower the clamp over both bosses and tighten the screws evenly until the clamp
   seats. If it will not sit flat, lift and reseat the pumps. Do not use screw force to
   correct alignment. Confirm firm pump retention and that no tube touches the cradle.

5. **Reconnect and seat.** Reconnect the Faston pairs to the marked motor tabs: the
   +X crown-groove pair serves pump A and the −X pair serves pump B. Return the leads to
   their grooves below the clamp crown. With power still disconnected, set the cartridge
   on its bay floor and present all four tube tips to the collet plate's holes. Push
   squarely and evenly: the tips enter the tees' collets and bottom, the tees return to
   connected, and the magnets draw the cartridge onto its seat with the front face
   flush. Check the complete perimeter and the electrical contact engagement. The tubes
   must remain straight, and the cartridge must hold its seat when gently pulled.

6. **Re-prime and observe.** Restore power and prime each channel through the funnel-fill
   path, then dispense from each until flow is clean. Inspect around the seated
   cartridge and the bay floor for seepage. Stop and
   disconnect power if a joint leaks, a pump shifts, or the cartridge moves off its seats.

## Factory preparation of replacement pumps

Prepare each pump with the specified BPT tube around the rotor. Pull Kamoer's two
barbed connectors out of the tube ends. Cut two [33.2 mm](TUBE_CUT) tubes from the
machine's black 1/4" LLDPE with a square, burr-free cut, and ease each outer edge so the
tube enters a tee's collet and O-ring without scoring them. Loosen the pump head's
housing, push one tube into each BPT end and snug the housing.

Seat both pumps in the cartridge under the closed cap, set the printed tube setting
jig on the cartridge's flat rear face and slide each tube until its tip meets
its jig stop: all four tips at the seated datum, [14.925 mm](TIP_FROM_CARTRIDGE) aft of
that face and enclosure Y[97.19 mm](TIP_Y) when seated, where they bottom in the tees.
Each tube then stands [20.026 mm](TUBE_PROJECTION) beyond the pump's barb plane with
[13.149 mm](TUBE_HELD) inside the BPT tube. Tighten the housing fully so it clamps the
BPT tube around both LLDPE tubes, recheck all four tips against the jig, then pull each
tube firmly by hand and confirm it does not slip. Check smooth wet surfaces, clean
bores, pump-end sealing and all four tip positions before supplying the replacement set.
The customer receives the complete prepared pumps and does not cut, trim or transfer
the tubes.

## Output condition

- Both complete pumps sit firmly on their cradle lands under the seated clamp.
- Both Faston pairs are connected and all four leads remain below the crown.
- All four straight tubes pass the collet plate and bottom in their pump tees, each tee
  at connected; the cartridge sits on its meeting magnet poles with its front face
  flush, and the contact pair is engaged.
- The pump tees, collet plate, upper tubes, hairpins and front-top's magnets
  remain installed in the appliance.
- Both channels prime and dispense with no observed dock or pump-end seepage.
- The water, CO2 and carbonated-water connections remain closed.

Dry-run wear of the BPT tubing and a customer return/drain procedure remain separate
service questions. This pump procedure does not depressurize the carbonator for shipping.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
