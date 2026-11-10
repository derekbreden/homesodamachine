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

The saved STEP and payload carry the conservative component envelopes. The measured
ports, separate barb profiles, mounting slots, rails and datum remain in the
detailed reference's parameter records. Native reference accessors read those data
directly; the model requires no Python construction at query time.

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

The [component-query source](https://github.com/derekbreden/homesodamachine/blob/0785c32f89a6e08609e5348aa2beb0096d560326/hardware/reference/g-ganen-pump/integration-envelope/native_queries.py)
is archived with the bound benchmark. Current [native geometry queries](/tools/hsm/README.md)
measure the saved detailed or conservative payload directly.

[component-section-cost.json](component-section-cost.json) records **5.572 s**
for that same room section, after a 6.065 s fresh import. Its 22 native fragments
are valid; the occupied bounds agree with the standard native query within
0.000000011 mm. The empty case passes. The helper retains component overlaps:
its summed volume is not union volume or material volume.

## Bound sources

The [envelope derivation, export and benchmark programs](https://github.com/derekbreden/homesodamachine/tree/0785c32f89a6e08609e5348aa2beb0096d560326/hardware/reference/g-ganen-pump/integration-envelope)
are archived in Git. The saved model, containment proof and component identities
retain the bindings recorded in this directory's manifests.
