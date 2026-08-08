# Enclosure Mechanical Assembly

The production procedure for standing the machine's pack inside its printed shell and closing the shell around it: refrigeration stratum on the floor, cold core behind it, the power column against the +X wall, the four printed pieces telescoped and cross-pinned, the drip tray in through its own slot, the display let into the facet. No internal plumbing runs, no AC/DC wiring runs — those are downstream in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md). The output is the mechanical canvas everything else lands on.

The arrangement is [`front_half.py`](/hardware/manifold-layout/front_half.py): it places every body and sizes the box around them, and `front-half.scorecard.json` beside it carries every port, every run and every clearance the placement holds. Design intent lives in [`/hardware/future.md`](/hardware/future.md) "Enclosure (back to front)", "Refrigeration", "User-facing surfaces", and "Safety". Part-level READMEs are the source of truth for every component this procedure handles; this document is the build-cadence wrapper.

## The box

Four printed PETG pieces — `enclosure-front-bottom`, `enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top` — measuring [223 × 481 × 358 mm](BOX_SIZE) over the outside with a [3 mm](WALL_T) wall ([`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py)). **There is no separate front panel and no separate back panel.** Every face is a wall of one of the four pieces, and every connection the appliance makes to the world is a hole in one of them: the rear face is the back pieces' own back wall, the display facet is a 45° chamfer in `enclosure-front-top`'s top-front arris, and the hopper is an opening in the top wall that both top pieces take their share of.

- **The Y seam is stated at [200](Y_SEAM).** The front pieces' rear walls telescope into the back pieces — a proud tongue on the side walls and ceiling, and inside the floor slab a shiplap rather than a tongue, so the floor stays flat where the cold core rides across it. Interlocking screw bosses cross-pin the seam from the ±X exteriors, at a level for each end of each piece.
- **The front column's Z seam is stated at [160](Z_SEAM_FRONT).** The back column's is searched instead — the cold core stands from the floor slab and the service bay stands on its lid, so that column runs solid and its seam takes whatever height the bed and its own lip's ring allow — and it lands at [207.7](Z_SEAM_BACK). The two stagger like a brick bond. The bottom pieces carry the lip and the socket pods, the top pieces the D-pins, and four X-axis screws cross each seam.
- Every piece prints standing on a Z face, lying on its closed face with its seam mouth up, and `bed-fit` on the card holds all four to the H2C's bed.

**Width is set by the refrigeration stratum, not the cold core.** The mated compressor and condenser measure [166](STRATUM_X) across; the core, yawed a quarter turn so its short face crosses the machine, measures [181](CORE_X). `_dims` stands the ±X walls one [14 mm](SIDE_BAND) boss chain off the widest body ON THE FLOOR — a body standing on the slab spans the interior wall to wall, so a wall on its face would leave the corner posts, boss chains and Z-seam pods nowhere to stand. Held off by their own reach, every one of them seats at full section and the bodies seat against the band.

## Scope

In: the integrated refrigerant-loop assembly (output of [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) — cold core with wound coil + plumbed compressor + condenser/fan, charged and run-up-verified); the four printed enclosure pieces + nameplate plaque blank ([`/hardware/printed-parts/enclosure/`](/hardware/printed-parts/enclosure/)); the six bodies seated through the rear wall (three umbilical PP1208E unions with the blue accent ring on the carbonated-water one, the tap-water PP1208E, the C14 mains inlet, and the CO2 DERPIPE) per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md); the drip tray + moisture sensor for the backflow vent; the Waveshare 4.3B display; the bench-built unpowered electronics shelf (output of [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md)).

Out: a complete mechanical chassis — refrigeration stratum standing on the floor slab with the compressor bolted down to it, cold core seated flat on that slab behind it with its front face mated against the stratum's aft plane, the power column standing on the core's cap against the +X wall, the four pieces telescoped and cross-pinned with every rear-wall body installed (`enclosure-back-top` last — see Open items 4), drip tray on its rails, display in its facet. Ready for [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md).

Not in scope: internal plumbing runs through the cabinet — the CO2 chain off the DERPIPE, the tap-water chain off its union, the flavor manifold and the three risers — see [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md); AC + DC + signal wiring runs — see [`wiring.md`](/hardware/assembly/wiring.md); installing the wound coil onto the vessel (already done in [`cold-core.md`](/hardware/assembly/cold-core.md) step 1); refrigerant-loop integration (already done in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)); nameplate plaque serialization, signing, and final application, and seating the silicone funnel in the hopper opening — both happen at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md), not here.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7 (printed enclosure parts), §8 (the rear wall's JG bulkheads), §3 (the §3 PP1208E tap-water inlet), §4 (the DERPIPE CO2 PTC), §5 (the C14 inlet), and §13 (mechanical attach hardware). **The compressor's four floor screws have no §13 row, and neither does anything else in the chassis fastener schedule at Open items 1** — every screw §13 buys is spent on the foam caps, the reservoir caps, the touch-flo plate or the electronics shelf. Status (ACQUIRED / ON-ORDER) lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11. The table below is the procedure-level summary.

| Item | Source / spec | Notes |
|---|---|---|
| Integrated refrigerant-loop assembly | Output of [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) | Cold core + plumbed compressor + condenser/fan, charged, run-up-verified, leak-checked |
| Four printed enclosure pieces | [`/hardware/printed-parts/enclosure/enclosure/`](/hardware/printed-parts/enclosure/enclosure/) | PETG, 3 mm wall; front-bottom, front-top, back-bottom, back-top, all four inside the H2C bed |
| Nameplate plaque (blank) | [`/hardware/printed-parts/enclosure/nameplate/`](/hardware/printed-parts/enclosure/nameplate/) | Pre-printed blank; serialized + signed + applied at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md), not here |
| C14 panel-mount inlet | MXR B07DCXKNXQ ([`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) §1) | Lands from INSIDE — flange on the rear wall's inner face, housing inboard, shroud out through the cutout, recessed [3–5 mm](AC_RECESS_DEPTH) |
| Tap-water bulkhead | John Guest PP1208E B00JYFU8MM ([back-panel §2](/hardware/printed-parts/enclosure/back-panel/README.md)) | Customer-facing 1/4" JG QC on the rear wall; the internal ASSE 1022 chain it feeds sits inside the cabinet |
| CO2-inlet bulkhead | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect ([`/hardware/reference/derpipe-co2-inlet/`](/hardware/reference/derpipe-co2-inlet/)) | **On the rear wall**, east of centre and below the umbilical row; red accent ring at the opening |
| Umbilical PP1208E bulkheads × 3 | John Guest B00JYFU8MM ([back-panel §6](/hardware/printed-parts/enclosure/back-panel/README.md)) | One row across the rear wall; blue accent ring on the carbonated-water union |
| Drip tray + moisture sensor | Tray: [`/hardware/printed-parts/enclosure/drip-pan/`](/hardware/printed-parts/enclosure/drip-pan/) (printed PETG); sensor: Shutao LM393 water-sensor module (B0B2W76MB1, [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md)) | Backflow-vent observation per [`/hardware/future.md`](/hardware/future.md) "Backflow vent monitoring"; sensor wires to SIG-9 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md), terminated at the shelf during [`wiring.md`](/hardware/assembly/wiring.md); the tray rides rails printed on the −X wall's inner face and draws west out through that wall to be emptied |
| Waveshare ESP32-S3-Touch-LCD-4.3B display | B0D925SBYF ([`/hardware/reference/waveshare-43b-display/`](/hardware/reference/waveshare-43b-display/)) | Let into the 45° facet of `enclosure-front-top`; its RS485 link lands in [`wiring.md`](/hardware/assembly/wiring.md) |
| Bench-built electronics shelf | Output of [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md) | Unpowered; AC pigtails hang free, terminated at the C14 inlet in [`wiring.md`](/hardware/assembly/wiring.md) |
| ruthex M3 heat-set inserts + M3 fasteners | ruthex B0D39W228K + BNUOK B0DJQGF665 / B0DJQGVK8S | Per the seam and mount schedules the printed pieces carry; the chassis stations that have none are at Open items 1 |
| Chassis bonding lead — compressor body | Green 18 AWG, ring terminal | Rings under one of the four M3 that bolt the compressor's feet to the floor slab, on the grommet's steel bushing; landed at the ground bus in [`wiring.md`](/hardware/assembly/wiring.md) |

