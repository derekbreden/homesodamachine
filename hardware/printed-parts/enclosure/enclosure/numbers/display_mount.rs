//! The display cover, the status plate beside it, and the enclosure's matching side-screw seats.
pub const GLASS: [f64; 2] = [113.5, 77.0];
pub const GASKET_THICK: f64 = 1.0;
pub const GLASS_THICK: f64 = 1.0;
pub const GLASS_LAP: f64 = 3.0;
pub const SIDE_BORDER: f64 = 11.0;
pub const END_BORDER: f64 = 3.0;
pub const STATION_INSET: f64 = 5.5;
pub const WIDTH: f64 = GLASS[0] + 2.0 * SIDE_BORDER;
pub const HEIGHT: f64 = GLASS[1] + 2.0 * END_BORDER;
pub const THICK: f64 = 3.0;
pub const CORNER: f64 = 5.0;
pub const WINDOW: [f64; 3] = [GLASS[0] - 2.0 * GLASS_LAP, GLASS[1] - 2.0 * GLASS_LAP, 2.5];
pub const STATIONS: [[f64; 2]; 4] = [
    [-WIDTH / 2.0 + STATION_INSET, -HEIGHT / 2.0 + STATION_INSET],
    [WIDTH / 2.0 - STATION_INSET, -HEIGHT / 2.0 + STATION_INSET],
    [-WIDTH / 2.0 + STATION_INSET, HEIGHT / 2.0 - STATION_INSET],
    [WIDTH / 2.0 - STATION_INSET, HEIGHT / 2.0 - STATION_INSET],
];
pub const CLEARANCE_DIA: f64 = 3.4;
pub const COUNTERBORE_DIA: f64 = 6.2;
pub const COUNTERBORE_DEPTH: f64 = 1.0;
pub const HEAD_DIA: f64 = 5.5;
pub const HEAD_HEIGHT: f64 = 3.0;
pub const SOCKET_FLATS: f64 = 2.5;
pub const SCREW_DIA: f64 = 3.0;
pub const SCREW_LENGTH: f64 = 6.0;
pub const INSERT_DIA: f64 = 4.6;
pub const INSERT_LENGTH: f64 = 4.0;
pub const PILOT_DIA: f64 = 4.0;
pub const PILOT_DEPTH: f64 = 4.4;
pub const BACKING: f64 = 3.0;

/// The display and the status plate share the facet's flat run, with one margin at each of its
/// side edges and the same margin between the two.
pub const FACET_MARGIN: f64 = 6.0;
/// Half the flat run across: the box's half-width less the rounds along the facet's sides.
pub const FACET_HALF: f64 =
    crate::shell::APPLIANCE_WIDTH / 2.0 - crate::structure::SIDE_RADIUS;
/// The display's centre from the box's middle. It slides toward −X, leaving the far run to the plate.
pub const SLIDE_X: f64 = -(FACET_HALF - FACET_MARGIN - WIDTH / 2.0);

/// The status plate: the rest of the flat run, as tall as the cover, in the cover's own frame.
pub const STATUS_WIDTH: f64 = 2.0 * FACET_HALF - 3.0 * FACET_MARGIN - WIDTH;
pub const STATUS_HEIGHT: f64 = HEIGHT;
pub const STATUS_CX: f64 = WIDTH / 2.0 + FACET_MARGIN + STATUS_WIDTH / 2.0;
/// Its screws, level with the cover's: the same inset from its own edges.
pub const STATUS_STATIONS: [[f64; 2]; 4] = [
    [STATUS_CX - STATUS_WIDTH / 2.0 + STATION_INSET, -STATUS_HEIGHT / 2.0 + STATION_INSET],
    [STATUS_CX + STATUS_WIDTH / 2.0 - STATION_INSET, -STATUS_HEIGHT / 2.0 + STATION_INSET],
    [STATUS_CX - STATUS_WIDTH / 2.0 + STATION_INSET, STATUS_HEIGHT / 2.0 - STATION_INSET],
    [STATUS_CX + STATUS_WIDTH / 2.0 - STATION_INSET, STATUS_HEIGHT / 2.0 - STATION_INSET],
];

/// The plate's white artwork, the rear nameplate's: sunk into the black face and standing proud.
pub const INK_DEPTH: f64 = 0.72;
pub const INK_RISE: f64 = 0.48;
/// The frame, the nameplate's line weight, drawn inside the screw heads.
pub const FRAME_LINE: f64 = 0.42;
pub const FRAME_INSET: f64 = STATION_INSET + HEAD_DIA / 2.0 + 1.25;
pub const FRAME_CORNER: f64 = 2.0;
/// The brand mark across, and the height of its centre on the plate.
pub const MARK_WIDTH: f64 = 12.0;
pub const MARK_Y: f64 = 10.1;
/// The rule under the mark, in the frame's weight.
pub const RULE_LENGTH: f64 = 20.0;
pub const RULE_Y: f64 = 0.1;
/// The full-thickness translucent light window follows the LED's mounting bore.
pub const LIGHT_DIA: f64 = LED_BORE_DIA;
pub const LIGHT_Y: f64 = -7.4;
pub const LIGHT_RING: [f64; 2] = [LIGHT_DIA / 2.0 + 0.6, LIGHT_DIA / 2.0 + 0.6 + FRAME_LINE];
pub const LABEL: &str = "ON";
pub const LABEL_Y: f64 = -14.9;

/// The CHANZON clear-lens blue LED stands behind the printed diffuser.
pub const LED_DIA: f64 = 5.0;
pub const LED_FLANGE_DIA: f64 = 5.8;
pub const LED_FLANGE: f64 = 1.0;
pub const LED_LENGTH: f64 = 8.7;
pub const LED_SET_BACK: f64 = 1.0;
/// Its bore below the plate's seat: the flange and a slip.
pub const LED_BORE_DIA: f64 = 6.4;
/// The channel from the bore's foot to the display's PCB pocket that carries its leads.
pub const LEAD_HALF_SPAN: f64 = 3.5;
