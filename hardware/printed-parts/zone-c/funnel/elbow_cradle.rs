//! The PET-GF cradle, printed on the stock's bottom face.
mod cradle_geometry;
use anyhow::Result;
use hsm_kernel::part::{args,write_part};
use hsm_kernel::{Body,v3};
use std::path::Path;

fn main() -> Result<()> {
    let (n,out) = args()?;
    let cradle = cradle_geometry::cradle(&n)?;
    cradle_geometry::selftest(&n,&cradle)?;
    if out == Path::new("--check") {
        println!("{{\"checked\":true}}");
    } else {
        let printed = cradle.translate(v3(0.0,0.0,-n.list("block")?[3]));
        println!("{}",write_part(&out,"elbow-cradle",&[Body {
            name:"elbow-cradle",color:Some(n.color("color")?),solid:&printed,
        }])?);
    }
    Ok(())
}
