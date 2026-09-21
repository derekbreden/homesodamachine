# G Ganen conservative integration envelope

This is a separate clearance model of the [measured G Ganen reference](../README.md).
Its 26 valid native solids contain the corresponding detailed native components.
The model has 5,496 faces; the detailed reference has 26,490. The casing loft,
motor cylinder, both measured barb profiles and the four identical common feet
are exact native copies. The other components are convex outer polytopes.

The largest outward surface distance is **0.148580 mm**, bounded against the
detailed native solid over the entire component. The largest increase of an
individual axis-aligned component extent is **0.000316 mm**. These are reduction
bounds, with a 0.000002 mm geometry comparison tolerance; they do not establish
the scanner's absolute accuracy or the sprayed sample's dimensional tolerance.
The raw scans retain their native scale and coordinates.

## Native evidence

[containment.json](containment.json) records every component's source and reduced
face counts, native convexity, supporting planes, outward distance, bounding-box
change and volume. [native-validation.json](native-validation.json) records the
STEP round trip. [artifact-manifest.json](artifact-manifest.json) binds the
envelope, viewer payload, source programs and checks to the frozen detailed
reference.

The convex source solids have planar faces and straight edges. Their vertices
lie inside every outward native face plane, and their native volumes agree with
the convex hulls of those same vertices. The outer polytope's supporting planes
contain every source vertex. Its native face/edge/volume checks establish the
same planar convex solid as the plane intersection. The maximum distance from a
convex polytope to a convex set occurs at a polytope vertex: every reduced native
vertex is compared with the exact planar source boundary triangles. This check
uses the native polyhedral geometry, without a tessellation tolerance.

The hull builder drops numerical faces that collapse below the CAD kernel's
vertex resolution; every resulting native solid must remain valid, convex and
volume-equivalent to the complete supporting-plane intersection. Synthetic
checks exercise a rotated thin prism, a many-face convex surface and rejection
of a concave source.

## Interface and scope

`g_ganen_integration.py` exposes `build_parts()`, `build()`, `build_scene()` and
`build_assembly()`. The native import is cached per unchanged STEP and proof.
The measured `port`, `port_profile`, `suction`, `discharge`, `mount_slots`,
`sliding_rails`, `mount_seat_z` and `parameters` APIs come directly from the
detailed reference. There is no common invented barb diameter, fixed mounting
rectangle or loaded rubber thickness.

The four flexible rubber feet remain separate bodies at their observed poses.
Each foot can move along local X independently. Their shared nominal 7 mm
geometry retains visible slots and reliefs; hidden throat, rail retention and
compression remain outside the reference scope. The port
exterior does not certify hose insertion or retention. The intended +90° Z
placement maps local +Y discharge to enclosure −X. The local Z=0 bearing datum
remains distinct from the lowest point of a free rubber foot.

This model supports conservative rigid-neighbor clearance checks. A contact
introduced by up to 0.15 mm of local outward envelope can be checked against the
detailed component. Material mass, strength, rubber compression and mounting
hardware passage are outside its scope. Production placement, cap and routes have independent current checks; the
reference boundary is recorded in
[integration-handoff.md](../integration-handoff.md).

## Query cost

[native-query-cost.json](native-query-cost.json) records the exact predecessor
STEP named in that file. These retained host timings are historical and do not
claim current whole-pump performance. The rigid components are unchanged; the
common-foot update has its own native round-trip and component-identity proof.
The benchmark uses the detailed implementation with its named STEP substituted. Both operations use a
fresh STEP import and the same 90-second total process budget. The distance
probe is a 5 mm box beside the +Y head lug; the room-section probe intersects
X −60..70, full Y and Z 20..58. These are host timings during shared local work,
not a full-assembly performance guarantee.

| Query | Detailed reference | Integration envelope |
| --- | ---: | ---: |
| Fresh STEP import for distance | 50.108 s | 5.543 s |
| Distance query | 0.609 s | 0.186 s |
| Distance to the same box | 2.523605 mm | 2.499829 mm |
| Standard room-section query | exceeded 90 s total process limit | 37.348 s |

`native_queries.intersect_components(shape, cutter)` clips every native solid
independently and returns their occupied compound. Intersection distributes over
the components' union, so this preserves occupied space without partitioning
overlaps between the envelopes. `occupied_bounds(result)` returns XYZ min/max,
or `None` for an empty result. Both arguments use the same coordinate frame;
placed solids and a world-frame cutter can be supplied directly.

[component-section-cost.json](component-section-cost.json) records **5.572 s**
for that same room section, after a 6.065 s fresh import. Its 22 native fragments
are valid; the occupied bounds agree with the standard native query within
0.000000011 mm. The empty case passes. The helper retains component overlaps:
its summed volume is not union volume or material volume.

## Reproduce

From the repository root:

```sh
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/freeze_reference.py --check
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/selftest_envelope.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/derive_envelope.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/export_envelope.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/benchmark_integration.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/benchmark_component_sections.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/freeze_envelope.py
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/integration-envelope/freeze_envelope.py --check
```

Derivation caches native solids under `.cache/g-ganen-integration-envelope`, with
source and cache digests. The exporter keeps its candidate there until the
native round trip passes, then copies the proven STEP and bound viewer payload
into this folder. The scripts do not write production sources or the shared
dependency trace.
