# CO₂ connection and rear grid

This selected-component arrangement includes the connected water header, CO₂
regulator/check, dry-side electronics and their local connections, funnel/frame,
bare rear fittings, and native ideal wall/roof solids. It is an isolated layout
study; production equipment carriers and enclosure parts are outside its scope.

The six rear fittings occupy a regular two-column, three-row grid. Column centres
are X37.25 and X77.5 mm; row centres are Z334.376, Z302.376 and Z270.376 mm.
Column pitch is 40.25 mm and row pitch is 32 mm. In the enclosure coordinate
frame, the assignments are:

| Row | West (−X) | East (+X) |
| --- | --- | --- |
| Upper | Water in | CO₂ in |
| Middle | Faucet vent | Soda out |
| Lower | Flavor A | Flavor B |

Fixed fitting flanges seat on the flat exterior at Y471.3. One common interior
recess gives the nuts a seat at Y465.3, retaining 6 mm of mounting stock. Separate
bare nut envelopes include barrel bores. Their dimensions and the fitting-source
limits are recorded in `interfaces.json` and the parent wet/dry references.
Printed label collars are not part of this arrangement.

The retained 4 mm and CO₂ bulkhead bodies use coarse exterior occupancy
references, not scanned collet profiles. The 6.35 mm fitting nuts are estimated
20 mm across flats by 4 mm deep; the other nut dimensions follow their retained
supplier references. These limits apply to the nominal clearance results.

The water group sits 7 mm forward of the PCB-low-fore study. Its relative fitting
positions, pump-joint angle and square plumbing axes are fixed. Both valve bodies
are clocked 180° about their own vertical ports, with heads pointing forward
(−Y). This leaves a direct CO₂ drop behind V-K. The water supply remains one
straight tube from the upper-west bulkhead to the ASSE inlet.

The CO₂ path is rear bulkhead → JG inlet adapter → WR1105 regulator → directly
threaded GASHER check → JG outlet adapter → trimmed stem elbow → continuous
6.35 mm tube through the cold-core guide. The regulator uses the scanned WR1110
exterior. The regulator and check have compatible male-outlet/female-inlet
1/4 NPT interfaces, requiring no intermediate push-connect adapters or tube.
The inlet adapter uses an estimated 11 mm thread engagement; direct regulator
to check engagement is 9.18 mm and the check's outlet adapter uses 11 mm.
The resulting nominal inlet-to-outlet mouth span is 132.47 mm.

The [NeoFit acetal stem-elbow family](https://www.freshwatersystems.com/products/neofit-acetal-natural-white-stem-elbow-1-4-tube-x-1-4-stem)
is the selected downward turn. Its concealed stem is trimmed for the nominal
15.7 mm JG socket insertion. External fitting shoulders meet. The drop has a
small, broad S offset and enters the fixed core guide at
`(77.500000016, 322.2999999, 253.4)` mm with a vertical tangent. The guide is a
passive hole around a continuous tube, not an additional coupling.

Native roof pockets retain at least 3 mm of the 9 mm ceiling. The simple CO₂
rectangle retains 7 mm. `parts/` holds valid single-solid STEP context and its
tessellated snapshots. `co2-parts/` holds portable part meshes, native adapter
models, manufacturer dimensions and source provenance.

The manual selected-scene fit query reports no unrelated intersections across
bodies, tubes, installed local leads and wall/roof solids. The CO₂ drop clears
V-K by 8.16 mm, and the local lower-west flavor bend clears the pump by 3.87 mm.
These are nominal geometric clearances. Thread make-up, socket depths and local
formed-tube departures remain estimates. Soda, vent and flavor fittings show
local departures only; their complete onward routes are not placed. WAGOs are
deferred until primary components and their wire routes are arranged. V-B and
reservoir routes are outside this selected group.

Rebuild the native context manually through the CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "CO2 grid context" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-grid/context.py
```

Generate the selected scene, interface datums and packed viewer meshes:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-grid/study.py --check
```

`--check` is an optional manual query; no recurring check is installed.
