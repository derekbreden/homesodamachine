# Assembly instruction cards

Bench-side instruction cards for building the Kitchen edition, one card per hand
operation, printed full-bleed on 4" × 6" gloss (Epson EcoTank, borderless). The
deck walks the whole build in the order of [`/hardware/assembly/`](/hardware/assembly/)'s
procedure docs. A card is a rendering of its procedure step — when a procedure
changes, its cards rebuild.

**A figure the machine owns is derived, not typed.** A dimension, a count, a
station, a fastener quantity: the card carries it in a `data-gen` marker, and
[`_cards_sync.py`](_cards_sync.py) writes it from the built appliance. What a
card owns outright is its craft — the hand technique, the order of operations,
the reason a step is shaped the way it is. See [The gate](#the-gate).

## Layout

- One `.html` per card, named `<code>-<slug>.html` (e.g. `pv-03-rod-register.html`),
  authored against a fixed 1800 × 1200 canvas (6 × 4 in at 300 dpi, landscape).
- [`style.css`](style.css) — the shared card system. [`STYLE.md`](STYLE.md) — the
  design idioms the system implements, and the EcoTank print settings.
- `img/` — CAD renders used by cards, produced by
  [`tools/render/render-step-posed.js`](/tools/render/render-step-posed.js).
- `out/` — the printable deck: one PNG per card plus `deck.pdf` (6 × 4 in pages).
- [`_build.py`](_build.py) — runs the gate, renders every card HTML to `out/`
  via [`tools/render/render-card.js`](/tools/render/render-card.js), and
  assembles `deck.pdf`. Underscore-prefixed: the dev-server never runs it.
- [`_cards_sync.py`](_cards_sync.py) — the doc-sync driver: every figure the
  cards state that the machine owns, derived from `enclosure_assembly.machine()`, plus
  which card carries which. [`_cardgen.py`](_cardgen.py) — the marker syntax and
  the checks. Both underscore-prefixed for the same reason.

```
tools/cad-venv/bin/python hardware/assembly/cards/_build.py
```

## The gate

`_build.py` builds the appliance and reads every derived figure on every card
against it before a single card renders, so a stale deck cannot come off the
printer. Run it alone while writing a card:

```
tools/cad-venv/bin/python hardware/assembly/cards/_cards_sync.py --check   # report drift
tools/cad-venv/bin/python hardware/assembly/cards/_cards_sync.py           # write it away
```

A marker is [`tools/docgen`](/tools/docgen/)'s `[value](NAME)` translated to a
page that gets printed: the name goes in an attribute, where it never draws, and
the element's own text is the value.

```html
<span class="dim" data-gen="WALL_BOSSES">15</span>
<td class="v" data-gen="BOX_SIZE">223 &#215; 481 &#215; 358 mm</td>
```

A marked element holds text and nothing else. The value in the file is never
authoritative — `_cards_sync.py`'s variable is.

**To put a derived figure on a card**, in `_cards_sync.py`:

1. Derive it in that subsystem's function, off the machine rather than off
   another document. Prefer a structural reading to a coordinate — "the east end
   of the row" survives the row moving and `z 342.4` does not.
2. Assert the structure the sentence around it rests on, the way
   [`_bom_sync.py`](/hardware/scripts/_bom_sync.py) asserts `not ml.JOINS`. "Nothing
   is cut in the front wall" holds no number, so only an assertion can put it
   back.
3. Wrap the value on the card, add the name to that card's set in `cards`, and
   name `_cards_sync.py` in the card's `.src` footer — the bench's own Sources
   line.

A new subsystem is one function taking the built machine and returning
`(facts, cards)`, plus an entry in `SUBSYSTEMS`. Names live in **one namespace
across the whole deck**, so two cards cannot state the same wall's boss count
and disagree. A card stating nothing the machine owns needs no entry.

A part named on a card resolves to a line in [`bom.md`](/hardware/ledger/bom.md)
or [`tools.md`](/hardware/ledger/tools.md) — the two ledgers a build draws on.
`purchases.md` and `inventory.md` record what was bought, which is a different
question. [`check_ledger.py`](/hardware/scripts/check_ledger.py) reads every card
and procedure against all four and reports the names that resolve to history
only, any procedure without a doc-sync driver, the generic materials the deck
asks for by description rather than by brand (a fork terminal and a tube of RTV
have no ASIN and no brand, so nothing else sees them), and any `bom.md §N`
citation that names an ASIN the section does not hold:

```
tools/cad-venv/bin/python hardware/scripts/check_ledger.py
```

## The deck

Subsystems print in the build order of [`/hardware/future.md`](/hardware/future.md)
"Build order" — the procedure docs' dependency chain, held in one place as
`SUBSYSTEM_ORDER` in [`_build.py`](_build.py). A card's number is its position
*within* its subsystem, not in the deck, so the three bench subsystems (CA, ES,
FU) can be built whenever before the chassis needs them. Where one subsystem's
first card depends on another's last, the card says so by code. Per-subsystem
accent colors are defined in `STYLE.md`.

### PV — Pressure vessel ([pressure-vessel.md](/hardware/assembly/pressure-vessel.md))

| Card | Operation |
|---|---|
| PV-01 | Chamfer the end-plate port holes |
| PV-02 | Tap 1/4"-18 NPT — four ports |
| PV-03 | Drill the rod register — both plates |
| PV-04 | Break the plate edges — asymmetric |
| PV-05 | Cut the level rods — three per appliance |
| PV-06 | Tack-weld the float rod to the bottom plate |
| PV-07 | Deburr the tube + prep the weld surfaces |
| PV-08 | Weld the bottom plate to the tube |
| PV-09 | Close the vessel — float in, top plate welded |
| PV-10 | Dye-penetrant inspection of the closure welds |
| PV-11 | Hydro test — 180 PSI, 30 minutes |
| PV-12 | Citric-acid passivation |
| PV-13 | Build the PRV-shroud subassembly |
| PV-14 | Install the port fittings, sparge stone, PRV |

### CC — Cold core ([cold-core.md](/hardware/assembly/cold-core.md))

| Card | Operation |
|---|---|
| CC-01 | Wind the evaporator coil on the mandrel |
| CC-02 | Dress the vessel wall — reeds, probe, foil |
| CC-03 | Transfer the coil + set the band |
| CC-04 | Bond the coil probe + close the foil over the coil |
| CC-05 | Press the shell inserts — twelve |
| CC-06 | Pour the cap foam — both caps |
| CC-07 | Build the reed columns |
| CC-08 | Seat the reservoir rods + floats |
| CC-09 | Close the reservoirs — gasket, cap, vent |
| CC-10 | Lower the vessel — elbow already on it |
| CC-11 | Seat the reservoirs in their pockets |
| CC-12 | Route the seven penetrations |
| CC-13 | Stack the copper plugs |
| CC-14 | Pour the body foam |
| CC-15 | Reed columns in, gaskets on, caps down |

### RL — Refrigerant loop ([refrigerant-loop.md](/hardware/assembly/refrigerant-loop.md))

| Card | Operation |
|---|---|
| RL-01 | Verify the donor + factory charge |
| RL-02 | Vent the factory R-600a |
| RL-03 | Start argon, cut the loop |
| RL-04 | Tie in the suction line |
| RL-05 | Pinch-swage the capillary tie-in |
| RL-06 | Pull vacuum |
| RL-07 | Mass-metered recharge |
| RL-08 | First run-up + leak check |

### CA — Cable assemblies ([cable-assemblies.md](/hardware/assembly/cable-assemblies.md))

| Card | Operation |
|---|---|
| CA-01 | Build a harness — cut, crimp, sleeve, test |
| CA-02 | The harness schedule |

### ES — Electronics shelf ([electronics-shelf.md](/hardware/assembly/electronics-shelf.md))

| Card | Operation |
|---|---|
| ES-01 | Prepare the shelf |
| ES-02 | Stage the AC distribution + ground bus |
| ES-03 | Stage the PSU, relays, PCBA |
| ES-04 | Land the AC pigtails |
| ES-05 | Stage DC distribution + 12 V branches |
| ES-06 | Land the RELAYS J5 loom |
| ES-07 | Pre-power continuity + isolation check |

### FU — Faucet + umbilical ([faucet-and-umbilical.md](/hardware/assembly/faucet-and-umbilical.md))

| Card | Operation |
|---|---|
| FU-01 | Cut the three LLDPE tubes |
| FU-02 | Route the tubes through the shell |
| FU-03 | Foam the carbonated-water tube |
| FU-04 | Sleeve the bundle |
| FU-05 | Bag with the installer kit |

### EN — Enclosure mechanical ([enclosure-mechanical.md](/hardware/assembly/enclosure-mechanical.md))

One card per procedure step, in the procedure's own order.

| Card | Operation |
|---|---|
| EN-01 | Stage the four printed pieces |
| EN-02 | Seat the rear wall's connection bodies |
| EN-03 | Bolt the compressor down to the slab |
| EN-04 | Stand the condenser on the compressor's tangent |
| EN-05 | Seat the cold core behind the stratum |
| EN-06 | Stand the power column on the +X flank |
| EN-07 | Close the box |
| EN-08 | Slide the drip tray in through the −X wall |
| EN-09 | Display into the facet, hopper opening clear |

### IP — Internal plumbing ([internal-plumbing.md](/hardware/assembly/internal-plumbing.md))

| Card | Operation |
|---|---|
| IP-01 | CO2 path — rear wall to cold core |
| IP-02 | Water path — rear wall to cold core |
| IP-03 | Flavor manifold — valves and tees |
| IP-04 | Flavor manifold — pumps and channels |
| IP-05 | Risers to the umbilical bulkheads |
| IP-06 | Witness and tidy every joint |

### WR — Wiring ([wiring.md](/hardware/assembly/wiring.md))

| Card | Operation |
|---|---|
| WR-01 | Chassis-ground bonds |
| WR-02 | AC mains — C14 to compressor + PSU |
| WR-03 | Dielectric + continuity check, AC side |
| WR-04 | Cabinet 12 V runs |
| WR-05 | Signal looms |
| WR-06 | Bundle, route, strain-relieve |

### FC — Firmware + commissioning ([firmware-and-commissioning.md](/hardware/assembly/firmware-and-commissioning.md))

| Card | Operation |
|---|---|
| FC-01 | Verify wiring-out + first DC power-on |
| FC-02 | Flash the three ESP32s |
| FC-03 | Sensor health walkthrough |
| FC-04 | Valve + pump self-test |
| FC-05 | Compressor smoke test + setpoints |

### AB — Acceptance + burn-in ([acceptance-and-burn-in.md](/hardware/assembly/acceptance-and-burn-in.md))

| Card | Operation |
|---|---|
| AB-01 | Inspect, connect, power on |
| AB-02 | First water fill + CO2 at 90 PSI |
| AB-03 | First dispenses — water, flavor A, flavor B |
| AB-04 | Clean cycle + air purge |
| AB-05 | Level-sensing transitions |
| AB-06 | Burn-in + per-serial log |
| AB-07 | Drain + air-purge for transit |

### FS — Finish, pack, ship ([finish-pack-ship.md](/hardware/assembly/finish-pack-ship.md))

| Card | Operation |
|---|---|
| FS-01 | Wipe down + final inspection |
| FS-02 | Drain dry + nameplate |
| FS-03 | Cap the inlets + photograph |
| FS-04 | Pack the install kit + carton |
| FS-05 | Weigh, label, hand off |

### GT — Technique (appendix)

General instructions for techniques the numbered cards lean on; each
card names the procedure docs whose rules it compiles.

| Card | Technique |
|---|---|
| GT-01 | NPT joints — tape, engagement, witness |
| GT-02 | Push-to-connect — cut, click, tug |
| GT-03 | Crimp lugs — ferrules, forks, fastons, rings |
| GT-04 | JST-XH crimping — wings, lance, housing |
| GT-05 | Heat-shrink + sleeve — collars, lacing, braid |
