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

Search favors the object named by the canonical description over connected
parts that mention it: a water regulator leads its inlet tube and snap cap.
Variant suffixes supply qualifiers; a supplier-code opening segment uses the
following descriptive segment to identify its object. Complete names, aliases
and manufacturer numbers retain their identity value. Human aliases can supply
an alternate object name, while CAD paths and route aliases remain context.
Ambiguous peers retain a stable alphabetical order. Browser search and the
local part finder share this ranking.

Search presents each material through its canonical record. Navigation into an
assembly's model sits beneath that record. Installed-location choices expand
for repeated materials when their BOM quantities and model bindings identify
the placements. Separate solids belonging to a material share the installed
view action; their CAD body names remain geometry identifiers.

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
`placements` groups the bodies of each individually modeled copy and can give
each placement a readable `label`. A compound part keeps its pieces together in
that body set. Placement bindings use the same frame as `bodies`; the material's
geometry includes both forms of binding.

The required count stays in `quantity`. Placements can cover only the drawn
copies of a partly modeled item; undrawn quantities do not create locations.
Stock and cost calculations use the BOM quantities independently of placements.
Lengths and other stock measures do not imply a count of installed copies.

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

A related material with explicit `bodies` can use that relationship as its
inspection context. An installation-line assembly's relationship supplies its
geometry when the machine model draws it; its install-kit BOM supplies quantities.

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

The bench handoffs follow the existing build path. A completed handoff moves
as a unit into the next operation, with free tubes and conductors supported.
The float and fitted relief assembly enter the carbonator; the instrumented
carbonator and closed reservoirs enter the insulated core; the equipped core
enters the connected refrigeration assembly.

| Material | Completed handoff | Next assembly |
| --- | --- | --- |
| HSM-0032 — Magnetic level float | Printed body with its captive magnet | Carbonator or fitted reservoir |
| HSM-0565 — Carbonator bottom endcap and guide assembly | Machined cap with its tacked guide rod | HSM-0567 vessel weldment |
| HSM-0566 — Carbonator top endcap and stop assembly | Machined cap with its tacked upper stop | HSM-0567 vessel weldment, after the float enters |
| HSM-0567 — Carbonator vessel weldment | Closed tube, prepared caps and captive float | Inspection, proof and cleaning, then HSM-0004 port fitting |
| HSM-0553 — Carbonator pressure-relief assembly | Elbow, relief valve and shroud with its seal cured | HSM-0004 carbonator |
| HSM-0004 — Carbonator vessel | Welded vessel, captive float and guides, port elbows and relief assembly | HSM-0554 instrumented carbonator and coil |
| HSM-0554 — Instrumented carbonator and coil assembly | Carbonator, bonded coil, probes, reed bridge and reeds, and earth lead | HSM-0557 insulated core |
| HSM-0568 — Flavor reservoir cap assembly · channel A | Cap with captured liquid and air grips | HSM-0555 fitted reservoir A |
| HSM-0569 — Flavor reservoir cap assembly · channel B | Cap with captured liquid and air grips | HSM-0556 fitted reservoir B |
| HSM-0555 — Fitted flavor reservoir assembly · channel A | Closed reservoir with its gasket, float, guide, tube grips and closure hardware | HSM-0557 insulated core |
| HSM-0556 — Fitted flavor reservoir assembly · channel B | Closed reservoir with its gasket, float, guide, tube grips and closure hardware | HSM-0557 insulated core |
| HSM-0348 — Reservoir A reed harness · J6 | Soldered and laced column with its reservoir reeds and free board ends | HSM-0557 insulated core, then board housing completion |
| HSM-0349 — Reservoir B and carbonator reed harness · J7 | Soldered reservoir B column with its paired ribbon and free carbonator branch | HSM-0557 insulated core, joining the instrumented vessel's reed pair |
| HSM-0557 — Insulated cold-core assembly | Cured insulation, instrumented carbonator, fitted reservoirs, routed continuous tubes, dry reed columns and looms, and closed casing | HSM-0003 equipped cold core |
| HSM-0558 — Backflow-preventer threaded assembly | TAP connector, reducing coupling, ASSE body, flare adapter and stem reducer made up together | HSM-0547 back-top |
| HSM-0559 — CO₂ secondary regulator and check assembly | PISCO regulator with its outlet stem check connected | HSM-0547 back-top |
| HSM-0560 — Water-pump discharge joint assembly | Reinforced cuff, trimmed reducer, stem clamp, fold and check | HSM-0003 equipped cold core, after the bare pump is seated |
| HSM-0570 — Water-pump suction joint assembly | Reinforced cuff, trimmed reducer, stem clamp and receiving elbow | HSM-0003 equipped cold core, after the bare pump is seated |
| HSM-0561 — Flavor A fore-valve assembly · Y-C to V-E | Tee, upper tube and fore valve | HSM-0548 front-top |
| HSM-0562 — Flavor A fore-valve assembly · Y-D to V-F | Tee, upper tube and fore valve | HSM-0548 front-top |
| HSM-0563 — Flavor B fore-valve assembly · Y-F to V-H | Tee, upper tube and fore valve | HSM-0548 front-top |
| HSM-0564 — Flavor B fore-valve assembly · Y-G to V-I | Tee, upper tube and fore valve | HSM-0548 front-top |
| HSM-0571 — Faucet valve insert assembly | Donor valve, attached lever, thimble and dispensing tube | Faucet shell installation, before the supply connection |
| HSM-0572 — Filtered installation water-line assembly | Tee, jumper, filtered run and TAP collar | HSM-0341 installation kit |
| HSM-0573 — Primary CO₂ regulator and tether assembly | Regulator, outlet adapter, red tether and CO₂ collar | Acceptance, then HSM-0341 installation kit |

The [cold-core procedure](../assembly/cold-core.md),
[vessel procedure](../assembly/pressure-vessel.md),
[relief procedure](../printed-parts/cold-core/prv-shroud/README.md) and
[plumbing procedure](../assembly/internal-plumbing.md) own the handoff sequence.
Reservoir tubes are fitted after the closed reservoirs enter their casing
pockets. The water pump enters its lid seat bare; its prepared discharge joint
is fitted afterward. Cure, test and calibration evidence stays with the actual
article and operation.

The faucet's **HSM-0106 tubing cut set** contains **HSM-0574 dispensing tube**
and **HSM-0575 supply tube**. Product BOMs place these cuts at their actual
handoffs: the dispensing cut in the valve insert and the supply cut in the
completed faucet. The cut set remains searchable as their preparation set.
Reed-column manufacturing inputs are ribbon, reeds and supplies; the completed
column is the assembly output.

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
| HSM-0161 — Fixed pump assembly | The installed pump pair with prepared stubs, motor receptacles and independent flange retainers. Each pump loads motor-first into its own integral guide on loose front-top and is secured from below. The actual seated tees set the stubs before their clamps are tightened. | [Pump installation](../assembly/internal-plumbing.md), [pump mount](../printed-parts/enclosure/pump-dock/README.md) |
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
