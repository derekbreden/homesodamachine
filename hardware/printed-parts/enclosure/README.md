# Enclosure

The under-counter appliance enclosure — outer dimensions, internal zoning, and what lives where. This README is the architectural orientation for the printed enclosure as a whole; panel-specific design lives in the sub-folders.

The enclosure dimensions are driven by three things, in order:

1. The foam shell's envelope at the back (Zone A) — the only volume that cannot move or compress.
2. The electronics shelf + back-panel terminations zone above the foam shell (Zone B).
3. The compressor + condenser + fan zone in front of the foam shell (Zone D).

Everything else fits into the voids those three create.

## The 4 zones

- **Zone A (back-bottom):** Foam shell, occupies the volume entirely. ~[283](FOAM_SHELL_X) × [181](FOAM_SHELL_Y) × [213.4](FOAM_SHELL_Z) mm. Penetrations on the +Y front wall and the +Z top only — back, sides, and bottom are clean. Geometry source: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).
- **Zone B (back-top):** Electronics shelf + back-panel terminations + GFCI module. The shelf is a flat 2D panel; the zone has significant spare volume even at modest height. The CO2 line traverses through here on its way from the front face to the foam-shell's +Z top entry. Shelf detail: [`/hardware/assembly/electronics-shelf.md`](/hardware/assembly/electronics-shelf.md). Back panel: [`back-panel/README.md`](back-panel/README.md).
- **Zone C (front-top):** The flavor funnel over the pump cartridge under a single centered top door — the removable silicone funnel seats on top, the pump cartridge sits beneath it. Detail: [`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md).
- **Zone D (front-bottom):** Compressor + condenser + fan + water-inlet plumbing subsystem. Compressor sits on the floor in its sheet-metal shroud in front of the foam shell. Condenser along one ±X side wall with the fan axis crossing side-to-side. The Multiplex backflow preventer + drip pan + moisture sensor + SeaFlo pump live here as a co-located plumbing cluster. Compressor shroud: [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md).

## What is firm

- Foam shell occupying Zone A entirely, penetrations on +Y front and +Z top only.
- Appliance width ≈ foam shell width (~[283 mm](APPLIANCE_WIDTH)).
- Appliance depth = foam shell depth + condenser depth (~[331 mm](APPLIANCE_DEPTH)).
- Compressor + condenser + fan in Zone D with side-to-side airflow (fan axis between the two ±X side walls).
- Compressor shroud around the compressor's terminal block + PTC relay/overload (UL 60335-2-89, ~130 × 130 × 100 mm working envelope, only metal part in the enclosure).
- Electronics shelf in Zone B above the foam shell.
- GFCI module on the electronics shelf.
- Flavor funnel over the pump cartridge in Zone C, under a single centered top door — funnel removable for cleaning, pump cartridge reached beneath it.
- Multiplex backflow preventer + drip pan + moisture sensor as a co-located plumbing cluster on the water-inlet path, with the drip pan sitting directly under the Multiplex's atmospheric vent.

## What is flexible

- SeaFlo diaphragm pump — anywhere internal.
- Valve manifold (12 Beduan solenoids) — anywhere internal.
- WR1110 secondary regulator placement — has to be along the front → foam-shell top CO2 path, but the bracket location along that path is open.
- PRV vent termination location — somewhere warm-side where a relief event won't soak anything important.
- Service-access volumes for the BPV31 piercing valve and the reservoir-cap path — required negative space rather than objects, but they constrain whatever placements we choose.

## What is on the front face

- ESP32-S3 rotary display — detachable, with a ~1 m cord that pays out behind the panel as the customer pulls the display out. Default state shows the selected flavor; the rotary mechanism toggles between flavors; a subtle three-dot affordance reaches advanced settings. Typical detached placement is the cabinet's false-drawer-front exterior above the cabinet door (the empty flat panel just below the counter where a drawer would normally go) — anywhere the cord reaches works.
- Front-dispense spout (the drill-trigger moment).
- CO2 inlet — possibly migrated to the furthest-forward edge of a side face. Disconnection-under-pressure cable-whip and asphyxiation risk make this the most physically dangerous connection.

The GFCI module sits on the electronics shelf.

## Sub-folders

- [`back-panel/`](back-panel/) — rear face of the enclosure.
- [`front-panel/`](front-panel/) — front face of the enclosure.
- [`nameplate/`](nameplate/) — separately-printed serialized plaque mounted on the rear face.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/_enclosure_dimensions.py`
