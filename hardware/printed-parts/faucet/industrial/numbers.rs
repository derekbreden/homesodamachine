//! The Industrial faucet's numbers, in millimetres: the shell's gooseneck and cutters on round
//! stock of its own below the zone-5 seam (a foot disc, a body over the Westbrass and the neck
//! standing on it), and its round above-counter plate and gasket.

use hsm_faucet_numbers::shell::*;

// The base.

/// The round foot the base, the plate and the gasket share.
pub const FOOT_RADIUS: f64 = FOOT_WIDTH.max(FOOT_DEPTH) / 2.0;
/// The foot disc's top.
pub const FOOT_TOP: f64 = 14.0;
/// The body over the Westbrass: its centre behind the shank, and the stock it leaves the cable's
/// turn.
pub const BODY_CENTER_Y: f64 = 5.4;
pub const SIGNAL_TURN_STOCK_ALLOWANCE: f64 = 1.0;
pub const BODY_RADIUS: f64 = WESTBRASS_BORE_DIAMETER / 2.0 + BODY_CENTER_Y + WALL_THICKNESS_MIN + SIGNAL_TURN_STOCK_ALLOWANCE;
pub const BODY_TOP: f64 = ZONE4_Z_TOP;
/// The neck standing on the body up to the seam, and how far it runs on past it.
pub const NECK_CENTER_Y: f64 = SODA_FAUCET_TUBE_Y + TUBE_SHELL_CENTER_Y;
pub const NECK_RADIUS: f64 = TUBE_SHELL_OUTER_R;
pub const NECK_JOIN_OVERLAP: f64 = 0.2;
