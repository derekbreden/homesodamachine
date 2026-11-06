//! The bulkhead ring's identification: the band each rear port's word is lettered in, the
//! lettering, and the word and filament key each station carries. The chips on the wall and the
//! collars on the tubes take these by name, so a word changed for a port changes on both.

/// The band a port's identification is lettered in, the chip's thickness, and the label's rise.
pub const RING_W: f64 = 7.05;
pub const THICK: f64 = 2.0;
pub const RISE: f64 = 18.789;
/// The lettering: its face and weight, its em and cap height, the recess its word fills and how
/// far the word stands proud, and the margin round a word.
pub const WORD_FONT: &str = "Helvetica";
pub const WORD_KIND: &str = "bold";
pub const WORD_SIZE: f64 = 6.5;
pub const WORD_CAP: f64 = 4.951;
pub const WORD_DEPTH: f64 = 1.0;
pub const WORD_RAISE: f64 = 0.48;
pub const WORD_MARGIN: f64 = 1.0;
/// Each word's measured width along its band.
pub const WORD_WIDTHS: [(&str, f64); 5] =
    [("TAP", 12.657), ("SODA", 18.411), ("CO2", 12.813), ("FLAVOR", 25.952), ("DRAIN", 19.671)];
/// Each station in order: its name, the word it carries, and the key its two filaments are read
/// under.
pub const STATIONS: [(&str, &str, &str); 6] = [
    ("water", "TAP", "water"),
    ("carb", "SODA", "carb"),
    ("co2", "CO2", "co2"),
    ("flavor-a", "FLAVOR", "flavor"),
    ("flavor-b", "FLAVOR", "flavor"),
    ("drain", "DRAIN", "drain"),
];
