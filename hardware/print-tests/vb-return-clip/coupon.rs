//! Crops the V-B return clip and its full lid footing from the production solid for a fit print.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Solid, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const LID: &str = "hardware/printed-parts/cold-core/foam-cap";
const PIECE: &str = "foam-cap-lid-top";
const NAME: &str = "vb-return-clip";
const MARGIN: f64 = 3.;

fn hash(data: &[u8]) -> String {
    format!("{:x}", Sha256::digest(data))
}

fn main() -> Result<()> {
    let lid = Path::new(LID);
    let out = Path::new("hardware/print-tests/vb-return-clip/parts");
    let regions_path = lid.join("fore-snap-print-regions.json");
    let production: Value = serde_json::from_slice(&fs::read(&regions_path)?)?;
    let lid_stl = hash(&fs::read(lid.join(format!("{PIECE}.stl")))?);
    ensure!(
        production["native_artifact_sha256"][PIECE][".stl"] == lid_stl,
        "regenerate the lid's print regions for this export"
    );
    let rows = production["pieces"][PIECE]
        .as_array()
        .context("lid print regions")?;
    let seat = rows
        .iter()
        .find(|row| row["name"] == "V-B return clip and lid root")
        .context("V-B clip region")?;
    let [x0, x1, y0, y1, _, z1]: [f64; 6] = serde_json::from_value(seat["applied_source_bounds_mm"].clone())?;
    let model = lid.join(format!("{PIECE}.step.npz"));
    let bodies = hsm_kernel::import::model(&model)?;
    let lo = v3(x0 - MARGIN, y0 - MARGIN, bodies[0].solid.bounds().min.z - MARGIN);
    let hi = v3(x1 + MARGIN, y1 + MARGIN, z1 + MARGIN);
    let crop = bodies[0].solid.intersect(&Solid::cuboid(lo, hi))?;
    crop.check()?;
    ensure!(
        crop.components().len() == 1,
        "the clip and lid footing must be one print"
    );
    fs::create_dir_all(out)?;
    let stl = stl_bytes(&[&crop])?;
    fs::write(out.join(format!("{NAME}.stl")), &stl)?;
    let mut modifiers = vec![];
    for row in rows {
        let [a, b, c, d, e, f]: [f64; 6] = serde_json::from_value(row["applied_source_bounds_mm"].clone())?;
        let bounds = [
            a.max(lo.x),
            b.min(hi.x),
            c.max(lo.y),
            d.min(hi.y),
            e.max(lo.z),
            f.min(hi.z),
        ];
        if bounds.chunks_exact(2).any(|span| span[0] >= span[1]) {
            continue;
        }
        let mut modifier = row.clone();
        modifier.as_object_mut().unwrap().remove("world_bounds_mm");
        modifier["applied_source_bounds_mm"] = json!(bounds);
        modifier["machine_bounds_mm"] = json!(bounds);
        modifiers.push(modifier);
    }
    let regions = json!({
        "producer": "hardware/print-tests/vb-return-clip/coupon.rs",
        "source_print_regions": regions_path, "source_print_regions_sha256": hash(&fs::read(regions_path)?),
        "native_artifact_sha256": {NAME: {".stl": hash(&stl)}}, "pieces": {NAME: modifiers},
    });
    fs::write(
        out.join(format!("{NAME}.print-regions.json")),
        serde_json::to_vec_pretty(&regions)?,
    )?;
    let bounds = crop.bounds();
    let record = json!({
        "source_model": model, "source_model_sha256": hash(&fs::read(&model)?), "source_stl_sha256": lid_stl,
        "coupon_stl_sha256": hash(&stl), "bounds_mm": [bounds.min.to_array(), bounds.max.to_array()],
        "volume_mm3": crop.volume(), "connected_solids": 1, "watertight": true,
    });
    fs::write(out.join("geometry.json"), serde_json::to_vec_pretty(&record)?)?;
    Ok(())
}
