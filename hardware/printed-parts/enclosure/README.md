# Enclosure

The appliance enclosure — outer dimensions, internal zoning, and what lives where. This README is the architectural orientation for the printed enclosure as a whole; part-specific design lives in the sub-folders. The cabinet it installs into, and what is already in there, is [`/marketing/install-envelope.md`](/marketing/install-envelope.md).

The [fit-clearance coverage](clearance-audit.md) records the shared 0.15 mm static allowance, 0.25 mm sliding allowance and the additional 0.25 mm per supported face across the enclosure and its printed accessories.

This is the **thin** machine: tall and narrow, [215 mm](APPLIANCE_WIDTH) wide × [466.3 mm](APPLIANCE_DEPTH) deep × [361 mm](APPLIANCE_HEIGHT) tall. All three are bounds rather than consequences. `enclosure._dims` measures the pack against each and enters the reading in `BOUNDS`; the box comes back at its stated size either way, so a pack that overruns one gets a wall drawn through it and a red row saying by how much.

- **Width** is `enclosure.appliance_width`, struck symmetric about x = 0. What the pack owes it is clearance, not a datum: a body on the floor slab spans the interior wall to wall, so a floor body is held one [14](WALL_STANDOFF) mm side band in from the wall **where it meets the Y seam's interlocking blocks in depth and in height**. The vertical screws pass through those blocks. Outside their height and depth, the band is open (`enclosure.east_band_free_y`), and a body hung on the flank stands in it. The widest body on the floor is the cold core: its foam shell is ~[283](FOAM_SHELL_X) × [181](FOAM_SHELL_Y) × [213.4](FOAM_SHELL_Z) mm, **yawed a quarter turn** so the 181 runs across the machine and the 283 front to back. The compressor bay ahead of it measures [173.6](COMP_BAY_W) across.
- **Height** is `enclosure.appliance_height` — the silhouette the edition exists for. The contents live under it, and the scorecard carries the reading when they do not.
- **Depth** is `enclosure.rear_plane_y` at the +Y wall. Only the FRONT wall follows the pack, standing one seam clearance ahead of the frontmost body — the compressor bay's own [160](COMP_BAY_D) mm, with the core's long axis behind it.

What the core's yaw buys is vertical: a column above and ahead of it, where the width used to be spent sideways.

## Where the pack stands

**The compressor bay is the front of the floor, up to z [146](COMP_BAY_TOP).** The compressor stands **upright** on its own plate — the oil charge sits in the bottom of the hermetic can and the pickup is gravity-fed, so a yaw is the only turn it has. Its shell is a pressed oblong, so it meets a neighbour along a TANGENT LINE and not a face. The condenser block is struck beside it on the compressor's discharge tangent at x [33.9](MATE_X) and the pair is yawed as one — the compressor's own front face is what that pair is stood on — and the block then goes EAST off that plane, as far as the +X wall's own boss chain leaves free. That carries the block's airflow axis **across the machine**: only its [56](CONDENSER_ACROSS) mm of fan-and-finstack depth runs on X, its [154](CONDENSER_LONG) mm long face runs front to back, and its [137](CONDENSER_STANDING) mm standing face fills the height. It draws through the −X side and exhausts out the +X one it stands against, so the hot end leaves by the nearest wall and what crosses the cabinet is the cool intake. **It is the one body on this floor that does not stand on the slab**: it hangs off its own four sheet flanges, [9](CONDENSER_LIFT) mm up, in a groove off the front wall at the fore pair and on a bored finger under each of the aft pair's two holes. The standoff is the finger's own bore — a screw down through 0.4 mm of sheet has to close on an insert, and an insert needs depth under it. The pair's two crowns differ by [11](COMP_BAY_STEP) mm, the condenser's being the higher; the compressor's roof stands at [135](COMPRESSOR_ROOF). **Neither reaches the flavour manifold**, whose valves are held by the valve trays and cap cradles. The four pump tees stand in front-top's tee wall behind its collet plate, and their lower returns' stem elbows stand clear of the condenser's top ([pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md)). Geometry sources: [`/hardware/reference/compressor/README.md`](/hardware/reference/compressor/README.md), [`/hardware/reference/condenser-block/`](/hardware/reference/condenser-block/).

**The cold core is the back of the floor.** It stands flat on the floor slab — its bottom cap's lid is a plane and every cap screw is down in a counterbore, so nothing goes under it — and packed off the REAR: its own aft face seats flush on the inner face of the rear Z-seam lip, one `rear_seam_clear` inside `rear_plane_y`. Its front face lands at y [182.3](CORE_FRONT_Y) and what falls out AHEAD of it is the lane the refrigerant loop's two drawn legs cross. Its cap's lid at z [253.4](CORE_CROWN) is the service bay's floor. Geometry source: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).

