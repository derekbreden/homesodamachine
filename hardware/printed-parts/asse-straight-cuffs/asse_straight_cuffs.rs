//! The ASSE straight cuffs' files: each TPU cuff turned over to print on its tube end, a file set
//! apiece.
//!
//!     asse-straight-cuffs [<output directory>]
use anyhow::{Result, bail};
use hsm_asse_straight_cuffs_numbers::CUFFS;
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Plane, Profile, V2, V3, v2, v3};
use std::path::PathBuf;

const OUTPUT: &str = "hardware/printed-parts/asse-straight-cuffs";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: asse-straight-cuffs [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    for cuff in &CUFFS {
        let section: Vec<V2> = cuff.section().iter().map(|&[r, z]| v2(r, z)).collect();
        let solid = Plane::XZ
            .revolve(&Profile::polygon(&section), 360., V2::ZERO, v2(0., 1.))?
            .rotate(V3::ZERO, V3::X, 180.)
            .translate(v3(0., 0., cuff.socket_depth));
        let name = cuff.name();
        let bodies = [Body { name: &name, color: Some(hsm_catalog::tpu_black()), solid: &solid }];
        println!("{}", write_part(&out, &name, &bodies)?);
    }
    Ok(())
}
