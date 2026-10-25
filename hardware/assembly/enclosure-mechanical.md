# Enclosure Mechanical Assembly

The mechanical build joins the refrigeration base, cold core, front valve manifold
and above-core equipment inside four printed quadrants. The funnel frame installs
after the accessible central plumbing and wiring connections. The electronics
ceiling is continuous; rear connections are prepared on the open back-top.
The [above-core arrangement](/hardware/manifold-layout/above-core.md) defines native
component poses and mechanical ownership. The procedures for the fluid paths and
conductors are [internal plumbing](internal-plumbing.md) and [wiring](wiring.md).

The current fit adjustment covers PET-GF mating with PET-GF in the enclosure. Rigid-part
fits elsewhere remain subject to the same printed-face allowances and are unresolved by
this pass. Compliant gaskets and seals use their specified installed squeeze in the compression
direction. The core's nominal crown remains Z253.4 and its hold-down foot is Z253.65.
The [native fit review](/hardware/printed-parts/enclosure/enclosure/y-seam-fit-review.json)
binds the measured enclosure interfaces and local stock to their production artifacts.
Its cradle finish and protected-joint comparison retain the named hook, web and
silicone-bearing measurements. It does not establish physical assembly force or lifetime.

## The box

Four printed PET-GF15 quadrants — `enclosure-front-bottom`, `enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top` — measuring [215 × 466.3 × 361 mm](BOX_SIZE) over the outside ([`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py)), plus the `enclosure-pump-cartridge` and its top clamp: six printed enclosure pieces in all. Every standing face is a wall of a quadrant: the rear face is the back pieces' own +Y wall, the 30° display plane and its tangent curves are part of `enclosure-front-top`'s top-front arris, the flat front below the facet is the pump cartridge's face, and the funnel opening is cut in the top wall, both top pieces taking their share of it.

- **The Y seam is stated at [200](Y_SEAM).** The front pieces' +Y walls telescope into the back pieces — a proud tongue on the side walls and ceiling, and a full-thickness, square-ended tongue inside the floor slab, so the floor stays flat where the cold core rides across it. At each ±X corner a stack of knuckles, alternating between the front and back pieces, is held by two vertical M5 screws: an [M5 × 120](LOWER_ROD) up from the handhold ceiling through front-bottom's knuckle into an insert in back-bottom's knuckle under the Z seam, and an [M5 × 50](UPPER_ROD) down from back-top's roof into an insert in front-top's knuckle under the funnel frame. Four screws in all.
- **The Z seam is one stated plane, both columns, at [160](Z_SEAM_FRONT)** — the seam line runs level round the box and the four pieces meet at a four-way corner on each side wall. Both columns run solid there (the compressor bay and flavour deck forward, the cold core and service bay aft), so the seam runs through each on the lane its lip's ring keeps of the pack. The bottom pieces carry the lips and hooked rails; the top pieces carry the mating feet and channels. The Z seams take no screws; at the corners the seam's screws hold the tops down.
- **The wall is a fact about a face, not about the box.** [3 mm](WALL_T) is the section a piece starts from and every exterior wall carries at least [6 mm](LIP_UNDERWALL), each grown INWARD — the stated silhouette and `interior_x` both stand still, and only the piece carrying a section knows about it. A bottom piece gets its [6 mm](LIP_UNDERWALL) for nothing down all three of its lipped sides, the lip's own skin carried to the slab. On the top pieces it is stated per face: [9 mm](FRONT_TOP_FLANK) on `enclosure-front-top`'s ±X flanks, [9 mm](BACK_TOP_FLANK) on `enclosure-back-top`'s, 9 mm on its +Y wall and 9 mm on its ceiling, a slab the piece prints on, pocketed over every body that stands in it back to the unchanged z = [352](CEILING_LANE) pack lane. The front face is [9 mm](FRONT_WALL); the complete flavour pack stands behind it with the removable pump face on that same exterior plane. **The floor is the one section that grows OUTWARD** — [6 mm](FLOOR_T) of slab under both bottom pieces, and the stated height is struck to its underside, so the slab stands in the silhouette rather than in the cavity and everything the pack sets on the floor stays where it was. What noses into a section is never moved for it: the wall gives that station back as a stated, 45°-chamfered relief — a Wago well, the PRV chase's rib, the CO2 nut's clamp stack — and `back_wall_t_at`, `box-front` and `back-top-flank-clear` are what read those back against the pack.
- Three quadrants bed on their Z− face — the bottoms on their floor slabs, front-top on its seam rim, mouth down — and back-top beds on its ceiling's outer face, its mouth up. The lower pump cradle and top clamp take their own print orientations; the bed-fit checks belong to each part's source.

**Width is a stated bound, not a consequence of what stands inside.** [215 mm](APPLIANCE_W), struck symmetric about x = 0 — the axis the whole pack is centred on — exactly as the height and the rear plane are stated. No body sets it: a narrower body taking a wider one's place does not make the machine narrower, and a pack that outgrows it reads red on `box-width` rather than quietly resizing the appliance. What that check requires OF a body on the floor is one [14 mm](SIDE_BAND) side band of clearance to the ±X walls **where the seam's corner stacks stand**. The lower knuckles reach 13.75 mm into that band, leaving 0.25 mm to the core. Their reach is in Y and in Z as much as in X: a stack runs from a front knuckle's root [3 mm](Y_STACK_FRONT_ROOT) fore of the seam to the back pieces' thickened flank; the lower stands from the handhold ceiling to the Z seam, the upper from Z[281.4](Y_STACK_UPPER_FLOOR) to the ceiling. Outside those footprints the band is open. The widest thing on the slab is the **cold core**: yawed a quarter turn so its short face crosses the machine, it still measures [181](CORE_X) against the mated compressor and condenser's [174](COMP_BAY_X).

## Scope

Start with the charged refrigeration-loop assembly, the printed quadrants and
cartridge parts, the fixed front manifold, and the unpowered components in
[electronics-bay.md](electronics-bay.md). End with the shell joined around the core
and both roof openings available for final connection work. Fit the roof closures
only when that work is complete. Native fit records describe nominal geometry;
physical assembly force and durability retain the qualification limits below.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7 (printed enclosure parts), §8 (the +Y wall's JG bulkheads), §3 (the §3 PP1208E tap-water inlet), §4 (the ABU44 CO2 bulkhead), §5 (the C14 inlet), and §13 (mechanical attach hardware). The compressor's four floor screws, their M5 inserts and their fender washers are §13 rows of their own, and so are the condenser's two M3 × 8 and their inserts; **the cold core's grips bill nothing** — they are printed features of the pieces themselves, closed by the seam's corner screws already in §13. Status (ACQUIRED / ON-ORDER) lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11. The table below is the procedure-level summary.

| Item | Source / spec | Notes |
|---|---|---|
| Integrated refrigerant-loop assembly | Output of [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) | Cold core + plumbed compressor + condenser/fan, charged, run-up-verified, leak-checked |
| Six printed enclosure pieces | [`/hardware/printed-parts/enclosure/`](/hardware/printed-parts/enclosure/) | PET-GF15 enclosure set: four quadrants, lower pump cradle, pump top clamp |
| Tee caps × 4 | [`/hardware/printed-parts/enclosure/pump-dock/`](/hardware/printed-parts/enclosure/pump-dock/README.md) (printed PET-GF, solid) | Inspected here; snapped over the pump tees at [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3 |
| Nameplate | [`/hardware/printed-parts/enclosure/nameplate/`](/hardware/printed-parts/enclosure/nameplate/) | Printed per unit with its identity encoded in the QR; scanned and snapped in at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md), not here |
| Rear fluid fittings, C14 and RJ11 | [Production arrangement](/hardware/manifold-layout/above-core.md) | Six fluid fittings in a 2 × 3 grid; C14 west/upper, RJ11 west/lower |
| Drop-in funnel frame and snap-in drain joint | [Funnel](/hardware/printed-parts/zone-c/funnel/README.md) | Cradle snaps into the frame’s 3 mm web; frame fastens from above |

Tooling: standard hand tools — Phillips + hex (2.5 mm for M3 socket caps, 4 mm for M5), soldering iron + ruthex insert tips for any inserts not pre-installed at the printed-part stage, a level, and a bench fixture that holds the pieces square while the pack goes in (not yet specified — see Open items).

## Procedure

**The box closes in slides, and the slides fix the order.** Each column's top slides onto its bottom on the Z seams' hooked rails, and **the two columns are mirrored**: front-top enters fore of home, in open air ahead of the box, and draws AFT; back-top enters aft of home, in open air behind it, and draws FORE. Each arrives from the end of the box it stands at, so neither is lifted over the other. A top slides over everything its bottom holds, so the front column closes over the seated stratum with the flavour pack riding the moving piece (§4), and the back column closes over **nothing**: its tub is bare when back-top comes on (§6), because the cold core cannot pass under that piece's own +Y wall. The core enters afterward, through the mouth — the closed back assembly rides forward over the core where it stands tethered to the compressor bay, one continuous motion that ends in the Y seam's own telescope — and the four corner screws close the box. The same four open it. The OVER port and its rectangular chip are fitted while back-top is open on the bench.

### 1. Stage the printed pieces

The bottom pieces' printed lifting ceilings are the finger-contact surfaces of the
handholds. Both halves share one R6 opening and exterior transition, mirrored on the
two flanks, so the lifting edge follows one profile across the Y seam.
Remove loose support material before closing the two halves. The current
bare surfaces' finish, cleanup and comfort remain unqualified by other parts' underside
results.

Print-inspect all six enclosure pieces — the four quadrants, lower pump cradle and pump top clamp — plus this unit's nameplate. Inspect the collet plate's four teardropped tube holes, the release face behind them and the tee wall's four teardropped bores. On the ridge wall behind the display, verify the J9 loom's +X teardrop passage is open and the display backing's cavity face is continuous. The pump cartridge goes in downstream; the pumps they serve are landed in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md). Wipe down every interior face; remove brim residue and any stray support material at the +Y wall's bores, the rails' heads and channels — a bead in a channel is a 100 mm slide that binds at one station — the Y seam's lips and knuckles, and — above all — **the floor slab the cold core lands on**. The core bears on that slab across its whole footprint, so a bead of brim under it is a high spot, not a blemish. Both halves of the floor joint print on their bed faces and end square, one running fit apart. Set the nameplate aside in the unit's build folder; it does not go on at this step (see [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md)). **The display's two printed parts go in that folder with it**, not loose on the bench: the cover plate ([`/hardware/printed-parts/enclosure/display-cover/`](/hardware/printed-parts/enclosure/display-cover/README.md)) and, under it, the TPU gasket ring that goes between the plate's lap and the display's glass ([`/hardware/printed-parts/enclosure/display-gasket/`](/hardware/printed-parts/enclosure/display-gasket/README.md)). Both go on at §8, and the ring is soft, black and one wipe from being swept off a bench unnoticed — a display closed without it is a display the cover plate does not hold.

Front-top and the lower pump cradle carry four attracting SB443-IN pairs, eight blocks:
one column of two on each pump's line in each part, printed in. Each part's print pauses
once while its two slots are loaded down their printed rails, front-top's in the tee wall
behind the bay face and the cradle's in its flat back
([magnet record](/hardware/printed-parts/enclosure/pump-dock/magnet-retention.md)).
Inspect each column's exposed pole faces for chips and check that every block is captured,
moving no more than its 0.1 mm on the rails. The contact pair retains its own
separate factory magnets. Installed cartridge retention is established on the completed
dock rather than inferred from an individual magnet's advertised pull.

Install ruthex heat-set inserts everywhere the pieces call for them. Standard procedure: soldering iron on the insert, press straight down until flush. All of them go in *before* anything is in the box, while there is bench access from every face.

**This step is the one place in the build that presses both M3 bodies, and they are indistinguishable in the hand but for length.** RX-M3x5.7 and RX-M3Sx4.0 carry the same ⌀4.6 knurl into the same ⌀4 hole; a short one pressed where the long one belongs is a weaker joint that looks finished, and a long one pressed where it does not fit will not seat flush. Work from two labelled troughs, not one dish:

- **Full-length RX-M3×5.7.** The condenser fingers, four funnel-frame ledges and relay mounts take full-length inserts. The core's PCB and pump mount columns use the [cold-core mount schedule](/hardware/printed-parts/cold-core/_above_core_mounts.py), with the lid removed for insert installation.
- **Short RX-M3S×4.0.** The C14's two rear-wall bosses and the relays' eight west-wall bosses take short inserts. Install them before the purchased bodies. Their mounting faces are the insert-top datums; use M3 × 10 with Ø7 × 0.5 mm washers at C14 and M3 × 6 through each relay board.
- **M1.4 — two.** The contact pair's male seat in the bay bulkhead's fore face on `enclosure-front-top`. The connector face is recessed [0.125 mm](POGO_FACE_RECESS); its ear datum is [3.125 mm](POGO_EAR_HOST_DEPTH) and the insert's top [5.125 mm](POGO_INSERT_HOST_DEPTH) inside the printed face. The insert starts [2 mm](POGO_INSERT_SETBACK) behind the ear datum. The 2.6 mm wide loading stadium admits the whole Ø2.3 knurl; the Ø2.0 pilot continues 5.5 mm from the insert-top datum. The T18 insert kit stops at M2; use a fine conical tip. The pump clamp's two use the same recessed installation at the cartridge build ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3).
- **M5 — eight.** The four posts standing off the floor slab under the compressor's feet, and the Y seam's four corner-stack stations: back-bottom's two knuckles under the Z seam and front-top's two knuckles under the funnel frame, each pressed in from above. A second tip off the same T18 kit.

The acquired VECO-T T18 assortment includes I/LB fine tips; the M2–M8 insert kit
does not provide an M1.4 tip. Cold-check that the selected fine tip reaches the
insert through the 2.6 mm loading passage without bearing on its printed wall. The modeled knurl clearance does not establish the actual T18 tip profile or cold fit.

Install each M1.4 insert before its connector is fitted. Hold the loose piece with
the bore vertical. Use a spare insert and the existing calipers to set the cold
tip/probe's insertion travel to [5.125 mm](POGO_INSERT_HOST_DEPTH) from the printed mating face; mark that
travel on the probe. Heat and press straight through the clearance entry, stopping
with the insert's top [5.125 mm](POGO_INSERT_HOST_DEPTH) below that face. Allow it to cool, then verify the
depth with the cold probe and calipers before seating the connector. Do not use
the blind end or the connector's screw to force the depth. The current installation must seat a whole insert without melting the ear datum or moving
the connector face more than ±0.05 mm from its designed [0.125 mm](POGO_FACE_RECESS) recess. The M1.4×8 screw engages
[4 mm](POGO_THREAD_ENGAGEMENT) of its 4 mm body and leaves [0.5 mm](POGO_SCREW_TIP_AIR) before the pilot's blind end. Existing coupon acceptance retains its identified seat geometry; the recessed installation and actual tool fit remain unqualified.

The [native heat-set audit](/hardware/printed-parts/enclosure/enclosure/heat-set-review/README.md)
checks the complete host walls, blind relief, caps, entry paths and every corner-stack knuckle.
Use locally solid deposition through these hosts and their roots as specified in
that review. Installed fit, pullout and assembled drop performance remain physical
qualification items.

**Prepare the supports on the bench.** Thread the ASSE, regulator and gas-pair
ties through their fixed-shell windows, and the meter ties through its
back-top collar-bearing windows. Seat the ASSE, regulator and gas bodies in back-top's supports.
Fit bare V-A and V-K to its integral seats, attach their prepared blade leads
and complete their fitted plumbing and inlet header while back-top is open
on the bench. Mount the PSU, relays and meter on back-top; prepare its
continuous external inlet, holder, foam and concealed rear join there. Keep
the funnel frame separate. V-B, the pump and PCB travel with the cold core.

Dry-fit the seams with the box empty: slide each column's top onto its bottom — front-top entering fore of front-bottom's front wall and running AFT to its stop blocks, back-top entering aft of back-bottom's rear wall and running FORE to its own — then part them again and telescope front-bottom into back-bottom, front-top into back-top. Confirm every slide runs its whole travel without shaving, reaches its assembled position, and every knuckle passes its neighbours as the halves telescope.

**Check the printed screw passages at the dry fit.** Each screw must pass through its
[Ø5.6](Y_STACK_CLEARANCE) clearance holes by hand and start in its insert without forcing the
parts sideways. Remove loose support material from the open passages. Confirm the blocks
pass one another during the closing slide. The modeled gaps accommodate printed surface
roughness, including at seating faces; they are not a promise of open space after tightening.
**Then take it all apart again** — the pack goes in first.

### 2. Populate the rear connection face

Work with back-top loose. All station centres are world X/Z millimetres:

| Row | West fluid column X37.25 | East fluid column X77.5 |
|---|---|---|
| Z338.376 | 1/4-inch water inlet, Ø17.44 bore | 1/4-inch CO2 inlet, Ø17.3 bore |
| Z306.376 | 4 mm atmospheric vent, Ø15.3 bore | 1/4-inch soda outlet, Ø17.44 bore |
| Z274.376 | 4 mm flavor A, Ø15.3 bore | 4 mm flavor B, Ø15.3 bore |

Seat each flange outside and its panel nut on the relieved inside land. The fluid
panel retains a 6 mm clamping stack: 4 mm printed wall and 2 mm identification chip. Keep moving release
collets free. Actual fitting make-up and insertion witnesses determine physical
assembly; the reference envelopes do not establish those dimensions.

Fit C14 at X−68.5/Z330, flange in its shallow rear pocket and solder tabs inboard.
The inboard aperture follows the measured chamfered wiring-body profile with
0.25 mm clearance; the separate outboard recess follows the flange's rounded,
tapered outline. This fit basis retains the neighboring WAGO wall and full
3 mm pilot surrounds. Confirm actual seating before tightening; the native
reference does not qualify the physical fit.
Two M3 × 10 screws and Ø7 × 0.5 mm washers engage the short inserts in the wall's integral bosses; the washers bridge the flange countersinks. Fit
RJ11 at X−30/Z274.376 from inside, tang first, and seat its snap latch on the printed
catch. Its receptacle retains the fitted 1 mm shoulder above the swing ease,
3 mm pocket surround and broad wall-rooted corbel. Complete solder/IDC
preparation while the piece is accessible and unpowered.

### 3. Stand the compressor bay on the floor

The compressor body comes in as part of the integrated refrigerant-loop assembly with all refrigerant lines already brazed to it. **It is never separated from that assembly at any point in this procedure.**

**The compressor is the one body in the box that is bolted down to it.** `enclosure._floor_bosses` stands a post on the floor slab under each of the four holes in the compressor's own mounting plate, and each post rises *through* the rubber grommet in that hole to just under the grommet's crown — so the posts locate the body before a screw is turned, and the standoff a screw crosses is the one the plate asked for rather than a number typed anywhere. **The post is the sleeve the mount needs**: Ø12 standing in a Ø14 bore, the rubber round it working in shear, and its crown the surface the washer comes to rest on after squeezing the top flange [0.4](GROMMET_SQUEEZE) mm. Sequence:

1. Set the assembly down with the compressor's **covered power box facing the front**. Its bolt pattern is symmetric about the plate's centre and the power box is not, so the box is the only feature that tells the two ends apart ([`/hardware/reference/compressor/README.md`](/hardware/reference/compressor/README.md) "Frame") — a plate that will not take all four posts is on the wrong end. Confirm the donor's moulded terminal cover is present, uncracked, unmodified, and securely retained; it stays with the compressor throughout the build.
2. Lower it straight down onto the four posts, the cold-core assembly steady on its cart with no tension on the refrigerant lines.
3. Drop an M5 × 25 fender washer over each post and drive one M5 into its ruthex insert. **Draw it down until the washer lands on the post's crown, then stop.** The post's crown stands [0.4](GROMMET_SQUEEZE) mm under the grommet's, so the washer squeezes the top flange by that much on its way and the post takes the load after it — the preload is printed in and no torque figure sets it. A screw that still turns freely has not reached its post; one that needs a bar on it is being driven into a stop that is already home. The washer spans the grommet's bore and lands on nothing but rubber and post, so the can still stands on its four grommets.

The condenser+fan stands east of it, hard against the depth the +X wall's own furniture leaves free, and **off the slab on its own mount**. **An oblong can has no flat face.** The compressor's discharge stub stands on the tangent at its own +X extreme, and the block's header is re-dressed to that stub's column and plane ([`compressor.stations()`](/hardware/reference/compressor/README.md)) — so the lane the block's east position opens is crossed by one straight length of tube and nothing about the two bodies has to touch. Its air crosses the machine through the flank grilles ([the condenser's vents](/hardware/printed-parts/enclosure/enclosure/README.md#the-condensers-vents)).

Both of the block's Y faces stand 20 mm back over its whole width, leaving 0.4 mm of folded sheet at the crown and at the base of each ([`/hardware/reference/condenser-block/README.md`](/hardware/reference/condenser-block/README.md)). Those four flanges are what the box takes:

4. **Feed the aft end onto the fin.** A single fin stands off the +X wall in the bay's east lane with a finger reaching west off it at either end (`enclosure._cond_mount`). Bring the block in with those fingers entering its aft recess, then push it **forward** until the two fore flanges are 3 mm into the grooves of the front wall's two rails (`enclosure._cond_cradle`) and its fore face is flat against the rails' shoulder. **The rails are the datum in Y and their grooves in Z** — the same bargain the gas sensor's card slot strikes. The block is now standing on the lower rail's crown and the lower finger, 9 mm clear of the slab — the depth the lower finger's own bore takes.
5. **Two screws close it.** Both go **down** the one vertical line the donor drilled through its aft flanges. Drive an M3 × 8 through the crown flange's Ø5 hole into the upper finger's ruthex, then one through the base flange's into the lower finger's. **The lower one is reached from behind** — in through the open aft face of that recess, on a long ball-end key leaned aft of the upper finger, with the bay's east lane and the core's bay still clear. Snug both; the sheet is four tenths.

**The gas sensor goes in before either body does.** The MQ-6 card lies ALONG the −X strip and drops straight down into the two grooved posts printed on the floor of it (`enclosure._west_cradle`), can facing WEST toward the flank and header facing EAST into the bay — down until the card lands on the shoulder at the foot of each groove, and there is no screw because the card has no hole. Do it with the front-bottom piece still open on the bench: once the compressor is down, the slot is a reach past a charged assembly for no reason. Its loom lands later, in [`wiring.md`](/hardware/assembly/wiring.md). **Card in the wrong way round is the one error this slot allows** — the can must face the wall, with the four pins standing out into the open bay where the loom can reach them.

**The flavour manifold arrives with `enclosure-front-top`.** Its eight fixed valves
press into the two valve trays, four seats per deck. Y-C, Y-D, Y-F and Y-G are purchased
PP0208E pump tees behind the collet plate, one on each pump port, each branch standing in a
bore through front-top's tee wall. A short straight upper tube joins each tee to the
fore valve over it, and a lower return of two stem elbows and a straight tube joins its lower collet to its rear valve. Keep the
valve terminals and release collets accessible during bench assembly.

**Fit the pump tees before closing front-top.** Its tee wall carries [4](DOCK_TEES) bores behind the collet plate's holes. Seat the rear valves, bring each tee with its upper tube and fore valve in, the branch into its bore from the wall's aft face until the collet bottoms against the plate, and press the fore valve onto its posts. Fit the lower returns from the underside while it is open. The complete bench order is in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3.

After chassis closure, the prepared cartridge's four LLDPE tubes pass the collet plate
into the tees' branch collets together and bottom there, and the magnets seat the
cartridge. The plate holds each branch collet pressed, so pulling the cartridge draws the tubes
straight out; the tees and tubing stay in front-top.

`enclosure-front-top` **slides AFT onto `enclosure-front-bottom`** — brought in from the front, standing [97.66 mm](RAIL_TRAVEL_FRONT) proud of the bottom piece's front wall and drawn straight back to its assembled position at the stop blocks aft of the tee wall. The broad shoulder has 0.25 mm of modeled allowance, and each rail end has 0.25 mm to its stop. This is the piece that carries the display facet, front half of the funnel opening, fixed valve trays, collet plate and the manifold prepared at [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3. The pump tees, their upper tubes and lower returns travel with front-top during this chassis slide. A slide that binds mid-travel is something standing in the channel's lane; a slide that will not close the last millimetre is a foot meeting something on a stop block's face.

The assembled dock's dry connection cycle in [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) records simultaneous tube release and reinsertion, magnetic seating and electrical continuity. Wet sealing, retention under pressure and endurance remain separate qualifications.

The cold core stays **on its cart** through this step, tethered to the compressor bay by the two drawn refrigerant legs hanging out the open back. Keep the cart tracking the bench so neither leg is ever in tension; the core's own seating is §6's ride.

### 5. Populate the cold-core roof and fixed west wall

Mount the PCB flat west/forward on the core lid. Fit the pump with its
motor fore–aft and discharge −X, on four identical rubber feet. V-B enters its
upright socket wall east of the PCB. Use the actual mount holes, fasteners and
insert datums in [electronics-bay.md](electronics-bay.md) and the
[core mount source](/hardware/printed-parts/cold-core/_above_core_mounts.py).
The lid's below-board fluid fittings and routes go in before the PCB.

Fit the PSU and both relays to back-top's dry west wall. Fit the meter to its
sidewall-rooted collar bearings and prepare its inlet and rear outlet there.
Seat the mains WAGOs in the rear-wall
wells. Core-side junctions and ground hardware go in their own lid mounts;
front manifold commons go in front-top. Leave the cross-quadrant conductor ends
accessible for final connection. Keep PSU terminal screwdriver approaches clear.

### 6. Close the box

The column seams use their mirrored slides and four M5 screws. The pump,
PCB and V-B belong to the core. Back-top carries the PSU, relays, meter,
its external continuous inlet/holder/foam and concealed rear join, V-A/V-K
and their fitted plumbing, the complete inlet header, ASSE and gas group.
The V-A low feed connects to front-top's Y-A. Complete rear connections on
the open back-top; keep the funnel opening available for central handoffs.
The populated closing path and continuous-line handling retain the scope of
the [manual assembly record](/hardware/mechanical-qualification/enclosure-above-core/rear-plumbing-assembly.json).

Preassemble the rear soda fittings and meter together while back-top is open.
Their concealed blue tube occupies a nominal 15.7 mm in the meter and
16.891 mm in the return elbow. Replace those allowances with actual receiving
marks. The core guide adds no joint or physical cut in the inlet tube.
Keep the atmospheric drain-vent path open while dressing its final connection.

1. **Back column.** Slide back-top fore onto the empty back-bottom from its aft entry position, through the 237.5 mm rail travel to the stops. Keep the wiring ends supported inside the column and clear of its seam. The ASSE, gas group, source valves and header, PSU, relays, meter and external inlet belong to back-top. Keep the funnel frame separate. Populated-group motion is qualified only to the scope stated in the manual record.

2. **The back assembly rides forward over the core.** Stand the closed back column behind the core's cart, mouth facing the core's aft face, and bring it FORE — the Y-seam mouth swallowing the core, the slab passing under it, the hold-down feet's eased tips riding over the cap's crown — one continuous motion that runs the column's whole depth and ends as the Y seam's own telescope: over the last [17.8 mm](Y_OVERLAP) the front assembly's proud tongue enters the back's mouth, the floor's tongue closes square inside the slab, the corner stacks' knuckles pass one another into place, and the handholds' inner walls close. The rear seam band, front-bottom's corner pockets and cap brackets provide 0.25 mm around the nominal core plan and above its crown. The floor is one plane at Z−0.35: 0.25 mm running plus 0.10 mm cavity-floor transition allowance, over 5.65 mm of slab. The hold-down foot is Z253.65. These are allowances for printed material under the [fit policy](/hardware/printed-parts/enclosure/clearance-audit.md). **Set the core's lid tenants before this ride**: the water pump and everything else that stands on the cap goes on at [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) while the core is still on the open cart, where every face of it is bench work.

   The meter and rear outlet join remain together on back-top. Support the
   continuous inlet where it crosses the plain core guide and keep the
   inter-quadrant tube and wire handoffs free. Do not use the enclosure
   screws to force a fluid joint or a binding slide home.

3. **Four screws.** Support the flank securely over the bench edge.
   Allow about 125 mm clear below the enclosure for the lower screws to enter or withdraw,
   and about 60 mm above the roof for the upper screws.

   Feed each [M5 × 120](LOWER_ROD) screw upward through the handhold's head pocket and
   the knuckles into the insert in back-bottom's knuckle under the Z seam. For each upper
   station, insert the [M5 × 50](UPPER_ROD) screw downward through its roof pocket into
   front-top's knuckle; the upper pocket continues into the funnel opening above the frame. Start every screw in its
   cooled insert by fingers for several turns. Put the long leg of a 4 mm hex key in
   the head and turn its short leg with thumb and forefinger. Stop at the first distinct
   seating resistance, with the head on its floor and free play removed. Do not use a
   screw to pull a binding slide home. The modeled PET-GF-to-PET-GF block allowances
   accommodate printed material; the heads bear on nominal pocket floors. Tightening
   does not guarantee a visible block gap remains.

   No installation torque or retained clamping force is established for these printed parts.
   The lower screws connect both bottom pieces to back-top; the upper screws connect the two
   tops and retain front-top on its sliding rails. The hooked rails retain each top vertically.

   **The brackets retain the core's nominal envelope.** Two brackets
   (`enclosure._core_holds`) stand in the [3 mm](REAR_SEAM_CLEAR) band behind the nominal
   core. The west bracket is 6 mm wide at X−43.6..−37.6 beside the rear
   jack; the east bracket is 9 mm wide at X56.6..65.6 beside the pump. Each has its foot
   [12 mm](CORE_HOLD_REACH) forward onto the aft edge of the cap. Their feet are Z253.65,
   0.25 mm above the nominal cap crown.

Complete rear-wall wiring and tubing on the open back-top subassembly.
Use the remaining funnel opening for the accessible central handoffs between
the front manifold, core and back-top.
Inspect the rear soda engagement and connect the drain-vent line last.
Follow [internal plumbing §4](internal-plumbing.md#4-rear-beverage-connections)
for the bench preassembly and actual insertion marks. The manual rear record
retains the nominal fitting contact and does not qualify hand/tool access,
collet fit, connection force or thread tightening.
The nearby PCB connections remain accessible until the funnel frame is fitted.
Check that all tubing and conductors stay clear of the seam screws and closure
bearings. Keep power disconnected during this work.

Lower the frame and fasten its four M3 screws with the silicone funnel absent.
Lay the silicone funnel and its apron over the screw heads afterward.

For teardown, lift the silicone and disconnect and support the tubing at the
frame's cradled drain elbow. Remove the four funnel-frame screws and lift the
frame with its drain cradle.
Disconnect and support the tubing and leads that cross the separating quadrants,
then reverse the M5 joints and slides.
Pump-cartridge service uses its separate front opening.

**The collet plate is part of front-top.** Confirm through the open bay that each of the
[4](DOCK_TEES) pump tees' collet faces shows through its plate hole and the mating surfaces
are clear.

The bay rides open during enclosure assembly. Connect the prepared cartridge only after
the chassis is closed, per [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md):
present the four straight tubes to the collet plate's holes and push evenly until they
bottom in the tees and the magnets seat the cartridge. Withdrawal separates the magnets,
electrical contact and four collet joints while the tees and tubing stay in front-top.

### 7. Check the vent route

The white 4 mm atmospheric-vent line connects the ASSE's west-facing adapter to
the middle-left rear fitting and the faucet's separate open outlet over the bowl.
Keep that entire path unobstructed. Its actual sleeve fit, retention and venting
performance remain subject to the part's qualification record.

### 8. Let the display into the facet, and clear the funnel opening

The machine display sits in the rounded 30° top. Seat its glass in the shallow
counterbore with the PCB passing through the housing. Handle it ESD-safe.

Place the 1 mm TPU ring on the glass border, aligned with the cover window. Flex
the accepted cover's middle outward to enter both horizontal wings into their
pockets, then let the bezel seat against its back datum. Its visible face finishes
flush with the housing. Confirm that both wings are captured and the cover
resists lift. The [accepted cover](../printed-parts/enclosure/display-cover/README.md)
and [bound native integration check](../printed-parts/enclosure/enclosure/accepted-fit-integration/current-geometry-check.json)
identify the accepted receiver geometry within the check's listed source hashes; there are no display-cover screws.
Leave the display's RS485 and power leads loose for [`wiring.md`](/hardware/assembly/wiring.md).

The ridge wall immediately below the display has the J9 teardrop at
+X for the display loom. Deburr the passage. The fixed J13-to-contact ribbon runs
along the bulkhead crown below the funnel frame. Complete the contact work at the **unpowered,
loose front-top bench stage (EN-10), before the valves, funnel frame and closing slides**.
The bay bulkhead's fore face carries the male seat; its solder tails sit inside the lead
passage when mounted, so prepare and insulate those joints with the half outside its seat.

Use the 350 mm 22 AWG 4P fixed DC-5 ribbon from
[`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md#contact-pair--dc-5).
Split its contact end back 20 mm, put individual heat-shrink sleeves on the conductors,
and feed that free end forward through the bulkhead's lead bore into the empty pump bay.
Solder to the male half in machine-X order: `AM2`, `AM1`, `BM2`, `BM1` from +X to −X.
Insulate each joint, then draw the slack back through the bore. Seat the male half with
its marked end at **−X** and both ear plates on the datum 3 mm behind the connector
contact face, or [3.125 mm](POGO_EAR_HOST_DEPTH) behind the printed mounting face.
Use a **hand-operated 1.3 mm hex driver** to seat **two M1.4 × 8** screws into
the **two M1.4 × 4 × Ø2.3** inserts pressed at §1. Stop with the ear plates
seated flat, without rotating the inserts or bending the ears. Powered torque
settings are not qualified for this joint. The 1 mm ears and
[2 mm](POGO_INSERT_SETBACK) setback give [4 mm](POGO_THREAD_ENGAGEMENT)
nominal thread engagement and [0.5 mm](POGO_SCREW_TIP_AIR) blind-end clearance. The
[mounting audit](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md) identifies those
datums, the attracting orientation and the installed compression limits.

Lay the bare local ribbon along the bulkhead's crown below the funnel frame, with a
relaxed exit behind the contact's insulated solder joints. Keep its labeled J13 end
unplugged and supported, clear of the rails, valves and fixed pump links during the
closing slides. Final cabinet routing and the J13
connection belong to WR-04. The cartridge's leads remain in its cap; nothing on the
cartridge shares this fixed lead. Both connector halves are mounted before the
unpowered cartridge seating and compression check at IP-05.

The silicone funnel seats in a separate drop-in PET-GF frame across the Y seam.
The elbow cradle’s two wings snap through the frame’s 3 mm lower web; the frame
carries the PP0308E elbow and vertical stub. The plug bears on the released hook
tops. Complete and inspect the drain connection before fitting the silicone funnel.

After central connection work, lower the frame vertically onto its four ledges
and engage the cradle’s snap seat. Install four M3 × 12 screws from above into
the RX-M3×5.7 inserts. Seat the heads in their counterbores without using the
screws to pull a binding frame home. The [manual drop-in review](/hardware/printed-parts/zone-c/funnel/drop-in-review/native-review.json)
models the bare frame with the cradle, elbow, stub and tubing removed, plus the
static web/socket and screw stack. Disconnect the drain tube or release the
cradle snap before frame withdrawal. Connected-tube motion, snap-release access
and force, physical fit and the drain seal remain separate qualifications.

The silicone funnel seats on its stub and frame separately; its apron rests on the
roof and covers the frame screw wells. Lift it for cleaning and frame screw access.

## Output condition

- Compressor and condenser retained on their specified floor/wall mounts, with the donor electrical cover intact and the refrigerant loop supported.
- Cold core seated within its nominal floor pocket and hold-down envelope; PCB, pump and V-B on their core mounts.
- Four quadrants home, four M5 seam screws seated, no tube or conductor trapped in a joint.
- Fixed front manifold and rear connection bodies installed; V-A/V-K and their complete inlet header on back-top; PSU, relays and meter on back-top; junctions on their specified parents.
- Machine display retained by the accepted cover and gasket, with contact-pair installation retaining its named fit scope.
- Rear connections completed on the open back-top; accessible central handoffs completed before the drop-in frame is fitted.

Native geometry does not establish physical slide effort, printed support cleanup,
load capacity or lifetime. Preserve accepted results at the
[mechanical qualification index](/hardware/mechanical-qualification/README.md).
The populated build still needs its physical fixture and build-orientation record
before a production procedure can claim a completed assembly qualification.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_enclosure_mechanical_sync.py`
