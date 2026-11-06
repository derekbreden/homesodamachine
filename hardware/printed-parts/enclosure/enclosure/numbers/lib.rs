//! The enclosure's numbers, as its pieces and its model take them: the declared Box's types, the
//! shell's constants and wall faces, the catalog's dimensions and colours, the quadrants and
//! their bands, the exterior's structure, the flute field, and the rear wall's layout and plain
//! lands.
pub mod catalog;
pub mod disposal;
pub mod faces;
pub mod field;
pub mod layout;
pub mod pump;
pub mod quadrant;
pub mod rear_wall;
pub mod shell;
pub mod spec;
pub mod structure;

/// An axis-aligned box: its X, Y and Z spans, each low then high.
pub type Bounds = [f64; 6];
pub type P2 = [f64; 2];
pub type P3 = [f64; 3];
/// A body's colour, linear RGB, as its files carry it.
pub type Color = [f64; 3];
