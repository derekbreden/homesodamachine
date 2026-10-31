# Installed wiring review

Current routing checks wires and cable jackets against larger installed bodies.
Wire-to-wire and wire-to-tube contacts are excluded. Endpoint contacts remain
local to each named attachment. The review and route search are manual commands.

The [installed-wiring binding](installed-wiring-binding.json) compares the
materialized standalone wiring STEP and manifest with the current electrical
graph and native source bodies. It records conductor and housing counts from
that graph, source-curve agreement, geometric signatures and STEP reader
validity separately. The current record binds all 120 bodies and 101 conductor curves; every
source and readback body is valid. The routing report resolves its five mesh
witnesses with exact native readings and local attachment bounds.

Run the manual reader after the appliance and its wiring are materialized:

```sh
tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/installed_wiring_binding.py --update-routing-review
```

Use the workstation CAD queue. The optional `--source-cache PATH` reuses
explicitly bound native source solids after matching current curves,
termination metadata, jacket geometry and generator hashes. All actual wiring
bodies are still read back. The default composes only the source wiring; it
does not regenerate mechanical parts.

`--update-routing-review` preserves the mesh snapshot and its artifact hashes
in [routing-review.json](../routing-review.json), then attaches the current
readback and scoped dispositions of the listed witnesses. Native-zero mesh
witnesses, corrected contacts and unresolved readings remain distinguishable.
It does not rerun the full mesh scene, equipment contacts or wire packing.

The local contact receipts retain their exact geometry and query scopes:

- [Ground and J2 dressing](ground-j2-wiring-review.json): its recorded earth-stack fixture,
  fore paired-tube seat and locally dressed bond/COM/FAN paths.
- [Routing witnesses](routing-witness-native-review.json): named endpoint
  readings, the pump-head subsolid diagnosis and corrected coil/pump guides.
- [Reservoir A routes](/hardware/mechanical-qualification/enclosure-above-core/reservoir-a-route-review.json):
  fixed anchor points, free tube curves and named local wire substitutions.
- [Composition](native-review.json), [junctions](junction-review.json),
  [tubes](tube-review.json), [walls](wall-review.json) and
  [assembly contacts](aggregate-review.json): their specified native fixtures,
  named parts and artifact hashes.

These reports are not invoked by builds or commits. Source geometry and
native interference readings do not qualify physical wire bends, crimp entry,
packing, flexible service motion, installation force or the unlocated donor
and motor-tab landings.
