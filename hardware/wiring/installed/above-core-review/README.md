# Installed wiring review

Current routing checks wires and cable jackets against larger installed bodies.
Wire-to-wire and wire-to-tube contacts are excluded. Endpoint contacts remain
local to each named attachment. The review and route search are manual commands.

The [installed-wiring binding](installed-wiring-binding.json) records the current
producer sources, materialized manifest, closed fine-model solids and exact
standalone-to-installed viewer arrays. The production mesh-kernel wiring is
attached to the retained native physical assembly. The current graph contains
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

Use the workstation CAD queue. The `--native` reader uses the production fine
model beside the wiring STEP when present and compares its viewer arrays with
the installed assembly. It does not regenerate mechanical parts.

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
