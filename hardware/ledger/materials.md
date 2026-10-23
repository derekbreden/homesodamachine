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
sealing thimble has a cylindrical wall and a cap; a copper-slot cover is a plastic
cover around a copper tube. Identification plates and collars are named for the
port or line they mark. Fitted tubes are named for their circuit and connection
role, with stock details where useful.

| Material | Canonical description | Naming role |
| --- | --- | --- |
| HSM-000268 | Faucet lever · PET-GF | Shared faucet part with its print stock |
| HSM-000090 | Faucet tube sealing thimble · TPU 85A | Physical form, sealing role and stock |
| HSM-000023 | Cold-core copper-slot covers | Covers supplied as a two-piece set |
| HSM-000277 | Flavor A pump suction flex tube · 1/4 inch black LLDPE | Circuit, connection role and stock |
| HSM-000055 | Interstate Pneumatics WR1105 CO₂ secondary regulator | Installed manufacturer identity and function |

CAD body keys, route IDs and file paths identify engineering representations.
The component inspector shows the body key alongside the material name and
number, so repeated occurrences and geometry reports remain distinguishable.
`aliases` carries searchable bench vocabulary and those engineering identifiers.
Description edits retain the material number, geometry bindings and physical
acceptance records.

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
the machine catalog includes modeled parts and selected service hardware, with
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

`contexts: [{"material": "HSM-000001"}]` allows an assembly with no separate
model to be inspected in a containing material's model. The cartridge uses the
soda machine as its context; the vessel and magnetic level float use the cold
core. Context inspection keeps the selected assembly's own identity and BOM and
highlights its represented contents. A representation may also specify
`context: true` to use a particular enclosing model file. Context representations
do not allocate that enclosing model's identity to the contained material.

Some parts, including embedded magnets and cartridge fasteners, have no individual
geometry in the containing model. The two ASSE outlet fittings share a combined
envelope, as do the constituents of each pump fitting chain. Their BOM quantities
and document links remain available without claiming independently selectable
geometry.

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
| HSM-000161 — Pump cartridge assembly | Both complete prepared pumps with their four clamped LLDPE tubes, lower cradle, top clamp, female contact half, moving motor leads and Fastons, four printed-in SB443-IN magnets, and mounting hardware. The fixed male half, the four pump tees in the tee wall, the collet plate, the upper tubes and lower returns, and the four mating magnets stay in the appliance. The customer replaces complete prepared pumps under the cap; the dock retains its physical qualification scope. | [Cartridge build](../assembly/internal-plumbing.md), [service boundary](../service/pump-replacement.md) |
| HSM-000004 — Carbonator vessel | Vessel, port fittings, pressure relief, captive float and welded guide rod. The other two floats and guide rods belong to the cold core's reservoir installation. | [Vessel build](../assembly/pressure-vessel.md) |
| HSM-000087 — ASSE 1022 water-fitting assembly | Backflow preventer and four inlet/outlet fittings, between its two tube collets and bare atmospheric vent. The vent sleeve, return tube and mounting hardware belong to the machine. | [Fitting assembly](../reference/asse1022-assembly/README.md) |
| HSM-000058 — Water-pump discharge check valve | One HLGHLG B0FSSZS6HH check between its two push-connect collets. Tubes, the pump's elbows and installation hardware belong to the machine. | [Water-path assembly](../assembly/internal-plumbing.md), [check-valve scope](../reference/hlghlg-check-valve/README.md) |

The KPHM600-SW3B17 pump's fitted representation lives in the `kamoer-kphm400`
reference directory. The water-pump check fitting model lives in the
`hlghlg-check-valve` directory and is installed with the G Ganen water pump.
Manufacturer identity and current assembly descriptions are stated independently
of those model paths.
The WR1105 secondary regulator uses the scanned WR1110 exterior representation;
its [fit and representation scope](../reference/wr1110-regulator/README.md) remains
attached to the material record.
