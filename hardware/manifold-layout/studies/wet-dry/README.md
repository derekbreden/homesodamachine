# Electronics and rear fluid connections

This candidate groups the electronics on the **−X side** and the six bare fluid
and gas bulkheads on the **+X half of the rear panel**. The connected water
assembly retains the poses in [`../ceiling-fit/`](../ceiling-fit/). Printed
bulkhead collars and lettering are omitted.

## Arrangement

The Mean Well IRM-90-12ST stands upright against the −X wall, with AC entry aft
and DC entry forward. The populated main PCB lies horizontally above it,
components upward. Both relays lie flat beneath the PCB. C14, faucet data,
ground stud and the main WAGO bank occupy the −X half of the rear panel.
The other four manifold/sensor WAGOs form a group on the forward −X wall,
between the funnel and V-A. All nine WAGOs face wire entry toward the interior;
their conservative lever-opening spaces clear the selected parts.

The PCB spans X−96 to −23.20, Y347 to 437.82 and Z328 to 349.10 mm. Its underside
is Z330; four existing mounting contacts are X−92.50/−26.20 and
Y356.316/434.316. Its tails clear the relays by **1.6 mm**. Its aft edge clears
the main WAGO bank by **5.88 mm**. The supply clears V-A by **1.70 mm**.

**This arrangement requires a removable PCB carrier.** Relay screws face upward
beneath the PCB, so the relays are wired before the PCB is installed; later
terminal access requires PCB removal. The carrier, fastening details and complete
wire routes are outside this fit study. This service arrangement is a choice for
review, not a completed mount design. Electronics do not occupy the forward
funnel enlargement area.

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
A flat electronics recess opens to Z351, retaining **4 mm of roof** and **1.90 mm
above the highest PCB component**. The ASSE and regulator recesses retain 3 mm
of roof. The enclosure exterior and cold-core cap height remain the study datums.
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
datums with their parts. [`bulkhead-fit.json`](bulkhead-fit.json),
[`auxiliary-fit.json`](auxiliary-fit.json),
[`fore-wago-fit.json`](fore-wago-fit.json) and [`study.json`](study.json) record
the manual geometry questions. WAGO opening checks include extra open-lever
occupancy, rather than checking only closed connector bodies.

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
