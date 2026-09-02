# Future

This directory is what the project is for and where it is going. This page carries the
vision and the plan; [`pie-in-the-sky/`](/future/pie-in-the-sky/) carries the desires that
have no plan yet. Everything else in the tree describes what is: the machine as it stands
is [`/hardware/README.md`](/hardware/README.md), who it is for is
[`/marketing/target-market.md`](/marketing/target-market.md).

## What the machine is for

A person walks to their kitchen sink, turns a handle, and a glass fills with Diet Mountain
Dew — as cold and as carbonated as the can, and colder and fizzier than most. They never
buy a can again. That is the whole of it.

The alternatives on the market do not do this. Canned soda means hauling twenty-four to
forty-eight cans a week from store to car to kitchen, and running out. Home carbonation
means carbonating warm water into a bottle that is flat before it reaches the glass, which
is why the machines sell enormously and get used twice. The gap is refrigeration: cold water
holds carbonation and warm water does not, and no consumer product refrigerates and
carbonates and dispenses on demand.

The flavor is not a substitute. Pepsi sells its own formulations as SodaStream-compatible
concentrate to anyone, so a machine that injects it dispenses the brand rather than an
approximation of it. What is missing is the machine.

## What done looks like

Three marks, in order. Each one is finished when a physical thing exists, not when a
document says so.

**One. The machine pours in Derek's kitchen.** One appliance, built end to end from this
tree — carbonator welded and hydro-tested, loop brazed and charged, core foamed, box
printed, board flashed, faucet plumbed through the counter — standing under his own sink
where the prototype stands now, pouring both flavors daily for a month without being
opened. Until this exists the tree describes a machine that has never been built once.

**Two. Ten machines in ten kitchens.** Ring 1 of
[`target-market.md`](/marketing/target-market.md) "The internal plan": the first ten units
go to people Derek knows, or one degree out, at whatever price moves them. The deliverable
is not the revenue. It is ten machines in daily use by people who did not build them,
generating failures Derek did not predict, and supplier relationships priced at a run of
fifty. Ring 1 closes when the tenth unit is installed and the design is tighter than what
unit one received.

**Three. The Founder Edition run.** Units 001–050 at $7,500, numbered and signed, one
person building them at roughly a dozen a year. This is the public plan and the price
anchor; it opens when the machine has been built enough times that the build is boring.

## What stands between here and the first mark

Every subsystem is specified, costed, and drawn. What is owed is the doing of it, once
each, in the order [`/hardware/README.md`](/hardware/README.md) "Build order" gives.

| Owed | Where the procedure is |
|---|---|
| The first production closure weld, PT-checked, hydro-tested, passivated | [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) |
| The first refrigerant loop brazed to a carbonator and charged | [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) |
| The first cold core foamed in place around a welded carbonator | [`cold-core.md`](/hardware/assembly/cold-core.md) |
| The whole enclosure printed as one set of quadrants that close on each other | [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) |
| One appliance plumbed, wired, commissioned, and burned in for eight hours | [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md), [`wiring.md`](/hardware/assembly/wiring.md), [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) |
| One faucet installed through a real countertop by the customer's own path | [`quickstart/`](/hardware/quickstart/) |

None of these are open design questions. They are the hours in
[`labor.md`](/hardware/ledger/labor.md) — ten attended hours per unit — and the machine
hours in [`machine-time.md`](/hardware/ledger/machine-time.md), spent for the first time.

## What the tree is for

The repository is a manufacturing system, and that is deliberate. It cuts the parts, prices
them, names them, checks itself, and publishes what it holds, so that the fiftieth unit
costs what the ledgers say and not what the first one taught. A generator that draws a part
also writes its own documentation, its figures, and the card the operator builds from; a
check that can be automated is, so that a fact cannot rot quietly.

The risk this creates is the obvious one. A tree that can be improved forever will be, and
improving it feels like progress in a way that welding does not. The marks above exist to
name the difference. Nothing in this repository is finished by a commit.

## The dates

The tree derives its own numbers — cost, mass, hours, clearance — but it cannot derive a
date, because a date is a promise about Derek's own weeks and nobody else can make it. The
dates for the three marks are his to set here, and this is the page they belong on.
