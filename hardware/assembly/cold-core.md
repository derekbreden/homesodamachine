# Cold Core Assembly

Build the insulated core on the bench, then populate its equipment lid. The
closed core is **HSM-0557**. The pump, controller, V-B and junctions complete
**HSM-0003**, which goes into **HSM-0552 refrigeration assembly**. Leave the
free tubing and conductors available for the enclosure connections.

Start with a hydro-tested and passivated carbonator with its qualified
water-inlet jet. Join the finished core to the donor in refrigeration
integration. [Pressure vessel](pressure-vessel.md) · [Water-inlet jet](water-inlet-jet.md) · [Refrigeration integration](refrigerant-loop.md) · [Internal layout in 3D](https://homesodamachine.com/parts#step:cold-core-layout%2Fcold-core-assembly.step)

## Inputs per appliance

Check the per-unit parts list for quantities, stock and fasteners and the
purchase ledger for availability. [BOM](../ledger/bom.md) · [Purchase ledger](../ledger/purchases.md)

| Bench operation | Parts and references |
|---|---|
| Instrument and wind the carbonator | GOORY ACR copper, 3M 425 foil tape, coil mandrel, reed bridge and setting gauge, carbonator and coil probes, reed switches, and the solid green earth lead with its vessel-side ring. [Coil drawing](../cold-core-layout/evaporator-coil-drawing.pdf) · [Reed bridge](../printed-parts/cold-core/reed-bridge/README.md) · [Earth bond](pressure-vessel.md#upper-rim-earth-bond) |
| Prepare the casing | PET-GF shell, equipment lid, bottom cap and B-fill holder. Use the specified M5 closure screws and inserts and the M3 PCB inserts and screws. [Shell](../printed-parts/cold-core/foam-shell/README.md) · [Lid and bottom cap](../printed-parts/cold-core/foam-cap/README.md) |
| Assemble the reservoirs | PETG bodies and caps, TPU perimeter gaskets and liquid/air grips, ASA Aero floats with RC62 magnets, rods, M3 fasteners and the two reservoir reed columns. [Reservoirs](../printed-parts/cold-core/reservoir/README.md) · [Cable assemblies](cable-assemblies.md) |
| Pour and close the core | The specified FSD closed-cell PU kit, mixing supplies, removable masking tape, 3M 425 foil tape and a B-fill tube offcut. The relief assembly uses the specified exterior shroud seal. [Foam-fill trials](../print-tests/foam-fill/README.md) · [Shroud seal](../printed-parts/cold-core/prv-shroud/README.md#subassembly-procedure) |
| Populate the lid | PCB and J10 leads, G Ganen pump and its snap cap, V-B, junctions, and the specified fittings and tubes. [Pump installation](../reference/g-ganen-pump/installation/README.md) · [Electronics bay](electronics-bay.md) · [Internal plumbing](internal-plumbing.md) |

## Procedure

### 1. Dress the carbonator wall, then wind the evaporator coil

This operation takes the **HSM-0004 carbonator** and produces the
**HSM-0554 instrumented carbonator and coil assembly**.

1. Fit the solid green earth lead's closed ring to bare steel on the upper
   vessel rim. Orient the crimp barrel upward and support the lead so it
   cannot load the ring. Leave the free end available for lid threading.
   Record the bond reading before covering the attachment. [Rim attachment](pressure-vessel.md#upper-rim-earth-bond) · [Bond measurement](wiring.md#1-chassis-ground-bonds-single-point-ground-on-the-rear-wall)
2. Fit the DS18B20 flat against bare steel in the winding gap on the west
   flank. Turn its insulated leads along the gap before routing them up.
   Set the carbonator reed bridge with its gauge at the rod-register azimuth.
   Seat the reeds against the steel in their through-pockets. Check the
   float's travel and switching positions while the vessel is accessible.
   [Reed bridge](../printed-parts/cold-core/reed-bridge/README.md) · [Float and reed calibration](../printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration)
3. Rough-form the evaporator winding on the mandrel. Set the final
   right-hand winding and its relief over the reed bridge per EVAP-01.
   Apply the continuous 3M 425 thermal interface to bond the winding to
   the vessel. Form and check both tails against the drawing, including
   each lane's bends, exit station and working length.
   [Coil-forming procedure](handwork.md#bend-copper-around-the-pressure-vessel) · [EVAP-01](../cold-core-layout/evaporator-coil-drawing.pdf)
4. Before closing the foil over the winding's outlet end, bond the DS18S20
   coil probe flat against the copper under the foil. The temperature bus
   feeds the coil probe first, then the vessel-wall probe. Support the
   copper tails and the free leads when moving the assembly.

### 2. Press the casing and PCB inserts

Press RX-M5×9.5 inserts squarely into both faces of the shell until their
mouths are flush. Keep the blind screw-tail passages clear. Press the
RX-M3×5.7 PCB inserts into the equipment lid's integral posts. Keep the
equipment mounts clear for the top closure screws.
[Closure hardware and pilots](../printed-parts/cold-core/foam-cap/README.md#m5-closure-hardware)

### 3. Attach and fill the bottom cap

1. Bolt the open-topped bottom cap to the empty shell. The shell floor
   bounds the pour cavity. Seat every head below the cap's outside face.
   Mask the joint and the outward-open screw pockets.
2. Invert the empty casing onto its open upper rim, with the pour ports
   facing up. Keep the equipment lid and vessels aside. Distribute the
   measured charge through all four ports so each quarter receives foam.
   Keep the air vents clear throughout the pour. Follow the foam kit's
   mixing, working-time and cure instructions.
3. After cure, trim the pour and vent openings flush and remove the
   temporary masks. Foil-patch the openings and screw pocket mouths
   and apply the perimeter band. Set the casing upright with the
   bottom cap still bolted on. [Bottom cavity and ports](../printed-parts/cold-core/foam-shell/README.md#bottom-foam-and-open-body-pour)

### 4. Reservoir subassembly (both, at the bench)

1. Fit the flush liquid and air spools into the matching cap seats.
   The caps and captured grips form **HSM-0568** and **HSM-0569**.
   [Tube grips and air paths](../printed-parts/cold-core/reservoir/README.md#tube-grips-and-air-paths)
2. Check the float slides freely on its rod. Press the reservoir inserts
   into the wall-top bosses, place the perimeter gasket and lower each
   cap over the guide rod. The rod needs end clearance so the gasket can
   seat. Fasten the caps to complete **HSM-0555** and **HSM-0556**.
   [Float and guide installation](../printed-parts/cold-core/magnetic-float/all-aero/installation.md)
3. Prepare the **HSM-0348 J6** and **HSM-0349 J7** reed columns on the
   bench. Prove each reed with the float magnet before lacing the column.
   Leave the board ends free for threading. J7's carbonator reed pair
   travels with the instrumented vessel and joins J7 during closure.
   Keep both reservoir columns on the bench until after the body pour.
   [Reed column layout](../printed-parts/cold-core/reservoir/level-sensing.md) · [Harness procedure](cable-assemblies.md#procedure-per-assembly)

### 5. Body-side install

Work with the shell upright and its equipment lid off.

1. **Lower the vessel and form the copper exits.** Start with straight,
   deburred tails. Clock the coil to its lanes, feed both tails through
   the shell holes from inside and lower the vessel in stages while
   drawing the tails outward. Support the copper while forming the
   bends. Seat the vessel on its support ring and check the exits and
   working lengths against EVAP-01. Reject kinks, creases and
   flattening. Burnish overlapping 3M 425 collars around the clean
   copper and shell, within the casing's foil allowance. Keep the
   copper mouths and insert pockets clear.
   [Coil drawing](../cold-core-layout/evaporator-coil-drawing.pdf) · [Copper feed-throughs](../printed-parts/cold-core/foam-shell/README.md#copper-feed-throughs)
2. **Route the carbonator tubes.** Seat the water inlet in the top
   elbow's adapter and bring it up through the `water-in` lane. The
   bottom CO₂ inlet and soda outlet use the push-fit elbows made up
   at the bench. Route them through their respective support-ring
   slots and bring the free tubing up to `co2-in` and
   `carb-water-out`. Seat and tug-test each joint the pour will cover.
   The tubes continue through the lid to the warm-side fittings.
   [Internal routes](../cold-core-layout/layout/routes.rs) · [Warm-side arrangement](../manifold-layout/above-core.md)
3. **Fit the relief outlet.** Install the shroud's vent tube, trim the
   outlet at its shell face and leave the discharge chase clear. Verify
   the exterior shroud seal has cured and the relief path is open.
   [Shroud procedure](../printed-parts/cold-core/prv-shroud/README.md#subassembly-procedure)
4. **Seat the reservoirs and stage the straight risers.** Lower the
   closed reservoirs into their pockets. Set A's fill and both air
   tubes to their headspace depths. Seat both draw tubes through their
   TPU grips to the floor with the specified angled ends. Locate the
   exposed ends on their lid-hole axes. Reserve B-fill for the
   front feed after lid closure. [Draw and fill seats](../printed-parts/cold-core/reservoir/floor-and-dip-tube.md) · [Air tubes](../printed-parts/cold-core/reservoir/vent.md)
5. **Route the shared sensor and earth loom.** Carry the temperature bus,
   carbonator reed leads and solid green bond into the shared west-side
   sensor passage. Form and support the earth wire along the same run.
   Leave the free ends available for threading. Prove both probes and
   the reed circuits, and repeat the steel-to-free-end bond reading
   while the attachment is accessible. [Installed wire routes](../wiring/README.md) · [Bond measurement](wiring.md#1-chassis-ground-bonds-single-point-ground-on-the-rear-wall)

### 6. Open-body foam pour

1. **Dry-fit B-fill before mixing foam.** Align the bend holder over
   Reservoir B's TPU grip. Thread the loose risers and leads through
   the equipment lid and seat it dry. Feed an offcut of the fill tubing
   lengthwise from the front through the lid, holder and grip. Set a
   witness mark at the front entry for the specified tip projection
   below the reservoir cap. Transfer the mark to the production tube
   from its reservoir end. Withdraw the offcut from the front before
   lifting the lid for the pour. [B-fill route datums](../cold-core-layout/layout/b_fill.rs)
2. **Protect the B-fill approach.** With the lid off, reinsert the marked
   offcut through the holder and grip as a locator. Keep its pull end
   accessible at the fore entry. Use removable masking to keep foam
   out of the straight approach and the gap between the guide exit and
   grip. The pour captures the lower holder. Keep the locator free
   to withdraw after cure.
3. **Mask the dry pockets and service paths.** Bridge each reservoir
   cap's perimeter to its pocket rim with burnished 3M 425 foil tape.
   Mask both dry reed channels, including the complete fore side
   outlet for B. Protect the upper insert mouths and the outside
   penetrations. Support the straight risers on their lid-hole axes.
   Keep the installed tube lumens and relief path open.
4. **Pour through the open shell.** Use the measured charge and
   distribute it through the connected body cavity within the kit's
   working time. The foam covers both closed reservoir caps and surrounds
   the staged risers. Let it cure with the equipment lid off.
5. **Clear the lid seat and B-fill route.** Pull the locator from
   the front and remove the temporary masks. Trim the foam below
   the equipment lid's seating plane. Clear the B-fill approach for
   the full tube envelope down to the bottom of the shell's fore
   entry. Keep the rim, insert mouths and reed channels clear.
   Prove the tubing and sensing leads before closing the lid.

### 7. Close and populate the top lid

1. Drop the proved reed columns into the dry channels. Lead A's
   conductors through the aligned lid bore and B's free conductors
   through the fore side window. Thread the straight risers and the
   shared sensor and earth loom through the lid.
2. Orient the lid with its B-fill opening at the front. Lower it over
   the holder's flush top and align the shell's screw pattern. Install
   the closure screws while the equipment mounts are empty and check
   that the heads seat below the lid face.
3. **Feed the final B-fill tube from the front.** With the lid seated,
   push the tube lengthwise through the round inlet and bend holder
   into the TPU grip to the marked depth. Leave the valve end free
   for connection to V-I during plumbing assembly.
   [Internal plumbing](internal-plumbing.md) · [B-fill passage in 3D](https://homesodamachine.com/parts#step:manifold-layout%2Fenclosure-assembly.step?find=solid%3A%20cold-core%2Fline-reservoir-b-fill%0Asolid%3A%20cold-core%2Freservoir-b-fill-guide)
4. Seal the dry lid perimeter, the seam around the B-fill holder
   and the cable and tube penetrations with the specified foil tape.
   Leave the reservoir air tubes and the relief discharge open.
   This completes **HSM-0557**.
5. Terminate J10 on the loose PCB before mounting it. Seat the bare
   pump and snap cap, install V-B, then fit their plumbing and dress
   the harness branches. Complete the J6 and J7 housings and J7's common
   junction after threading. Leave the free solid earth lead for direct landing
   at the rear PE WAGO when back-top is open.
   [Pump installation](../reference/g-ganen-pump/installation/README.md) · [Electronics bay](electronics-bay.md#assembly) · [Bond landing](wiring.md#1-chassis-ground-bonds-single-point-ground-on-the-rear-wall)

For lid service, release the fore-entry seal, disconnect V-I and withdraw
B-fill lengthwise from the front before lifting the lid. Free the other
tubes and loom ends as needed for access and restore the foil seals on
closure. [Plumbing](internal-plumbing.md) · [Wiring](wiring.md)

## Warm-side check valves

The water-side stem check sits at the pump discharge elbow. The gas-side
stem check seats in the PISCO outlet. Use their specified flow directions
and receiving depths from the [above-core layout](../manifold-layout/above-core.md)
and [plumbing procedure](internal-plumbing.md).

## Output condition

Both closures are seated and their heads recessed. The cured foam is trimmed
and the dry joints and underside openings are foil-sealed. The coil tails
retain their EVAP-01 working lengths. Both reservoirs have free float travel,
clear air paths, and tubes seated to their marked depths. The reed channels
are dry and the relief discharge is clear. Record the results of the checks
before handing **HSM-0003** to [refrigeration integration](refrigerant-loop.md).

## Bench verification

- The axial B-fill path has CAD clearance. The dry fit and first pour establish
  printed threading, locator withdrawal and post-cure alignment.
- Establish the charges, distribution and cleanup for the selected kit in
  the foam-fill trials. Use the batch instructions for handling and cure.
  [Foam-fill trials](../print-tests/foam-fill/README.md)
- The finished float and vessel establish the calibrated reed heights.
  Reservoir release depends on the water and syrup-dwell results.
  [Reed calibration](../printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration) · [Wetted-surface test](../printed-parts/cold-core/reservoir/wetted-surface-test.md)
