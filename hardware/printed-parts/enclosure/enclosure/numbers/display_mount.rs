//! The display cover and the enclosure's matching side-screw seats.
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
