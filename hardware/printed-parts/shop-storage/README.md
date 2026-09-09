# Shop storage

Gridfinity holders for the shop's tools and stock. [42](HOLDER_COUNT) of them, each one
module on the [42 mm x 42 mm x 7 mm](GRID) grid, each standing anywhere a baseplate
reaches, each printing on its own feet without support.

A holder is the unit of being wrong. A figure that turns out badly costs the one module
it is in, and the rest of the bench keeps working.

## What a figure is allowed to decide

A holder is printed before the thing it holds is ever measured, so the figures it is cut
from carry where they came from, and there are two readings that are not interchangeable:

- **exact** — a standard, or the maker's own drawing of the item. An M3 screw is M3, a
  T18 barrel is 6.5 mm, a 6P4C jack is 6P4C, a John Guest PP0208E is 39.1 x 16.3 mm.
  The thing is no bigger than this *and* no smaller.
- **a parcel** — a listing's shipping box. The thing came out of it, so the thing is no
  bigger than the box. It says nothing whatever about how small the thing is.

The reading is per axis, because that is how the world publishes. Klein gives the
11063W's overall length to a thousandth of an inch and neither of its other two figures.
RIDGID gives the 150 an overall length and nothing else. BNTECHGO publishes its 22 AWG
wire's 1.7 mm outside diameter, its 250 ft length, its 60 strands — and no figure at all
for the reel they are wound on. One exact axis and two parcels is the ordinary case.

So: **geometry that grows to fit its content may read a parcel. Geometry cut to a content,
or spanning it, may not.** [`_bound.py`](_bound.py) is that rule, and `Env.least` refuses
a parcel to its face at build time rather than at the printer.

Everything here is one of four shapes, and three of them never ask a lower bound at all.

## The four shapes

[`_holder.py`](_holder.py) cuts them. Each is chosen for what it does *not* need to know.

![Reels of 40, 72 and 110 mm in the one cradle](reel-cradle.png)

**Cradle** — a 90-degree V trough, [72 mm x 35 mm](TROUGH) on the reel size and
[58 mm x 28 mm](ROLL_TROUGH) on the roll size. Anything round rests on two lines in a V
and centres itself between them, and it does that at every radius. A reel turns as the
wire is pulled. Nothing is cut to a reel's diameter or to its width, so no figure about a
reel can be wrong here. A narrow reel wanders along the trough; a `spacer` takes up the
slack, and any number of them stack. The picture above is one cradle with reels of 40, 72
and 110 mm lying in it: the small one beds down between the walls, the largest rides on
the two mouth edges, and all three come out centred on the same axis and free to turn.
[`holders.py`](holders.py) draws it as `reel-cradle-witness.step` from the same arithmetic
the trough is cut by.

**Comb** — one slot per tool, cut along Y and packed across X. A slot runs its own mouth
width down a parallel throat, then closes to a [5 mm](SLOT_ROOT) root over the last
[14 mm](SLOT_TAPER) of its depth. A tool goes in head down and descends until its own
thickness meets the taper: a crimper head stops at the bottom of the throat with the whole
throat around it, a tweezer runs on to the root and is pinched there. The mouth is the
tool's thinnest parcel figure plus [2 mm](SLOT_CLEAR) — an upper bound, which is the
reading a parcel gives honestly. Each slot is cut to its own tool, so a 15 mm pliers
wrench does not rattle in a mouth sized for a 41 mm tubing cutter.

**Index** — bores at a nominal diameter. This is the one shape that cuts *to* a size, so
it takes exact figures only and refuses anything else at build time: a bore fails loose as
surely as it fails tight. Rows read front to back and each row is pitched on its own
bores, so twelve 9/64 in drills pack tight in front of five countersinks stepping 1/4 to
3/4 inch. Every bore is its nominal plus [1.5 mm](BORE_SLIP).

**Tub** — the library's own open bin, plain or divided. It reads an upper bound and
nothing else: whatever came out of that parcel goes in this compartment. Its footprint and
its divisions are a choice about how the bench wants the stock laid out; its depth is not,
and is derived from what goes in it rather than written down.

