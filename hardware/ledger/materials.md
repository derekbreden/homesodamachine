# Material catalog

[`materials.json`](materials.json) records the identities, composition, models and
documents shown by the [material explorer](https://homesodamachine.com/3d).
An assembly's contents can include other assemblies; quantities and ancestry follow
those relationships through every level.

## Identity

Each material has a permanent `HSM-000001`-format `id`, a readable `description`
and a `kind`. New records take the next unused number above the highest allocated
number. Existing numbers stay with their material when descriptions, manufacturer
numbers or file paths change. Allocated numbers are never reused.

`aliases` and `manufacturer_number` are searchable vocabulary. A material can have
several model files and documents. A numbered assembly describes a coherent unit;
its identity alone makes no promise about separate stocking, sale or replacement.
Build and service documents establish those meanings and their acceptance scope.

## Names and descriptions

`description` is the canonical material name in search results, BOM rows,
component selection, Find results, model titles and navigation. It must make sense on its own.
Use sentence case and the part's actual form and function. Add context when it
distinguishes the part: **Faucet lever**, **Machine display gasket** and
**Weld rotator motor carriage**. Assembly instructions can use **lever** or
**gasket** once the surrounding text establishes which part they mean.

Use a ` · ` suffix for a distinguishing style, channel, position, size or stock.
Name style-specific faucet parts **Sculpted faucet …** or **Industrial faucet …**;
shared parts use **Faucet …**. Flavor channels use **A** and **B**, matching the
[fluid topology](../topology/fluid-topology.md). Standard hardware uses its type,
dimensions and useful manufacturer designation, such as **M3 × 10 socket-head
screw**. Bought parts use the manufacturer identity specified by the current
build and purchasing records.

Names describe the supplied part and its present purpose. Construction methods,
scan provenance and fabrication instructions belong in its documentation. A
sealing thimble has a cylindrical wall and a cap; a tube restraint is a plastic
cover around a copper tube. Identification plates and collars are named for the
port or line they mark. Fitted tubes are named for their circuit and connection
role, with stock details where useful.

| Material | Canonical description | Naming role |
| --- | --- | --- |
| HSM-000268 | Faucet lever · PET-GF | Shared faucet part with its print stock |
| HSM-000090 | Faucet tube sealing thimble · TPU 85A | Physical form, sealing role and stock |
| HSM-000277 | Flavor A pump suction flex tube · 1/4 inch black LLDPE | Circuit, connection role and stock |
| HSM-000331 | PISCO RVFUP1/4-1/4-0.3 preset regulator · CO₂ secondary · 0.3 MPa | Installed manufacturer identity, function and setting |

CAD body keys, route IDs and file paths identify engineering representations.
The component inspector shows the body key alongside the material name and
number, so repeated occurrences and geometry reports remain distinguishable.
`aliases` carries searchable bench vocabulary and those engineering identifiers.
Description edits retain the material number, geometry bindings and physical
acceptance records.

## Engineering drawings

Engineering drawings belong in the part's own `documents` with
`kind: "engineering-drawing"`, a readable `title`, and the PDF's hardware-relative
`path`. The material explorer features these above the relationship tabs and
offers a 3D/Drawing switch. Drawings inherited from containing assemblies remain
reference documents. A published PDF also needs its `.pdf.json` sidecar; PDFs
carried by the checkout are registered in `web/contracts/documents.js` so an
artifact restore preserves the committed edition.

## Contents and quantities

`bom.items` contains direct child occurrences. Each names a `material`, `quantity`
and `unit`. The same material can occur in several assemblies. Quantity is per
immediate parent; the explorer multiplies quantities along each path to report
the quantity in the assembly being inspected. `where used` follows the same
occurrences toward every recorded parent and ancestor.

An assembly is counted through its parent occurrence. Its components occur within
that assembly. Purchased pack sizes, delivered costs, fabrication consumables and
stock allowances remain in [`bom.md`](bom.md). Its per-unit costing scope differs
from this composition catalog. Each catalog BOM's `scope` states its coverage;
the machine catalog includes modeled parts and selected hardware, with
remaining wiring, tubing and fasteners described by the build and cost records.

`bom.source` links the record that establishes the contents. `bom.imports` reads
an existing structured parts list through explicit material mappings. The tube
insertion tool imports quantities and roles from its own
[`parts.json`](../printed-parts/fixtures/tube-insertion/parts.json) when the catalog
is served. `parts` and `hardware` mappings can place an item in the BOM or give it
a separate `relationship`.

An item's `when` fields select an applicable variant, such as a faucet finish.
Quantities and geometry bindings follow the selected variant.

`relations` records connections such as `tool-for`, `used-with` and `variant`.
Tools, workpieces and associated equipment carry their own relationships and
identities. Their quantities belong in a product's contents only when they are
part of that product.

## Geometry and context

`models` lists representations belonging to the material. BOM-item `bodies`
names the geometry representing that occurrence, relative to its parent's model.
`prefix` carries a child's model namespace into its containing model; the cold
core's prefix in the soda machine is `cold-core/`. Multiple solids can represent
one purchased material, and a combined envelope can represent several materials.
Physical quantities come from the parts and assembly records.

`contexts: [{"material": "HSM-000001"}]` allows an assembly with no separate model
to be inspected in a containing material's model. The pump mount assembly uses
the soda machine as its context; the vessel and magnetic level float use the cold
core. Context inspection keeps the selected assembly's own identity and BOM and
highlights its represented contents. A representation may also specify
`context: true` to use a particular enclosing model file. Context representations
do not allocate that enclosing model's identity to the contained material.

Some cataloged hardware has no individual geometry in the containing model. Their BOM quantities and document links remain available
without claiming independently selectable geometry.

Every named body in the cataloged machine, faucet, cold-core and build-tool
assembly views maps to a material. Routed tube sections share their fitted run's
identity; distinct cut runs have distinct numbers. Cabinet stock and cut lengths
are established by the routing and build records. Commercial consumables and
unmodeled hardware remain in the cost and assembly documents.

Installation context and tool workpieces carry numbered records and explicit
relationships outside the supplied product BOM. The kitchen countertop is an
installation reference; the rotator's tube and insertion tool's tubing and seal
are workpieces. They can be inspected without being counted as parts of the tool.

A component with no standalone STEP opens the existing geometry in its owning
assembly through a `?component=` view. That view allocates no second identity or
CAD file. Its material record, containing assemblies and documents remain the
same. Direct component-source lookup uses the catalog's canonical model first.

The faucet lever is HSM-000268: one physically accepted printed shape, shared by
both faucet styles and the standalone model. Its installation representation uses
the authored nominal rest placement; physical fit/function evidence retains its
recorded scope.

## Recorded assembly boundaries

| Material | Contents and interfaces | Authority |
| --- | --- | --- |
| HSM-000161 — Pump mount assembly | Both prepared pumps with their four clamped LLDPE tubes, the snap-fit lower retainer, and the Fastons that land DC-5 on the motor tabs. Two full-depth integral wings engage front-top’s flank receivers and hold the lower retainer against the fitted upper half, whose broad stock continues into the display housing and roof. The prepared unit loads motor-first from below on loose front-top, before the pump tees and valve plumbing; pump and display wires share one rear passage. Physical fit and retention retain their qualification scope. | [Pump installation](../assembly/internal-plumbing.md), [pump mount](../printed-parts/enclosure/pump-dock/README.md) |
| HSM-000004 — Carbonator vessel | Vessel, port fittings, pressure relief, captive float and welded guide rod. The other two floats and guide rods belong to the cold core's reservoir installation. | [Vessel build](../assembly/pressure-vessel.md) |
| HSM-000173 — Multiplex 19-0897 ASSE 1022 backflow preventer | The bare purchased body. Its two TPU 85A straight cuffs (HSM-000334, HSM-000335), the branch stem tee in the outlet cuff, the vent sleeve, return tube and saddles belong to the machine. | [Water and gas assembly](../assembly/internal-plumbing.md), [straight cuffs](../printed-parts/asse-straight-cuffs/README.md) |
| HSM-000058 — neoFit ACHV44-E single check valve | One 1/4-inch push-connect check with a nominal 0.3 psi crack pressure, used at both the pump discharge and downstream of the PISCO CO2 regulator. Tubes, elbows and installation hardware belong to the machine. | [Water and gas assembly](../assembly/internal-plumbing.md), [check-valve scope](../reference/neofit-achv44-check/README.md) |

The KPHM600-SW3B17 pump's fitted representation lives in the `kamoer-kphm400`
reference directory. Both purchased check positions use the shared
`neofit-achv44-check` reference.
Manufacturer identity and current assembly descriptions are stated independently
of those model paths.
The PISCO secondary regulator uses the envelope modeled from its OEM catalog; its
[representation scope](../reference/compact-inline-candidates/README.md) remains
attached to the material record.
