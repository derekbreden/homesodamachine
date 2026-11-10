// samples.rs retains production contact surfaces and crops the faucet in its manufacturing pose.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Font, HAlign, Kind, Plane, Solid, VAlign, stl_bytes, v3};
use serde_json::{Value, json};

fn point(v: &Value) -> Result<hsm_kernel::V3> {
    Ok(v3(v[0].as_f64().context("x")?, v[1].as_f64().context("y")?, v[2].as_f64().context("z")?))
}

fn main() -> Result<()> {
    let dir = hsm_sandbox::out()?;
    let mut spec: Value = serde_json::from_slice(&std::fs::read(dir.join("inputs/spec.json"))?)?;
    let font = Font::find("Helvetica Neue", Kind::Bold)?;
    let label_height = spec["label_height_mm"].as_f64().context("label height")?;
    let mut output = Vec::new();
    for family in spec["families"].as_array_mut().context("families")? {
        let id = family["id"].as_str().context("family id")?.to_owned();
        let source = hsm_kernel::import::model(dir.join("inputs").join(format!("{id}.npz")))?;
        let rotation = family["rotation_x_degrees"].as_f64().unwrap_or(0.);
        let posed = source[0].solid.rotate(v3(0., 0., 0.), v3(1., 0., 0.), rotation);
        let lift = if family["normalize_pose_to_original_bed"].as_bool().unwrap_or(false) {
            -posed.bounds().min.z
        } else { 0. };
        let posed = posed.translate(v3(0., 0., lift));
        let crop = posed.intersect(&Solid::cuboid(point(&family["crop_min_mm"])? ,point(&family["crop_max_mm"])?))?;
        ensure!(crop.components().len() == 1, "{id} needs a connected production crop");
        let min_z = crop.bounds().min.z;
        family["actual_crop_min_z_mm"] = json!(min_z);
        family["source_pose_bed_lift_mm"] = json!(lift);
        let name = format!("{id}D");
        let labeled = if family["label_center_world_mm"].is_null() {
            crop
        } else {
            let center = point(&family["label_center_world_mm"])?;
            let letters = Plane::XY.text(&font, &name, 3., label_height + 0.05,
                HAlign::Center, VAlign::Center)?.translate(center - v3(0., 0., 0.05));
            crop.union(&letters)?
        };
        ensure!(labeled.components().len() == 1, "{name} label attaches to existing stock");
        let printed = labeled.translate(v3(0., 0., -min_z));
        printed.check()?;
        std::fs::write(dir.join(format!("{name}.stl")), stl_bytes(&[&printed])?)?;
        let b = printed.bounds();
        output.push(json!({"id":name,"family":id,"condition":"D",
            "bounds_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]],
            "volume_mm3":printed.volume(),"posed_z_to_print_z_mm":-min_z,
            "rotation_x_degrees":rotation,"source_pose_bed_lift_mm":lift,
            "watertight":true,"solids":1}));
    }
    std::fs::write(dir.join("geometry.json"), serde_json::to_vec_pretty(&json!({"spec":spec,"specimens":output}))?)?;
    println!("{}", dir.join("geometry.json").display());
    Ok(())
}
