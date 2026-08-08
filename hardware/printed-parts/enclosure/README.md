# Enclosure

The appliance enclosure — outer dimensions, internal zoning, and what lives where. This README is the architectural orientation for the printed enclosure as a whole; panel-specific design lives in the sub-folders. The cabinet it installs into, and what is already in there, is [`/marketing/install-envelope.md`](/marketing/install-envelope.md).

This is the **thin** machine: tall and narrow, [223 mm](APPLIANCE_WIDTH) wide × [481 mm](APPLIANCE_DEPTH) deep × [358 mm](APPLIANCE_HEIGHT) tall. Two of those three are bounds rather than consequences:

- **Width** is the widest body ON THE FLOOR plus the seam machinery's own reach either side. `enclosure._dims` stands each ±X wall one [14](WALL_STANDOFF) mm boss chain off that body, so the boss band the wall carries lands on the body's own face rather than in front of it. The refrigeration stratum is that body — the shroud and the condenser mated, [189](STRATUM_W) across. The cold core is narrower: its foam shell is ~[283](FOAM_SHELL_X) × [181](FOAM_SHELL_Y) × [213.4](FOAM_SHELL_Z) mm and it is **yawed a quarter turn**, so the 181 runs across the machine and the 283 runs front to back.
- **Height** is stated (`enclosure.appliance_height`) — the silhouette the edition exists for. The contents live under it; the build fails if they cannot.
- **Depth** follows the pack: the stratum's own [178](STRATUM_D) mm, the core's long axis behind it, and the walls and standoffs around the pair.

What the core's yaw buys is vertical: a column above and ahead of it, where the width used to be spent sideways.

## Where the pack stands

**The refrigeration stratum is the front of the floor, up to z [151](STRATUM_TOP).** The compressor stands **upright** on its own plate — the oil charge sits in the bottom of the hermetic can and the pickup is gravity-fed, so a yaw is the only turn it has. Its shell is a pressed oblong, so it meets a neighbour along a TANGENT LINE and not a face. The condenser block stands beside it on the same floor, its west face on the compressor's discharge tangent at x [27](MATE_X), and the pair is yawed as one and centred on x = 0. That carries the block's airflow axis **across the machine**: only its [56](CONDENSER_ACROSS) mm of fan-and-finstack depth runs on X, its [178](CONDENSER_LONG) mm long face runs front to back, and its [151](CONDENSER_STANDING) mm standing face is what fills the height. It draws through the −X side and exhausts out the +X one it stands against, so the hot end leaves by the nearest wall and what crosses the cabinet is the cool intake. The pair's two crowns differ by [16](STRATUM_STEP) mm, the condenser's being the higher; the compressor's roof stands at [135](COMPRESSOR_ROOF). Geometry sources: [`/hardware/reference/compressor/README.md`](/hardware/reference/compressor/README.md), [`/hardware/reference/condenser-block/`](/hardware/reference/condenser-block/).

**The cold core is the back of the floor.** It stands flat on the floor slab — its bottom cap's lid is a plane and every cap screw is down in a counterbore, so nothing goes under it — with its front face butting the stratum's aft plane at y [178](CORE_FRONT_Y), gap 0 by intent. Its cap's lid at z [253.4](CORE_CROWN) is the service bay's floor. Geometry source: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).

**The flavour manifold stands on the stratum's crown**, [188.4](MANIFOLD_W) × [243.1](MANIFOLD_D) × [161.6](MANIFOLD_H) mm, topping out at z [313.1](MANIFOLD_TOP). It is folded: a quarter turn about X lays its pump-head faces down and a half turn about Z brings the pumps to the front of it, so the two valve decks — [59.4](DECK_SEP) mm apart — stand aft of the pumps rather than over them, and every mouth that faced the back now faces up. What it sets down ON is not a body but the four spine hairpins the fold put on its own underside, at the aft end under those decks: the pack rests on four tube arcs and the pump-head faces stand [16.87](PUMP_FACE_CLEAR) mm clear of the crown. [6](OVERHANG_N) of its bodies reach aft over the cold core, overhanging its front face by up to [65.08](CORE_OVERHANG) mm and clearing its crown by [3.114](CORE_OVERHANG_CLEAR) mm — the seam between the two halves is measured against what reaches BELOW that crown, and what stands over it is left to overhang. Geometry source: [`/hardware/manifold-layout/README.md`](/hardware/manifold-layout/README.md).

**The service bay is the column over the core's cap** — [98.6](DECK_HEIGHT) mm from the lid at [253.4](DECK_TOP) to the interior ceiling — in three lanes:

- **The middle lane is the water pump.** The SeaFlo lies flat on the crown, motor axis front to back because it is 187 long against a 181-wide cap, aft face flush with the core's own back. Its crown at z [325.4](PUMP_CROWN) is the tallest thing in the bay, and the panel deck overhead is struck on it.
- **The +X flank is the power block**, every body on one wall seat so the whole group stands clear of the posts, pods and plugs the Y seam puts in that band: the PSU brick on its side, the controller board forward of it on the same seat, and the relay, the AC hub and the ground stud stacked on the brick's crown. The C14 inlet and the CO2 chain take the wall above and below them.
- **The −X lane is the tap water.** It runs FORWARD from the back wall: the bulkhead union, the ASSE 1022 backflow chain butted straight onto it, the split one straight length ahead of that, then the flow regulator on the same axis. V-K and the suction chain sit east of the pump on the same cap. The chain's atmospheric vent weeps down its own column onto the drip basin, which stands over the pump's bracket on rails printed on the −X wall and draws out through that wall's slot to be emptied.

