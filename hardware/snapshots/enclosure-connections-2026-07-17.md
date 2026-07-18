# Enclosure connections — the three placed components — Snapshot 2026-07-17

**This is a point-in-time snapshot, not a living document.** Pack state: on top of commit
`29ffb5d4`. Scope: the three components that carry held placement rules today —
`foam-assembly` (cold core), `compressor-shroud`, `condenser+fan` — evaluated for whether
their positions and rotations serve the connections each must make. Re-running this against a
later pack produces a fresh dated file. The durable rules are in
[`requirements.md`](/hardware/printed-parts/enclosure/enclosure-assembly/requirements.md); the
executable form is the `located` axis + `PORTS` in
[`scorecard.py`](/hardware/printed-parts/enclosure/enclosure-assembly/scorecard.py).

Coordinate frame: **+X right, +Y back, +Z up**, origin at the lower-front-left corner.

## TL;DR

- The three components are the **refrigeration subsystem**, bound by the sealed refrigerant
  loop (compressor discharge → condenser → drier/cap-tube → evaporator → compressor suction)
  plus the cold core's beverage penetrations. That loop lived in **no** topology file until
  this pass — the `routed` denominator silently omitted it. It is now declared
  (`REFRIGERANT_SEGMENTS`), so the loop is counted (routed 0/59).
- **Ports located: foam 10/10, compressor 4/4, condenser 0/3.** Foam's penetrations and the
  compressor shroud's holes are documented by their generators, so both derived cleanly and
  are on-surface-verified. The condenser is a harvested-donor placeholder box with **no port
  geometry** — its three connectors (refrigerant in, refrigerant out, fan power) are declared
  but unpositioned, pending its teardown. Questions to pin them are at the bottom.
- **Headline Q1 finding: the compressor's rotation points its refrigerant stubs at neither
  mate.** Both copper stubs land on the world **−Y (front) face**, while the condenser is to
  the **+X (right)** and the evaporator is to the **+Y (back)**. The current 90° rotation is
  defensible only if front-face service access was the intent; otherwise a different rotation
  would shorten both refrigerant runs. Flagged for a decision, not silently accepted.
- **Headline Q3 finding: 4 mm behind the condenser.** The channel between the condenser's
  back face and the cold-core front is 4 mm — tight for the filter-drier + capillary-tube
  subassembly (a "fat copper cylinder") that is brazed to the condenser outlet and must reach
  the evaporator.

## The subsystem and its connections

| component | placed bbox (world) | role |
|---|---|---|
| `foam-assembly` | X[0, 283] Y[155, 336] Z[9.5, 262.9] | cold core: carbonator + evaporator coil + 2 reservoirs |
| `compressor-shroud` | X[14, 192] Y[0, 133] Z[3, 154.5] | hermetic compressor under a fire-rated shroud |
| `condenser+fan` | X[213, 269] Y[0, 151] Z[3, 181] | finned condenser + axial fan (airflow along X) |

