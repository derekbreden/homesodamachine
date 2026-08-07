# Flavor Reservoir Level Sensing

Reed-and-float level sensing for each flavor reservoir, following the same architecture as the carbonator vessel ([future.md](/hardware/future.md) "Level sensing" section), with **[4](REEDS_PER_RES) reed switches per reservoir** for ~13-serving-step granularity over the usable fill range.

## Architecture

**Inside the reservoir:**

- A vertical **1/8" ([3.175 mm](ROD_DIAMETER)) 316L SS rod** (Tandefio B0CY4DWJFQ — same SKU as the carbonator vessel's float rod), separately supplied (not printed), cut to [175.4 mm (6.91 in)](RESERVOIR_ROD_LEN). The rod sits at `(x = ±[107](ROD_POSITION_X), y = [32.5](ROD_POSITION_Y))` — the +Y rear half of the reservoir, opposite the bulkhead exit (which faces the −Y front half at y=−28..−64). Bottom end drops into a blind bore in a standing printed **boss** rising from the reservoir BODY wet slope — the slope itself stays continuous and unbroken, no hole cut through it. Top end slips into the existing register **boss** hanging from the cap's underside (resized for the [3.175 mm](ROD_DIAMETER) rod). Specified in `reservoir.py` in this directory — `ROD_POSITION_X`, `ROD_POSITION_Y`, `ROD_DIAMETER`, `ROD_BORE`, `ROD_BOSS_OD`, `ROD_BOSS_HEIGHT`, `BODY_BOSS_HEIGHT`, `BODY_BOSS_FLOOR`. The cavity at y=+45 is ~38 mm wide (vs ~24 mm at y=0), holding the donor donut (27.75 mm measured OD); the rod sits near the far +X wall so the donut rides against it for the short magnet-to-reed path (see "Magnet–reed signal-path geometry" below).
- A small **magnetic float** sliding on the rod. Donor is the YXQ 45 mm float switch (Amazon B08HWRMRQR) in the BOM for the carbonator — a crimped stainless-steel capsule (the commodity ⌀~28 mm SS float common to nearly every SS float switch) with a ferrite ring magnet sealed inside. SS float on the SS rod — same metal, no galvanic couple, no sticky contact.

**Outside the reservoir:**

- A pre-soldered **column of [4](REEDS_PER_RES) reed switches** wired to a bundle of **5 × 22 AWG black silicone conductors** (4 reed signals + 1 shared common return) — the same wire as every other reed/sensor run ([bom.md](/hardware/ledger/bom.md) §11), not a jacketed cable. Each reed has both leads hand-soldered to its signal conductor and the shared common; the bundle runs the length of the column past all [4](REEDS_PER_RES) reeds and is laced (heat-shrink between reeds) into a single pre-assembled piece stiff enough to drop into the foam-shell channel — no per-reed mounting feature needed inside the cold core.
- The **foam shell carries the channel that holds the column** — no separate printed reed-holder part. The channel is a **3-walled box that extrudes OUTWARD** from the reservoir pocket's far ±X wall, out to the outer shell wall it butts against — on this side there is no outboard foam. The original wall is the channel's back / inner face; two new ±y side walls extend outward; a new outer face closes the box. It is a **single vertical channel** centered on y=+45, sized to slip-fit the reed-and-wire column. Full height — top open at the wall top so the column can be dropped in from above before the cap is installed; cavity bottom rests on the foam shell floor at z=`wall_and_floor_thickness`.
- The cable exits as **two ⌀6.5 bores that do not meet**: one −Y through the pocket's −Y wall at `(x = [±109](CABLE_HOLE_X), y = [-62.5](WALL_HOLE_Y), z = [6](WALL_HOLE_Z))`, and one through the outer shell's **−X** front wall — the same wall the shared copper/PRV slot pierces — at that side's station on the front port field. Between them the cable turns onto the port lane and climbs it. **Both** sides' cables cross the −Y wall, because there is one front field and it is on that lane. Reservoir A's draw crosses the same wall at the same y and z, inboard of the cable at x = [±97](FLAVOR_HOLE_X) against the cable's outboard [±109](CABLE_HOLE_X), so the two ⌀6.5 holes keep clear PETG between them; reservoir B's draw leaves by its own +Y wall, so B's cable has that wall to itself. The bag-pocket bottom is open, so the cable runs free from the bottom of the reed channel through the pocket interior to this hole — no dedicated cable channel.
- The column is **held mechanically** by the channel — bottom shelf catches it from below, ±y side walls constrain it laterally, the cap on top traps it from above when installed. **No foam encapsulation** — the reed channel is its own cavity outboard of the pocket wall, and the pre-soldered column drops into it after the body pour has cured ([cold-core.md](/hardware/assembly/cold-core.md) "Final assembly"), so foam never reaches the reeds or their cable. The bag pocket the cable crosses on its way out is an air cavity: the reservoir fills it to [0.5 mm](RESERVOIR_CLEARANCE) on every side and at the top, leaving the pour no way in.