Between them, [`_holder.py`](_holder.py) keeps [3 mm](WALL) of plastic anywhere it is not
following a stock library profile, and the label ledge on every tub takes
[12 mm](LABEL_TAPE) tape. Nothing is lettered in the plastic; the tables below are what
tells one compartment from the next.

## Where to start

Nothing here needs the rest of it. A holder is one print and it docks on any baseplate,
so the bench can grow a module at a time. In the order the bench misses them:

1. [`dock-3x3`](holders/dock-3x3.step) — everything else stands on it. Print two.
2. [`reel-cradle`](holders/reel-cradle.step) and a [`reel-spacer`](holders/reel-spacer.step)
   or two — the wire reel, and the shape that answers the shelf it replaces.
3. [`crimp-comb`](holders/crimp-comb.step), [`xh-tub`](holders/xh-tub.step) — the JST
   station, which is the job that got printed first and fit worst.
4. [`m3-tub`](holders/m3-tub.step), [`insert-tub`](holders/insert-tub.step) — the two the
   appliance build reaches for at every station.

Everything after that is whichever bench is annoying you.

## What is printed

### Cradles — anything round

| Holder | Units | Takes |
|---|---|---|
| [`reel-cradle`](holders/reel-cradle.step) | [3 x 3 x 6](REEL_CRADLE_SIZE) | BNTECHGO 22 AWG silicone, 250 ft black; BNTECHGO 28 AWG 4-conductor silicone ribbon, 50 ft; ELEGOO polyimide tape, four widths |
| [`roll-cradle`](holders/roll-cradle.step) | [2 x 2 x 5](ROLL_CRADLE_SIZE) | Kester 24-6337-0027 0.031 in, 1 lb; Kester 44 0.020 in, 3/4 oz pocket pack; Chemtronics Soder-Wick on its ESD bobbin; Millrose 70894 PTFE thread seal tape |
| [`reel-spacer`](holders/reel-spacer.step) | [3 x 3](REEL_SPACER_SIZE) | — |
| [`roll-spacer`](holders/roll-spacer.step) | [2 x 2](ROLL_SPACER_SIZE) | — |

### Combs — anything flat that stands

| Holder | Units | Takes |
|---|---|---|
| [`crimp-comb`](holders/crimp-comb.step) | [3 x 2 x 9](CRIMP_COMB_SIZE) | iCrimp SN-2549 ratcheting crimper, AWG 28-18; haisstronica HS-9327 ratchet crimper, AWG 22-10; Preciva ferrule crimper, AWG 28-5 |
| [`strip-comb`](holders/strip-comb.step) | [3 x 3 x 8](STRIP_COMB_SIZE) | Klein 11063W Katapult stripper, 8-20 AWG solid; Klein 11057 wire stripper; VCE GJ668BL modular crimper |
| [`punch-comb`](holders/punch-comb.step) | [2 x 2 x 8](PUNCH_COMB_SIZE) | Klein VDV427-300 impact punchdown, 66/110 blade; MASTERCOOL 70025 capillary tube cutter |
| [`cut-comb`](holders/cut-comb.step) | [2 x 2 x 7](CUT_COMB_SIZE) | KATA micro flush cutter; Mudder tubing cutter |
| [`fine-comb`](holders/fine-comb.step) | [2 x 1 x 8](FINE_COMB_SIZE) | iFixit precision tweezers — extra-fine, angled, blunt |
| [`tube-comb`](holders/tube-comb.step) | [3 x 3 x 9](TUBE_COMB_SIZE) | KNIPEX 86 01 180 Pliers Wrench; RIDGID 150 constant-swing tubing cutter |

### Indexes — anything whose size is a standard

