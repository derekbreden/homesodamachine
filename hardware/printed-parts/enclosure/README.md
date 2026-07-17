# Enclosure

The under-counter appliance enclosure — outer dimensions, internal zoning, and what lives where. This README is the architectural orientation for the printed enclosure as a whole; panel-specific design lives in the sub-folders.

The foam shell's envelope at the back (Zone A) is the one volume that cannot move or compress; the enclosure width follows it. Everything else is a working arrangement packed into the voids around it, rearrangeable within the constraints below.

## The 4 zones

- **Zone A (back-bottom):** The cold core — foam shell (~[283](FOAM_SHELL_X) × [181](FOAM_SHELL_Y) × [213.4](FOAM_SHELL_Z) mm) plus its foam-cap stacks top and bottom — occupies the volume entirely. Penetrations on the −Y front wall (facing the appliance front / the user) and the +Z top only — the +Y rear, sides, and bottom are clean. Geometry source: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).
- **Zone B (back-top):** The band above the cold core — the appliance's service bay. The whole electronics shelf (power assembly, controller PCBA, DC distribution block) lies flat on the foam-cap top in the band's front half, and every panel termination — the faucet umbilical, the tap-water inlet, and the C14 mains inlet — penetrates the rear face above the cold core, its body hanging in the band's open rear half. The CO2 line crosses the band's front edge to the foam-cap's +Z top entry, which sits in open air ahead of the shelf. The valve-manifold trays are not yet placed. Shelf detail: [`/hardware/printed-parts/electronics/`](/hardware/printed-parts/electronics/). Back panel: [`back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md).
- **Zone C (front-top):** The flavor funnel over the two peristaltic pumps — a wide silicone funnel dropping through the top-wall opening right of the display, its whole floor one ramp falling to the spout, lifting out by hand to reach the pumps beneath it. Detail: [`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md).
- **Zone D (front-bottom):** Compressor + condenser + fan + water-inlet plumbing subsystem. Compressor sits on the floor in its sheet-metal shroud in front of the foam shell. Condenser along one ±X side wall with the fan axis crossing side-to-side. The Multiplex backflow preventer + drip pan + moisture sensor + SeaFlo pump live here as a co-located plumbing cluster. Compressor shroud: [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md).

## Constraints the layout respects

The zone arrangement above is the current pack — a working layout. It is free to rearrange so long as it respects these physical and functional realities:

- The foam shell is the largest single solid; it cannot move or compress. Its penetrations are on the −Y front and +Z top only — the +Y rear, sides, and bottom stay clean.
- Appliance width follows foam shell width (~[283 mm](APPLIANCE_WIDTH)); the shell is the widest object.
- Appliance depth carries the compressor/condenser block and the foam shell seated against the rear wall behind it, stacked along Y (currently ~[342 mm](APPLIANCE_DEPTH)).
- The condenser and fan need side-to-side cross-flow airflow to reject heat — fan axis between the two ±X side walls.
- The compressor shroud is a fixed-size sheet-metal part enclosing the terminal block + PTC relay/overload (UL 60335-2-89, 130 × 175 × 150 mm interior, the only metal part in the enclosure).
- The flavor funnel feeds the pumps from above and stays top-removable for cleaning.
- The Multiplex drip pan sits directly under the Multiplex's atmospheric vent; the backflow preventer + drip pan + moisture sensor co-locate on the water-inlet path.
- The CO2 line runs from the front face to the foam-cap +Z top entry; the WR1110 secondary regulator sits somewhere along that path.
- The carbonated-water dispense run from the foam-shell −Y water outlet to the front spout stays short.

Everything else is open: which zone holds the electronics, where the compressor block sits relative to the shell, the funnel/pump position and its door, the exact zone boundaries and appliance depth, and all intra-zone placement — SeaFlo diaphragm pump, valve manifold (12 Beduan solenoids), WR1110 bracket along the CO2 path, PRV vent termination on the warm side where a relief event won't soak anything important, and the service-access voids for the BPV31 piercing valve and the reservoir-cap path.

## What is on the front face

- ESP32-S3 config display — a 4.3" touchscreen fixed in the front face, angled up toward the standing user. Default state shows the selected flavor; touch reaches flavor-image/ratio tuning, clean cycles, priming, and advanced settings.
- Front-dispense spout (the drill-trigger moment).
- CO2 inlet — possibly migrated to the furthest-forward edge of a side face. Disconnection-under-pressure cable-whip and asphyxiation risk make this the most physically dangerous connection.
## Sub-folders

- [`back-panel/`](/hardware/printed-parts/enclosure/back-panel/) — rear face of the enclosure.
- [`front-panel/`](/hardware/printed-parts/enclosure/front-panel/) — front face of the enclosure.
- [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/) — separately-printed serialized plaque mounted on the rear face.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/_enclosure_dimensions.py`