**The front flavour manifold** carries eight fixed valves on two decks behind the
removable pump cartridge. Its four purchased pump tees pass through front-top's tee wall;
upper tubes and lower returns are assembled while that piece is open. V-A mounts on the
cold-core lid beside the west wall and V-B east of the PCB. Their links to Y-A
and Y-B are native production routes. Source geometry:
[`manifold-layout/`](/hardware/manifold-layout/README.md).

**The service bay stands above the Z253.4 cold-core lid.** The pump's motor runs fore–aft
and its discharge faces −X. The PCB lies flat west/forward and the PSU flat west/aft.
Two relays mount on the west wall. The ASSE body lies above the pump with its vent west;
the transverse YZMSZ water regulator feeds V-A. V-K stands beside the east wall on its core-lid upright. The compact
PISCO regulator and neoFit ACHV44-E check form a folded gas group beside that wall.
The [production arrangement](/hardware/manifold-layout/above-core.md) defines their exact
native poses, supports, cap entries and qualification limits.

The funnel frame drops in vertically and takes four recessed screws. Its drain cradle
snaps into the frame's bottom web. Final connections beneath the funnel are made with
the frame absent. An empty screw-fastened panel over the west/aft electronics space provides a
second service opening; it carries no components, wires, tubes or clips.

**The top of the box is packed.** The top-front arris is rounded wall to wall — an R12 off the front wall, a 30° plane, an R18 onto the roof — with the enclosure display let into the plane. Immediately behind it, the funnel takes the top wall's full width and reaches aft for the plan area its capacity needs — which puts it across the front↔back seam, both halves taking their share of the opening. Detail: [`enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md), [`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md).

**The back column carries no open Z band under its content, so its seam runs through it.** The core's cap stack runs from the floor slab and the whole bay stands on its lid, so the column is solid to the bay's crown and every band it leaves open stands higher than a [320](BED_Z) mm bed carries the piece beneath. A Z seam's lip is a one-wall ring inset from the cavity, and the pack stands one wall off the front and +Y walls and one boss chain off the sides. Both columns share the stated seam at [160](BACK_Z_SEAM), leaving [180.8](BACK_BOTTOM_H) mm under the back seam. The front column's condenser and valve-tray wall roots bound that plane; the staggered tray's lower band stays inset from the lip. The cold core spans the seam in both columns.

**The rear connection face** carries six fluid fittings in two columns at X37.25 and
X77.5, with rows at Z338.376, 306.376 and 274.376. Water/CO2 enter at the top,
vent/soda leave at the middle, and flavor A/B leave at the bottom. C14 is west/upper,
RJ11 west/lower. The rear wall is 9 mm stock with a 6 mm fluid-panel clamping section.

**The cold core's fluid routes leave through its cap.** Reservoir cap bores retain their
own datums while selected lid guides clear the PCB and pump. B-fill uses two actual
compact fittings under the lid; A-fill and B-draw use shallow offsets. The gas guide
follows the folded gas group. The carbonator water and soda fitting datums stay fixed.
Tube geometry, insertions and spool choices are authored beside the production poses;
nominal CAD paths are not physical cut-length or pressure qualification.

## Constraints the layout respects

The arrangement above is the current pack — a working layout. It is free to rearrange so long as it respects these physical and functional realities:

- The foam shell is the largest single solid and it cannot compress. Its depth is derived, not fixed: `enclosure_assembly.build_foam` takes the front face as an argument and the pack strikes it on the compressor bay's aft plane, so the core follows whatever stands ahead of it. Its yaw puts its short axis across the machine and its long one front to back, which is what leaves the column above and ahead of it.
- The core spans the box's full depth, so it goes in before the front and back halves telescope together around it. The seam's furniture all lives in the bands the standoffs open, so none of it meets the core.
- The cold core stands flat on the floor, on its bottom foam-cap lid: its cap screws, driven up from below, sit in counterbores in the lid's own head pads ([cold core](/hardware/assembly/cold-core.md)).
- The condenser's airflow axis is its own short dimension, and it lies ACROSS the machine: the block draws through its finstack from the −X side face and exhausts out the +X one it stands against, so the air crosses the cabinet rather than turning inside it and the hot end leaves by the nearest wall.
- The compressor stands upright, on its own feet, and cannot be laid on its side or inverted: the oil charge sits in the bottom of the hermetic can and the pickup is gravity-fed. That fixes its plate on the floor, which leaves a yaw as the only turn it has — and a yaw keeps its copper-bearing tangents horizontal, so the copper always leaves sideways.
- The compressor is the one body on the floor the box fastens: four posts on the slab, struck off its own plate pattern, each rising through the rubber grommet in a plate hole to that grommet's crown, where a washer stops on it.
- The funnel drains by gravity to the funnel gate, V-B, below it: the fixed PP0308E elbow turns the drain aft, and the selected links reach V-B through compact elbows with no upward gravity-drain leg. The silicone stays top-removable for cleaning.
- The ASSE 1022 vent uses its printed TPU drain adapter and white 4 mm LLDPE to the white 4 mm OVER, through the umbilical and faucet to its separate open outlet over the bowl.
- Everything the customer draws leaves by the rear umbilical, so the carbonated-water run from the core's outlet to its own bulkhead stays short.

