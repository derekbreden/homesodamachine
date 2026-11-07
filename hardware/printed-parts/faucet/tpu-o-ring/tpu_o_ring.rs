//! The faucet's TPU thimble, cap down, as it seals the soda tube into the Westbrass's top water
//! port: the cap's bore continues into the open sleeve the tube stands in.
//!
//!     tpu-o-ring [<output directory>]
use anyhow::{Result, bail};
use hsm_faucet_numbers::catalog;
use hsm_kernel::part::write_part;
use hsm_kernel::*;
use hsm_tpu_o_ring_numbers as ring;
use std::path::PathBuf;

const NAME: &str = "tpu-o-ring";
const OUTPUT: &str = "hardware/printed-parts/faucet/tpu-o-ring";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: tpu-o-ring [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;

    let height = ring::TOTAL_HEIGHT;
    let cap = ring::CAP_THICKNESS;
    let body = Solid::cylinder(V3::ZERO, V3::Z, ring::OUTER_DIAMETER / 2.0, height)?;
    let cap_hole = Solid::cylinder(V3::ZERO, V3::Z, ring::CAP_HOLE_DIAMETER / 2.0, height)?;
    let sleeve = Solid::cylinder(v3(0.0, 0.0, cap), V3::Z, ring::INNER_DIAMETER / 2.0, height - cap)?;
    let thimble = body.cut_all(&[cap_hole, sleeve])?;
    let body = Body { name: NAME, color: Some(catalog::tpu_black()), solid: &thimble };
    println!("{}", write_part(&out, NAME, &[body])?);
    Ok(())
}
