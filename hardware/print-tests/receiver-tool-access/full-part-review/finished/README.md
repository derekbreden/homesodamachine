# Complete enclosure print set

The complete HSM-000081 back top, HSM-000079 front top, HSM-000082 lower pump
retainer and HSM-000020 equipment lid are prepared for printing, subject to
the successful matched-snap review Derek specified. These are the full appliance
parts with their production fits, receiver tool openings and installation paths.
No job in this set has been submitted.

The [readiness record](../readiness.json) binds each final mesh to its reviewed
native project and print archive. The binary files are delivered in
`~/Downloads/HSM-full-enclosure-2026-11-03/`; Git holds the recipes, hashes and
reviews. Each print-only archive contains exactly the reviewed G-code and its
checksum. Editable projects are in `projects/` and the complete sliced source
archives are in `reviewed/` beside the print-only files.

Both shell tops use Mark2's fixed left hardened 0.4 mm Standard nozzle and
black PET-GF. The retainer and equipment lid use Mark1's corresponding nozzle
and material. The emitted Textured PEI trims are +0.02 mm for Mark2 and
+0.16 mm for Mark1. Ordinary shell stock uses two walls and 15% gyroid;
the retainer and lid use their selected three-wall recipe. The prepared
projects include the complete local solid hosts and the specified surface bands.

All four native reviews read actual deposited model, support and brim beads
against the 20 mm bed border. They also read the fine/transition bands,
show-face contacts, local dense-host deposition, tie openings and removable
groove ribbons where applicable. Support decisions retain Tree(auto)/Default.
The lid's constrained branch growth keeps its automatic supports within the
bed border.

Follow the [support-removal instructions](support-removal.json) on each loose,
unloaded part before installing hardware. These include every small support
body without interface labels. Use the tiny flathead already used successfully
in the rear receiver cavities; cut larger branches into pieces and withdraw
them through the named open mouths. This reading establishes access, while
actual removal effort belongs to the printed article.

The [geometry review](geometry-review.json) records the exact approved cap
hashes and current closed print meshes. The full native assemblies, installed
scene and installation views carry the finished parts, with unrelated bodies
retained. The [assembly and service sequence](../../README.md#assembly-and-service)
includes the PISCO fore-loading path and receiver tool access. The lower
cartridge uses the complete paired, pointed-wing geometry and prints with
source +Y as its build axis.
