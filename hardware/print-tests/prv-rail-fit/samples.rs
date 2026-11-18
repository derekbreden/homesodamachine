//! Paired production crops expose the west rail and PRV chase for a sliding fit trial.

use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{args, write_part};
use hsm_kernel::{Body, Solid, V3, import, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::Path;

fn point(value: &Value) -> Result<V3> {
    Ok(v3(
        value[0].as_f64().context("x")?,
        value[1].as_f64().context("y")?,
        value[2].as_f64().context("z")?,
    ))
}

fn digest(path: &Path) -> Result<String> {
    Ok(format!("{:x}", Sha256::digest(std::fs::read(path)?)))
}

fn clipped_bounds(bounds: &Value, low: V3, high: V3) -> Result<Option<Value>> {
    let entries = bounds.as_array().context("region bounds")?;
    let mut values = [0.0; 6];
    for (axis, (start, end)) in [(low.x, high.x), (low.y, high.y), (low.z, high.z)]
        .into_iter().enumerate()
    {
        values[axis * 2] = entries[axis * 2].as_f64().context("region minimum")?.max(start);
        values[axis * 2 + 1] = entries[axis * 2 + 1].as_f64().context("region maximum")?.min(end);
        if values[axis * 2] >= values[axis * 2 + 1] {
            return Ok(None);
        }
    }
    Ok(Some(json!(values)))
}

fn print_features(source: &Value, low: V3, high: V3, name: &str, stl: &Path) -> Result<Value> {
    let mut result = json!({
        "producer": "prv-rail-fit",
        "source_stl_sha256": digest(stl)?,
        "boundary_overlap_mm": source["boundary_overlap_mm"],
    });
    for key in ["support_free_regions", "bridge_regions", "support_regions"] {
        let mut regions = Vec::new();
        for region in source[key].as_array().into_iter().flatten() {
            let Some(bounds) = clipped_bounds(&region["bounds_source_mm"], low, high)? else { continue };
            let mut cropped = region.clone();
            cropped["bounds_source_mm"] = bounds;
            if let Some(blocking) = region.get("blocking_bounds_source_mm") {
                cropped["blocking_bounds_source_mm"] = clipped_bounds(blocking, low, high)?
                    .context("selected region blocker")?;
            }
            if name == "prv-rail-bottom" && region["name"] == "PRV vent mouth" {
                let passage = &cropped["bounds_source_mm"];
                cropped["blocking_bounds_source_mm"] = json!([
                    low.x, high.x, passage[2], passage[3], low.z, high.z,
                ]);
                cropped["reason"] = json!("Keep the open vent passage clear while the neighboring bottom rail bearing receives its cavity-floor trees.");
            }
            regions.push(cropped);
        }
        result[key] = json!(regions);
    }
    let mut stock = Vec::new();
    if name == "prv-rail-top" {
        for row in source["removable_support_stock"].as_array().into_iter().flatten() {
            let x = row["center_x_mm"].as_f64().context("rail cap center")?;
            let span = row["span_y_mm"].as_array().context("rail span")?;
            let start = span[0].as_f64().context("rail start")?.max(low.y);
            let end = span[1].as_f64().context("rail end")?.min(high.y);
            if x <= low.x || x >= high.x || start >= end {
                continue;
            }
            let mut cropped = row.clone();
            cropped["span_y_mm"] = json!([start, end]);
            stock.push(cropped);
        }
    }
    result["removable_support_stock"] = json!(stock);
    Ok(result)
}

fn main() -> Result<()> {
    let (numbers, out) = args()?;
    std::fs::create_dir_all(&out)?;
    let source_features = Path::new(numbers.text("top_print_features")?);
    let features: Value = serde_json::from_slice(&std::fs::read(source_features)?)?;
    let mut records = Vec::new();
    let mut solids = Vec::new();
    for row in numbers.get("pieces")?.as_array().context("pieces")? {
        let name = row["name"].as_str().context("coupon name")?;
        let path = Path::new(row["model"].as_str().context("production model")?);
        let mut source = import::model(path)?;
        ensure!(source.len() == 1, "one production solid in {}", path.display());
        let source = source.remove(0);
        let low = point(&row["crop_min_mm"])?;
        let high = point(&row["crop_max_mm"])?;
        let solid = source.solid.intersect(&Solid::cuboid(low, high))?;
        solid.check()?;
        ensure!(solid.components().len() == 1, "{name} is one connected production crop");
        println!("{}", write_part(&out, name, &[Body { name, color: source.color, solid: &solid }])?);
        let stl = out.join(format!("{name}.stl"));
        let native = print_features(&features, low, high, name, &stl)?;
        std::fs::write(out.join(format!("{name}.print-features.json")), serde_json::to_vec_pretty(&native)?)?;
        let bounds = solid.bounds();
        records.push(json!({
            "name": name,
            "source_model": path,
            "source_sha256": digest(path)?,
            "source_crop_mm": [low.to_array(), high.to_array()],
            "actual_bounds_mm": [bounds.min.to_array(), bounds.max.to_array()],
            "stl_sha256": digest(&stl)?,
            "volume_mm3": solid.volume(),
            "print_up_source": row["print_up_source"],
            "production_bed_source_z_mm": row["production_bed_source_z_mm"],
            "coupon_bed_source_z_mm": row["coupon_bed_source_z_mm"],
            "omitted_ordinary_layers": row["omitted_ordinary_layers"],
        }));
        solids.push(solid);
    }
    let result = json!({
        "purpose": "Bind the paired vent and rail fit specimens to their production solids, crops and layer phase.",
        "pieces": records,
        "seated_overlap_mm3": solids[0].shared_volume(&solids[1])?,
        "production_print_features": source_features,
        "production_print_features_sha256": digest(source_features)?,
    });
    std::fs::write(out.join("geometry.json"), serde_json::to_vec_pretty(&result)?)?;
    Ok(())
}
