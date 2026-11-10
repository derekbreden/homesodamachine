//! samples.rs makes singly anchored inclined roofs for support-release comparisons.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Font, HAlign, Kind, Plane, Profile, Solid, VAlign, stl_bytes, v2, v3};
use serde_json::{Value, json};

fn main() -> Result<()> {
    let out = hsm_sandbox::out()?;
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../..");
    let spec: Value = serde_json::from_slice(&std::fs::read(root.join("hardware/print-tests/petgf-dense-roofs/inclines/matrix.json"))?)?;
    let shape = &spec["geometry"];
    let value = |key: &str| shape[key].as_f64().with_context(|| key.to_string());
    let (wall, reach, width, start, thick) = (value("wall_mm")?, value("reach_mm")?, value("width_mm")?, value("underside_start_z_mm")?, value("roof_thickness_z_mm")?);
    let font = Font::find("Helvetica Neue", Kind::Bold)?;
    let mut records = Vec::new();
    for plate in spec["plates"].as_array().context("plates")? {
        for row in plate["samples"].as_array().context("samples")? {
            let id = row["id"].as_str().context("id")?;
            let angle = row["angle_from_bed_deg"].as_f64().context("angle")?;
            let slope = angle.to_radians().tan();
            let points = vec![v2(0., 0.), v2(wall, 0.), v2(wall, start),
                v2(wall + reach, start + reach * slope), v2(wall + reach, start + reach * slope + thick),
                v2(0., start - wall * slope + thick)];
            let profile = Profile::polygon(&points);
            let roof = Plane::XZ.extrude(&profile, width)?.translate(v3(0., width / 2., 0.));
            let tab = Solid::cuboid(v3(-7., -width / 2., 0.), v3(0.1, width / 2., 2.));
            let label = Plane::XY.text(&font, id, 3., 0.53, HAlign::Center, VAlign::Center)?.translate(v3(-3.4, 0., 1.95));
            let coupon = roof.union(&tab)?.union(&label)?;
            ensure!(coupon.components().len() == 1, "{id} must be one connected coupon");
            coupon.check()?;
            std::fs::write(out.join(format!("{id}.stl")), stl_bytes(&[&coupon])?)?;
            let b = coupon.bounds();
            records.push(json!({"id":id,"angle_from_bed_deg":angle,"bounds_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]],"volume_mm3":coupon.volume(),"single_body":true}));
        }
    }
    std::fs::write(out.join("geometry.json"), serde_json::to_vec_pretty(&json!({"purpose":"Bind the single-wall incline coupons to their authored geometry.","specimens":records}))?)?;
    Ok(())
}
