//! Host policies retain the controller limits and optical qualification thresholds.
pub const MAX_SIGMA_MM: f64 = 0.0025;
pub const HOLDOUT_P95_MM: f64 = 0.005;
pub const HOLDOUT_MAX_MM: f64 = 0.010;
pub const FRAME_MAX_AGE_NS: u64 = 200_000_000;
pub const MAX_REVERSAL_DEADBAND: i32 = 32;
pub const MAX_RESPONSE_CONDITION: f64 = 30.;