The refrigerant loop, verified-by-disassembly in
[`reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md):

- **refrig-1** compressor discharge → condenser inlet
- **refrig-2** condenser outlet → filter-drier → capillary tube → evaporator inlet *(the
  drier + cap-tube ride this leg as one preserved subassembly)*
- **refrig-3** evaporator outlet → compressor suction

The cold core additionally terminates the beverage system (carb-water out, two reservoir/bag
lines, CO2 in, water in from the SeaFlo, PRV vent) and the low-voltage sensing (reservoir
reeds, carbonator reeds, tank/evap temperature) — its 10 modeled connectors below.

## Q1 — Can each connect to each other the way each needs?

**The connections all exist and are now declared. Two are geometrically well-served; the rest
are blocked on the compressor's rotation and the condenser's undefined ports.**

- **refrig-3 (evaporator → compressor suction): serviceable.** The evaporator outlet exits
  the foam front face at (141.5, 155, 191); the compressor suction stub is at (146.75, 0, 78).
  The X's align to ~5 mm. Both face −Y (front), so the line is front-face-to-front-face — it
  exits the compressor forward, curves up 113 mm and back 155 mm to the foam's forward stub.
  Workable in annealed copper, but the back-and-up run is longer than it would be if the
  compressor stubs faced the cold core.
- **refrig-1 (compressor discharge → condenser): long, and pointed wrong.** The discharge
  stub is at (59.25, 0, 78) on the front face, front-**left**; the condenser is far right
  (X ≥ 213). The line must cross ~154 mm rightward across the front of both floor parts, and
  the stub faces away from the condenser (−Y, not +X). The condenser inlet position is
  undefined, so the run's true length/bends can't be closed yet.
- **refrig-2 (condenser → evaporator): can't be assessed.** The condenser outlet + its brazed
  drier/cap-tube are unpositioned. The evaporator inlet is fixed at (141.5, 155, 72). See Q3
  for the 4 mm channel this subassembly has to live in.
- **The rotation, precisely.** `_contents.py` rotates the shroud 90° about Z before placing
  it. That maps the shroud's one copper-bearing face (native −X "left") to world −Y (front)
  and its AC face (native +Y "back") to world −X (left wall). So **both refrigerant stubs face
  the front wall**; the AC gland faces the left wall. The AC orientation is fine — the cable
  drops from the shelf and enters from the left. The refrigerant orientation is the open
  question: the single copper face can only point one way, and it currently points at neither
  mate. If front access for brazing/service was the intent, keep it; otherwise rotating the
  compressor so copper faces +Y (serves the evaporator directly) or +X (serves the condenser)
  removes one U-turn.

## Q2 — Does every connector have a position on the component?

**foam 10/10 ✓ · compressor 4/4 ✓ · condenser 0/3 ✗.** Now measured by the `located` axis.

- **foam-assembly — all 10 located and on-surface.** Eight tube penetrations from the
  foam-shell penetration table (carb-water out, reservoir A/B, CO2 in on the +Z top, the two
  evaporator stubs, water in, PRV vent) plus the two reed-cable exits on the −Y wall. Derived
  from the documented cut coordinates; added.
  - *Sub-finding:* the two reed-cable holes carry the **reservoir** level reeds. The tank
    sensors that also land at the cold core — the DS18B20/DS18S20 temperature bus (SIG-1) and
    the carbonator reeds (SIG-2/3) — have **no clearly dedicated exit** in the penetration
    record. They likely share the reed holes or the copper slot; worth pinning when the cold
    core's wiring exits are finalized.
- **compressor-shroud — all 4 located.** The shroud's own generator documents its holes: the
  AC gland (back face) and earth bond, and the two copper clearance holes (left face). Carried
  through the rotation + placement to world coordinates and on-surface-verified. This was
  richer than expected — the compressor's ports were already defined by its sheet-metal part.
- **condenser+fan — 0 of 3.** A placeholder box harvested from the donor ice maker, with no
  port geometry. Its refrigerant inlet, refrigerant outlet, and 12 V fan-power connector are
  declared (so they are visible and counted) but unpositioned. **These are the questions
  below.**

## Q3 — What channels and spaces have these placements created?

Measured between the placed bodies:

| channel | gap | what routes here |
|---|---|---|
| compressor +X ↔ condenser −X | **21 mm** | the refrig-1 discharge line crossing to the condenser; interacts with condenser airflow |
| compressor +Y ↔ foam −Y | **22 mm** | the refrig-3 suction line's back-run; the carb-water riser climbs the foam face just east |
| condenser +Y ↔ foam −Y | **4 mm** | the refrig-2 drier + cap-tube subassembly — **tight** |

- **The 4 mm channel is the risk.** The filter-drier is a fat copper cylinder brazed to the
  condenser outlet; with the cap-tube helix it is a rigid subassembly that must reach from the
  condenser (right) to the evaporator inlet at (141.5, 155, 72) (center-back). 4 mm of depth
  behind the condenser will not hold it — it must live in the 21 mm inter-part channel or
  above the condenser top (Z 181 → foam top 262.9), not behind it. This constrains where the
  condenser outlet port should be (Q below).
- **The 21 mm inter-part channel** is the main floor-level artery: the discharge line and the
  drier/cap-tube both want it, and the condenser's fan pulls air across X through this region.
  Planning it as a shared refrigerant + airflow corridor (rather than discovering the conflict
  when routing) is the Q3 takeaway.
- **Airflow is unplaced infrastructure.** The condenser fan blows along X (side to side). The
  block sits against the right; the enclosure needs intake/exhaust vents on the side walls
  aligned to it. No wall vents exist yet — a future gate (condenser airflow), named here.
- **Planning for more components:** the floor tier is nearly full front-to-back (compressor
  Y[0,133], condenser Y[0,151], foam from Y=155). The only real slack is the 21 mm X-channel
  and the volume **above** the compressor (Z 154.5 → the water deck) and condenser (Z 181 →
  pump-2). Refrigerant routing should claim the X-channel now, before the water-deck parts
  above it are pinned.

## Open questions — to locate the condenser's three ports

The condenser is a harvested donor block, so these come from the physical part, not a
generator. **How to answer:** give each as a **face + two offsets** in the placed frame, or a
world (x, y, z). The condenser occupies **X[213, 269] (56 wide), Y[0, 151] (151 deep), Z[3,
181] (178 tall)**; its faces are −X (interior side, x=213), +X (right-wall side, x=269), −Y
(front, y=0), +Y (toward cold core, y=151), top (z=181). Example answer: *"refrigerant inlet:
+Y face, 40 mm up from the base, 30 mm in from the −X edge."*

1. **Refrigerant inlet** (from the compressor discharge) — which face, and where on it?
2. **Refrigerant outlet + the drier/cap-tube subassembly** — which face is the outlet on, and
   roughly how big is the brazed drier + cap-tube bundle hanging off it (so its envelope can be
   modeled against the 4 mm / 21 mm channels)?
3. **Fan power** (the DC-8 12 V lead) — which face does the fan's pigtail exit?
4. **Airflow direction** — which X face is intake and which is exhaust (sets the side-wall vent
   plan)?

And two confirmations on the compressor:

5. Is the **front-facing** copper (both stubs on the −Y wall) intended for front service
   access, or should the compressor rotate so copper faces a mate?
6. Of the two copper holes, is the **inboard/+X** one (world x=146.75) the **suction** (from
   evaporator) and the **outboard/−X** one (world x=59.25) the **discharge** (to condenser)?
   The shroud calls them "inlet/outlet"; the loop needs suction/discharge assigned.

## Resolution — 2026-07-17 (same day)

All answered and applied; `located` moved 8% → 12% (3/25), the pack still closes.

- **Condenser refrigerant ports on the −X face** (interior side, toward the compressor), from
  step-viewer picks: **inlet (213, 5.5, 175.5)** top-front, **outlet (213, 145.5, 8.5)**
  bottom-back — diagonal corners, the drier + cap-tube hanging off the low-back outlet toward
  the evaporator. **Fan on the +X face**; airflow runs **−X → +X**, so the −X ports side is the
  intake and the +X fan side the exhaust (the side-wall vent plan follows this).
- **Compressor re-rotated −90° (was +90°)** so both copper stubs face **+Y, toward the foam /
  cold core** — not −Y, which faces the removable front shell of that disassembled quadrant.
  The Q1 rotation finding is resolved: suction now exits toward the evaporator directly. The AC
  gland moved to the +X face (into the inter-part channel). Same 178×133×151 footprint, so the
  pack is unchanged. **x=59.25 = suction** (→ evaporator outlet); **x=146.75 = discharge**
  (→ condenser inlet).
- **Correction recorded:** "front-facing for service" was wrong — in the four-piece enclosure
  the −Y face is *toward* the shell that comes off to service this quadrant. A connector's face
  points at its mate, always; that is now a stated rule in requirements.md (`located`).
