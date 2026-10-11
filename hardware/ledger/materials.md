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

The machine's composition is partial. Remaining material identities include the
keystone jack, gas-path adapters, grip covers, tee-carrier springs, inlet tube
collars and funnel drain stub. Their models and build records remain available
through the explorer's CAD search and assembly documents. The harvested condenser
and fan are recorded as one donor unit; their individual service contents are
outside the recorded scope.

## Recorded assembly boundaries

| Material | Contents and interfaces | Authority |
| --- | --- | --- |
| HSM-000161 — Pump cartridge assembly | Both complete pumps, lower cradle, top clamp, four LLDPE connecting ends, female contact half, moving motor leads and Fastons, enclosed retention ring and mounting hardware. The fixed male half, tee carrier, release plate and tees stay in the machine. The cartridge is the planned separately purchasable service assembly; the intended customer procedure retains its qualification scope. | [Cartridge build](../assembly/internal-plumbing.md), [service boundary](../service/pump-replacement.md) |
| HSM-000004 — Carbonator vessel | Vessel, port fittings, pressure relief, captive float and welded guide rod. The other two floats and guide rods belong to the cold core's reservoir installation. | [Vessel build](../assembly/pressure-vessel.md) |
| HSM-000087 — ASSE 1022 water-fitting assembly | Backflow preventer and four inlet/outlet fittings, between its two tube collets and bare atmospheric vent. The vent sleeve, return tube and mounting hardware belong to the machine. | [Fitting assembly](../reference/asse1022-assembly/README.md) |
| HSM-000045 — Water-pump suction fitting assembly | MAACFLOW barb adapter and PP450822E, between barb tip and tube collet. | [Water-path assembly](../assembly/internal-plumbing.md) |
| HSM-000058 — Water-pump discharge fitting assembly | MAACFLOW barb adapter, GASHER check valve and PP450822E, between barb tip and tube collet. Hose and installation hardware belong to the machine. | [Water-path assembly](../assembly/internal-plumbing.md), [check-valve scope](../reference/gasher-check-valve/README.md) |

The KPHM600-SW3B17 pump's fitted representation lives in the `kamoer-kphm400`
reference directory. The two water-pump fitting models live in `seaflo-*`
directories and are installed with the G Ganen water pump. Manufacturer identity
and current assembly descriptions are stated independently of those model paths.