Tooling: standard hand tools — Phillips + hex (2.5 mm for M3), soldering iron + ruthex insert tip for any inserts not pre-installed at the printed-part stage, a level, and a bench fixture that holds the pieces square while the pack goes in (not yet specified — see Open items).

## Procedure

**The box closes around the pack, not the other way round.** The cold core spans the Y seam and the back column's Z seam; the hopper opening spans the Y seam; the flavor pack sets down on the stratum's crown. So the bodies stand on the bottom pieces' floor, the top pieces come down over them, and the front assembly telescopes into the back. Only the drip tray goes in from outside, last, through its own slot — which is what that slot is for.

### 1. Stage the four printed pieces

Print-inspect all four pieces and the nameplate blank. Wipe down every interior face; remove brim residue and any stray support material at the rear wall's bores, the seam lips and socket pods, and — above all — **the floor slab the cold core lands on**. The core bears on that slab across its whole footprint, so a bead of brim under it is a high spot, not a blemish, and the slab is two pieces meeting at the Y seam's shiplap. Set the nameplate plaque aside in the unit's build folder; it does not get applied at this step (see [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md)).

Install ruthex M3 heat-set inserts everywhere the pieces call for them — the Y seam's socket pods, the Z seams' sockets, the C14's two bosses on the rear wall, the four posts standing off the floor slab under the compressor's feet, and the [15](EAST_BOSSES) +X wall bosses the power column bolts to. Standard heat-set procedure: soldering iron on the insert, press straight down until flush. All inserts go in *before* anything is in the box, while there is bench access from every face.

