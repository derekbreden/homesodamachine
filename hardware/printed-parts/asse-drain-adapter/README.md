# ASSE drain adapter

One TPU 85A sleeve connects the Multiplex 19-0897 atmospheric-vent barb
directly to the white neoFlo 4 mm OD / 2.5 mm ID LLDPE drain. Two existing
four-inch nylon zip ties close separate recessed lands, one around each
inserted part. The customer outcome is a compact connection with an open,
visible fault discharge and a drain tube that can be routed without a
separate hose or rigid adapter stack.

This is an **unprinted fit candidate**. The sockets, zip-tie retention,
water tightness and complete fault discharge have no physical acceptance.

| Feature | Relaxed print dimension |
|---|---|
| Barb socket | Ø[6.10](BARB_BORE) mm × [12.8](BARB_DEPTH) mm |
| Tube socket | Ø[3.80](TUBE_BORE) mm × [14](TUBE_DEPTH) mm insertion |
| Bore transition | Smooth taper, [60](TAPER_ANGLE)° above the print bed |
| Overall length | [28.79](LENGTH) mm |
| Large / small outside diameter | Ø[14](BARB_OD) / Ø[10](TUBE_OD) mm |
| Minimum relaxed wall under a tie | [2.60](GROOVE_WALL) mm |
| Zip-tie lands | 2.8 mm flat width, 0.5 mm recess, 1 mm sloping shoulders |
| Solid CAD volume | [2.516](VOLUME) cm³ |

The large bore tapers smoothly into the 3.80 mm tube bore. There is no
internal shelf. A 14 mm insertion mark places the tube across its tie land
and grips the full small socket. The barb tip ends above the reducer when
the sleeve mouth is 0.5 mm below the body. The open bore exceeds the tube's
Ø2.5 mm nominal ID; it is not a vent flow rating.

## Fit basis

[Anderson Brass](https://www.andersonbrass.com/asse-1022-backflow-preventers)
specifies a 1/4-inch hose barb for the applicable ABF connection. Hose size
describes the mating hose ID, not the crest diameter. The 6.10 mm socket is
0.25 mm below that 6.35 mm hose size. The reference model's Ø8 mm cylinder
is an unmeasured occupied envelope, so it does not establish the socket's
actual interference. `BARB_BORE` and `BARB_DEPTH` are explicit fit parameters.

The 3.80 mm socket has 0.20 mm nominal diametral interference with the
4 mm tube. The [organizer's accepted Ø4.40 mm drain bore](../faucet/umbilical-organizer/physical-acceptance.json)
belongs to rigid PET-GF and a sliding fit. It does not establish the actual
tube diameter or a TPU sealing-bore correction. The
[Touch-Flo TPU record](../faucet/tpu-o-ring/print-log.md) establishes successful
85A seating for that identified part; it supports using available compliant
stock, without transferring its seal or fit acceptance to this sleeve.

The deployed sleeve has separate printable and installed representations.
The installed CAD opens the sockets to the reference barb envelope and
4 mm tube and conserves nominal annular area when increasing the outside
radii. It is a conservative occupancy approximation for routing, not a
computed elastomer strain, sealing pressure or retained tie tension.

## Print and assemble

Print upright with the large socket on the bed and the small socket up.
The internal reducer, external taper and bore-entry chamfers rise 60° above the bed;
recessed tie shoulders expand at 0.5 mm per millimetre of build rise. No supports are needed inside the sealing bores.
Use dry TPU 85A and a solid process: 100% zig-zag infill, four
continuous wall loops, 0.20 mm first layer and 0.24 mm layers above it. Keep hole
and contour compensation at zero for the first fit. The [Mark2 print project](asse-drain-adapter-tpu85a-right06-mark2.3mf)
and [reviewed native slice](native/asse-drain-adapter-tpu85a-right06-mark2/asse-drain-adapter-tpu85a-right06-mark2.gcode.3mf)
use the right 0.6 mm nozzle, 225°C nozzle / 35°C bed, and the saved +0.04 mm
TPU Z trim. [Native review](native-review.json) binds the source mesh, settings,
full bead envelope and support result. The native estimate is about 36 minutes
and contains no supports. This fit-trial job has not been sent to a printer.

1. Put two loose four-inch / 2.54 mm-wide ties around their respective lands.
2. Slide the large socket over the entire vent barb, leaving the sleeve mouth
   just below the device body. Use water for assembly lubrication if needed.
   Do not push TPU into the vent opening or pull on the vent fitting.
3. Square-cut the 4 mm tube. Mark 14 mm from its end and insert until the
   mark meets the sleeve mouth.
4. Snug each tie by hand until its joint grips; stop before visibly flattening
   the tube, distorting the vent fitting or cutting the sleeve. The ties supply
   retained squeeze independently; interference alone is not a retention claim.
5. Route the tube with R25-or-larger bends, leaving its initial straight lead
   unloaded. Clock the tie heads toward the accessible bay and flush-cut tails.

An ordinary fit-up decides whether these socket dimensions can be retained:
both ends must seat without damaged stock, the tube must reach its mark,
ties must hold without visible ovalization, and the passage must stay open.
Leakage and axial retention require an assembled result; no numeric pressure,
pull force or lifetime acceptance is asserted.

The [fault-drip record](../faucet/vent-qualification/README.md) defines the
unsealed outlet over the bowl. The complete rising 2.5 mm-bore drain has no
device-specific vent-backpressure approval or physical fault-flow result.
This connection design does not establish those properties.

The [assembly clearance record](../../manifold-layout/drain-clearance-check.json)
measures this sleeve and return against the identified saved installed scene,
including the conservative foam envelope. Its route has two R25 bends and
110.23 mm of tube outside the sleeve. The nominal minimum gaps are 1.44 mm
at the sleeve and 1.22 mm at the white return. Other assembly members and
their viewer surfaces are retained. The prior whole-machine facts and
scorecard remain evidence of their identified source build; this local
materialization does not qualify all machine checks.

Regenerate from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py`