## Reed pitch and what it gets you

Useful Z range for the float on the rod: ~40 mm above the floor (above the wet slope max) to ~210 mm (just below the cap) = ~170 mm of float travel.

| Reeds | Pitch (mm) | Servings per step |
|---|---|---|
| 3 | ~70 | ~17 |
| **4** | **~45** | **~13** |
| 5 | ~35 | ~10 |

[4](REEDS_PER_RES) reeds at ~45 mm pitch is the working spec. The customer-facing display is a 5-state fuel gauge (0, 1, 2, 3, [4](REEDS_PER_RES) reeds triggered) corresponding to roughly empty / quarter / half / three-quarter / full, with each step ≈ 13 servings.

## Magnet–reed signal-path geometry

**Measured (bench, on both the SS carbonator tube and the printed reservoir):** the reed trips reliably with the magnet within ~2 mm of the wall, and gives no signal by ~3 mm off. The float must ride against the wall — `ROD_POSITION_X` parks it there.

**Reed orientation.** The donor donut is an axially-magnetised ferrite ring. Radially outside it, on its mid-plane — where every reed in this appliance sits — the field is purely axial: the radial component vanishes by symmetry on the equatorial plane, the tangential component by axisymmetry. Every reed therefore stands with its [14 mm](REED_GLASS_L) glass envelope **vertical**, parallel to the rod. A reed lying across the path sees nothing; one tilted θ off vertical couples as sin θ. Vertical also puts the trip at the donut's mid-plane, which is what makes one reed one level.

The dominant term in the magnet-to-reed path is **how far the donut floats off the cavity far wall**, not the wall thickness. The fixed part of the path is the reservoir wall (3 mm) + reservoir/pocket clearance (0.5 mm) + ~half a reed body — together ~5 mm. The variable part is the donut-to-wall gap, set by `ROD_POSITION_X` against the measured 27.75 mm donut and its off-center seating on the 1/8" rod (the rod's bore clearance lets the donut settle toward the wall). At `ROD_POSITION_X = [107](ROD_POSITION_X)` the donut's outer edge rides against the cavity far wall (x ≈ 118), keeping the ferrite magnet within a few mm of the reed column — the comfortable-margin end of the table below.

**Signal-strength numbers** for the donor ferrite donut (27.75 mm measured OD, Br ≈ 0.3 T ferrite; field on axis is conservative for a donut this size):

| Magnet→reed distance | Field on axis (approx) | Reed pull-in needed |
|---|---|---|
| ~4 mm (donut riding the cavity far wall) | ~150–200 gauss | ~60–100 gauss — comfortable margin |
| ~6 mm | ~70–100 gauss | ~60–100 gauss — adequate margin |
| ~7.5 mm | ~40–60 gauss | ~60–100 gauss — marginal |
| ≥ ~10 mm (donut floating off the wall) | < 40 gauss | ~60–100 gauss — no pull-in |

The working requirement is that the donut **ride against the cavity far wall**, which puts the magnet in the ~4 mm comfortable-margin row; `ROD_POSITION_X` is set to do that for the measured donut. The field falls off a cliff as the donut moves off the wall — by ~10 mm of magnet-to-reed distance there is no pull-in.

**Off-axis tolerance.** The donut is pinned against its wall, so the magnet-to-wall gap is zero on the rod's own azimuth and opens as the reed walks off it. For the [27.75 mm](DONUT_OD) donut against a flat printed wall the gap grows as s²/(2 × 13.875) — 0.9 mm at 5 mm of lateral offset, 3.6 mm at 10 mm. Inside the carbonator's [123.7 mm](TUBE_ID_MM) bore the wall curves with the donut and the growth is gentler: 0.7 mm at 5 mm, 2.8 mm at 10 mm. **Height is the tight axis; lateral placement has millimetres of slack.**