The crossing airflow's grilles are the flanks' own flutes, pierced over the finstack — an intake on the −X face and an exhaust on the +X one ([the condenser's vents](/hardware/printed-parts/enclosure/enclosure/README.md#the-condensers-vents)); what ducts the block's faces to them is open. The gap beside each grille is [40 mm](/marketing/install-envelope.md), sized so the slot is not what the fan is fighting while it runs.

**The cabinet does not need venting.** ~240 W is what the condenser sheds *while the compressor runs*, and what the cabinet has to carry away is the average behind it: a heavy day's 2.5 L chilled from tap to 2 °C is 314 kJ out of the condenser, which is 3.6 W over 24 hours, call it 5–10 W with the cold core's standing loss on top — a duty cycle around 4 %. A sink base sheds that through the gaps it already has. The Lillium carbonator under this project's own sink has done exactly that for six months in a new house with nothing but door gaps, and keeps its water nearly ice cold on little power. So the grilles answer to the fan, not to the cabinet. The two source tees use commercial collets for factory plumbing. Four more purchased PP0208E tees take the pump tubes at the collet plate, each joined to its fore valve by a short upper tube and to its rear valve by a lower return of two stem elbows and a straight tube. The collet plate holds each tee's branch collet pressed, so during a [pump change](/hardware/service/pump-replacement.md) the four pump tubes draw straight out. Withdrawal and insertion force, retention under pressure, sealing, cleanability and lifetime require physical qualification; the accepted pump-holder and connector fits keep their identified scope.

## What is on the front face

- The machine display — a 4.3" touchscreen let into the rounded 30° top, centred, angled up toward the standing user. Default state shows the selected flavor; touch reaches flavor-image/ratio tuning, clean cycles, priming, and advanced settings.
- The pump cartridge's face — the flat front under the facet, jamb to jamb, filling the bay it slides out of with both peristaltic pumps aboard. A straight pull draws its four pump tubes out of the pump tees' branch collets and parts the four magnet pairs and the electrical contact pair. Detail: [`enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md) "The pump cartridge and its bay".
- Nothing else. Every fluid connection the customer makes is on the +Y wall of back-top: the water inlet, the CO2 inlet, and the umbilical that carries carbonated water and both flavours up to the faucet.

## Sub-folders

- [`y-wall-of-back-top/`](/hardware/printed-parts/enclosure/y-wall-of-back-top/) — that wall's connection inventory. Not a separate part: it is a wall of `enclosure-back-top`.
- [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/) — the 104.53 × 38 mm horizontal brand-and-QR plate, seated in a raised flat field of back-top’s +Y wall below the port grid, retained by its integral horizontal wings.
- [`rear-identification/`](/hardware/printed-parts/enclosure/rear-identification/) — six compact color chips seated under the rear fittings, with raised port names and common row pitch.
- [`electronics-access-panel/`](/hardware/printed-parts/enclosure/electronics-access-panel/) — the empty screw-fastened roof closure over the rear electrical connections.
- [`valve-tray/`](/hardware/printed-parts/enclosure/valve-tray/) — the plate of four valve seats under each of the flavour manifold's two decks. Not a separate part: both are `enclosure-front-top`'s own material, wall to wall.
- [`pump-tray/`](/hardware/printed-parts/enclosure/pump-tray/) — the case-derived collar source used twice in the small `enclosure-pump-cap` top clamp: a plate over the molded flange, an octagonal wall around the boss, and a shoulder around the motor can. Neither collar is separate. Pump weight bears through the molded skirt into the large lower `enclosure-pump-cartridge` cradle.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/_enclosure_dimensions.py`
