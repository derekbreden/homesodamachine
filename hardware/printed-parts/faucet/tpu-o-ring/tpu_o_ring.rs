//! The faucet's TPU thimble, cap down: its cap bore continues into the open sleeve.
//! `tpu_o_ring.py` holds the dimensions and the native body its guide readers use.
use anyhow::Result;
use hsm_kernel::part::{args, write_part};
use hsm_kernel::*;

fn main() -> Result<()> {
    let (n, out) = args()?;
    let height = n.f("total_height")?;
    let cap = n.f("cap_thickness")?;
    let body = Solid::cylinder(V3::ZERO, V3::Z, n.f("outer_radius")?, height)?;
    let cap_hole = Solid::cylinder(V3::ZERO, V3::Z, n.f("cap_hole_radius")?, height)?;
    let sleeve = Solid::cylinder(v3(0.0, 0.0, cap), V3::Z, n.f("inner_radius")?, height - cap)?;
    let thimble = body.cut_all(&[cap_hole, sleeve])?;
    let name = n.text("name")?;
    println!("{}", write_part(&out, name, &[Body {
        name, color: Some(n.color("color")?), solid: &thimble,
    }])?);
    Ok(())
}