Dry-fit the seams with the box empty: front-bottom into back-bottom, front-top into back-top, then each column's bottom into its top. Confirm every lip telescopes without shaving and every cross-pin plug drops into its socket. **Then take it apart again** — the pack goes in on open floor.

### 2. Seat the rear wall's six connection bodies

All six land in `enclosure-back-top`, on the bench, before that piece goes anywhere near the pack. This is the easier work surface, and it lets each bulkhead's torque load react against a wall that is unobstructed from inside.

**Every hole in this wall is struck on its own fitting's mouth**, so a bore and the barrel that passes it cannot land on two different columns ([`front_half.py`](/hardware/manifold-layout/front_half.py) `back_wall_ports`). The stations:

| Body | Station (x, z) | Wall opening | Seating |
|---|---|---|---|
| Umbilical unions × 3 (PP1208E) | [-80 / -32 / +16](UMBILICAL_STATIONS) at z [337.2](PORT_ROW_Z) | Ø18 round | Flange on the OUTER face, threading through, nut clamped inside |
| Tap-water union (PP1208E) | x [-74](WATER_BACK_X), z [305.4](WATER_BACK_Z) | Ø18 round | Same; its inboard collet is what the ASSE chain butts against |
| C14 mains inlet | [x 54, z 330](C14_BACK) | Rounded rectangle | Flange on the INNER face, two M3 into its own bosses, shroud out through the cutout |
| CO2 DERPIPE PTC | [x 48, z 290](CO2_BACK) | Ø15.42 round | Seated on its own inboard stub tip; the GASHER check threads onto that stub in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) |

**The CO2 comes in at the back wall**, not at the front — tank, tap and umbilical all land on the one face the customer reaches at install. Nothing at all is cut in the front wall.

The three umbilical unions stand [48 mm](UMBILICAL_PITCH) apart on one line. A JG bulkhead nut is [22.86](PORT_NUT_D) mm across the face and a chain of three made-up nuts occupies [82.58](PORT_CHAIN_3) mm, so the row leaves a socket room to get on each nut with its neighbours already made up. The C14's flange is [47](C14_FLANGE_W) mm wide and stands east of the row on its own storey.

Install, in this order:

