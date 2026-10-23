# Folded CO₂ layout candidate

The gas path turns down immediately after its rear-bulkhead handoff, runs down
through a PISCO RVFUP1/4–1/4-0.3 regulator, returns upward through a Fluidfit
HCVU1/4–1/4 check, then turns down toward the cold core. Five NeoFit stem elbows
form the 90° inlet and two 180° returns. All stems are trimmed to their host's
full insertion depth with their shoulders flush; the devices have no threaded
transition adapters. A 16 mm exposed tube connects this group to the bulkhead.

The [reference models](../../../reference/compact-inline-candidates/README.md)
retain the manufacturer's 62.4 mm regulator and 45.5 mm check lengths and
their socket depths. Regulated flow is downward; check flow is upward. Each
return advances 25.0952 mm fore. A concealed tube joins the first return's
female socket to the check's female inlet.

The selected water group, original V-K/V-A clocking and PCB retain their
co2-tpu poses. The whole six-port wet grid sits 4 mm higher, preserving its
two columns and 32 mm row pitch. The existing water-feed span rises gently
to that grid. The soda outlet uses one west-facing stem elbow; the adjacent
4 mm vent/drain has a straight local departure. Full onward soda, vent and
flavor routes remain outside this study.

The proposed gas guide is `(77.5, 368.7622, 253.4)` mm, 46.4622 mm aft of the
existing guide, along the cold core's existing gas port lane. The straight
drop clears V-K. The cap bore and the tube route below the cap have not been
migrated to the production core. The source of that lane and its independently
placed cap conduit is `hardware/printed-parts/cold-core/_cold_core_interface.py`.

The detailed selected-mesh query reports no unrelated intersections. Gas
hardware occupies approximately 21.5 × 77.0 × 90.0 mm, excluding the external
inlet tube, bulkhead and final straight drop. The lower return clears the
plain core face by 2.74 mm. The inlet elbow and upper rear fittings use the
gas roof pocket at Z352, retaining 3 mm of roof stock; the water pockets also
retain 3 mm. These are nominal exterior-model results, with the stem elbows'
undimensioned molded details still estimated.

PISCO specifies air service and free reverse flow. The downstream check
provides the separate one-way function. PISCO's exact CO₂ suitability and
immediate dispatch are unconfirmed; these are layout candidates. See
[sourcing](sourcing.json) for current specifications and availability limits.
No purchase or production component replacement is recorded by this study.

Native STEP and mesh files for the host-specific stems and selected wall/roof
context are in `parts/`. Rebuild them through the shared CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "Folded CO2 host stems and context" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-fold/build.py
```

Regenerate the scene, interfaces and ignored viewer payload; `--check` asks
the selected exterior-fit question manually:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-fold/study.py --check
```
