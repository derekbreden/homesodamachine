# Flavor module

One whole flavor as one sub-assembly: four solenoid valves, one peristaltic
pump, two Tee junctions, the [10](SEGMENTS) tube segments between them, and the
loom that lands every coil and the motor on one connector — all carried on one
printed **L** that sets down over the cold core and hangs its pump down the
front column.

Everything one flavor needs. Nothing another flavor touches. Four ports on the
boundary and no other number crossing it.

    tools/cad-venv/bin/python hardware/printed-parts/flavor-module/flavor_module.py

`flavor_module.py` → `flavor-module.step` (one), `flavor-module-pair.step` (both,
in the enclosure's own frame). `_report()` measures every figure on this page off
the built solids.

## The circuit

[`../../topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)
channel B, whose reservoir carries **two mouths of its own** — the draw on the
bulkhead at the bottom of its wet V, the fill on a bore in its own cap — so its
two bag valves each reach one directly and no junction stands at the bag.

```
      IN ──→ V-select ──┐                            ┌──→ V-nozzle ──→ OUT
                        ├─ Y-suction ─→ PUMP ─→ Y-discharge ─┤
    DRAW ──→ V-draw ────┘                            └──→ V-fill ───→ FILL
```

Two valves merge at the suction junction, two split at the discharge one. The
graph is planar, and the module is that planar embedding drawn in metal.

Every segment in it, against the topology's own numbering:

| Segment | Module run | |
|---|---|---|
| — | `select-in` | the module's inlet port → V-select |
| fluid-19 | `select-suct` | V-select → Y-suction |
| fluid-20 | `draw-suct` | V-draw → Y-suction |
| fluid-21 | `suct-pump` | Y-suction → pump inlet |
| fluid-22 | `pump-disch` | pump outlet → Y-discharge |
| fluid-23 | `disch-fill` | Y-discharge → V-fill |
| fluid-24 | `fill-mouth` | V-fill → the cap's FILL bore |
| fluid-26 | `draw-mouth` | the cap's DRAW conduit → V-draw |
| fluid-27 | `disch-noz` | Y-discharge → V-nozzle |
| fluid-28 | `nozzle-out` | V-nozzle → the rear panel |

## Two lines

**Two parallel runs along Y, a valve at each end of each and its Tee between
them.** Both valves on a line and the Tee joining them stand on ONE axis, so
each of the four legs inside a junction is a single straight length with no
corner in it at all. Each Tee's branch faces down into the lane under the deck,
where the pump's own barb reaches it.

| Line | Forward valve | Junction | Aft valve | Branch |
|---|---|---|---|---|
| Suction | V-draw → the cap's DRAW mouth | Y-suction | V-select → IN | pump inlet |
| Discharge | V-fill → the cap's FILL mouth | Y-discharge | V-nozzle → OUT | pump outlet |

Each boundary port stands where the thing it mates does. Both reservoir mouths
open on the cap at the deck's FORWARD end; the nozzle bulkhead is in the rear
panel at its AFT end. Two lines carry two forward seats and two aft seats, so
draw and fill hold the forward pair and select and nozzle the aft — and each
line's two valves are then the pair its Tee's run takes.

So **both world ports stand side by side on the deck's AFT face.** The source
that feeds IN reaches the deck's rear rather than the front column.

## The L

The free volume in this machine, once the foam shell assembly is in it, IS an L
— and the module is that shape because the room is:

```
  z 140.6 ┌────────┬──────────────────────────────┐
          │  FOOT  │   DECK — the module's plate  │
  z 0     │        ├──────────────────────────────┤
          │  pump  │                              │
          │  tower │      FOAM SHELL ASSEMBLY     │
  z-253.4 └────────┴──────────────────────────────┘
          y -187.4  y 0                      y 291.5
```

- **DECK** — one plate over the cap carrying all four valve cells, both Tee
  cradles, both mouth apertures and the loom raceway. [82.25](DECK_PLATE_X) ×
  [313](DECK_PLATE_Y) mm, which is one piece on a 320 mm bed.
- **FOOT** — a well the pump drops into from above, closed by the deck over it.
  The pump goes here because a KPHM400 on end is the one body in a flavor
  channel that wants more height than the bay over the core has, and the front
  column is the only place in the machine that has it.

The two legs meet at the core's front-top arris. **The module is an assembly,
not a part** — same as the foam stack it sits on — so the L does not have to
print in one piece, only to go together on a bench and install as one.

## The port plane, and the lane under the deck

Every port axis is on one plane at z = [55](PORT_PLANE). A Tee's branch hangs a
`BRANCH_REACH` below its own run and so comes out UNDER the plate whatever the
plate's thickness, which makes the band beneath the deck the lane both pump legs
run in — and that lane carries the corner that turns each of them up into its
branch. At z = [9.53](UNDER_DECK) each corner seats a full stock radius. The
pump's barbs stand ON that lane, so a leg crosses the core's front plane already
at the height it will run at and turns exactly once.

The [6.5 mm](BARB_OFFSET) between a barb and its Tee's own column is spent as a
LEAN of [2.3](BARB_LEAN)° over the whole run — inside the
[22](COLLET_SKEW)° a push-to-connect collet grips through — so no leg spends a
corner of its own on it.

## What the module holds itself to

`_report()` measures all of it, in the order it was asked for. Current state:

| | |
|---|---|
| every component and tube | 4 valves, 2 junctions, 1 pump, [10](SEGMENTS) segments, 6 wire bundles + trunk |
| not overlapping | 290 pairs tested, **0 clashing** |
| the arrangement | every corner at R[25.4](WORST_BEND), four legs straight, no leg crossing another |
| an L | 7 bodies into the foot, 23 onto the deck |
| around the foam shell | **0** bodies into the core's box |
| inside the thin enclosure | **0** bodies outside the cavity |
| two of them | [22.25](PAIR_GAP) mm between the pair, 186.8 of the cavity's 209 mm |

Module box [82.25](MODULE_X) × [364.1](MODULE_Y) × [216.3](MODULE_Z) mm.

The five wire bundles and their trunk ride a raceway that runs ABOVE every coil — the one band
the valves leave open and nothing else wants — so a drop is short and vertical
and no wire shares a lane with a tube.

## Interface

`PORTS` is the whole of it. Nothing outside the module needs any other number
from inside it.

| Port | Mates | Where |
|---|---|---|
| `in` | the shared source's select leg | deck's aft face, suction line |
| `out` | the rear panel's flavor bulkhead | deck's aft face, discharge line |
| `draw` | the cap's reservoir DRAW conduit | forward, on the cap's own column |
| `fill` | the cap's reservoir FILL bore | forward, one conduit pitch aft of it |

## What it asks of the machine

1. **Both reservoirs present draw and fill as two mouths on the top cap.**
   Reservoir B does. Reservoir A carries ONE mouth on the core's front face and
   one line for both its fill and its draw through a third junction, so the
   mirrored instance wants reservoir A re-plumbed to its twin's arrangement —
   which is also what drops the third junction.
2. **Both flavor bulkheads stand on the module's own OUT stations** — z 283.4
   rather than the rear port row's 358.2, each on its module's discharge line.
3. **The shared source node stands aft**, where both modules present IN.

The check is against the raw cavity less the foam shell assembly. The pack that
stands in the enclosure today is not in it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/flavor-module/flavor_module.py`
