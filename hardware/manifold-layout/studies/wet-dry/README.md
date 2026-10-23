# Connected electronics and rear fluid connections

This candidate groups the electronics on the **−X side** and the six bare fluid
and gas bulkheads on the **+X half of the rear panel**. The connected water
assembly retains the poses in [`../ceiling-fit/`](../ceiling-fit/). Printed
bulkhead collars and lettering are omitted.

## Arrangement

The Mean Well IRM-90-12ST lies flat on the cold-core cap, with AC entry aft
and DC entry forward. The populated main PCB lies horizontally above it,
components upward, with J10's power-wire entry facing forward. Both relays lie
flat beneath the PCB. The C14 inlet is vertical, with faucet data above it.
The inlet, data, ground stud and main WAGO bank occupy the −X half of the rear panel.
The other four manifold/sensor WAGOs form a group on the forward −X wall,
between the funnel and V-A. All nine WAGOs face wire entry toward the interior;
their conservative lever-opening spaces clear the selected parts.

The PCB spans X−90 to −17.20, Y336 to 426.82 and Z322 to 343.10 mm. Its underside
is Z324; the four existing mounting contacts are X−87.00/−20.70 and
Y339.50/417.50. Its tails clear the relays by at least **13.10 mm**. The supply
clears V-A by **5.37 mm** and the pump by **5.70 mm**. Each relay has **3 mm**
between its underside and the supply envelope.

**This arrangement requires a removable PCB carrier.** Relay screws face upward
beneath the PCB; terminal access requires lifting the PCB and its local leads.
The supply's rear mounting axes sit behind the inlet/data parts and two rear
WAGOs: fasten the supply before installing those parts, and remove them for
supply replacement. The carrier, fastening details and complete wire routes are
outside this fit study. Electronics do not occupy the forward funnel enlargement
area.

## Connections and access

[`connections/`](connections/) contains mating housings for the ten active JST
headers, their populated local conductors, both J10 power leads, and local leads
at the supply and relay contact terminals. The unused J8 expansion header has a
separate optional mating envelope. These objects move with their owner component;
their frozen inputs do not depend on the current production pack.

JST housing dimensions and nominal mated height follow the official XH drawing.
The local lead model uses Ø1.7 mm insulated wires, a 3 mm axial departure and a 4 mm
centerline bend, then an 8 mm run toward the nearest board edge. These are layout
estimates. The highest wire surface is Z343.25, leaving **2.75 mm** under the
ordinary ceiling and **2.50 mm** beside the left wall. The J10 leads depart
forward for 12 mm. Their wire-entry direction and upward screwdriver axes are
separate interfaces.

Each JST has a separate 6 mm axial unplugging sweep. J10, all six physical supply
poles and all three contact poles on each relay have Ø3.5 × 40 mm screwdriver
probes. Normal access has the roof removed; lifting the PCB also opens the relay
and supply tool columns. The supply's two local AC wires bend upward with a
2 mm straight and R5 centerline, clearing the rear wall by **0.80 mm** in the
Ø3 mm power-lead model. Pole pitch follows the supply manufacturer's drawing;
terminal heights and relay entry geometry remain explicit reference estimates.
Probe dimensions establish the modeled access, not a complete hand/tool model.

[`placement-fit.json`](placement-fit.json),
[`wago-open-fit.json`](wago-open-fit.json) and
[`connections/selected-audit.json`](connections/selected-audit.json) record the
selected poses, local conductor interactions and service conditions. The manual
check in [`study.json`](study.json) includes installed plugs and local leads
against the selected body, tube, clamp and native context meshes. Local
departures do not establish complete end-to-end harness routing.

## Forward placement context

[`forward-context/`](forward-context/) preserves the actual V-B, formed outlet,
reservoir fill/draw lines and funnel-drain neighbors for placement review.
The diagnostic PCB footprint is X−74 to −1.20 and Y182 to 272.82. With its
underside at Z257 it intersects V-B and reservoir plumbing. At underside
Z310–324 it intersects the funnel and frame in both simple horizontal
clockings, including the connected JST envelopes. These readings apply to
that footprint; other forward layouts remain possible with wet-part changes.
The translucent diagnostic boards are excluded from the installed arrangement.

## Rear fluid bank

| Connection | X, mm | Z, mm | Tube OD, mm |
|---|---:|---:|---:|
| Water in | 37.25 | 334.376 | 6.35 |
| Soda out | 72 | 333 | 6.35 |
| Faucet vent / drain | 45 | 301 | 4 |
| CO2 in | 72 | 301 | 6.35 |
| Flavor A | 45 | 270 | 4 |
| Flavor B | 72 | 270 | 4 |

All six flange seats are at Y468.3. One flat 3 mm exterior recess in the nominal
9 mm rear wall leaves **6 mm panel stock** for the fittings. The water connection
remains straight into the ASSE, with **29.125 mm exposed tube**. The other five
connections show only their first 20 mm of inward tube departure; they are not
complete routes to their equipment.

The bare bulkheads clear the water hardware by at least **3.60 mm**, and the
20 mm tube departures by at least **5.47 mm**. The closest bulkhead pair has
**4.56 mm** between its reference surfaces. Water and soda unions use the existing
estimated retention-nut occupancy; the NeoFit reference bodies include their
coarse inboard nut envelopes. These checks establish occupied space, not fitting
retention or final mounting details.

## Walls and roof

[`context.py`](context.py) exports plain native wall and ceiling solids in
[`parts/`](parts/). The existing ASSE recess extends over the aligned water inlet.
The electronics fit beneath the ordinary **9 mm roof** without a PCB recess.
The ASSE and regulator recesses retain 3 mm of roof. The enclosure exterior and
cold-core cap height remain the study datums.
Panel openings represent clearance envelopes; the keystone retainer and C14
fastening detail are not designed here.

## Evidence and reproduction

[`source-inventory.json`](source-inventory.json) identifies the frozen assembly
mesh, reference generators, source poses and part datums. Its assembly bytes
match the artifact pointer; that pointer marks source regeneration of this
assembly as unproven. Component snapshots retain that evidence limit.

[`layout.json`](layout.json) records the selected transforms.
[`pcb-terminals.json`](pcb-terminals.json) and
[`electronics-terminals.json`](electronics-terminals.json) carry nominal connector
datums with their parts. Separate physical wire-mouth and screw-head datums are
in [`connections/world-datums.json`](connections/world-datums.json).
[`bulkhead-fit.json`](bulkhead-fit.json) records the retained fluid bank. WAGO
opening checks include extra open-lever occupancy, rather than checking only
closed connector bodies.

From the repository root:

```sh
PYTHONPATH=. tmp/takeover/cadq "Wet and dry context" -- \
  tools/cad-venv/bin/python hardware/manifold-layout/studies/wet-dry/context.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/wet-dry/study.py --check
```

The selected meshes and native context have no unrelated-body intersections.
Intended fitting interfaces and panel crossings are identified as mates. The
source studies supply the water hardware; this generator reads frozen meshes
without importing the production pack. The complete gas circuit, remaining
equipment, installed routes and production-pack migration are outside this study.
No automatic check or production dependency is added.
