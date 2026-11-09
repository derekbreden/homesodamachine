# Stock and build records

[`stock.json`](stock.json) connects material numbers to dated usable-stock
evidence and records measured assembly work for [Build from stock](https://homesodamachine.com/build).
The material explorer's Stock tab opens the same plan for its selected part.

## Available materials

The opening balances come from [`batch-forecast.json`](batch-forecast.json).
Its credits are dated estimates, including reusable development parts. The
current BOM supplies the inputs of each part, and the material catalog supplies
the contents of each assembly. Current purchase receipts and explicitly
identified stock use `resources`, `bindings` and `observations` in `stock.json`.
An observation replaces a balance and carries its date, evidence and uncertainty.
An ordered quantity remains incoming until a receipt is recorded.

The plan aggregates shared stock across every occurrence in the requested
assembly. A donor yields its recorded kit of parts; those outputs share the
donor requirement. Printed material follows the part's mass allocation, color
and the forecast's process allowance. Mixed terminal sizes, stock recorded in
incompatible cutting units and unrecorded manufacturing inputs remain visible
as missing records. An unknown quantity receives no stock credit.

The reported capacity counts materials. Assembly instructions and their
physical qualification records establish the fabrication and fit requirements.
Each request starts with the same balances; browsing plans reserves nothing.

## Completed parts and assemblies

A material observation uses `material`, `onHand`, `reserved`, `asOf`, `sources`
and `estimated`. Use `finish` when the stock applies to a particular finish.
The quantity is usable loose stock of that numbered material, including a
completed assembly when it is held as a unit. Stock already in an assembly is
represented by the completed assembly's balance. Its components and consumed
raw materials receive no second credit.

The planner uses completed stock before expanding the remaining demand into
components and manufacturing inputs. A missing completed-stock record offers
no completed-stock credit; a recorded manufacturing input can still supply
the work to make it. A physical count can replace an acquired-pack estimate.
Reservations reduce availability while retaining the physical count.

## Actual build effort

`builds` records completed physical work by material number. Each run carries
`material`, `quantity`, `attendedMinutes`, `completedAt`, `sources` and a short
`note`; a finish-specific run also carries `finish`. Record hands-on time for
the stated scope and describe any rework or preparation it includes. Equipment
waits belong to machine time. No elapsed agent or CAD-build duration is assembly
labor.

The website shows measured attended work beside the labor ledger's allocated
planning estimate. No measured run is inferred from that estimate. A work
record establishes effort; an accompanying stock observation establishes the
remaining usable balance.