- **The four JG unions** — flange + EPDM O-ring bearing on the wall's outer face, threading through the bore, nut drawn up from inside. Mechanical capture only; no wall-side gasket. Push-to-connect on both sides, so no tool touches either collet. Confirm the blue-ringed union is the one at [+16](UMBILICAL_CARB_X) — the user-facing rule at install is "blue tube into the blue-ringed bulkhead" per [back-panel "Umbilical port — tube identification"](/hardware/printed-parts/enclosure/back-panel/README.md), and that rule only works if the ring is where the customer expects it.
- **The C14 inlet** — it lands from *inside*: flange against the wall's inner face, two M3 into the printed bosses either side of it, and only its moulded shroud reaches out through the cutout. Drawn home, the C13 cord housing nests into the [3–5 mm](AC_RECESS_DEPTH) recess on insertion. Solder-tab pins face into the cabinet.
- **The DERPIPE** — 5/16" collet outboard, NPT stub inboard, seated so the wrench hex clears the wall's outer face by enough for a socket. The stub is what the GASHER makes up against, so nothing threads onto it here.

Set the populated back-top piece aside; the power column joins it at step 5, and it closes in step 6.

### 3. Stand the refrigeration stratum on the floor

The compressor body comes in as part of the integrated refrigerant-loop assembly with all refrigerant lines already brazed to it. **It is never separated from that assembly at any point in this procedure.**

**The compressor is the one body in the box that is bolted down to it.** `enclosure._floor_bosses` stands a post on the floor slab under each of the four holes in the compressor's own mounting plate, and each post rises *through* its hole to the plate's crown — so the posts locate the body before a screw is turned, and the standoff a screw crosses is the one the plate asked for rather than a number typed anywhere. Sequence:

1. Set the assembly down with the compressor's **power box facing the front**. Its bolt pattern is symmetric about the plate's centre and the power box is not, so the box is the only feature that tells the two ends apart ([`/hardware/reference/compressor/README.md`](/hardware/reference/compressor/README.md) "Frame") — a plate that will not take all four posts is on the wrong end.
2. Lower it straight down onto the four posts, the cold-core assembly steady on its cart with no tension on the refrigerant lines.
3. Drive one M3 into each post's ruthex insert. **The screw bears on the grommet's steel bushing: the grommet is the isolation element and is never crushed.**

The condenser+fan stands east of it on the same slab, both packed forward — the front wall stands its own seam clearance off their front faces, and nothing else fences them there. **An oblong can has no flat face.** Where a box would meet a neighbour anywhere on a wall, this shell touches the condenser's intake plane along one line — the tangent at its own +X extreme — and the compressor's discharge stub stands on that same line ([`compressor.stations()`](/hardware/reference/compressor/README.md)). So the mating and the refrigerant loop's first joint are one reading, and a gap in one is a gap in the other. Nothing in the box fastens the condenser; it stands on the floor and is held by it and by the body it mates against (see Open items 1, and Open items 2 for the openings its air still has no route through).

**The flavor pack sets down on their crown.** [`manifold_layout`](/hardware/manifold-layout/manifold_layout.py)'s ten valves, six tees and two Kamoer pumps come in as one folded pack that rests on its own four spine hairpins across the two crowns, pump-head faces standing clear above them. It is landed and plumbed in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3, not here; what this step owes it is a level pair of crowns and a clear floor beneath.

### 4. Seat the cold core behind the stratum

The core lands flat on the floor slab — its bottom foam-cap lid is the whole bearing surface, a plane with every cap screw down in a counterbore in its own head pad. Nothing goes under it. Sweep the slab clear of debris first: it is the core's datum, and the Y seam's floor overlap is a shiplap inside the slab, so it is flat across the joint.

