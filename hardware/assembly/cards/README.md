# Assembly instruction cards

Bench-side instruction cards for building the Kitchen edition, one card per hand
operation, printed full-bleed on 4" × 6" gloss (Epson EcoTank, borderless). The
deck walks the whole build in the order of [`/hardware/assembly/`](/hardware/assembly/)'s
procedure docs; every number on a card is copied verbatim from its source
procedure, which remains the source of truth. A card is a rendering of its
procedure step — when a procedure changes, its cards rebuild.

## Layout

- One `.html` per card, named `<code>-<slug>.html` (e.g. `pv-03-rod-register.html`),
  authored against a fixed 1800 × 1200 canvas (6 × 4 in at 300 dpi, landscape).
- [`style.css`](style.css) — the shared card system. [`STYLE.md`](STYLE.md) — the
  design idioms the system implements, and the EcoTank print settings.
- `img/` — CAD renders used by cards, produced by
  [`tools/render/render-step-posed.js`](/tools/render/render-step-posed.js).
- `out/` — the printable deck: one PNG per card plus `deck.pdf` (6 × 4 in pages).
- [`_build.py`](_build.py) — renders every card HTML to `out/` via
  [`tools/render/render-card.js`](/tools/render/render-card.js) and assembles
  `deck.pdf`. Underscore-prefixed: the dev-server never runs it.

```
tools/cad-venv/bin/python hardware/assembly/cards/_build.py
```

## The deck

Codes follow the build order of [`/hardware/future.md`](/hardware/future.md)
"Build order". Per-subsystem accent colors are defined in `STYLE.md`.

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
| CC-02 | Foil-skin the vessel + transfer the coil |
| CC-03 | Bond the coil probe + close the foil over the coil |
| CC-04 | Pour the cap foam — both caps |
| CC-05 | Press the shell inserts — twelve |
| CC-06 | Build the reed columns |
| CC-07 | Seat the reservoir rods + floats |
| CC-08 | Close the reservoirs — gasket, cap, vent |
| CC-09 | Stage the cavity — elbow in, vessel down |
| CC-10 | Bond the tank probe + route the sensor leads |
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

### IP — Internal plumbing ([internal-plumbing.md](/hardware/assembly/internal-plumbing.md))

| Card | Operation |
|---|---|
| IP-01 | CO2 path — front panel to cold core |
| IP-02 | Water path — rear panel to cold core |
| IP-03 | Flavor manifold — valves and tees |
| IP-04 | Flavor manifold — pumps and channels |
| IP-05 | Risers to the umbilical bulkheads |
| IP-06 | Witness and tidy every joint |

### CA — Cable assemblies ([cable-assemblies.md](/hardware/assembly/cable-assemblies.md))

| Card | Operation |
|---|---|
| CA-01 | Build a harness — cut, crimp, sleeve, test |
| CA-02 | The harness schedule |

### ES — Electronics shelf ([electronics-shelf.md](/hardware/assembly/electronics-shelf.md))

| Card | Operation |
|---|---|
| ES-01 | Prepare the shelf trays |
| ES-02 | Stage the AC distribution + ground bus |
| ES-03 | Mount the PSU, relays, PCBA |
| ES-04 | Land the AC pigtails |
| ES-05 | Stage DC distribution + 12 V branches |
| ES-06 | Land the RELAYS J5 loom |
| ES-07 | Pre-power continuity + isolation check |

### WR — Wiring ([wiring.md](/hardware/assembly/wiring.md))

| Card | Operation |
|---|---|
| WR-01 | Chassis-ground bonds |
| WR-02 | AC mains — C14 to compressor + PSU |
| WR-03 | Dielectric + continuity check, AC side |
| WR-04 | Cabinet 12 V runs |
| WR-05 | Signal looms |
| WR-06 | Bundle, route, strain-relieve |

### EN — Enclosure mechanical ([enclosure-mechanical.md](/hardware/assembly/enclosure-mechanical.md))

| Card | Operation |
|---|---|
| EN-01 | Stage the shell + back panel |
| EN-02 | Mount the compressor with its shroud |
| EN-03 | Mount the condenser + fan |
| EN-04 | Seat the cold core at the rear |
| EN-05 | Drip pan + moisture sensor |
| EN-06 | Install the top hopper |
| EN-07 | Mount the populated back panel |
| EN-08 | Seat the electronics shelf |

### FU — Faucet + umbilical ([faucet-and-umbilical.md](/hardware/assembly/faucet-and-umbilical.md))

| Card | Operation |
|---|---|
| FU-01 | Cut the three LLDPE tubes |
| FU-02 | Route the tubes through the shell |
| FU-03 | Foam the carbonated-water tube |
| FU-04 | Sleeve the bundle |
| FU-05 | Bag with the installer kit |

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

### FS — Finish, pack, ship ([finish-pack-ship.md](/hardware/assembly/finish-pack-ship.md))

| Card | Operation |
|---|---|
| FS-01 | Wipe down + final inspection |
| FS-02 | Drain dry + nameplate |
| FS-03 | Cap the inlets + photograph |
| FS-04 | Pack the install kit + carton |
| FS-05 | Weigh, label, hand off |
