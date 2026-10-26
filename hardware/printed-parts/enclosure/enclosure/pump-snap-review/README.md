# Pump retainer snap review

The lower pump retainer carries two full-Y wings rooted above their lower hooks.
The standalone STEP/STL has the relaxed 0.35 mm outward tip pose; the appliance
STEP, appliance viewer and installation GLB have the 0.10 mm seated pose. These
cubic shapes illustrate the two positions. They are not calculated elastic
responses.

Each receiver has 0.25 mm nominal Y end clearance and its floor is 0.15 mm below
the hook's underside. A central 4.5 mm tool port has a continuous 45° roof across
the pocket and access opening. The full-Y wings and hooks retain the common end
planes. The fitted pump profiles and their supporting source functions retain
their identified scope.

[`review.py`](review.py) is a manual reading of the current exported geometry.
Run it after both individual pieces, the full appliance STEP/viewer and the
`pump-mount.glb` installation scene have been regenerated:

```sh
tmp/takeover/cadq "pump snap native review" -- tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/pump-snap-review/review.py
```

The script binds its source inputs and every read artifact by SHA-256 and writes
`native-review.json`. It checks valid single native bodies, the printed relaxed
retainer against its source, full-Y wings and hooks, the retained pump inverse
spaces, seated separation, receiver floor areas and nominal clearances. A single
analytic 45° face on each receiver must contain all three roof stations.

The release-tool reading uses a conservative 3.31 mm diameter cylinder around
the photographed screwdriver, with 58 mm below the receiver-edge fulcrum and an
8 mm tip reach. On each side it samples insertion from 15 mm below the fulcrum
and levering from 0° to 34°. Intended wing contact is excluded from fixed-body
interference; the fixed carrier and actual front-top remain in the reading.
These are discrete native samples. They do not prove a continuous collision-free
path, release force, tip pressure or retraction of both ends of a broad wing.

[`baseline-hardware.json`](baseline-hardware.json) freezes the preceding
appliance/viewer identities and the appliance and installation-scene member
lists. The current native STEP is read with its body names and placements.
Every previous member must remain except the three pump-retainer screws and
three inserts. The current native front-top must equal its individual STEP,
and the current installed retainer must equal the seated source body. The
viewer and GLB must show the seated tip span under the common scene transform.
The member comparison establishes retained membership; it does not establish
geometric identity of every unrelated hardware body.

This reader exports no production geometry, contacts no printer and is not
called by a build, hook or scorecard. Local 100% zig-zag infill modifiers cover
the complete hooks, wings and upper roots, and the receiver bands through the
flank roots. They intersect existing material and preserve the openings.
Ordinary wall, infill and Tree(auto)/Default support settings elsewhere keep
their current recipe.

Printed fit, pump retention under load, creep, repeated use and removal remain
physical qualifications. Accepted observations of the earlier pump fit,
faucet display and funnel snap remain specific to their identified articles.

The [offline print receipt](print-review.json) binds both current meshes, their region
record, native projects, sliced archives and path reviews for Mark1’s left 0.4 mm nozzle
in black PET-GF. Both native reviews pass. The retainer has no emitted support and a
62.55 mm minimum bead-to-bed-edge margin; front-top records 31 support bodies and a
25.27 mm minimum margin. The sampled snap-host bead coverage is at least 98.9% in the
retainer and 99.5% in the receiver regions. These are emitted-path samples and support
topology readings; physical cleanup, fit, force, retention and lifetime remain unqualified.