Lower the core straight down as a single pre-assembled unit. Its whole [283](FOAM_SHELL_X) × [181](FOAM_SHELL_Y) footprint (per [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "outer_shell" + "foam_lid") bears on the slab, its **front face mated flush against the stratum's aft plane** — 0 by intent, which is what makes the refrigerant runs between them short — and the ±X boss bands' own seam posts fence it sideways.

The coil stubs are already brazed into the donor loop (suction line + cap-tube join) per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) step 4–5 — no brazing work happens here. Confirm no tension is induced on the refrigerant lines as the core seats; the stratum was placed first specifically so the core comes straight down without dragging the brazed joints. Re-check the BPV31 cap is tight (the appliance's single permanent service-access point per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Output condition").

**The core is reached entirely through its lid.** All [7](CAP_CONDUITS) warm-side fluid terminations are cap conduits — bores up the cup's own columns, opening upward on the lid's outer face — so every line that reaches the core arrives at the deck the service bay stands on, and **no live station goes through a core wall**. What is left on the core's front face is the two reed cables and the copper/PRV slot above them; the front face is mated against the stratum, which is exactly why nothing else is bored there. Confirm the seven conduit mouths are open and their countersunk lips clean before anything stands on the lid.

### 5. Stand the power column on the +X flank

The bench-built shelf's five bodies stand against the **+X wall**, and their feet come down onto the cold core's cap when the piece carrying them closes. Each is turned so its own mounting plane — the PSU's potted base, the board's underside, the relay's and the hub plate's undersides, the ground stud's landing face — faces that wall and lands on **one common seat**, the plane the refrigeration stratum's own east face defines. That is what puts the whole group clear of the Y seam's posts, pods and plugs in one test rather than five. **No tray stands under any of them.**

**What holds each one is a printed boss per hole.** `enclosure._east_bosses` grows [15](EAST_BOSSES) of them off that wall's inner face — one for every hole in every body's own pattern, each reaching out to that body's own mounting plane and bored back from its tip for a ruthex M3 short, so the standoff a screw crosses is what the body asked for rather than a number typed anywhere. The screw goes the other way: in through the body from the room. Pattern and screw schedule are [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md)'s.

**Every one of those bosses is on `enclosure-back-top`**, which is why this step is bench work on that piece and not work inside a standing box: the bodies are offered up to its wall and screwed down there, alongside the six connection bodies of step 2, and they come down with it.

The column, aft to fore:

- **Mean Well IRM-90-12ST PSU** — lying on its side against the wall so only its 33.5 mm depth reaches into the lane and its 109 mm long axis runs fore and aft. Its aft face stands just clear of the rear seam, under the C14 inlet's own column.
- **Teyleten relay #1** and the **AC hub** (three Wagos in one printed carrier) stack on the brick's crown, aft-flush with it, each with a clearance floor over the one below. The **ground ring-terminal stack** stands on the relay's own floor, one clearance forward of the frontmost face the pair presents.
- **Controller PCBA** forward of the brick on the same seat, its long edge fore and aft down the flank so only its thickness and components reach inboard. Handle it ESD-safe; the four holes are its electrically isolated MH1–MH4, and the screw heads seat on the top-face pads.

**Relay #2 and the DC distribution block have no station** — see [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md); stage them loose. The shelf is **unpowered** at this step: the AC pigtails from the hub's Wagos hang free and get terminated at the C14's solder-tab pins, which stand on the same wall just aft of the hub, in [`wiring.md`](/hardware/assembly/wiring.md). The compressor's earth-bond lead routes toward the ground stack and waits.

Confirm the board's two exposed edges are clear to a hand and a plug, and that nothing on this flank stands in front of a rear-wall body's own reach inboard.

### 6. Close the box

Join each column at its Z seam, then telescope the front assembly into the back. Every seam closes the same way: the **bottom** piece's three-sided lip telescopes +Z up into the **top** piece, whose D-pins drop into the bottom piece's socket pods as it comes down, and four X-axis screws cross the seam from the ±X exterior faces — one per side wall per Y column.

1. **Front column** — `enclosure-front-top` down over `enclosure-front-bottom`. This is the piece that carries the display facet and the front half of the hopper opening, and it passes over the flavor pack rather than landing on it.
2. **Y seam** — the front assembly telescopes +Y into the back: a proud tongue on the side walls and ceiling, the floor's shiplap inside the slab, and the cross-pin plugs dropping into their sockets as the pieces close. Screws drive in from the ±X exteriors at every level.
3. **Back column** — `enclosure-back-top`, populated per steps 2 and 5, comes down over `enclosure-back-bottom` last. **This piece is the lid over the whole service bay**: the cold core's cap and everything that stands on it — the power column, the water pump, the tap-water chain and the drip tray's own rails — all lie inside its volume, and lifting it is the only access to any of them. Whether it closes here or after the downstream runs are made is not settled; see Open items 4.

With the box closed, confirm from inside: the four JG unions' cabinet-side collets, the DERPIPE's NPT stub and the C14's solder-tab pins are all exposed and reachable; the compressor's terminal block is clear for the AC run arriving from the power column; and **no plumbing or wiring has been routed through any bulkhead at this point.**

### 7. Slide the drip tray in through the −X wall

The tray's rails are printed on `enclosure-back-top`'s −X wall, so this follows that piece down whenever it closes.

Lay the moisture sensor flat in the printed basin ([`drip-pan/README.md`](/hardware/printed-parts/enclosure/drip-pan/README.md)) first, on the floor inside the coves, with its leads over the rim. The probe goes in the tray before the tray goes in the machine: once it is on its rails the basin is under the ASSE chain, and a hand laying a plate flat in it would be reaching past those fittings to do it.

Then **slide the tray in through the slot in the −X side wall**, rim first, east until it stops. The slot is one opening in two rectangles, each cut at what the tray is widest at its own height — the rim above the flange's underside, the 45° haunch below it. The rim rides the two rails printed on that wall's inner face, the tray's two haunches sit down between their inboard edges and centre it, and the stop bar closing the rails' east ends is what it comes to rest against: home is when the rim's west edge is flush with the wall's inner face.

**What carries it is its own rim.** Nothing reaches under the floor — the basin lies over the SeaFlo, so section beneath it would be height charged twice. Nothing fastens the tray either: it draws west back out the same slot to be emptied. Seated, it stands under the fall off the Multiplex 19-0897's atmospheric vent tip, which `front_half.check_vent_lands` holds to the basin's flat floor, inside the coves, so the drip lands on the moisture plate and not on a wall it runs down the outside of. Route the leads toward the power column and leave them loose — termination happens in [`wiring.md`](/hardware/assembly/wiring.md) (run SIG-9 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md)).

