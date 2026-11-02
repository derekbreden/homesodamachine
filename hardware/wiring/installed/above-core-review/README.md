# Installed wiring review

Current routing checks wires and cable jackets against larger installed bodies.
Wire-to-wire and wire-to-tube contacts are excluded. Endpoint contacts remain
local to each named attachment. The review and route search are manual commands.

The [installed-wiring binding](installed-wiring-binding.json) records its producer
sources, materialized manifest and geometry format. The current graph contains
119 wiring bodies and 100 conductor curves. The [full routing screen](../routing-review.json)
and [closed-solid contact follow-up](../contact-review.json) identify their exact
exported artifacts and distinguish zero-volume witnesses from local endpoint contact.
The [mounted junction reading](junction-review.json) covers the nine rooted
WAGOs; the [final-junction reading](../final-junction-review.json) covers the
three free joins beneath the funnel opening.

Run the manual reader after the appliance and its wiring are materialized:

```sh
python3 tools/run.py --cad -- tools/cad-venv/bin/python hardware/wiring/installed/review.py
python3 tools/run.py --cad -- tools/cad-venv/bin/python hardware/wiring/installed/review.py --native
```

The `--native` reader selects the geometry named by the materialization. A
manifest with `wiring_fine_model_sha256` selects `fine_review`. Otherwise, a
production model beside the wiring STEP selects `production_solid_review`;
without either, the reader uses the native STEP fallback.

The production-model reader accepts the native producer's bare body names and
f64 V/T arrays. It checks closed, connected mesh-kernel solids and exact
standalone-to-installed viewer vertex and triangle arrays in `production_solids`.
That production export attaches mesh-kernel wiring to the retained native
physical assembly. It does not regenerate mechanical parts or claim kernel
source/model bindings.

Kernel wiring has a separate fine-model inspection:

```sh
python3 tools/run.py -- tools/cad-venv/bin/python hardware/wiring/installed/review.py --fine
```

It checks authoritative fine topology, source/model hashes and exact installed
presentation arrays in `fine`. Both manual readers select fine geometry when
the manifest names a kernel model:

```sh
python3 tools/run.py -- tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/installed_wiring_binding.py
python3 tools/run.py -- tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/aggregate_review.py
```

The binding reader regenerates the bound numeric recipes through Rust and compares
their authoritative fine bodies, current electrical graph, curves and conductor
stock in `fine_source`. The contact reader's `fine_contacts` queries every fine
AABB overlap, including contained stock, with exact closed-entry commons. Only
the named endpoint and fuse-stub spheres are removed. The two physical empty J4
cells apply only when both named cells contain the complete remaining contact.
Presentation arrays do not select or measure those contacts. Each production,
fine and native record retains its own format, artifact hashes and scope.

For a kernel materialization, `aggregate_review.py --refresh-cache` writes an
explicit fine-model index under `tmp/above-core-electrical-fixture/fine/`.
Native BREP fixture indexes remain scoped to native materializations.

Native STEP source binding uses the workstation CAD queue:

```sh
python3 tools/run.py --cad -- tools/cad-venv/bin/python hardware/wiring/installed/above-core-review/installed_wiring_binding.py
```

Its optional `--source-cache PATH` reuses explicitly bound native source solids
after matching current curves, termination metadata, jacket geometry and generator
hashes. All actual wiring bodies are still read back. The default composes only
the source wiring; it does not regenerate mechanical parts.

The wire/source reader does not repeat the mesh contact screen. A contact
follow-up must query the exact wire and obstacle bodies named by the current
screen; a reader binding alone does not renew an older contact receipt.

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