| Holder | Units | Takes |
|---|---|---|
| [`tip-index`](holders/tip-index.step) | [3 x 2 x 5](TIP_INDEX_SIZE) | Hakko / VECO-T T18 soldering tip; heat-set insert tip, M2 to M8 |
| [`drill-index`](holders/drill-index.step) | [3 x 3 x 5](DRILL_INDEX_SIZE) | Drill Hulk 9/64" M35 cobalt jobber drill; Mollom hole-saw pilot drill; Brown & Sharpe 599-792-30 spring tap guide; HSS 1/4"-18 NPT taper pipe tap; JNB Pro 82-degree countersink, 1/4 in head; JNB Pro 82-degree countersink, 3/8 in head; JNB Pro 82-degree countersink, 1/2 in head; JNB Pro 82-degree countersink, 5/8 in head; JNB Pro 82-degree countersink, 3/4 in head |
| [`dowel-index`](holders/dowel-index.step) | [2 x 1 x 5](DOWEL_INDEX_SIZE) | POWERTEC 71476 ground dowel pin |

### Tubs — everything loose, and everything that just stands

| Holder | Units | Takes |
|---|---|---|
| [`m3-tub`](holders/m3-tub.step) | [3 x 2 x 6](M3_TUB_SIZE) | BNUOK M3 x 25, 12.9 black oxide; BNUOK M3 x 12, 304 SS — wet joints; BNUOK M3 x 12, 12.9 black oxide — dry joints; BNUOK M3 x 10, 12.9 black oxide; BNUOK M3 x 8, 12.9 black oxide |
| [`m5-tub`](holders/m5-tub.step) | [3 x 2 x 7](M5_TUB_SIZE) | MewuDecor M5 x 10, 12.9 black oxide; M5 x 25 mm OD fender washer, 304 SS; ruthex RX-M5x9.5 heat-set insert |
| [`insert-tub`](holders/insert-tub.step) | [3 x 1 x 3](INSERT_TUB_SIZE) | ruthex RX-M3x5.7 heat-set insert — the appliance default; ruthex RX-M3Sx4.0 heat-set insert — shallow bores only; ruthex RX-M2x4 heat-set insert |
| [`small-tub`](holders/small-tub.step) | [3 x 2 x 5](SMALL_TUB_SIZE) | Sutemribor M2 x 6, 12.9 black oxide; McMaster 91223A412 M3 x 6 ultra-low-profile, 316 SS; McMaster 91223A413 M3 x 8 ultra-low-profile, 316 SS; neodymium disc magnets, 3 x 1 mm N52; LVDALAB PTFE membrane filters, 13 mm x 0.45 um |
| [`ferrule-tub`](holders/ferrule-tub.step) | [3 x 3 x 7](FERRULE_TUB_SIZE) | 0.34 mm2 ferrule, turquoise — 22 AWG; 1.5 mm2 ferrule, black — 16 AWG; 0.5 mm2 ferrule, white; 0.75 mm2 ferrule, grey; 1 mm2 ferrule, red; 2.5 mm2 ferrule, blue |
| [`shrink-tub`](holders/shrink-tub.step) | [3 x 3 x 7](SHRINK_TUB_SIZE) | 2:1 heat shrink, 1.06 - 1.59 mm; 2:1 heat shrink, 2.12 mm; 2:1 heat shrink, 3.18 - 3.57 mm; 2:1 heat shrink, 3.97 mm; 2:1 heat shrink, 5.08 - 5.95 mm; 2:1 heat shrink, 7.94 - 9.92 mm |
| [`terminal-tub`](holders/terminal-tub.step) | [3 x 3 x 8](TERMINAL_TUB_SIZE) | 6.3 mm female push-on, red — Baomain; 4.8 mm female push-on, red — Baomain; #4 ring, red — smseace; 6.3 mm female, assorted — three kits decanted; 4.8 mm female, assorted — three kits decanted; 2.8 mm male — Baomain 0.11 in |
| [`lever-tub`](holders/lever-tub.step) | [3 x 1 x 8](LEVER_TUB_SIZE) | WAGO 221-413, 3-conductor; WAGO 221-415, 5-conductor; WAGO 221-420, 10-conductor |
| [`tie-tub`](holders/tie-tub.step) | [3 x 2 x 10](TIE_TUB_SIZE) | 4" zip tie, 2.5 mm strap; 6" zip tie, 2.5 mm strap; 8" zip tie, 4.8 mm strap |
| [`xh-tub`](holders/xh-tub.step) | [3 x 3 x 8](XH_TUB_SIZE) | JST SXH-001T contacts, loose; pre-crimped XH leads; JST XH 3P housing; JST XH 4P housing; JST XH 5P housing; JST XH 6P housing; JST XH 7P housing; JST XH 9P housing; JST XH 10P housing |
| [`keystone-tub`](holders/keystone-tub.step) | [2 x 2 x 6](KEYSTONE_TUB_SIZE) | RiteAV RJ11 6P4C punchdown keystone jacks, black; EZYUMM RJ11 6P4C 3-prong modular plugs |
| [`junction-tub`](holders/junction-tub.step) | [3 x 3 x 7](JUNCTION_TUB_SIZE) | John Guest PP0208E — union tee; John Guest PP0308E — union elbow |
| [`bulkhead-tub`](holders/bulkhead-tub.step) | [3 x 3 x 11](BULKHEAD_TUB_SIZE) | John Guest PP1208E — bulkhead union; neoFit ABU44-E acetal bulkheads; PureSec 90-degree elbow bulkheads; NeoFit push-fit ball valves |
| [`adapter-tub`](holders/adapter-tub.step) | [3 x 3 x 17](ADAPTER_TUB_SIZE) | John Guest PI010822S / PP010822E / PP010821WP — male connectors; John Guest PP450822E — female adapter; John Guest PI4512F6S / PP061208W — flare adapter and reducer stem; MALIDA, TAILONZ and DERPIPE push-fit |
| [`npt-tub`](holders/npt-tub.step) | [3 x 3 x 14](NPT_TUB_SIZE) | GASHER and ChillWaves 1/4 NPT check valves; GAGIRA, LTWFITTING and TAISHER couplings and elbows; LTWFITTING and MAACFLOW barb adapters; John Guest MI4508F4SLF — brass flare connector |
| [`pressure-tub`](holders/pressure-tub.step) | [2 x 2 x 15](PRESSURE_TUB_SIZE) | Interstate Pneumatics WR1110 regulator; Control Devices SV-125 relief valve |
| [`stock-tub`](holders/stock-tub.step) | [3 x 3 x 15](STOCK_TUB_SIZE) | John Guest PP2308E — two-way divider; YDS and WC-316SS-06 hose clamps; Siptenk 1/4 in tube stiffeners |
| [`copper-tub`](holders/copper-tub.step) | [3 x 1 x 4](COPPER_TUB_SIZE) | Joywayus brass 1/4" SAE 45-degree flare nuts; 1/4" OD ACR copper slip couplings |
| [`service-tub`](holders/service-tub.step) | [3 x 2 x 15](SERVICE_TUB_SIZE) | Supco D111 filter-drier; Supco BPV31 bullet-piercing valve |
| [`flux-tub`](holders/flux-tub.step) | [3 x 3 x 16](FLUX_TUB_SIZE) | MG Chemicals 8341 flux, 49 g jar; BEEYUIHF no-clean flux, 30 mL; no-clean flux syringes, 10 cc, four |
| [`brush-quiver`](holders/brush-quiver.step) | [2 x 2 x 24](BRUSH_QUIVER_SIZE) | acid flux brushes, 36 standing |
| [`heat-gun-tub`](holders/heat-gun-tub.step) | [2 x 2 x 25](HEAT_GUN_TUB_SIZE) | QWORK mini heat gun |
| [`deburr-tub`](holders/deburr-tub.step) | [4 x 1 x 6](DEBURR_TUB_SIZE) | Noga NG8150 deburr tool, NogaGrip-1 handle |
| [`saw-tub`](holders/saw-tub.step) | [4 x 2 x 6](SAW_TUB_SIZE) | Mollom hole-saw arbor with its pilot fitted; Bosch DSB1013 spade bit, 1 in x 6 in |
| [`die-tub`](holders/die-tub.step) | [2 x 2 x 5](DIE_TUB_SIZE) | Drill America 1-1/2" OD round adjustable NPT die |
| [`hotend-tub`](holders/hotend-tub.step) | [3 x 2 x 8](HOTEND_TUB_SIZE) | DUROZZLE silicone hotend socks; H2C hotends, the four a both-printer swap pulls |
| [`depressor-quiver`](holders/depressor-quiver.step) | [3 x 2 x 24](DEPRESSOR_QUIVER_SIZE) | JMU 6" tongue depressors, 100 |
| [`pigment-tub`](holders/pigment-tub.step) | [2 x 2 x 15](PIGMENT_TUB_SIZE) | BBDINO black silicone pigment, 150 g |

