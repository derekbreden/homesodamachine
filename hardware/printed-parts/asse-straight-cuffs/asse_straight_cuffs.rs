//! Two straight TPU cuffs from their source-owned axial sections.
use anyhow::{Context, Result};
use hsm_kernel::part::{args, write_part};
use hsm_kernel::{v2, v3, Body, Plane, Profile, V2, V3};

fn main() -> Result<()> {
    let (numbers, output) = args()?;
    for cuff in numbers.get("cuffs")?.as_array().context("cuffs")? {
        let side = cuff["side"].as_str().context("cuff side")?;
        let depth = cuff["depth"].as_f64().context("socket depth")?;
        let points = cuff["profile"].as_array().context("axial section")?.iter().map(|row| {
            Ok(v2(row[0].as_f64().context("radial station")?, row[1].as_f64().context("axial station")?))
        }).collect::<Result<Vec<_>>>()?;
        let solid = Plane::XZ.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(0., 1.))?
            .rotate(V3::ZERO, V3::X, 180.).translate(v3(0., 0., depth));
        let name = format!("asse-{side}-cuff");
        println!("{}", write_part(&output, &name, &[Body {
            name: &name, color: Some(numbers.color("color")?), solid: &solid,
        }])?);
    }
    Ok(())
}