### 8. Let the display into the facet, and clear the hopper opening

The **display** goes into the 45° facet chamfered across the top-front arris of `enclosure-front-top` — a solid surface running the box's full width, with the glass centred on it and flat facet either side. The glass is the datum: it seats in the bezel counterbore and the body hangs behind it through the PCB cut-through. Handle it ESD-safe. It is held by the counterbore and nothing else today — see Open items 3. Leave its RS485 and power leads loose for [`wiring.md`](/hardware/assembly/wiring.md).

The **hopper is an opening, not a part.** `enclosure._hopper_hole` cuts it in the top wall behind the display facet, sized off the placed funnel's own collar, and the opening crosses the Y seam — so both top pieces carry their share of it and there is no screw pattern to land. Deburr and wipe the collar seat: the removable silicone funnel's brim underside rests on this face, and brim residue or a stray support nib holds the basin proud and crooked in its frame. Then sight straight down the opening and confirm the fall corridor to the pump row below is clear — the funnel's spout drops through open air to V-B's own inlet, and the pack's keep-outs hold that corridor open. The funnel itself ([`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md)) is seated at finish-and-pack, after the wipe-down, not here.

## Output condition

A complete mechanical chassis ready for [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md):

- Refrigeration stratum standing on the floor slab, compressor west and condenser east, the compressor bolted down on four floor posts with its power box forward and its terminal block bare
- Condenser + fan standing on the compressor's +X tangent, the two closed on that line and the discharge joint made on it
- Cold core seated flat on the floor slab behind the stratum, front face mated flush against it, no tension on the refrigerant lines, all [7](CAP_CONDUITS) cap conduits open on the lid
- Four printed pieces telescoped and cross-pinned at the Y seam and both Z seams, every seam screw driven from a ±X exterior face — `enclosure-back-top` last, since it is the lid over the whole service bay
- Rear wall carrying all six connection bodies: the three PP1208E umbilical unions in one row at z [337.2](PORT_ROW_Z) (blue ring on the carbonated-water one), the PP1208E tap-water union below them, the C14 inlet on its own storey east of the row, and the DERPIPE CO2 inlet below that. Nothing is cut in the front wall.
- Power column bolted to `enclosure-back-top`'s +X wall on [15](EAST_BOSSES) printed bosses, feet on the cold core's cap — PSU, relay #1, AC hub, ground stack and PCBA, every mounting plane on one seat, no tray under any of them — unpowered, AC pigtails hanging free
- Drip tray + moisture sensor on their rails under the backflow vent's fall, sensor leads routed toward the power column (not yet terminated)
- Display let into the facet of `enclosure-front-top`, leads loose
- Hopper opening deburred, fall corridor clear, silicone funnel **not** yet seated (see [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md))
- Nameplate plaque blank set aside in the unit's build folder, **not** applied
- Chassis bonding lead ring-terminated under one of the compressor's four floor screws, on the grommet's steel bushing, routed toward the ground stack, not yet terminated at the bus
- No internal plumbing runs, no AC/DC/signal wiring runs