### The dock

| Holder | Units | Takes |
|---|---|---|
| [`dock-3x3`](holders/dock-3x3.step) | [3 x 3](DOCK_3X3_SIZE) | — |

## What stays out of a holder

Wider than a footprint, longer than a bin, or already at home somewhere else:

| Stays where it is | Why |
|---|---|
| Drill America DWT tap wrench, MOTOKU die handle | 483 mm and 315 mm — both longer than any footprint |
| Mollom 124 mm hole saw | its own cut is 123.8 mm across a 123.5 mm cell |
| Tap Magic EP-Xtra, 16 oz | 203 mm tall, and every cut on the press reaches for it |
| BBDINO silicone kit, PU foam kit, Ease Release, Krylon | two-bottle kits and aerosols, all over a footprint |
| TCP Global 32 oz cups, Pouring Masters 5 oz column | 134 mm across and a 227 mm column |
| Hakko FX-888D, FR-301, KOTTO extractor, Kaisi mat, AORAEM hands | bench instruments, not stock |
| findmall and STARTECHWELD 8 in MIG spools | the welder's, and 203 mm across |
| 3M Virtua CCS glasses, FAST CHIP alloy | 138 mm and 165 mm, both over a cell's diagonal |

## Build

From the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/shop-storage/holders.py
```

That cuts every holder, runs its shape's own checks against everything it is said to
take, writes one coloured STEP per holder into [`holders/`](holders/), and rewrites this
README's figures. A holder whose contents do not fit does not export: the check raises
and names the holder, the content and the two figures that disagree.

While a footprint or a pack count is being settled, the depths alone come back in a
second rather than a build:

```sh
tools/cad-venv/bin/python hardware/printed-parts/shop-storage/holders.py --sizes
```

And every slot whose width rests on a parcel rather than a measurement — the ten places
where a caliper would buy something, and the only places it would:

```sh
tools/cad-venv/bin/python hardware/printed-parts/shop-storage/holders.py --parcels
```

A slot cut to a parcel is honest and loose: the tool is certainly no thicker than the
box's least side, and looser than the slot by however much the box was oversized. The
lean that buys is held inside the slot's own share of the block, so it is slack and not
a failure. One measured figure in [`catalog.py`](catalog.py) closes each one.

Both layers under it answer for themselves. [`_bound.py`](_bound.py) checks the reading
rule against the case that made it necessary, and [`_kit.py`](_kit.py) — the Gridfinity
vocabulary: the library's own bodies, its division formula, its seating and containment
checks — against the bodies cq-gridfinity actually renders:

```sh
tools/cad-venv/bin/python hardware/printed-parts/shop-storage/_bound.py
```

```sh
tools/cad-venv/bin/python hardware/printed-parts/shop-storage/_kit.py selftest
```

Every holder prints in Bambu PETG Basic black from the AMS 2 Pro on the H2C's right
hotend, so shop storage never queues for the left hotend the exterior and the cold core
share. Keep the exported orientation and leave supports off; every cut opens upward and
no overhang passes 45 degrees. Every holder fits the H2C's
[325 x 320 x 320 mm](H2C_ENVELOPE) envelope. The two spacers are the one exception to
"as exported, as printed" and say so in their own docstring: they come off the bed the
other way up.

## Prior art

- The 42 x 42 x 7 mm module, the base profile, the stacking lip and the 12 mm label ledge
  are the [Gridfinity specification](https://github.com/gridfinity-unofficial/specification),
  rendered by the MIT-licensed [`cq-gridfinity`](https://github.com/michaelgale/cq-gridfinity).
- The V trough is a machinist's V-block: two lines of contact, self-centring at every
  radius, which is the whole reason a cradle needs no figure about the reel in it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/shop-storage/holders.py`
