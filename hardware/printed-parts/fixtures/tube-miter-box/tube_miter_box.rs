//! The two open tube troughs and razor slot, in the original upright print frame.
use anyhow::{ensure, Result};
use hsm_kernel::part::{args, write_printed, Numbers};
use hsm_kernel::{v3, Body, Solid, V3};

fn block(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

fn build(n: &Numbers) -> Result<Solid> {
    let size = n.list("block")?;
    let (width, length, height) = (size[0], size[1], size[2]);
    let floor = n.f("trough_floor")?;
    let mut cuts = vec![];
    for trough in n.list("troughs")?.chunks_exact(3) {
        let (x, radius) = (trough[0], trough[1]);
        let axis = floor + radius;
        cuts.push(Solid::cylinder(v3(x, -1.0, axis), V3::Y, radius, length + 2.0)?);
        cuts.push(block(x - radius, x + radius, -1.0, length + 1.0, axis, height + 1.0));
    }
    let (y0, y1) = n.pair("slot_y")?;
    let half_slot = n.f("slot_length")? / 2.0;
    cuts.push(block(-half_slot, half_slot, y0, y1, n.f("slot_floor")?, height + 1.0));
    let body = block(-width / 2.0, width / 2.0, 0.0, length, 0.0, height).cut_all(&cuts)?;
    body.check()?;
    ensure!(body.components().len() == 1 && body.volume() > 0.0,
            "tube miter box must be one closed positive-volume body");
    let blade = n.list("razor_bounds")?;
    let razor = block(blade[0], blade[1], blade[2], blade[3], blade[4], blade[5]);
    ensure!(body.shared_volume(&razor)? <= 1e-6,
            "razor at the end of its stroke meets the block");
    ensure!(floor > blade[4], "razor edge does not pass the tube floor");
    let actual = body.bounds().size();
    ensure!(actual.to_array().iter().zip(&size).all(|(a, b)| (a - b).abs() <= 1e-6),
            "unexpected print envelope");
    Ok(body)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let body = build(&n)?;
    // This bench fixture keeps its existing STEP/STL output contract. Its fine
    // model binds the actual printed facets; it has no viewer payload.
    println!("{}", write_printed(&out, "tube-miter-box", &[Body {
        name: "tube-miter-box", color: Some(n.color("color")?), solid: &body,
    }])?);
    Ok(())
}