The card's own reading of the chassis at this point: [59](BODY_COUNT) bodies placed, the pack closing with no two solids sharing volume, and every printed piece on the bed.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **The compressor is fastened; nothing else on the floor is.** Its four grommeted feet have posts under them, struck off its own hole pattern the way the C14's two bosses are struck off its. The condenser's harvested fan-shroud ears have nothing to land on and `enclosure.py` cuts nothing for them, so the condenser and the cold core alike are held by the slab they stand on and by each other. What this needs is the ear stations on `enclosure-front-bottom` — and the condenser's ear pattern is still an estimate until a donor is measured. It also needs the §13 BOM rows for the screws, which do not exist for the compressor's four either: §13 bills the foam caps, the reservoir caps, the touch-flo plate and the electronics shelf, and nothing on this floor.

2. **The condenser's air has no route through the box.** The mating settles where the body stands — east of the compressor, on that shell's own tangent — and the air path off it is the donor fan shroud's, per [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md). The box gives it nothing: `pack.east_ports` and `pack.front_ports` are both empty and the −X wall carries only the drip tray's slot, so there is no opening in any face for air to arrive by or leave by. Needs the openings cut at the finstack's own footprint, clear of the ±X boss chains and the Z-seam pods, on the faces that path asks for.

3. **Five placed bodies have no holder at all**, and the card names them: the ASSE 1022 chain, the suction chain, the discharge chain, the WR1110 secondary regulator and the DIGITEN flow meter. Each has a measured datum and measured room — every one of them is seated on one of its own mouths, at the station the run it carries fixes — and none has a bracket. The WR1110 is the sharpest case: it threads onto nothing at either end, standing one hop of tube ahead of the GASHER check on the CO2 chain's own axis, so a cradle has both a datum to stand off and a measured keep-out either side of it. The display is a sixth, held only by its bezel counterbore. Owned here, needed by [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §1 and §2.

4. **When `enclosure-back-top` closes, and the fixture that holds the box square while it does.** The box closes around its contents rather than receiving them: the cold core spans the Y seam and the back column's Z seam, the hopper opening spans the Y seam, and the flavor pack sets down on the stratum's crown. Of the four pieces, three follow from that. The fourth does not. **`enclosure-back-top` is the lid over the entire service bay** — the cold core's cap, the power column on the +X flank, the water pump, the tap-water chain and the drip tray's own rails all stand inside its volume, and there is no other way in: the hopper opening is in the front column and the Y seam mouth faces the front pack. But [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md) both run downstream of this procedure and both work on that bay. So either this piece closes after them — and this document hands the chassis over with its back column open — or the two downstream procedures move ahead of it. Nothing states which, and all four documents' scope clauses assume the chassis is closed. Also unspecified: the bench fixture that holds the pieces square and the pack steady while they telescope, and whether the build proceeds upright or on its side.

5. **Cold-core bearing plane across the Y seam.** The seam falls inside the core's own footprint, so the core's datum is two printed floor slabs meeting at a shiplap. Open: a first-article check that they come off the plate flat and level enough that the core does not rock across the joint. It stands on its bottom cap's lid, a plate over pour foam that bears at its perimeter wall, so a step at the seam is taken there.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_enclosure_mechanical_sync.py`
