//! The umbilical organizer's numbers, in millimetres: a PET-GF puck under the mounting stack that
//! holds the soda tube, the flavor pair, the drain and the signal cable in their places. The quarter
//! inch soda bore takes the tested A sample's fit and the three 4 mm bores the tested B drain bore;
//! the black flavor stock's fit is unmeasured. Bore axes are in the faucet's mounting frame; the
//! puck prints upright, its origin the stock's centre and Z = 0 its bottom face.
use hsm_faucet_numbers::P2;
use hsm_faucet_numbers::paths::{LOWER_BUNDLE_X, LOWER_DRAIN_Y, LOWER_FLAVOR_X, LOWER_RIBBON_Y, LOWER_Y};

/// The round stock.
pub const OD: f64 = 32.0;
pub const LENGTH: f64 = 10.0;
/// The soda tube's bore.
pub const TUBE_BORE: f64 = 6.65;
/// The drain's and each flavor tube's bore.
pub const DRAIN_BORE: f64 = 4.40;
pub const FLAVOR_BORE: f64 = DRAIN_BORE;
/// The cable's flat slot.
pub const CABLE_SLOT_LENGTH: f64 = 5.4;
pub const CABLE_SLOT_DEPTH: f64 = 1.8;
/// The least material between passages.
pub const MIN_MATERIAL: f64 = 1.50;
/// The lead-in at each end of a tube bore, and of the cable's slot.
pub const ENTRY: f64 = 0.40;
pub const CABLE_ENTRY: f64 = 0.20;
/// The ease on the stock's two rims.
pub const OUTSIDE_EASE: f64 = 0.20;
/// How far the flavor pair spreads out from the stack's places, and how far the pair and the drain
/// sit forward of them.
pub const FLAVOR_SPREAD: f64 = 2.40;
pub const FLAVOR_FORWARD: f64 = 1.80;
pub const DRAIN_FORWARD: f64 = 2.30;
/// The cable's axis.
pub const CABLE_XY: P2 = [LOWER_BUNDLE_X, LOWER_RIBBON_Y];
/// The flavor pair's axes, in X either side, and in Y.
pub const FLAVOR_X: f64 = LOWER_FLAVOR_X + FLAVOR_SPREAD;
pub const FLAVOR_Y: f64 = LOWER_Y - FLAVOR_FORWARD;
/// The stock's centre: on the bundle's line, equidistant from the soda tube and the flavor pair.
pub const CENTRE_XY: P2 = [
    LOWER_BUNDLE_X,
    (FLAVOR_X * FLAVOR_X + FLAVOR_Y * FLAVOR_Y - LOWER_BUNDLE_X * LOWER_BUNDLE_X) / (2.0 * FLAVOR_Y),
];

/// What passes through the puck.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Passage {
    /// A round tube bore of this diameter.
    Bore(f64),
    /// The cable's flat slot.
    Slot,
}

/// Each passage's name, axis in the mounting frame, and kind.
pub const BORES: [(&str, P2, Passage); 5] = [
    ("S", [0.0, 0.0], Passage::Bore(TUBE_BORE)),
    ("F1", [LOWER_BUNDLE_X + LOWER_FLAVOR_X + FLAVOR_SPREAD, FLAVOR_Y], Passage::Bore(FLAVOR_BORE)),
    ("F2", [LOWER_BUNDLE_X - LOWER_FLAVOR_X - FLAVOR_SPREAD, FLAVOR_Y], Passage::Bore(FLAVOR_BORE)),
    ("D", [LOWER_BUNDLE_X, LOWER_DRAIN_Y - DRAIN_FORWARD], Passage::Bore(DRAIN_BORE)),
    ("SIG", CABLE_XY, Passage::Slot),
];
