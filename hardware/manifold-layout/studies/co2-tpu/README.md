# TPU CO₂ arrangement

The selected gas path is rear bulkhead → straight TPU external-boss cuff → WR regulator → directly threaded Gasher check → TPU outlet elbow → continuous tube through the fixed cold-core guide. The two TPU joints and four clamp bands are modeled in [tpu-joints](tpu-joints/model.py); their datums and evidence scope are in [joint interfaces](tpu-joints/interfaces.json).

The water group sits 29 mm fore of the PCB-low-fore source registration. Its fitting axes and original aft-facing V-K/V-A heads are retained. The low forward PCB and its plugs move 4 mm inboard; J7 leads turn inward over the board. The regular six-port grid and cold-core handoff retain their coordinates.

The three named ceiling pockets leave 3 mm above the water components and 6 mm above the gas lane. The rear fittings share one interior relief, retaining 6 mm of mounting panel. Native STEP, mesh and solid reports are in [parts](parts/).

The manual selected-mesh query reports no unrelated intersections. Gas tube–V-K clearance is 3.52 mm, pump–PCB 2.42 mm, and V-A outlet elbow–PCB 1.65 mm. Full onward soda, vent and flavor routes, complete wire routing, WAGO placement, V-B and reservoir routes are outside this selected arrangement. Local departures and wire bends establish their stated local occupied space.

Regenerate the viewer payload and optionally ask the selected-mesh fit question:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-tpu/study.py --check
```

Rebuild the native context through the shared CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "TPU CO2 context" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-tpu/context.py
```

The viewer payload is `out/viewer-data.json`. [study.json](study.json) records selected instances and the manual query; [interfaces.json](interfaces.json) records current poses, tube insertions and the gas centreline.

[Regulator research](regulator-search.json) records the dated manufacturer and
Prime-availability findings for a compact secondary with native push-connect
ports. KL26918 is the technical candidate; no immediate-dispatch Prime purchase
meeting all criteria was verified. No production replacement is selected.
