//! Four blind WAGO pocket sections with a solid rim to lever each removable tree out by its foot.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Solid, V3, reads, v3, write_stl};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

/// The openings are expressed in their print frames. X runs from the mouth to the blind back.
struct Pocket {
    name: &'static str,
    marks: usize,
    width: f64,
    height: f64,
    depth: f64,
}

const FLOOR: f64 = 7.16;
const CHEEK: f64 = 8.0;
const BACK: f64 = 8.0;
const ROOF: f64 = 6.0;

/// Measure the true exposed aperture from the same floor-tree record consumed by its full plate.
fn production_pocket(name: &'static str, marks: usize, site: &str, record: &str) -> Result<Pocket> {
    let features = reads::json(record)?;
    let stock_name = format!("{site} insertion pocket WAGO pocket floor tree");
    let tree = features["removable_support_stock"].as_array().context("removable support stock")?
        .iter().find(|row| row["name"] == stock_name && row["shape"] == "pocket_floor_tree")
        .with_context(|| format!("{record} has no tree for {site}"))?;
    let [x0, x1, y0, y1, z0, z1]: [f64; 6] = serde_json::from_value(tree["bounds_source_mm"].clone())?;
    // Remove floating-point cancellation from subtracting world coordinates in millimetres.
    let span = |end: f64, start: f64| ((end - start) * 1_000.0).round() / 1_000.0;
    Ok(Pocket { name, marks, width: span(y1, y0), height: span(z1, z0), depth: span(x1, x0) })
}

/// Keep an uninterrupted floor, side cheeks, roof and rear wall around the entire extraction path.
fn coupon(dir: &Path, p: &Pocket) -> Result<()> {
    let half = p.width / 2.0;
    let ceiling = FLOOR + p.height;
    let top = ceiling + ROOF;
    let stock = Solid::cuboid(v3(0.0, -half - CHEEK, 0.0), v3(p.depth + BACK, half + CHEEK, top));
    let slot = Solid::cuboid(v3(-1.0, -half, FLOOR), v3(p.depth, half, ceiling));
    let mut cuts = vec![slot];
    // Recess the identification dots into the top of the back wall, away from the pry edge.
    for dot in 0..p.marks {
        let y = (dot as f64 - (p.marks - 1) as f64 / 2.0) * 3.1;
        cuts.push(Solid::cylinder(v3(p.depth + BACK / 2.0, y, top - 0.72), V3::Z, 0.9, 1.0)?);
    }
    let body = stock.cut_all(&cuts)?.simplified()?;
    body.check()?;
    ensure!(body.components().len() == 1, "{} must be a single grip body", p.name);
    let stl = dir.join(format!("{}.stl", p.name));
    write_stl(&stl, &[&body])?;
    let pocket_bounds = [0.0, p.depth, -half, half, FLOOR, ceiling];
    let features = json!({
        "producer": "wago-pocket-pry",
        "source_stl_sha256": format!("{:x}", Sha256::digest(fs::read(stl)?)),
        "boundary_overlap_mm": 0.01,
        "support_free_regions": [{
            "name": format!("{} native tree exclusion", p.name),
            "bounds_source_mm": pocket_bounds,
            "review_interior": false,
            "reason": "The separate removable tree occupies the pocket. Its base lands on the floor and its removal path opens at the mouth."
        }],
        "bridge_regions": [{
            "name": format!("{} roof", p.name),
            "bounds_source_mm": [-0.1, p.depth + 3.0, -half - 3.0, half + 3.0, ceiling - 0.25, ceiling + 3.0],
            "bridge_print_axis_source": [0, 1, 0],
            "reason": "Lay the ceiling across the opening between the two solid sidewall landings, as on its parent."
        }],
        "removable_support_stock": [{
            "name": format!("Removable MAG WAGO pocket floor tree {}", p.name),
            "shape": "pocket_floor_tree",
            "reason": "Test extraction of the same single floor foot, broad roof interface and release gaps used in the complete part.",
            "bounds_source_mm": pocket_bounds,
            "print_up_source": [0, 0, 1],
            "mouth_direction_source": [-1, 0, 0]
        }]
    });
    fs::write(dir.join(format!("{}.print-features.json", p.name)), serde_json::to_string_pretty(&features)? + "\n")?;
    Ok(())
}

fn main() -> Result<()> {
    let dir = hsm_sandbox::out()?;
    let front = "hardware/printed-parts/enclosure/enclosure/enclosure-front-top.print-features.json";
    let rear = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.print-features.json";
    let lid = "hardware/printed-parts/cold-core/foam-cap/fore-snap-print-regions.json";
    for (name, marks, site, record) in [
        ("front-420", 1, "wago-mana", front),
        ("front-415", 2, "wago-manb", front),
        ("rear-413", 3, "wiring-junction-compressor-n", rear),
        ("lid-413", 4, "wago-gnd", lid),
    ] {
        coupon(&dir, &production_pocket(name, marks, site, record)?)?;
    }
    Ok(())
}
