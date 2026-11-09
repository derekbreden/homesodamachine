# Material catalog

[`materials.json`](materials.json) records the identities, composition, models and
documents shown by the [material explorer](https://homesodamachine.com/3d). The
explorer shows the PDFs among a material's `documents`; Markdown, scripts and
records there and in `bom.source` are for agents and are not shown.
An assembly's contents can include other assemblies; quantities and ancestry follow
those relationships through every level.

## Identity

Each material has a permanent `id`, a readable `description` and a `kind`. The
`id` is `HSM-` and the number padded to four digits, as in `HSM-0001`; past
`HSM-9999` the number takes a fifth digit and the earlier ids keep theirs. New
records take the next unused number above the highest allocated number. Existing numbers stay with their material when descriptions, manufacturer
numbers or file paths change. Allocated numbers are never reused.

`aliases` and `manufacturer_number` are searchable vocabulary, alongside the id,
description and model file paths. Search also reads the cost lines on each part:
a bought part is found by its purchase listing and ASIN, and stock and supplies
are results of their own that open the Cost tab of a part using them. Case,
plurals and the space between a size and its unit do not change a match; the
synonyms search treats as one word are in
[`materials.js`](../../web/contracts/materials.js). A material can have
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
| HSM-0268 | Faucet lever · PET-GF | Shared faucet part with its print stock |
| HSM-0090 | Faucet tube sealing thimble · TPU 85A | Physical form, sealing role and stock |
| HSM-0277 | Flavor A pump suction flex tube · 1/4 inch black LLDPE | Circuit, connection role and stock |
| HSM-0331 | PISCO RVFUP1/4-1/4-0.3 preset regulator · CO₂ secondary · 0.3 MPa | Installed manufacturer identity, function and setting |

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
reference documents. A published PDF also needs its `.pdf.json` sidecar of
`title`, `subtitle` and `pages`, with no cover image; PDFs carried by the
checkout are registered in `web/contracts/documents.js` so an artifact restore
preserves the committed edition.

## Contents and quantities

`bom.items` contains direct child occurrences. Each names a `material`, `quantity`
and `unit`. The same material can occur in several assemblies. Quantity is per
immediate parent; the explorer multiplies quantities along each path to report
the quantity in the assembly being inspected. `where used` follows the same
occurrences toward every recorded parent and ancestor.

An assembly is counted through its parent occurrence. Its components occur within
that assembly. Purchased pack sizes, delivered costs, supplies and stock
allowances remain in [`bom.md`](bom.md); its rows reach part numbers through
their cost tags ([Costs](#costs)). Each catalog BOM's `scope` states its
coverage. The machine catalog includes its parts, fasteners and bench harnesses;
wire, tubing stock and supplies are costed on the parts and assemblies that use
them rather than listed as contents.

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
core's prefix in the soda machine is `cold-core/`. A binding that begins `../`
names geometry the containing model draws: each tube the cold core pots is one
cold-core part, and the machine's model draws its free end above the lid. Multiple solids can represent
one purchased material, and a combined envelope can represent several materials.
Physical quantities come from the parts and assembly records.

`contexts: [{"material": "HSM-0001"}]` allows an assembly with no separate model
to be inspected in a containing material's model. The pump mount assembly uses
the soda machine as its context; the vessel uses the cold core. Context inspection keeps the selected assembly's own identity and BOM and
highlights its represented contents. A representation may also specify
`context: true` to use a particular enclosing model file. Context representations
do not allocate that enclosing model's identity to the contained material.

Some cataloged hardware has no individual geometry in the containing model. Their BOM quantities and document links remain available
without claiming independently selectable geometry.

Every named body in the cataloged machine, faucet, cold-core and build-tool
assembly views maps to a material. Routed tube sections share their fitted run's
identity; distinct cut runs have distinct numbers. Cabinet stock and cut lengths
are established by the routing and build records. Supplies and bulk stock have
no geometry or contents entry; their cost sits on the parts and assemblies that
use them.

Installation context and tool workpieces carry numbered records and explicit
relationships outside the supplied product BOM. The kitchen countertop is an
installation reference; the rotator's tube and insertion tool's tubing and seal
are workpieces. They can be inspected without being counted as parts of the tool.

A component with no standalone STEP opens the existing geometry in its owning
assembly through a `?component=` view. That view allocates no second identity or
CAD file. Its material record, containing assemblies and documents remain the
same. Direct component-source lookup uses the catalog's canonical model first.

The faucet lever is HSM-0268: one physically accepted printed shape, shared by
both faucet styles and the standalone model. Its installation representation uses
the authored nominal rest placement; physical fit/function evidence retains its
recorded scope.

## Costs

`cost_root` names the finished unit the ledgers price: HSM-0340, the machine,
faucet and install kit as they ship. Every data row of [`bom.md`](bom.md) and
every operation of [`labor.md`](labor.md) carries a hidden
`<!--parts HSM-0010 HSM-0013:2-->` tag naming the part numbers its dollars
or minutes belong to:

- a purchased part's row names that part, and its share is the part's price;
- a row of stock — tubing, wire, filament, copper — names the parts cut,
  printed or formed from it, weighted by what each uses;
- a row of supplies names the assembly or part that consumes them;
- an operation names the part it makes or the assembly it puts together.

A row's amount is divided among its parts in the finished unit by the weights
after the colons, or by each part's quantity in the unit when it has none, and
then across that part's pieces. A part costs its own share plus each child's
cost times the child's quantity, so an assembly carries its contents and the
work and supplies of putting it together, and the finished unit's roll-up
equals both ledgers' totals. A part outside the default build, such as an
Industrial faucet part, is costed in the configuration that contains it.

A part made in runs carries its operation's [run](labor.md): a float's labor is
its plate's setup shared across the batch, plus its own magnet. A bought part
carries the smallest lot the [batch forecast](batch-forecast.md) buys it in.
Both sit faintly under the line they price on the explorer's Cost tab.

[`web/lib/part-costs.js`](../../web/lib/part-costs.js) allocates; the explorer
and the [cost page](https://homesodamachine.com/cost#by-part) show the result.
`node web/scripts/part-costs.mjs` lists what is unallocated and where the
catalog's piece counts disagree with the ledger; `--tree` prints the costed
BOM, and a part number prints that part's cost.

## Stock and assembly work

[Build from stock](https://homesodamachine.com/build) follows the catalog's
assembly quantities and the current BOM's manufacturing inputs. The material
explorer's Stock tab opens that plan for the selected material.
[`stock.md`](stock.md) defines usable balances, completed assembly stock,
reservations and measured attended work; [`stock.json`](stock.json) holds
observations, physical activity and the explicit identity bindings to inventory
evidence. Completion consumes its recorded inputs and adds completed stock in
the same entry. Costing and availability read the authored physical BOM
quantities; purchasing credits completed stock before expanding those inputs.

## Recorded assembly boundaries

The prepared enclosure sections, refrigeration loop and removable funnel are
numbered assemblies in the machine BOM. Their contents follow the bench and
closing order in [mechanical assembly](../assembly/enclosure-mechanical.md),
[plumbing](../assembly/internal-plumbing.md) and
[wiring](../assembly/electronics-bay.md). Bare printed sections retain their own
numbers beneath the prepared assemblies. Final closure hardware, the display
and connections made through the funnel opening remain on the machine.

| Material | Contents and interfaces | Authority |
| --- | --- | --- |
| HSM-0547 — Enclosure back top assembly | Prepared rear section with the water and gas groups, rear ports and identification plates, meter, PSU, relays, mains junctions and rear wiring. The core-owned continuous tubes and final electrical handoffs meet it during installation. | [Mechanical assembly](../assembly/enclosure-mechanical.md), [rear plumbing](../assembly/internal-plumbing.md), [rear wiring](../assembly/electronics-bay.md) |
| HSM-0548 — Enclosure front top assembly | Prepared upper front section with the retained pumps, valve manifold, fitted tubes, commons and prepared looms. Reservoir and rear-port ends remain free for closing; display installation follows closure. | [Front manifold](../assembly/internal-plumbing.md), [mechanical assembly](../assembly/enclosure-mechanical.md) |
| HSM-0549 — Enclosure front bottom assembly | Lower front section with its heat-set inserts, gas sensor and sensor harness, ready to receive the connected refrigeration assembly. | [Mechanical assembly](../assembly/enclosure-mechanical.md) |
| HSM-0550 — Enclosure back bottom assembly | Lower rear section with its seam-anchor inserts and open sliding interfaces. | [Mechanical assembly](../assembly/enclosure-mechanical.md) |
| HSM-0551 — Flavor-fill funnel assembly | Removable frame with its drain cradle, outlet fittings, V-B feed tube, silicone funnel and cover. Frame screws and the V-B connection are final assembly work. | [Mechanical assembly](../assembly/enclosure-mechanical.md), [plumbing](../assembly/internal-plumbing.md) |
| HSM-0552 — Refrigeration assembly | Cold core, compressor, condenser, connecting refrigerant lines, service fittings, thermal cutoff and prepared compressor lead. The loop stays connected while the enclosure is assembled around it. | [Refrigeration](../assembly/refrigerant-loop.md), [mechanical assembly](../assembly/enclosure-mechanical.md) |
| HSM-0161 — Pump mount assembly | Both prepared pumps with their four clamped LLDPE tubes, the snap-fit lower retainer, and the Fastons that land DC-5 on the motor tabs. Two full-depth integral wings engage front-top’s flank receivers and hold the lower retainer against the fitted upper half, whose broad stock continues into the display housing and roof. The prepared unit loads motor-first from below on loose front-top, before the pump tees and valve plumbing; pump and display wires share one rear passage. Physical fit and retention retain their qualification scope. | [Pump installation](../assembly/internal-plumbing.md), [pump mount](../printed-parts/enclosure/pump-dock/README.md) |
| HSM-0004 — Carbonator vessel | Vessel, port fittings, pressure relief, captive float, welded guide rod and top-register float stop. The other two floats and guide rods belong to the cold core's reservoir installation. | [Vessel build](../assembly/pressure-vessel.md) |
| HSM-0173 — Multiplex 19-0897 ASSE 1022 backflow preventer | The bare purchased body. Its two TPU 85A straight cuffs (HSM-0334, HSM-0335), the branch stem tee in the outlet cuff, the vent sleeve, return tube and saddles belong to the machine. | [Water and gas assembly](../assembly/internal-plumbing.md), [straight cuffs](../printed-parts/asse-straight-cuffs/README.md) |
| HSM-0058 — neoFit ACHV44-E single check valve | One 1/4-inch push-connect check with a nominal 0.3 psi crack pressure, used at both the pump discharge and downstream of the PISCO CO2 regulator. Tubes, elbows and installation hardware belong to the machine. | [Water and gas assembly](../assembly/internal-plumbing.md), [check-valve scope](../reference/neofit-achv44-check/README.md) |

The KPHM600-SW3B17 pump's fitted representation lives in the `kamoer-kphm400`
reference directory. Both purchased check positions use the shared
`neofit-achv44-check` reference.
Manufacturer identity and current assembly descriptions are stated independently
of those model paths.
The PISCO secondary regulator uses the envelope modeled from its OEM catalog; its
[representation scope](../reference/compact-inline-candidates/README.md) remains
attached to the material record.