The carbonator's own reed mount, its two heights, and what they mean in dispensed volume are in [`../reed-bridge/README.md`](/hardware/printed-parts/cold-core/reed-bridge/README.md).

## GPIO budget

[4](REEDS_PER_RES) reeds × 2 reservoirs = **8 input GPIOs needed** for the flavor reservoir level sensing. Allocation:

- **Reservoir A's [4](REEDS_PER_RES) reeds** → MCP23017 0x20 PB[0:3] (Port B inputs beside the chip's 8 valve outputs on Port A). Both expanders are on the controller PCBA; the reeds reach them on the J6 / J7 looms.
- **Reservoir B's [4](REEDS_PER_RES) reeds** → MCP23017 0x21 PB[0:3]. The chip also carries the 4 MANIFOLD-B valve outputs (PA[4:7]), the condenser-fan bit (PA3), and the 2 carbonator reeds (PB[4:5]), leaving 5 spare bits. Map in [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd).

## Parts (per build)

Per-build additions for the flavor-reservoir level sensing are tracked in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §12 "Level sensing":

- **8 Gebildet reed switches** (B0CW9418F6) for the flavor reservoirs — same SKU as the carbonator's 2 reeds; 2 × 6-pack covers all 10 reeds per build (2 carbonator + 8 flavor) with 2 spares.
- **2 YXQ floats** (B08HWRMRQR) — one per flavor reservoir. Donor float ball + its ferrite magnet kept; switch body / cable discarded. With the reed column inside the foam-shell channel (~6 mm magnet-to-reed path), no neodymium upgrade needed. The carbonator's existing 1 unit becomes 3 units per build (1 carbonator + 2 reservoirs).
- **Reed-column wire** — 5 × 22 AWG black silicone conductors per reservoir (4 reed signals + 1 common return), cut from the same BNTECHGO 22 AWG stock as every other reed/sensor run ([bom.md](/hardware/ledger/bom.md) §11); the reed runs land at J6 / J7 as 22 AWG per [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). No jacketed cable — silicone stays flexible and survives thermal cycling in the cold core, where a PVC-jacketed multiconductor would stiffen. Every low-voltage run in the appliance is cut from this one 22 AWG stock; the jacketed cable in the build is only what leaves the cabinet or the shroud.

The reed inputs land on the controller PCBA's MCP23017s (bom.md §1) via the J6 / J7 looms — no expander hardware in this subsystem.

## Calibration

Each reed's position along the column is fixed by how the cable is laid out and where each reed is soldered in. The column's vertical position in the foam-shell channel is set by the channel's bottom shelf. [4](REEDS_PER_RES) reeds span the float's useful Z range with one reed per ~25% of usable volume.

The firmware reads the reed states as a 5-level encoding (0/4 through 4/4 triggered) and reports "servings remaining" in ~13-serving steps.

## Service

The reed column is mechanically held in the channel, not foam-encapsulated, so in principle it can be replaced — lift the cap off, pull the column up and out of the channel from above (the cap above is the only thing trapping it axially). Whether this is practical in the field depends on whether the reservoir has to come out first; the reservoir's outer +X face sits ~0.5 mm from the channel, so the column likely needs to be sized to clear that gap or the reservoir needs to lift out first.

The expected failure mode (reed glass tube fractures, contact corrodes) is well below the appliance's 10-year design lifetime for sealed glass reeds in a dry air environment.

The internal SS rod is a separately-supplied part captured at both ends by printed features: bottom in a blind bore inside a standing boss on the BODY wet slope, top in a slip-fit register boss on the cap's underside. Removing the cap (six M3 × 12 SHCS + gasket) lifts the rod's top out of the cap-side boss; the rod can then be drawn upward out of the body-side boss along with the float, or left standing in the body boss while the float alone is lifted off. The body boss has a printed-solid floor inside it (BODY_BOSS_FLOOR) — the rod tip bottoms out on PETG, never reaches the wet slope, and the slope itself is uncut so the rod cannot fall through into anything beneath it.

## Open items

- **Reed-channel cross-section refinement.** The column wire is settled — 5 × 22 AWG black silicone (4 reed signals + 1 common), same stock as the other reed runs. Remaining: confirm the foam-shell reed-channel cross-section (currently 6 mm deep × 8 mm wide) and the ⌀6.5 exit hole comfortably pass the laced 5-conductor bundle plus the reed bodies (the reed glass, not the wire, is the width driver), and settle the lacing pitch that makes the column stiff enough to drop in as one piece.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reed-bridge/reed_bridge.py`
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
