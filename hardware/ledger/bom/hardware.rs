//! The hardware the BOM counts that no part's numbers count: the screws the supply, the relays
//! and the C14 inlet take, the relay board and the short insert, the washer under each inlet
//! screw, the compressor plate's hole inset, reservoir A's and the cap's ties, and the seam rods
//! and the funnel frame's screws. Back-top's relay inserts stand back and their pilots run as its
//! rear wall's `hosts` cuts them.

/// The supply's ceiling screws, one through each of its mounting ears.
pub const PSU_SCREWS: usize = 4;

/// A relay board's wall screws, at its header end, their length, and the board they cross.
pub const RELAY_SCREWS: usize = 2;
pub const RELAY_SCREW_LENGTH: f64 = 8.0;
pub const RELAY_BOARD: f64 = 1.5;

/// The short RX-M3S insert each relay screw threads into.
pub const SHORT_INSERT: f64 = 4.0;

/// How far back-top stands each relay insert's face behind its board's hole, and how deep it
/// bores each wall insert's pilot.
pub const RELAY_SETBACK: f64 = 2.5;
pub const PILOT_DEPTH: f64 = 5.0;

/// The C14 inlet's flange screws, one in each ear, their length, and the washer each bears on
/// over the moulding's countersink.
pub const C14_SCREWS: usize = 2;
pub const C14_SCREW_LENGTH: f64 = 10.0;
pub const C14_WASHER: f64 = 0.5;

/// How far in from the compressor plate's edge its bolt holes stand.
pub const COMPRESSOR_HOLE_INSET: f64 = 14.5;

/// Reservoir A's tied stations: its aft saddle, whose slot takes the tie over both lines; the
/// fore pair snaps down into the lid's own seats (`hsm-foam-cap-numbers` `reservoir_a`).
pub const RESERVOIR_A_TIES: usize = 1;

/// The cap's six-inch tie paths: the one through the lid's support under V-B's outlet return,
/// the only union the lid carries (`hsm-foam-cap-numbers` `unions`).
pub const CAP_TIE_PATHS: usize = 1;

/// The rods one flank's Y stack takes, lower and upper, and the funnel frame's screws
/// (`ystacks::y_stack_rods` and `funnel::fasteners` in the enclosure's quadrants).
pub const SEAM_RODS: usize = 2;
pub const FUNNEL_SCREWS: usize = 4;
