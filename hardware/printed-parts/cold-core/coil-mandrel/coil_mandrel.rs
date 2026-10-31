//! The coil mandrel: a hollow ring the evaporator tube is wound on, a helical groove cut into
//! it over the wind zone, and a plain handle ring at either end. `coil_mandrel.py` holds the
//! numbers and writes them for this program.
//!
//!     cargo run --release --manifest-path tools/hsm/cold-core/Cargo.toml --bin coil-mandrel -- \
//!         <coil-mandrel.numbers.json> <out dir>
use anyhow::Result;
use hsm_kernel::part::{Numbers, args, write_part};
use hsm_kernel::*;

/// The ring between two radii, standing over a span of Z.
fn hollow_ring(r: (f64, f64), z: (f64, f64)) -> Result<Solid> {
    let section = Profile::circle(v2(0.0, 0.0), r.1).with_hole(Loop::circle(v2(0.0, 0.0), r.0));
    Plane::XY.at(v3(0.0, 0.0, z.0)).extrude(&section, z.1 - z.0)
}

/// The tube's circle, standing in the X-Z plane at the helix's start, carried up the wind zone
/// along the helix the tube is laid on, in a rotation-minimizing frame.
fn groove(n: &Numbers) -> Result<Solid> {
    let start = v3(n.f("helix_path_radius")?, 0.0, n.pair("wind_z_range")?.0);
    let pitch = n.f("pitch")?;
    let circle = Profile::circle(v2(0.0, 0.0), n.f("groove_profile_radius")?);
    Plane::new(start, V3::Z, V3::Y)?.helix_sweep(&circle, V3::ZERO, V3::Z, pitch, n.f("wind_length")? / pitch)
}

/// The grooved ring. The groove overshoots the wind zone by its own radius at each end, and the
/// handle rings fused back over it keep their walls whole.
pub fn build(n: &Numbers) -> Result<Solid> {
    let r = n.pair("mandrel_r_range")?;
    Solid::union_all(&[
        hollow_ring(r, n.pair("mandrel_z_range")?)?.cut(&groove(n)?)?,
        hollow_ring(r, n.pair("lower_handle_z_range")?)?,
        hollow_ring(r, n.pair("upper_handle_z_range")?)?,
    ])
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let mandrel = build(&n)?;
    let name = n.text("name")?;
    let body = Body { name, color: Some(n.color("color")?), solid: &mandrel };
    println!("{}", write_part(&out, name, &[body])?);
    Ok(())
}
