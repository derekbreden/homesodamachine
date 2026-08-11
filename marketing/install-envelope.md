# Install envelope

The space the appliance installs into: a standard kitchen sink base cabinet, already
occupied. This is the physical bound on the enclosure's silhouette, and it is stated once
for every edition — the cabinet belongs to the customer and does not change with which
machine goes into it.

Who that customer is, is in [`target-market.md`](/marketing/target-market.md); what they do
on install day is in [`unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).

## The cabinet

US kitchen sink base cabinets are standard stock: **34.5" high × 24" deep**, in widths of
**30", 33" and 36"** (24", 27", 39" and 42" are catalogued). Every major line — Hampton Bay,
Thomasville, Diamond, the RTA houses — ships those three numbers.

Interior clear height is **[755.7 mm](CABINET_CLEAR_H)**: the 34.5" carcass less the 4" toe
kick less the 3/4" deck. That derivation is the one the umbilical's length stack-up already runs on
([`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)
§1), and it is the cabinet number the appliance's own geometry is sized against.

## What is already in it

The cabinet is not empty, and its occupants take a **column out of the middle** rather than a
slice off one side:

| Occupant | Size | Where it sits |
|---|---|---|
| Garbage disposal | Ø 210–254 mm, 311–413 mm tall | bolted under the sink flange, hanging into the middle of the cabinet |
| P-trap + drain arm | — | behind and above the disposal's foot |
| Angle stops + supply lines | — | back wall or floor, to one side |
| CO2 cylinder, 5 lb | Ø 133 × 457 mm, plus regulator | on the cabinet floor beside the appliance |

The disposal is the largest of them and the one that shapes what is left. InSinkErator's
Evolution line is [8.25" wide × 12.25" tall](https://www.insinkerator.com) at the .75 and
1 HP sizes and 10" diameter × 16.25" tall for Cover Control Plus. It is fastened to the sink
and does not move.

**What is left is a slot beside it** — narrow across the cabinet, and as deep and as tall as
the cabinet is. Height and depth are uncontested there. Width is the constraint.

The CO2 cylinder stands in that same slot. It is customer-supplied (5 lb, per
[`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) "External"), stands beside the appliance
on a short tether to the rear-wall inlet
([`back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md)
"Connections inventory"), and is Ø 133 × 457 mm before its CGA-320 regulator. Appliance width
plus 133 mm plus a working gap is what the pair asks of the slot.

## What the appliance needs beyond its own box

- **[62 mm](TURN_IN) behind the rear face** — lead, 90° bend at R12, and collet. The collet
  stands [9.5 mm](COLLET_PROUD) proud of the port ring it bears on, and that ring stands
  [2 mm](PORT_RING_THICK) off the wall
  (`faucet-and-umbilical.md` §1, `printed-parts/enclosure/port-ring/`).
- **300 mm of pull-forward** — the umbilical's service loop, sized to bring the rear wall to
  the cabinet face so its own connections can be reached.
- **A gap at each side face** — the condenser draws through the grille on one side and
  exhausts through the other.
- **Headroom over the top wall** — the flavor funnel is filled by inverting a 440 mL
  concentrate bottle over it
  ([`zone-c/README.md`](/hardware/printed-parts/zone-c/README.md)).

## The editions against it

| | W × D × H | Footprint | Clear over the top wall |
|---|---|---|---|
| kitchen | [223 × 481 × 358 mm](KITCHEN_WDH) | [0.107 m²](KITCHEN_FOOTPRINT) | [397.7 mm](KITCHEN_CLEAR_TOP) |

Each silhouette is read off that edition's own box, and clear-over-top is the
[755.7 mm](CABINET_CLEAR_H) interior less the enclosure height. An edition with no row here
fails the sync, and so does a row no edition stands behind.

## What comparable devices measure

Appliances that install in this cabinet, or that carry the same subsystems:

| Device | W × D × H (mm) | W : D : H | Contents |
|---|---|---|---|
| [Brio Q60](https://briowt.com/products/brio-q60-4-stage-ro-sparkling-countertop-water-dispenser) | 220 × 467 × 430 | 1 : 2.12 : 1.95 | RO, compressor chiller, carbonator, CO2 cylinder, hot tank |
| [Quooker CUBE](https://www.quooker.co.uk) | 223 × 340 × 500 | 1 : 1.52 : 2.24 | carbonator + chiller, under-sink |
| [Waterdrop G3P800](https://www.homedepot.com) | 144–159 × 462 × 425–450 | 1 : ~3.1 : ~3.0 | tankless RO |
| [APEC ROES-50](https://www.apecwater.com/products/roes-50) | rack 133 × 406 × 445, tank Ø 279 × 381 | 1 : 3.05 : 3.35 | tanked RO |
| [Quooker COMBI+](https://www.quooker.co.uk) | Ø 200 × 530 | cylinder | hot tank |
| [InSinkErator HWT-F1000S](https://www.insinkerator.com) | 156 × 171 × 276 | 1 : 1.10 : 1.77 | 2/3 gal hot tank |

Every one of them is narrow. The width band is **133–223 mm**, and it holds across devices
whose insides have nothing in common — a cartridge rack, a hot tank, a
compressor-and-carbonator. Depth and height range over more than a factor of two in the same
set. Width is the dimension the category agrees on.

Brio's Q60 carries the same subsystems this appliance does — compressor chiller, carbonator,
CO2 cylinder, filtration, dispense — in 220 × 467 × 430 mm on a 0.103 m² footprint. It is a
countertop unit, so it never had to clear a trap, and it is narrow anyway.

The same band shows up in this machine's own parts. The two largest solids in the appliance
— the [foam shell](/hardware/printed-parts/cold-core/foam-shell/README.md) across its short
axis, and the mated [compressor](/hardware/reference/compressor/README.md) and
[condenser](/hardware/reference/condenser-block/README.md) across theirs — are within a few
millimetres of each other, and the thin edition's width is built
on the first of them
([`enclosure/README.md`](/hardware/printed-parts/enclosure/README.md)).

## Sources
[value](NAME) texts are updated by:
- `/tools/install_envelope_sync.py`
