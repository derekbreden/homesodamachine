//! Represents the purchased copper suction-line coupling in the parts viewer.
use anyhow::Result;
use hsm_kernel::{Pen, Plane, Profile, V2, v2};
use hsm_sandbox::{material, out, show};

const LENGTH_MM: f64 = 16.0;
const SOCKET_DIAMETER_MM: f64 = 6.35;
const WALL_MM: f64 = 0.6;

// The center roll and the deburred mouth edges follow the seller photos.
const ROLL_HALF_WIDTH_MM: f64 = 0.43;
const OUTER_ROLL_DEPTH_MM: f64 = 0.15;
const INNER_ROLL_DEPTH_MM: f64 = 0.23;
const MOUTH_EDGE_BREAK_MM: f64 = 0.06;

fn main() -> Result<()> {
    let end = LENGTH_MM / 2.0;
    let bore = SOCKET_DIAMETER_MM / 2.0;
    let outer = bore + WALL_MM;
    let half_roll = ROLL_HALF_WIDTH_MM;
    let edge = MOUTH_EDGE_BREAK_MM;
    let section = Pen::new(v2(-end, outer - edge))
        .line_to(v2(-end + edge, outer))
        .line_to(v2(-half_roll, outer))
        .arc_through(v2(0.0, outer - OUTER_ROLL_DEPTH_MM), v2(half_roll, outer))?
        .line_to(v2(end - edge, outer))
        .line_to(v2(end, outer - edge))
        .line_to(v2(end, bore + edge))
        .line_to(v2(end - edge, bore))
        .line_to(v2(half_roll, bore))
        .arc_through(v2(0.0, bore - INNER_ROLL_DEPTH_MM), v2(-half_roll, bore))?
        .line_to(v2(-end + edge, bore))
        .line_to(v2(-end, bore + edge))
        .close()?;
    let coupling = Plane::XY.revolve(&Profile::new(section), 360.0, V2::ZERO, v2(1.0, 0.0))?;

    show(
        &out()?,
        "copper-slip-coupling",
        &[("copper-slip-coupling", material("M_COPPER")?, &coupling)],
    )
}
