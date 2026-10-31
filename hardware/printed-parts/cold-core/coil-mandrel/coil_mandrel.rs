//! The coil mandrel: a hollow ring the evaporator tube is wound on, a helical groove cut into
//! it over the wind zone, and a plain handle ring at either end. `coil_mandrel.py` holds the
//! numbers and writes them for this program.
//!
//!     cargo run --release -p hsm-cold-core --bin coil-mandrel -- <numbers.json> <out dir>
use anyhow::Result;
use hsm_cold_core::{Numbers, args};
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
    let body = Body { name: n.text("name")?, color: Some(n.color("color")?), solid: &mandrel };
    write_payload(out.join("coil-mandrel.step.mesh"), &[body], None, None)?;
    write_stl(out.join("coil-mandrel.stl"), &[&mandrel])?;
    println!("coil-mandrel: {} triangles, {:.1} mm³", mandrel.tris().len(), mandrel.volume());
    Ok(())
}