**The top of the box is packed.** A flat 45° facet chamfers the whole top-front arris, wall to wall, with the ESP32-S3 config display let into it and flat 45° face either side. Immediately behind it, the flavor funnel takes the top wall's full width and reaches aft for the plan area its capacity needs — which puts it across the front↔back seam, both halves taking their share of the opening. Detail: [`enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md), [`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md).

**The back column carries no open Z band under its content, so its seam runs through it.** The core's cap stack runs from the floor slab and the whole bay stands on its lid, so the column is solid to the bay's crown and every band it leaves open stands higher than a [320](BED_Z) mm bed carries the piece beneath. A Z seam's lip is a one-wall ring inset from the cavity, and the pack stands one wall off the front and back walls and one boss chain off the sides, so that ring runs free at every height; the seam takes the bed's own band, nearest the box's half-height — [207.7](BACK_Z_SEAM), leaving [223.8](BACK_BOTTOM_H) mm under it. The cold core spans it, as it spans the front column's seam on the other side of the Y joint.

**What crosses the back wall.** The three umbilical unions — carbonated water to the faucet and the two flavour lines to their nozzles — cross on one storey at z [337.2](PORT_ROW_Z), at a [48](PANEL_PITCH) mm pitch, which is well past what a socket needs to reach a nut with its neighbours made up. The band they take is the one over the pump's crown and under the top wall, open from the west boss chain across to the C14's own corner. The tap-water union stands lower, at z [305.4](WATER_PORT_Z), on the ASSE chain's own inlet column, so the joint between the two is flush and the chain stands as far aft as the wall allows. The mains C14 and the CO2 chain take the +X flank beside the power block. Detail: [`back-panel/`](/hardware/printed-parts/enclosure/back-panel/).

**The cold core is reached through its cap, not through its wall.** All four reservoir lines land on cap conduits — bores up the cap's own columns, each opening on the lid's outer face, which is the bay's own floor — so a line reaching one arrives at the deck rather than at a body face, and none of them crosses the shell. Reservoir A is filled on [443.1](FILL_A_LEN) mm and drawn on [134.4](DRAW_A_LEN); reservoir B on [194.3](FILL_B_LEN) and [134.4](DRAW_B_LEN). The carb riser leaves the core's own outlet conduit and runs [225.5](CARB_LEN) mm forward to the flow meter lying inline ahead of its union. The two flavour lines that leave the machine are the longest runs it carries: [476.9](NOZZLE_A_LEN) mm and [360.9](NOZZLE_B_LEN) mm, each turning east on its own lane so neither stands where the other crosses.

**What the scorecard reports:** the `routed` axis at [90](ROUTED_PCT)% — [35](ROUTED_N) of the [39](CONNECTIONS_N) connections the machine owes are built. What is left is counted rather than dropped, so nothing disappears by being absent. The card written beside `front-half.step` carries the rest of the verdict — the clash check, the bend grades, and the gates that block an export.

## Constraints the layout respects

The arrangement above is the current pack — a working layout. It is free to rearrange so long as it respects these physical and functional realities:

- The foam shell is the largest single solid; it cannot move or compress. Its yaw puts its short axis across the machine and its long one front to back, which is what leaves the column above and ahead of it.
- The core spans the box's full depth, so it goes in before the front and back halves telescope together around it. The seam's furniture all lives in the bands the standoffs open, so none of it meets the core.
- The cold core stands flat on the floor, on its bottom foam-cap lid: the six M3 cap screws driven up from below sit in counterbores in the lid's own head pads.
- The condenser's airflow axis is its own short dimension, and it lies ACROSS the machine: the block draws through its finstack from the −X side face and exhausts out the +X one it stands against, so the air crosses the cabinet rather than turning inside it and the hot end leaves by the nearest wall.
- The compressor stands upright, on its own feet, and cannot be laid on its side or inverted: the oil charge sits in the bottom of the hermetic can and the pickup is gravity-fed. That fixes the shroud's open face downward, which leaves a yaw as the only turn it has — and a yaw keeps its copper-bearing face horizontal, so the copper always leaves sideways.
- The compressor shroud is a fixed-size sheet-metal part enclosing the terminal block + PTC relay/overload (UL 60335-2-89, 130 × 175 × 150 mm interior, the only metal part in the enclosure).
- The flavor funnel feeds the pumps from above and stays top-removable for cleaning.
- The drip pan sits directly under the ASSE 1022 chain's atmospheric vent; the backflow preventer + drip pan + moisture sensor co-locate on the water-inlet path.
- Everything the customer draws leaves by the rear umbilical, so the carbonated-water run from the core's outlet to its own bulkhead stays short.

**What is still open:** the side grilles the crossing airflow needs — an intake on the −X face and an exhaust on the +X one — and what ducts the block's faces to them; the funnel and pump access; and the brackets several bodies still hang without. The suction chain, the discharge chain, V-K's cradle, the CO2 regulator's and the flow meter's each have a measured datum and measured room; none of them has a holder. Those are the `held` axis.

## What is on the front face

- ESP32-S3 config display — a 4.3" touchscreen let into the 45° facet, centred, angled up toward the standing user. Default state shows the selected flavor; touch reaches flavor-image/ratio tuning, clean cycles, priming, and advanced settings.
- Nothing else. Every fluid connection the customer makes is on the back wall: the water inlet, the CO2 inlet, and the umbilical that carries carbonated water and both flavours up to the faucet.

## Sub-folders

- [`back-panel/`](/hardware/printed-parts/enclosure/back-panel/) — rear face of the enclosure.
- [`drip-pan/`](/hardware/printed-parts/enclosure/drip-pan/) — internal catch basin under the ASSE 1022 chain's atmospheric vent.
- [`front-panel/`](/hardware/printed-parts/enclosure/front-panel/) — front face of the enclosure.
- [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/) — separately-printed serialized plaque mounted on the rear face.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/_enclosure_dimensions.py`
